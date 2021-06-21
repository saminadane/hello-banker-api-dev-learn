from flask import request
from flask_restful import Resource
from modules.dbHelper import getCategories
from modules.miscHelper import categoryStats
        

class CategoriesApi(Resource):
    def get(self):
        type = request.args.get("type", default="all")
        return getCategories(type)

class CategoryStatsApi(Resource):
    def get(self):
        category = request.args.get("category", default=None)
        return categoryStats(category)