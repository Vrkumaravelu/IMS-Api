import json
from datetime import datetime, date
import logging
import pymysql
from DB_manager import DatabaseManager
import hashlib


class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (date, datetime)):
            return obj.isoformat()
        return super().default(obj)

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def sha1_hash_password(password):
    # Encode the password as bytes
    password_bytes = password.encode('utf-8')

    # Create a new SHA-1 hash object
    sha1_hash = hashlib.sha1()

    # Update the hash object with the password bytes
    sha1_hash.update(password_bytes)

    # Get the hexadecimal representation of the hash
    hashed_password = sha1_hash.hexdigest()

    return hashed_password

def lambda_handler(event, context):
    print("event" , event)
    
    data = json.loads(event['body'])
    print(data)
    try:
        update_leads_details = """
            UPDATE LMS.User
            SET
                Password=%s
           
            WHERE User_Id=%s
        """
        conn = DatabaseManager.get_db_connection()
        with conn.cursor() as cur:
            conn.begin()
            cur.execute(update_leads_details, (
                sha1_hash_password(data['Password']),
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
            "body": json.dumps({"status": "success", "User_Id": data['User_Id']})
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
  
  "User_Id" : "5",
  "Password":"1234"
}
) }
lambda_handler (event=events,context="")