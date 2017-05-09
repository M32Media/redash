import json, os
from redash.handlers import routes
from flask import request, render_template, jsonify, make_response
from flask_restful import Resource, abort
from redash import models
from redash.tasks import refresh_queries_http, get_tasks
from funcy import project


"""
API key validation decorator
"""
def validate_api_key(func):
    
    def validation_wrapper():
        
        #print(os.getenv('REFRESH_TOKEN'))        

        token = request.values.get('token')
        ext = request.args.get('ext') or 'json'

        print(request.headers.get('User-Agent'))

        #Verify presence of token and check if it exists in database
        if token:

            #Get Query ID if one is associated with token
            query = models.Query.get_by_token(token)

            if (query and query.latest_query_data_id ):

                return func(query.latest_query_data_id, ext)

            #When we have query object but the query is not working
            elif (query and not query.latest_query_data_id):

                message = {
                    'message': "Something is wrong with this query",
                }

                resp = jsonify(message)
                resp.status_code = 404

                return resp

            #When the token is invalid
            else:
                message = {
                    'message': "Your API token is invalid please contact M32",
                }

                resp = jsonify(message)
                resp.status_code = 401

                return resp

        #When token is not specified
        else:

            message = {
                'message': "No token found",
            }

            resp = jsonify(message)
            resp.status_code = 401

            return resp
        
    return validation_wrapper

"""
Expose Query Data to users that have an API key. Each API key is linked to one query.
"""
@routes.route('/api/query/data', methods=['GET'])
@validate_api_key
def ExposeQueryData(data_id, ext):

    result = models.db.session.query(models.QueryResult).filter(models.QueryResult.id == data_id).one()

    #Check the data format we want (Case Insensitive)
    if ext.lower() == 'csv':
        headers = {'Content-Type': "text/csv; charset=UTF-8"}
        response = make_response(result.make_csv_content(), 200, headers)
    elif ext.lower() == 'xlsx':
        headers = {'Content-Type': "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"}
        response = make_response(result.make_excel_content(), 200, headers)
    else:
        headers = {'Content-Type': "application/json"}
        response = make_response(result.data, 200, headers)
    
    return response

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


