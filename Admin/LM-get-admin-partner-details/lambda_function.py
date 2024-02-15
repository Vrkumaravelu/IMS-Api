import json
from datetime import datetime, timedelta, date
from DB_manager import DatabaseManager
import logging
import pymysql
from bson import json_util
from botocore.exceptions import ClientError




class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (date, datetime)):
            return obj.isoformat()
        return super().default(obj)

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    
    try:
        conn = DatabaseManager.get_db_connection()
        sql_select_lookup='''SELECT * FROM LMS.User'''
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

            "body": json.dumps("Database connection issue", cls=CustomJSONEncoder)  # Use the CustomJSONEncoder to handle datetime objects
        }
    finally:
        if conn:
            conn.close()

