import json, os
from datetime import datetime
from redash.handlers import routes
from flask import request, render_template, jsonify, make_response
from flask_restful import Resource, abort
from redash import models, utils
from redash.tasks import refresh_queries_http, get_tasks, refresh_query_tokens, refresh_selected_queries
from funcy import project
from redash.authentication.account import send_api_token
from redash.utils import collect_query_parameters, collect_parameters_from_request, json_dumps
from redash.cli.users import create as create_user

"""
API key validation decorator
"""
def validate_api_key(func):

    def validation_wrapper(dashgroup_name, subcategory_name, dashboard_name, url_tag):

        #print(os.getenv('REFRESH_TOKEN'))

        token = request.values.get('token')
        ext = request.args.get('ext') or 'json'

        print(request.headers.get('User-Agent'))

        #Verify presence of token and check if it exists in database
        if token:

            #Get Query ID if one is associated with token
            user = models.User.get_by_token(token)

            if (user):
                return func(dashgroup_name, subcategory_name, dashboard_name, url_tag, user, ext)

            #When the token is invalid
            else:
                return custom_response(401, "Your token is invalid please contact M32")

        #When token is not specified
        else:

            return custom_response(401, "No token found")

    return validation_wrapper



"""
Expose Data to client
"""
@routes.route('/api/data/<dashgroup_name>/<subcategory_name>/<dashboard_name>/<url_tag>', methods=['GET'])
@validate_api_key
def ExposeData(dashgroup_name, subcategory_name, dashboard_name, url_tag, user, ext):

    print("Dashgroup : {} - Sub : {} - Dashboard : {}".format(dashgroup_name, subcategory_name, dashboard_name));

    dashgroup = models.Dashgroup.get_by_name(dashgroup_name);

    if not dashgroup:
        print("Dashgroup does not exist")
        return custom_response(403)

    # Check if this user has admin rights
    admin = False

    for _id in user.group_ids:

        #Get the group associated with this id
        group = models.Group.get_by_id(_id)

        print(group.permissions)

        # Check permissions
        if not admin:
            admin = all(x in group.permissions for x in ['admin', 'super_admin'])

    #Verify user has access to this dashgroup
    if not models.UserDashgroup.find_by_ids(user.id, dashgroup.id):

        print("Not allowed to access this dashgroup")

        if not admin:
            print("Not Admin")
            return custom_response(403)

    dashboard = models.Dashboard.get_by_name("{}:{}:{}".format(dashgroup_name,subcategory_name,dashboard_name))

    if not dashboard:
        print("Dashboard does not exist in this dashgroup")
        return custom_response(403)

    visualizations = models.Visualization.get_by_url_tag(url_tag)

    if not visualizations:
        print("No visualization with slug")
        return custom_response(403)

    visualization = models.Widget.get_by_ids(dashboard.id, visualizations)

    if not visualization:
        print("No widget with visualization in this dashboard")
        return custom_response(403)

    query = models.db.session.query(models.Query).filter(models.Query.id == visualization.query_id).first()

    if not query:
        print("No Query Found")
        return custom_response(403)

    result = models.db.session.query(models.QueryResult).filter(models.QueryResult.id == query.latest_query_data_id).first()

    #Check the data format we want (Case Insensitive)
    if ext.lower() == 'csv':
        headers = {'Content-Type': "text/csv; charset=UTF-8"}
        response = make_response(result.make_csv_content(), 200, headers)
    else:
        headers = {'Content-Type': "application/json"}
        response = make_response(result.data, 200, headers)

    return response


@routes.route('/api/embeded/query/<visualization_id>/<query_token>', methods=['POST'])
def embededQueryResource(query_token, visualization_id):
    query = models.Query.get_by_token(query_token)

    #As for the EmbededQueryResultResource, this is sketchy and not really secure.
    referrer = request.get_json(force=True)["referrer"]
    if not models.VisualizationReferrer.find_by_ids(visualization_id, referrer):
        abort(403)

    result = query.to_dict(with_visualizations=True)
    headers = {'Content-Type': "application/json"}
    print(result)
    return make_response(json_dumps(result), 200, headers)

@routes.route('/api/embeded/result/<visualization_id>/<query_token>', methods=['POST'])
def embededQueryResultResource(visualization_id, query_token):

    def make_json_response(query_result):
        data = json.dumps({'query_result': query_result.to_dict()}, cls=utils.JSONEncoder)
        headers = {'Content-Type': "application/json"}
        return make_response(data, 200, headers)

    query = models.Query.get_by_token(query_token)
    query_result_id = query.latest_query_data_id
    query_result = models.QueryResult.get_by_id(query.latest_query_data_id)
    #This is unsafe, anyone could change the referrer in their post request but at least the route uses query api tokens.
    referrer = request.get_json(force=True)["referrer"]
    if not models.VisualizationReferrer.find_by_ids(visualization_id, referrer):
        abort(403)


    response = make_json_response(query_result)

    return response

'''
This route creates a user by specyfing the dashgroup id optionally

The json payload to provide this method is:
{
    "user": "<USER_NAME>",
    "token": "<REDASH_TOKEN>"
}
'''
@routes.route('/api/users/create', methods=['POST'])
def create_user():

    try:

        req = request.get_json(force=True)

        token = req.get('token', None)
        if not token:
            message = {'message': 'Please provide a token in the request JSON'}
            resp = jsonify(message)
            resp.status_code = 401
            return resp

        name = req.get('user', None)
        if not name:
            message = {'message': 'Please provide a name for the user (BQ Dataset)'}
            resp = jsonify(message)
            resp.status_code = 401
            return resp

        # We read a file we have server-side to compare with the token we send in the request
        # TODO: This is repeated code, should be wrapped up in a function
        try:
            with open("refresh.cfg", "r") as f:

                content = f.readlines()
                content = [x.strip() for x in content]
                cfg = {}

                for c in content:
                    c = c.split("=")
                    cfg[c[0]] = c[1]

        except Exception:

            message = {
                'message': "Your API token is invalid please contact M32",
            }

            resp = jsonify(message)
            resp.status_code = 401

            return resp

        #If token was valid
        if token == cfg["refresh_token"]:

            # This is the template we use for the email, it is a non-existing made up email
            email = 'user@{user}.com'.format(user=user)
            create_user(
                email=email, name=user, groups=[], is_admin=False, google_auth=False,
                password=None, organization='default', dashgroups=user)
            headers = {'Content-Type': 'application/json'}

            # The ` character creates problems for the conversion to JSON, so we need to dump the dict
            # without the UTF-8 encoding, and encode it manually after
            response = make_response(json.dumps({'user': user}, ensure_ascii=False).encode('utf8'), 202, headers)
            return response

        else:
            message = {'message': "Your API token is invalid please contact M32"}
            resp = jsonify(message)
            resp.status_code = 401
            return resp
    except Exception as e:
        import traceback
        return traceback.format_exc()
"""
This Route creates the celery tasks to query data from sources.
"""
@routes.route('/api/queries/refresh/only_selected', methods=['POST'])
def RefreshOnlySelectedQueries():

    req = request.get_json(force=True)

    token = req.get('token', None)
    if not token:
        message = {'message': 'Please provide a token in the request JSON'}
        resp = jsonify(message)
        resp.status_code = 401
        return resp

    months = req.get('months', [])
    if not months:
        message = {'message': 'Please provide at least one month in the form YYYYMM'}
        resp = jsonify(message)
        resp.status_code = 200
        return resp

    publishers = req.get('publishers', 'ALL')
    global_queries = req.get('global_queries', False)
    non_monthly_publisher_queries = req.get('non_monthly_publisher_queries', False)
    no_query_execution = req.get('no_query_execution', False)

    # We read a file we have server-side to compare with the token we send in the request
    # TODO: This is repeated code, should be wrapped up in a function
    try:
        with open("refresh.cfg", "r") as f:

            content = f.readlines()
            content = [x.strip() for x in content]
            cfg = {}

            for c in content:
                c = c.split("=")
                cfg[c[0]] = c[1]

    except Exception:

        message = {
            'message': "Your API token is invalid please contact M32",
        }

        resp = jsonify(message)
        resp.status_code = 401

        return resp

    #If token was valid
    if token == cfg["refresh_token"]:

        jobs = refresh_selected_queries(
            months=months, publishers=publishers, global_queries=global_queries,
            non_monthly_publisher_queries=non_monthly_publisher_queries,
            no_query_execution=no_query_execution)
        headers = {'Content-Type': "application/json"}

        # The ` character creates problems for the conversion to JSON, so we need to dump the dict
        # without the UTF-8 encoding, and encode it manually after
        response = make_response(json.dumps(jobs, ensure_ascii=False).encode('utf8'), 202, headers)
        return response

    else:
        message = {'message': "Your API token is invalid please contact M32"}
        resp = jsonify(message)
        resp.status_code = 401
        return resp

"""
This Route creates the celery tasks to query data from sources. It returns the IDs of those tasks
and we have to GET /api/queries/refresh/tasks to know their statuses. This method refreshes
all queries for the Redash system
"""
@routes.route('/api/queries/refresh/all', methods=['POST'])
def RefreshAllQueriesData():

    req = request.get_json(force=True)

    #Convert object to dict
    token = req['token']

    try:
        with open("refresh.cfg", "r") as f:

            content = f.readlines()
            content = [x.strip() for x in content]
            cfg = {}

            for c in content:
                c = c.split("=")
                cfg[c[0]] = c[1]

    except Exception:

        message = {
            'message': "Your API token is invalid please contact M32",
        }

        resp = jsonify(message)
        resp.status_code = 401

        return resp

    #If token was valid
    if token == cfg["refresh_token"]:

        #Refresh all queries here
        jobs = refresh_queries_http()

        job_ids = []

        for job in jobs:
            job_ids.append(job.to_dict().get('id', None))


        data = {}
        data['tasks'] = job_ids

        headers = {'Content-Type': "application/json"}
        response = make_response(json.dumps(data), 202, headers)

        return response;

    else:

        message = {
            'message': "Your API token is invalid please contact M32",
        }

        resp = jsonify(message)
        resp.status_code = 401

        return resp

"""
This Route creates the celery tasks to query only selected data from sources.
It returns the IDs of those tasks and we have to GET /api/queries/refresh/tasks
to know their statuses. The json for the request can contain:

- a list of publishers (publishers)
- a list of months (months) in the format YYYYMM

If no parameters are specified, the queries will affect all publishers for the
current month (e.g. if this is executed on any day of June, it will refresh all
queries for all publishers that depend on June data)
"""
@routes.route('/api/queries/refresh', methods=['POST'])
def RefreshQueriesData():

    req = request.get_json(force=True)

    #Convert object to dict
    token = req['token']

    publishers = req.get('publishers', 'ALL')
    months = req.get('months', datetime.now().strftime('%Y%m'))

    publishers = publishers if type(publishers) == type(list()) else [publishers]
    months = months if type(months) == type(list()) else [months]

    try:
        with open("refresh.cfg", "r") as f:

            content = f.readlines()
            content = [x.strip() for x in content]
            cfg = {}

            for c in content:
                c = c.split("=")
                cfg[c[0]] = c[1]

    except Exception:

        message = {
            'message': "Your API token is invalid please contact M32",
        }

        resp = jsonify(message)
        resp.status_code = 401

        return resp

    #If token was valid
    if token == cfg["refresh_token"]:

        jobs = refresh_selected_queries(months, publishers)

        job_ids = []

        for job in jobs:
            job_ids.append(job.to_dict().get('id', None))

        data = {}
        data['tasks'] = job_ids

        headers = {'Content-Type': "application/json"}
        response = make_response(json.dumps(data), 202, headers)

        return response;

    else:

        message = {
            'message': "Your API token is invalid please contact M32",
        }

        resp = jsonify(message)
        resp.status_code = 401

        return resp

@routes.route('/api/queries/refresh/tasks', methods=['POST'])
def TasksStatus():

    req = request.get_json(force=True)

    #Convert object to dict
    obj = json.loads(req['tasks'])

    data = get_tasks(obj['tasks'])

    headers = {'Content-Type': "application/json"}
    response = make_response(jsonify(data), 200, headers)

    return response

@routes.route('/api/email/test', methods=['GET'])
def EmailTest():

    class CustomUser:
        name = "Test User"
        api_key = "SOMEAPIKEYDUMMY"
        email = "arnaud.girardin444@gmail.com"

    send_api_token(CustomUser())

    return custom_response(200, "Sending Email !")


def custom_response(code, message="Something went wrong"):

    message = {
        'message': message,
    }

    resp = jsonify(message)
    resp.status_code = code

    return resp
