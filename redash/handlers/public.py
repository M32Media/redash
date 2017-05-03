from redash.handlers import routes
from flask import request, render_template, jsonify, make_response
from flask_restful import Resource, abort
from redash import models

"""
API key validation decorator
"""
def validate_api_key(func):

    def validation_wrapper():

        token = request.args.get('token')
        ext = request.args.get('ext') or 'json'

        #Verify presence of token and check if it exists in database
        if token:

            #Get Query ID if one is associated with token
            data_id = models.Query.get_by_token(token)

            if data_id:

                return func(data_id, ext)

            else:

                message = {
                    'message': "You don't have the credentials",
                }

                resp = jsonify(message)
                resp.status_code = 401

                return resp

        else:

            message = {
                'message': "You don't have the credentials",
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
