#!/usr/bin/env python

from __future__ import print_function
from future.standard_library import install_aliases
from flask_socketio import SocketIO, send, emit

install_aliases()

from urllib.parse import urlparse, urlencode
from urllib.request import urlopen, Request
from urllib.error import HTTPError

import json
import os
import math
import pandas as pd

import sys
sys.path.append('cognitiveSQL')

from flask import Flask
from flask import request
from flask import make_response
from flask import url_for, redirect
import psycopg2


import cognitiveSQL.Database as Database
import cognitiveSQL.LangConfig as LangConfig
import cognitiveSQL.Parser as Parser
import cognitiveSQL.Thesaurus as Thesaurus
import cognitiveSQL.StopwordFilter as StopwordFilter

import apiai

# Flask app should start in global layout
app = Flask(__name__, static_url_path='')
socketio = SocketIO(app)

parser = ""
apimedic_key = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJlbWFpbCI6ImRobW9kaUBkZWxvaXR0ZS5jb20iLCJyb2xlIjoiVXNlciIsImh0dHA6Ly9zY2hlbWFzLnhtbHNvYXAub3JnL3dzLzIwMDUvMDUvaWRlbnRpdHkvY2xhaW1zL3NpZCI6IjI5MSIsImh0dHA6Ly9zY2hlbWFzLm1pY3Jvc29mdC5jb20vd3MvMjAwOC8wNi9pZGVudGl0eS9jbGFpbXMvdmVyc2lvbiI6Ijk5IiwiaHR0cDovL2V4YW1wbGUub3JnL2NsYWltcy9saW1pdCI6Ijk5OTk5OTk5OSIsImh0dHA6Ly9leGFtcGxlLm9yZy9jbGFpbXMvbWVtYmVyc2hpcCI6IkJhc2ljIiwiaHR0cDovL2V4YW1wbGUub3JnL2NsYWltcy9sYW5ndWFnZSI6ImVuLWdiIiwiaHR0cDovL3NjaGVtYXMubWljcm9zb2Z0LmNvbS93cy8yMDA4LzA2L2lkZW50aXR5L2NsYWltcy9leHBpcmF0aW9uIjoiMjA5OS0xMi0zMSIsImh0dHA6Ly9leGFtcGxlLm9yZy9jbGFpbXMvbWVtYmVyc2hpcHN0YXJ0IjoiMjAwMC0wMS0wMSIsImlzcyI6Imh0dHBzOi8vYXV0aHNlcnZpY2UucHJpYWlkLmNoIiwiYXVkIjoiaHR0cHM6Ly9oZWFsdGhzZXJ2aWNlLnByaWFpZC5jaCIsImV4cCI6MTUwMzQwNzcwNSwibmJmIjoxNTAzNDAwNTA1fQ.OnZXAwtmhZmNAezcFdkZCTPMflbtIKIz5wm9FVyx_p0"

url = urlparse("postgres://caedtehsggslri:4679ba0abec57484a1d7ed261b74e80b08391993433c77c838c58415087a9c34@ec2-107-20-255-96.compute-1.amazonaws.com:5432/d5tmi1ihm5f6hv")
print (url.path[1:])
conn = psycopg2.connect(
    database=url.path[1:],
    user=url.username,
    password=url.password,
    host=url.hostname,
    port=url.port
)

@app.route('/')
def index():
    return redirect(url_for('static', filename='index.html'))


# @app.route('/speech')
# def speech():
#     return redirect(url_for('static', filename='index.html'))

# @app.route('/inventory')
# def inventory():
#     return redirect(url_for('static_url', filename='index.html'))

@app.route('/webhook', methods=['POST'])
def webhook():
    req = request.get_json(silent=True, force=True)

    print("Request:")
    print(json.dumps(req, indent=4))

    res = processRequest(req)

    res = json.dumps(res, indent=4)
    print(res)
    r = make_response(res)
    r.headers['Content-Type'] = 'application/json'
    return r


def processRequest(req):
    #print(req.get("result").get("action"))
    # if (req.get("result").get("action") == "inventory.search"):
    #     print("Inventory Search")
    #     incoming_query = req.get("result").get("resolvedQuery")
    #     queries = parser.parse_sentence(incoming_query.lower())
    #     #print(query for query in queries)
    #     queryString = ""
    #     table = ""
    #     for query in queries:
    #         table = query.get_from().get_table()
    #         columns = query.get_select().get_columns()
    #         queryString = queryString + str(query)
    #
    #     print(table)
    #     print(list(columns))
    #     # xAxis = columns[0][0].split('.')[1]
    #     # yAxis = columns[1][0].split('.')[1]
    #     print(queryString)
    #     cur = conn.cursor()
    #     cur.execute(queryString)
    #     rows = cur.fetchall()
    #
    #     # outText = ', '.join(str(x) for x in rows[0])
    #     # outText = ', '.join(str(element).split(".")[0] for row in rows for element in row)
    #     count = 0
    #
    #     outText = "The "
    #     for row in rows:
    #         isLast = len(row)
    #         for element in row:
    #             isLast = isLast - 1
    #             value = str(element).split(".")[0]
    #             if (columns[count][0] is not None):
    #                 # print(columns)
    #                 column = columns[count][0].split('.')[1]
    #             operation = columns[count][1]
    #             if (operation is None):
    #                 print("The Operation is None")
    #                 outText = outText + column + " is " + value
    #             elif (operation is "COUNT"):
    #                 print("The Operation is " + str(operation))
    #                 outText = outText + operation + " of " + table + " is " + value
    #             else:
    #                 print("The Operation is " + str(operation))
    #                 outText = outText + operation + " of " + column + " is " + value
    #             if (isLast is not 0):
    #                 outText = outText + " and the "
    #                 count = count + 1
    #     # print(','.join(str(element) for row in rows for element in row))
    #
    #     return {
    #         "speech": outText,
    #         "displayText": outText,
    #         # "data": data,
    #         # "contextOut": [],
    #         "source": "Dhaval"
    #     }
    # elif (req.get("result").get("action") == "show.visualization"):
    #     print("Inventory Visualization")
    #     incoming_query = req.get("result").get("resolvedQuery")
    #     print(incoming_query)
    #     chartType = req.get("result").get("parameters").get("chart-type")
    #     print(chartType)
    #     queries = parser.parse_sentence(incoming_query.lower())
    #     print(query for query in queries)
    #     queryString = ""
    #     table = ""
    #     for query in queries:
    #         table = query.get_from().get_table()
    #         columns = query.get_select().get_columns()
    #         queryString = queryString + str(query)
    #     print(queryString)
    #     cur = conn.cursor()
    #     cur.execute(queryString)
    #     rows = cur.fetchall()
    #     print(rows)
    #     print(list(columns))
    #     xAxis = columns[0][0].split('.')[1]
    #     yAxis = columns[1][0].split('.')[1]
    #     print(xAxis)
    #     df = pd.DataFrame(list(rows), columns = ["label", "value"])
    #     agg_df = df.groupby(['label'], as_index=False).agg({"value": "sum"})
    #     agg_df['label'] = agg_df['label'].astype('str')
    #     agg_df['value'] = agg_df['value'].astype('str')
    #     chartData = agg_df.to_json(orient='records')
    #     # chartData = [{"label": str(row[0]), "value": str(row[1])} for row in rows]
    #     print (chartData)
    #     # chartData = json.dumps(chartData)
    #     # final_json = '[ { "type":"' + chartType + '", "chartcontainer":"barchart", "caption":"' + chartType + ' chart showing ' + xAxis + ' vs ' + yAxis + '", "subCaption":"", "xAxisName":"xAxis", "yAxisName":"yAxis","source":[ { "label": "Mon", "value": "15123" }, { "label": "Tue", "value": "14233" }, { "label": "Wed", "value": "23507" }, { "label": "Thu", "value": "9110" }, { "label": "Fri", "value": "15529" }, { "label": "Sat", "value": "20803" }, { "label": "Sun", "value": "19202" } ]}]'
    #     final_json = '[ { "type":"' + chartType + '", "chartcontainer":"barchart", "caption":"A ' + chartType + ' chart showing ' + xAxis + ' vs ' + yAxis + '", "subCaption":"", "xAxisName":"' + xAxis + '", "yAxisName":"' + yAxis + '", "source":' + chartData + '}]'
    #     print(final_json)
    #     maxRecord = agg_df.ix[agg_df['value'].idxmax()].to_frame().T
    #     print(maxRecord)
    #     minRecord = agg_df.ix[agg_df['value'].idxmin()].to_frame().T
    #     print(minRecord)
    #     socketio.emit('chartdata', final_json)
    #     outText = "The " + xAxis + " " + str(maxRecord['label'].values[0]) + " has maximum " + yAxis + " while the " + xAxis + " " + str(minRecord['label'].values[0]) + " has minimum " + yAxis
    #     return {
    #         "speech": outText,
    #         "displayText": outText,
    #         # "data": data,
    #         # "contextOut": [],
    #         "source": "Dhaval"
    #     }
    if (req.get("request").get("intent").get("name") == "InventorySearch"):
        print("InventorySearch")
        incoming_query = req.get("request").get("intent").get("slots").get("message").get("value")
        print(incoming_query)
        queries = parser.parse_sentence(str(incoming_query).lower())
        # queries = parser.parse_sentence(incoming_query)
        # print(query for query in queries)
        queryString = ""
        table = ""
        for query in queries:
            table = query.get_from().get_table()
            columns = query.get_select().get_columns()
            queryString = queryString + str(query)

        print(table)
        print(list(columns))
        print(queryString)
        cur = conn.cursor()
        cur.execute(queryString)
        rows = cur.fetchall()
        outText = ', '.join(str(x) for x in rows[0])
        outText = ', '.join(str(element).split(".")[0] for row in rows for element in row)
        count = 0

        outText = "The "
        # for row in rows:
        #     isLast = len(row)
        #     for element in row:
        #         isLast = isLast - 1
        #         value = str(element).split(".")[0]
        #         if (columns[count][0] is not None):
        #             # print(columns)
        #             column = columns[count][0].split('.')[1]
        #         operation = columns[count][1]
        #         if (operation is None):
        #             print("The Operation is None")
        #             outText = outText + column + " is " + value
        #         elif (operation is "COUNT"):
        #             print("The Operation is " + str(operation))
        #             outText = outText + operation + " of " + table + " is " + value
        #         else:
        #             print("The Operation is " + str(operation))
        #             outText = outText + operation + " of " + column + " is " + value
        #         if (isLast is not 0):
        #             outText = outText + " and the "
        #             count = count + 1
        # print(','.join(str(element) for row in rows for element in row))

        # print(','.join(str(element) for row in rows for element in row))
        # return {
        #     "speech": type,
        #     "displayText": outText,
        #     # "data": data,
        #     # "contextOut": [],
        #     "source": "Dhaval"
        # }

        # alexaResponse.get("response").get("outputSpeech").get("text")=outText
        # alexaResponse.get("response").get("reprompt").get("outputSpeech").get("text")=outText
        with open("response/alexa_response.json", 'r') as f:
            alexaResponse = json.load(f)

        alexaResponse["response"]["outputSpeech"]["text"] = outText
        alexaResponse["response"]["reprompt"]["outputSpeech"]["text"] = outText
        return alexaResponse

if __name__ == '__main__':
    database = Database.Database()
    database.load("cognitiveSQL/database/inventory.sql")
    #database.print_me()

    config = LangConfig.LangConfig()
    config.load("cognitiveSQL/lang/english.csv")

    parser = Parser.Parser(database, config)
    from os import sys, path
    sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
    port = int(os.getenv('PORT', 5000))

    print("Starting app on port %d" % port)

    #app.run(debug=True, port=port, host='0.0.0.0')
    socketio.run(app, debug=True, port=port, host='0.0.0.0')