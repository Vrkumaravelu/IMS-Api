from decimal import Decimal
import json
from datetime import datetime, timedelta, date
from DB_manager import DatabaseManager
import logging
import pymysql
from bson import json_util

class CustomJSONEncoder(json.JSONEncoder):
# class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (date, datetime)):
            return obj.isoformat()
        elif isinstance(obj, Decimal):
            return str(obj)
        return super().default(obj)

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    User_id = event['queryStringParameters']['User_id']

    try:
        conn = DatabaseManager.get_db_connection()
        with conn.cursor() as cur:
            args = (User_id, User_id, User_id)
            cur.execute('''
                 SELECT
                    (SELECT Target FROM LMS.User WHERE User_Id = %s) AS target_loan_amount,
                    (SELECT COUNT(*) FROM LMS.Lead_Details WHERE Generated_Partner = %s) AS approved_leads,
                    (SELECT SUM(Loan_Amount) FROM LMS.Lead_Details WHERE Generated_Partner = %s) AS target_completion
            ''', args)

            row_headers = [x[0] for x in cur.description]
            rv = cur.fetchall()
            json_data = []
            for result in rv:
                json_data.append(dict(zip(row_headers, result)))
                print("json data", json_data)

            if not rv:
                return {
                    "statusCode": 404,
                    "headers": {
                        "Content-Type": "application/json",
                        "Access-Control-Allow-Headers": "Content-Type",
                        "Access-Control-Allow-Origin": "*",
                        "Access-Control-Allow-Methods": "OPTIONS,POST,GET,PUT,DELETE"
                    },
                    "body": json.dumps("Data Not Found In Database", default=json_util.default)
                }
            else:
                return {
                    "statusCode": 200,
                    "headers": {
                        "Content-Type": "application/json",
                        "Access-Control-Allow-Headers": "Content-Type",
                        "Access-Control-Allow-Origin": "*",
                        "Access-Control-Allow-Methods": "OPTIONS,POST,GET,PUT,DELETE"
                    },
                    "body": json.dumps(json_data, cls=CustomJSONEncoder)
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
            "body": json.dumps("Error occurs at connection", cls=CustomJSONEncoder)
        }
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    events = {"queryStringParameters": {"User_id": "2"}}
    lambda_handler(event=events, context="")
