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
    try :
        update_leads_details = """
            UPDATE LMS.Tellecaller
            SET
                Name=%s,
                Email_Id=%s,
                Password=%s,
                Gender=%s,
                Mobile_Number=%s,
                Employee_Id=%s,
                Designation=%s,
                Partner_Id=%s,
                Status=%s,
                Profile_Status=%s
            WHERE Tellecaller_Id=%s
        """

        conn = DatabaseManager.get_db_connection()
        with conn.cursor() as cur:
            cur.execute(update_leads_details, (
                data['Name'],
                data['Email_Id'],
                data['Password'],
                data['Gender'],
                data['Mobile_Number'],
                data['Employee_Id'],
                data['Designation'],
                data['Partner_Id'],
                data['Status'],
                data['Profile_Status'],
                data['Tellecaller_Id']
            ))
            print("Executed Successfully")
            conn.commit()
    except pymysql.Error as e:
        print(e)
        return {
                "statusCode": 200,
                "headers": {
                "Content-Type": "application/json",
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'OPTIONS,POST,GET,PUT,DELETE'
                },
                "body": json.dumps({"status": "success", "telle_caller_id":data['Tellecaller_Id']})
            }
    finally:
        if conn:
            conn.close()

