from redash.handlers import routes
from flask import request, render_template, jsonify
from flask_restful import Resource, abort



"""
API key validation decorator
"""
def validate_api_key(func):

    def wrapper():

        #Verify that the token is present
        token = request.args.get('token')

        if token:

            #Verify validity of token

            return func()

        else:
            message = {
                'message': "DON'T EVEN TRY YOU MONGREL",
            }

            resp = jsonify(message)
            resp.status_code = 501

            return resp
        
        

    return wrapper

"""
Expose Query Data to users that have an API key. Each API key is linked to one query.
"""
@routes.route('/api/query/data', methods=['GET'])
@validate_api_key
def ExposeQueryData():

    print("API call")

    return 'DATA'
