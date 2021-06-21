from flask_restful import Resource
from modules.dbHelper import getAccounts, getDistinctAccountTypes


class AccountsApi(Resource):
    def get(self):
        return getAccounts()

class DistinctAccountTypesApi(Resource):
    def get(self):
        return getDistinctAccountTypes()
