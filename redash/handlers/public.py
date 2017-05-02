from redash.handlers import routes

"""
Expose Query Data to users that have an API key. Each API key is linked to one query.
"""
@routes.route('/api/query/data', methods=['GET'])
def ExposeQueryData():
	return 'DATA'