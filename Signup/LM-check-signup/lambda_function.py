
from datetime import datetime, timedelta, date
from decimal import Decimal
import json
from DB_manager import DatabaseManager
import logging
import pymysql
from bson import json_util


class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        # print(obj)
        if isinstance(obj, (date, datetime)):
            
            return obj.isoformat()
        elif isinstance(obj, Decimal):
            
            return str(obj) 
        return super().default(obj)
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    print("Received Event:", event)
    check_values=event['queryStringParameters']['check_values']

    try:
        conn = DatabaseManager.get_db_connection()
        with conn.cursor() as cur:
            args = (check_values,)
            cur.callproc('SP_CHECK_SIGNUP', args)
            row_headers=[x[0] for x in cur.description]
            rv = cur.fetchall()
            
            # print(row_headers)
            json_data=[]
            for result in rv:
                json_data.append(dict(zip(row_headers,result)))
                # print(json_data)
            if not rv:
                return {
                    "statusCode": 404,
                    "headers": {
                        "Content-Type": "application/json",
                        "Access-Control-Allow-Headers": "Content-Type",
                        "Access-Control-Allow-Origin": "*",
                        "Access-Control-Allow-Methods": "OPTIONS,POST,GET,PUT,DELETE"
                    },
                    "body": json.dumps("Data Not Found In Database", default=json_util.default)  # <-- There is an undefined "json_util" here
                }
            else:
                json_data = []
                for result in rv:
                    json_data.append(dict(zip(row_headers, result)))
                    print(json_data)
                return {
                    "statusCode": 200,
                    "headers": {
                        "Content-Type": "application/json",
                        "Access-Control-Allow-Headers": "Content-Type",
                        "Access-Control-Allow-Origin": "*",
                        "Access-Control-Allow-Methods": "OPTIONS,POST,GET,PUT,DELETE"
                    },
                    "body": json.dumps(json_data, cls=CustomJSONEncoder)  # Use the CustomJSONEncoder to handle datetime objects
                }
    except pymysql.Error as e:
        print(e)
        return {
            "statusCode": 500,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Headers": "Content-Type",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "OPTIONS,POST,GET,PUT,DELETE"
            },

            "body": json.dumps("Error occurs at connection", cls=CustomJSONEncoder)  # Use the CustomJSONEncoder to handle datetime objects
        }
    finally:
        if conn:
            conn.close()
if __name__  == "__main__":
    events = {
        "queryStringParameters": {
            "check_values": "1234567890"
        }
    }
    lambda_handler(event=events, context="")