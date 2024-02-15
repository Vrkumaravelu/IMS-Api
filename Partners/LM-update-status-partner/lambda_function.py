import json
from datetime import datetime, date
import logging
import pymysql
from DB_manager import DatabaseManager


class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (date, datetime)):
            return obj.isoformat()
        return super().default(obj)

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    data = json.loads(event['body'])
    print(data)
    try:
        update_partner = """
            UPDATE LMS.User
            SET
                
                Profile_Status_Id=%s
                
           
            WHERE User_Id=%s
        """

        conn = DatabaseManager.get_db_connection()
        with conn.cursor() as cur:
            conn.begin()
            cur.execute(update_partner, (
                
                data['Profile_Status_Id'],
                int(data['User_Id'])  
            ))
            
            print("Executed Successfully")
            conn.commit()
        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'OPTIONS,POST,GET,PUT,DELETE'
            },
            "body": json.dumps({"status": "success", "Partner_Id": data['User_Id']})
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
            "body": json.dumps("Database Connection Issue", cls=CustomJSONEncoder)
        }
    finally:
        if conn:
            conn.close()


if __name__  == "__main__":
    events = {
"body": json.dumps(
  {
  "Profile_Status_Id": "4",
  "User_Id": "1"
}
) }
lambda_handler (event=events,context="")