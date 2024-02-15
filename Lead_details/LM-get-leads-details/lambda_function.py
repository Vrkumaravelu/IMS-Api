
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
    
    user_role_id=event['queryStringParameters']['user_role_id']
    user_id=event['queryStringParameters']['user_id']
    status_id= event['queryStringParameters']['status_id']
    # Lead_detail_id=event['queryStringParameters']['Lead_detail_id']

    try:
        conn = DatabaseManager.get_db_connection()
        with conn.cursor() as cur:
            args = (user_role_id,user_id,status_id)
            cur.callproc('SP_GET_LEAD_DETAILS', args)
            row_headers=[x[0] for x in cur.description]
            rv = cur.fetchall()
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
                    "body": json.dumps({"statusCode": 200, "message": "Data retrieved successfully", "data": json_data}, cls=CustomJSONEncoder)
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
            "user_role_id": "1",
            "user_id": "1",
            "status_id": "1",
            # "Lead_detail_id":""
        }
    }
    lambda_handler(event=events, context="")