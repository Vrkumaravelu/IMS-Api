import json
from DB_manager import DatabaseManager
import logging
import pymysql
from bson import json_util
from datetime import datetime, timedelta, date

logger = logging.getLogger()
logger.setLevel(logging.INFO)

class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (date, datetime)):
            return obj.isoformat()
        return super().default(obj)
    
def lookup_table(argument):
    switcher = {
        "bank": "Bank",
        "loan_process_status": "Loan_Process_Status",
        "loan_type": "Loan_Type",
        "profile_status":"Profile_Status",
        "user":"USERS",
        "user_role": "User_Role"
    }

    # get() method of dictionary data type returns
    # value of passed argument if it is present
    # in dictionary otherwise second argument will
    # be assigned as default value of passed argument
    return switcher.get(argument, "nothing")

def lambda_handler(event, context):
    
    type_id =event['queryStringParameters']['type']

    table_name = lookup_table(type_id)

    try:
        conn = DatabaseManager.get_db_connection()
        if table_name == "nothing":
            error = "No matching lookup table found for type {}".format(type_id)
            return {
                "statusCode": 200,
                "headers": {
                "Content-Type": "application/json",
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'OPTIONS,POST,GET,PUT,DELETE'
                },
                "body": json.dumps({"message": error})
            }
        else:

            sql_select_lookup='select * from {}'.format(table_name)
            with conn.cursor() as cur:
                cur.execute(sql_select_lookup)
                row_headers=[x[0] for x in cur.description]
                
                rv = cur.fetchall()
                json_data=[]
                for result in rv:
                    json_data.append(dict(zip(row_headers,result)))
                    
                return {
                    "statusCode": 200,
                    "headers": {
                    "Content-Type": "application/json",
                    'Access-Control-Allow-Headers': 'Content-Type',
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Methods': 'OPTIONS,POST,GET,PUT,DELETE'
                    },
                    "body": json.dumps(json_data, default=json_util.default)
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

            "body": json.dumps("invalid username and password", cls=CustomJSONEncoder)  # Use the CustomJSONEncoder to handle datetime objects
        }
    finally:
        if conn:
            conn.close()