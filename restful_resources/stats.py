from flask import request
from flask_restful import Resource
from modules.dbHelper import getMonthStats
from modules.miscHelper import inExStats

class MonthStatsApi(Resource):
    def get(self):
        month = request.args.get("month", default=None)
        return getMonthStats(month)

class InExStatsApi(Resource):
    def get(self):
        return inExStats()