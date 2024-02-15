import json
import boto3
from datetime import datetime, date
import logging
import pymysql
from DB_manager import DatabaseManager

s3 = boto3.client('s3')

class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (date, datetime)):
            return obj.isoformat()
        return super().default(obj)

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    print(event)
    print(event['body'])
    data = json.loads(event['body'])
    try:
        insert_tellecaller = """
            INSERT INTO LMS.Tellecaller (
                Name,
                Email_Id,
                Password,
                Gender,
                Mobile_Number,
                Employee_Id,
                Designation,
                admin_id,
                Status,
                Profile_Status,
                Read_access,
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s,%s)
        """

        conn = DatabaseManager.get_db_connection()
        with conn.cursor() as cur:
            cur.execute(insert_tellecaller, (
                data['Name'],
                data['Email_Id'],
                data['Password'],
                data['Gender'],
                data['Mobile_Number'],
                data['Employee_Id'],
                data['Designation'],
                data['admin_id'],
                int(data['Status']),
                int(data['Profile_Status']),
                int(data['Read_access'])
            ))
            print("Tellecaller Inserted Successfully")
            telle_caller_id = conn.insert_id()
            conn.commit()
        return {
                "statusCode": 200,
                "headers": {
                "Content-Type": "application/json",
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'OPTIONS,POST,GET,PUT,DELETE'
                },
                "body": json.dumps({"status": "success", "Admin Created Tellecaller":telle_caller_id})
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

            "body": json.dumps("Database Connection Issue", cls=CustomJSONEncoder)  # Use the CustomJSONEncoder to handle datetime objects
        }
    finally:
        if conn:
            conn.close()
        

