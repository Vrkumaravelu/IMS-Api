import json
from datetime import datetime, timedelta, date
from DB_manager import DatabaseManager
import logging
import pymysql
from bson import json_util

class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (date, datetime)):
            return obj.isoformat()
        return super().default(obj)

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    Partner_Id = event['queryStringParameters']['Partner_Id']

    try:
        conn = DatabaseManager.get_db_connection()
        with conn.cursor() as cur:
            args = (Partner_Id,)
            cur.execute(
                'SELECT TL.*, u.First_Name, u.Mobile_Number, u.Referral_Code FROM LMS.Tellecaller TL LEFT JOIN LMS.User u ON u.User_Id = TL.Partner_Id WHERE TL.Partner_Id = %s',
                args
            )
            row_headers = [x[0] for x in cur.description]
            rv = cur.fetchall()
            print("rv output" , rv)
            print(row_headers)
            json_data = []
            for result in rv:
                json_data.append(dict(zip(row_headers, result)))
                print("json data" , json_data)
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

# if __name__ == "__main__":
#     events = {"queryStringParameters": {"Partner_Id": "3"}}
#     lambda_handler(event=events, context="")

    finally:
        if conn:
            conn.close()