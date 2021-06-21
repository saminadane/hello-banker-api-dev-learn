from flask import request
from flask_restful import Resource
from modules.dbHelper import getTransactions, addTransactionsDB, fundTransferDB, getDescriptionSuggestions


class TransactionsListApi(Resource):
    def get(self):
        account = request.args.get("account", default=None)
        period = request.args.get("period", default=None)
        year = request.args.get("year", default=None)
        month = request.args.get("month", default=None)
        return getTransactions(account, period, year, month)


class AddTransactionApi(Resource):
    def post(self):
        json_data = request.get_json(force=True)
        date = json_data["date"]
        notes = json_data["notes"]
        amount = json_data["amount"]
        account = json_data["account"]
        category = json_data["category"]
        return addTransactionsDB(date, notes, amount, category, account)


class FundTransactionsApi(Resource):
    def post(self):
        json_data = request.get_json(force=True)
        date = json_data["date"]
        notes = json_data["notes"]
        amount = json_data["amount"]
        fromAccount = json_data["fromAccount"]
        toAccount = json_data["toAccount"]
        return fundTransferDB(date, notes, amount, fromAccount, toAccount)

class GetDescriptionSuggestionsApi(Resource):
    def get(self):
        keyword = request.args.get("keyword", default=None)
        type = request.args.get("type", default="regular")
        return getDescriptionSuggestions(keyword, type)