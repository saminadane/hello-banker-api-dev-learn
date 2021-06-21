import os
from flask import current_app as app
from flask import jsonify


def getDBPath():
    return os.path.join(app.config['SQLITE_DB_DIR'],
                        app.config['SQLITE_DB_FILE'])


def categoryStats(category):
    from modules.dbHelper import getCategoryStats, getDetailedCategoryStats
    year_month_data = getCategoryStats(category, period="YEAR_MONTH")
    year_data = getCategoryStats(category, period="YEAR")
    year_month_stats = getDetailedCategoryStats(year_month_data,
                                                period="YEAR_MONTH")
    year_stats = getDetailedCategoryStats(year_data, period="YEAR")
    finalStats = [{
        "year_month_data": year_month_data
    }, {
        "year_data": year_data
    }, {
        "year_month_stats": year_month_stats
    }, {
        "year_stats": year_stats
    }]
    return jsonify(finalStats)


def inExStats():
    from modules.dbHelper import getInEx
    incomeMonthly = getInEx("income", "monthly")
    expenseMonthly = getInEx("expense", "monthly")
    incomeYearly = getInEx("income", "yearly")
    expenseYearly = getInEx("expense", "yearly")
    data = [{
        "income_monthly": incomeMonthly
    }, {
        "expense_monthly": expenseMonthly
    }, {
        "income_yearly": incomeYearly
    }, {
        "expense_yearly": expenseYearly
    }]
    return jsonify(data)
