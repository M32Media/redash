import json, os
from redash.handlers import routes
from flask import request, render_template, jsonify, make_response
from flask_restful import Resource, abort
from redash import models
from redash.tasks import refresh_queries_http, get_tasks, refresh_query_tokens
from funcy import project
from redash.authentication.account import send_api_token

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

    print(ext)

    print("Dashgroup : {} - Sub : {} - Dashboard : {}".format(dashgroup_name, subcategory_name, dashboard_name));

    dashgroup = models.Dashgroup.get_by_name(dashgroup_name);

    #If dashgroup with the specified name exists
    if dashgroup:

        print("Dashgroup found")

        #Verify user has access to this dashgroup
        if models.UserDashgroup.find_by_ids(user.id, dashgroup.id):

            dashboard = models.Dashboard.get_by_name("{}:{}:{}".format(dashgroup_name,subcategory_name,dashboard_name))

            #If a dashboard with this name exists
            if dashboard:

                print("Dashboard found")

                visualization = models.Visualization.get_by_url_tag(url_tag)

                #Analyze slug here
                if visualization:

                    print("Visualization found")

                    #Check if the dashboard contains a widget with visualization
                    if models.Widget.get_by_ids(dashboard.id, visualization.id):

                        
                        #Find the query
                        query = models.db.session.query(models.Query).filter(models.Query.id == visualization.query_id).first()

                        if query :

                            result = models.db.session.query(models.QueryResult).filter(models.QueryResult.id == query.latest_query_data_id).first()

                            #Check the data format we want (Case Insensitive)
                            if ext.lower() == 'csv':
                                headers = {'Content-Type': "text/csv; charset=UTF-8"}
                                response = make_response(result.make_csv_content(), 200, headers)
                            else:
                                headers = {'Content-Type': "application/json"}
                                response = make_response(result.data, 200, headers)
                            
                            return response

                        else:

                            print("No Query found")

                            return custom_response(403)
                        
                    else:

                        print("No widget with visualization in this dashboard")

                        return custom_response(403)

                else:

                    print("No visualization with slug")

                    return custom_response(403)

            else:

                print("Dashboard does not exist")

                return custom_response(403)

        else:

            print("Not allowed to access this dashgroup")

            return custom_response(403)

    else:

        print("Dashgroup does not exist")

        return custom_response(403)


"""
This Route creates the celery tasks to query data from sources. It returns the IDs of those tasks
and we have to GET /api/queries/refresh/tasks to know their statuses
"""
@routes.route('/api/queries/refresh', methods=['POST'])
def RefreshQueriesData():

    req = request.get_json(force=True)

    #Convert object to dict
    token = req['token']

    #If token was valid
    if token == os.getenv('REFRESH_TOKEN'):

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

@routes.route('/api/update/tags', methods=['GET'])
def UpdateTags():

    models.Visualization.update_url_tags()

    return custom_response(200, "Updated Tags")

def custom_response(code, message="Something went wrong"):

    message = {
        'message': message,
    }

    resp = jsonify(message)
    resp.status_code = code

    return resp




