import sqlite3
import json
from flask import jsonify
from modules.miscHelper import getDBPath
from operator import itemgetter
import calendar


def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


def getAccounts(account='all', status='all', output="json"):
    db = sqlite3.connect(getDBPath())
    db.row_factory = dict_factory
    cursor = db.cursor()
    appendquery = statusquery = ""
    if account != "all":
        appendquery = "AND name = '%s'" % account
    if status != "all":
        statusquery = "AND status = '%s'" % status
    query = """
        SELECT name, balance, lastoperated, type, excludetotal, status
        FROM accounts
        WHERE 1 = 1 %s %s
        ORDER BY type
        """ % (appendquery, statusquery)
    cursor.execute(query)
    data = cursor.fetchall()
    db.close()
    if output is None:
        return data
    return jsonify(data)


def getIgnoredAccounts():
    ignoreAccounts = []
    accounts = getAccounts(output=None)
    for account in accounts:
        if account['excludetotal'] == 'yes':
            ignoreAccounts.append('"%s"' % account['name'])
    return ",".join(ignoreAccounts)


def getCategories(type='all'):
    db = sqlite3.connect(getDBPath())
    db.row_factory = dict_factory
    cursor = db.cursor()
    condquery = ""
    if not type == "all":
        condquery = "AND type = '%s'" % type
    query = """
        SELECT name, type FROM categories
        WHERE 1 = 1 %s
        ORDER BY type
        """ % condquery
    cursor.execute(query)
    data = cursor.fetchall()
    db.close()
    return jsonify(data)


def getDistinctAccountTypes():
    db = sqlite3.connect(getDBPath())
    db.row_factory = dict_factory
    cursor = db.cursor()
    query = """
        SELECT DISTINCT(type) as name
        FROM accounts
        ORDER BY name
        """
    cursor.execute(query)
    data = cursor.fetchall()
    db.close()
    return jsonify(data)


def getTransactions(accountname, period=None, year=None, month=None):
    db = sqlite3.connect(getDBPath())
    db.row_factory = dict_factory
    cursor = db.cursor()

    advQuery = limitQuery = ''

    if period is None:
        limitQuery = 'LIMIT 50'
    else:
        if 'PRE_' in period:
            if 'thisweek' in period:
                advQuery = "AND STRFTIME('%Y%W', opdate) = STRFTIME('%Y%W', DATE('NOW'))"
            elif 'thismonth' in period:
                advQuery = "AND opdate >= DATE('NOW', 'START OF MONTH')"
            elif 'lastmonth' in period:
                advQuery = "AND opdate BETWEEN DATE('NOW', 'START OF MONTH', '-1 MONTH') AND DATE('NOW', 'START OF MONTH')"
        elif 'selective' in period:
            advQuery = "AND STRFTIME('%Y', opdate) = '{0}' AND STRFTIME('%m', opdate) = '{1}'".format(
                year, month)

    query = "SELECT opdate, description, credit, debit, category \
            FROM transactions \
            WHERE account = '%s' %s \
            ORDER BY opdate DESC %s" \
            % (accountname, advQuery, limitQuery)

    cursor.execute(query)
    data = cursor.fetchall()
    db.close()
    return jsonify(data)


def fundTransferDB(date, notes, amount, fromAccount, toAccount):
    addTransactionsDB(date, notes, amount, "TRANSFER OUT", fromAccount)
    addTransactionsDB(date, notes, amount, "TRANSFER IN", toAccount)
    return jsonify({"status": "Funds Transfered successfully"})


def addTransactionsDB(date, notes, amount, category, account):
    db = sqlite3.connect(getDBPath())
    cursor = db.cursor()

    credit, debit, updatetype = ["NULL", amount, "debit"]
    if getCategoryType(category) == "IN":
        credit, debit, updatetype = [amount, "NULL", "credit"]

    query = """
        INSERT INTO transactions 
        VALUES('%s', '%s', '%s', %s, %s, '%s')""" % (date, notes, category,
                                                     credit, debit, account)
    cursor.execute(query)
    data = cursor.fetchall()
    db.commit()
    db.close()
    if len(data) == 0:
        if updateAccounts(account, amount, updatetype):
            returnString = {"status": "Transaction added successfully"}
        else:
            returnString = {
                "status":
                "Failed to update accounts table. But transaction recorded"
            }
    else:
        returnString = {"status": str(data[0])}

    return jsonify(returnString)


def getCategoryType(category):
    db = sqlite3.connect(getDBPath())
    cursor = db.cursor()

    query = "SELECT type FROM categories WHERE name = '%s'" % category
    cursor.execute(query)
    data = cursor.fetchone()
    db.close()
    return data[0]


def updateAccounts(name, amount, updatetype):
    db = sqlite3.connect(getDBPath())
    cursor = db.cursor()

    sign, operator = ["+", "-"]
    isassetAcc = checkAccountType(name)
    if not isassetAcc:
        sign = "-"
    if updatetype == "credit":
        operator = "+"

    query = """UPDATE accounts
            SET balance = balance %s %s%s, lastoperated = DATE('NOW')
            WHERE name = '%s'""" % (operator, sign, amount, name)
    cursor.execute(query)
    db.commit()
    db.close()
    return True


def checkAccountType(account):
    db = sqlite3.connect(getDBPath())
    cursor = db.cursor()
    isassetAcc = True

    query = "SELECT type FROM accounts WHERE name = '%s'" % account
    cursor.execute(query)
    data = cursor.fetchone()

    db.close()

    if data[0] == "Credit Card":
        isassetAcc = False
    return isassetAcc


def getMonthStats(month=None):
    db = sqlite3.connect(getDBPath())
    db.row_factory = dict_factory
    cursor = db.cursor()

    advQuery = "AND opdate >= DATE('NOW', 'START OF MONTH')"

    if not month is None:
        advQuery = "AND opdate BETWEEN DATE('NOW', 'START OF MONTH', '-1 MONTH') AND DATE('NOW', 'START OF MONTH')"

    query = """
        SELECT category, SUM(debit) AS debit, SUM(credit) AS credit
        FROM transactions
        WHERE category NOT IN ('TRANSFER IN', 'TRANSFER OUT') %s
        GROUP BY category
        ORDER BY debit DESC, credit DESC
        """ % advQuery

    cursor.execute(query)
    data = cursor.fetchall()
    db.close()
    return jsonify(data)


def getDescriptionSuggestions(keyword, type="regular", limit=10):
    db = sqlite3.connect(getDBPath())
    db.row_factory = dict_factory
    cursor = db.cursor()

    query = """
        SELECT DISTINCT(description) AS description 
        FROM transactions 
        WHERE description LIKE '%%%s%%'
        ORDER BY opdate DESC LIMIT %d
        """ % (keyword, limit)

    if not "regular" in type:
        query = """
            SELECT DISTINCT(description) AS description 
            FROM transactions 
            WHERE description LIKE '%%%s%%'
                AND category IN ('TRANSFER IN', 'TRANSFER OUT')
            ORDER BY opdate DESC LIMIT %d
            """ % (keyword, limit)

    cursor.execute(query)
    data = cursor.fetchall()
    db.close()
    return jsonify(data)


def getCategoryStats(category, period):
    db = sqlite3.connect(getDBPath())
    db.row_factory = dict_factory
    cursor = db.cursor()
    optype = "debit"
    opdateFormat = ""
    if getCategoryType(category) == "IN":
        optype = "credit"
    if period == 'YEAR_MONTH':
        opdateFormat = "STRFTIME('%Y%m', opdate)"
    else:
        opdateFormat = "STRFTIME('%Y', opdate)"

    query = """
            SELECT {0} AS x, ROUND(SUM({1})) AS y
            FROM transactions
            WHERE category = '{2}'
                AND account NOT IN ({3})
                AND category NOT IN ('TRANSFER IN','TRANSFER OUT')
            GROUP BY x
            ORDER BY x
            """.format(opdateFormat, optype, category, getIgnoredAccounts())
    cursor.execute(query)
    data = cursor.fetchall()
    db.close()
    return data


def getDetailedCategoryStats(data, period="YEAR_MONTH"):
    if data is None:
        return None
    else:
        totalSpent = sum(item["y"] for item in data)
        totalSpent = "%.2f" % totalSpent
        periodAvg = round(float(totalSpent) / float(len(data)))
        periodAvg = "%.2f" % periodAvg
        sortedData = sorted(data, key=itemgetter("y"))
        if period == "YEAR_MONTH":
            lowestPeriod = "%s %s" % (calendar.month_name[int(
                sortedData[0]["x"]) % 100], str(sortedData[0]["x"])[:-2])
            highestPeriod = "%s %s" % (calendar.month_name[int(
                sortedData[-1]["x"]) % 100], str(sortedData[-1]["x"])[:-2])
        else:
            lowestPeriod = sortedData[0]["x"]
            highestPeriod = sortedData[-1]["x"]
        lowest = {"period": lowestPeriod, "value": "%.2f" % sortedData[0]["y"]}
        highest = {
            "period": highestPeriod,
            "value": "%.2f" % sortedData[-1]["y"]
        }
        categoryStatsData = {
            "total": totalSpent,
            "average": periodAvg,
            "highest": highest,
            "lowest": lowest
        }
        return categoryStatsData


def getInEx(type, period):
    db = sqlite3.connect(getDBPath())
    db.row_factory = dict_factory
    cursor = db.cursor()

    optype = "debit" if type == "expense" else "credit"

    query = ""

    if "monthly" in period:
        query = """
            SELECT STRFTIME('%Y%m', opdate) AS x, ROUND(SUM({0})) AS y
            FROM transactions
            WHERE account NOT IN ({1})
                AND category NOT IN ('OPENING BALANCE','TRANSFER IN','TRANSFER OUT')
            GROUP BY x
            ORDER BY x
            """.format(optype, getIgnoredAccounts())
    else:
        query = """
                SELECT STRFTIME('%Y', opdate) AS x, ROUND(SUM({0})) AS y
                FROM transactions
                WHERE account NOT IN ({1})
                    AND category NOT IN ('OPENING BALANCE','TRANSFER IN','TRANSFER OUT')
                GROUP BY x
                ORDER BY x
                """.format(optype, getIgnoredAccounts())

    cursor.execute(query)
    data = cursor.fetchall()
    db.close()
    return data