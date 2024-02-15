import json
from datetime import datetime, timedelta, date
from DB_manager import DatabaseManager
import jwt
import logging
import pymysql
from bson import json_util
import secret_manager
import hashlib

class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (date, datetime)):
            return obj.isoformat()
        return super().default(obj)

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def encrypt_password(password):
    # Encode the password as bytes
    password_bytes = password.encode('utf-8')

    # Create a new SHA-1 hash object
    sha1_hash = hashlib.sha1()

    # Update the hash object with the password bytes
    sha1_hash.update(password_bytes)

    # Get the hexadecimal representation of the hash
    hashed_password = sha1_hash.hexdigest()

    return hashed_password

def generate_jwt_token(request_id, mobile_number, jwt_secret):
    issued_at = datetime.utcnow()
    expiration_time = issued_at + timedelta(minutes=30)  # Token expires after 30 minutes
    payload = {
        'sub': mobile_number,  # 'sub' claim for the principal subject
        'request_id': request_id,  # Additional custom claim
        'iat': issued_at.timestamp(),  # Issued at time
        'exp': expiration_time.timestamp()  # Expiration time
    }
    jwt_token = jwt.encode(payload, jwt_secret, algorithm='HS256')
    return jwt_token

def get_jwt_secret():
    secret_name = secret_manager.JWT_SECRET_KEY
    #client = boto3.client('secretsmanager')
    try:
        #get_secret_value_response = client.get_secret_value(SecretId=secret_name)
        return secret_name
    except Exception as e:
        print(f"Error retrieving secret: {e}")
        raise e

def lambda_handler(event, context):
    try:
        # Parse the request body as JSON
        request_body = json.loads(event['body'])
        
        # Extract user_name and user_password from the request body
        user_name = request_body.get('user_name')
        user_password = request_body.get('user_password')

        if user_name is None or user_password is None:
            return {
                "statusCode": 400,
                "headers": {
                    "Content-Type": "application/json",
                    "Access-Control-Allow-Headers": "Content-Type",
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Methods": "OPTIONS,POST,GET,PUT,DELETE"
                },
                "body": json.dumps("Bad Request: user_name or user_password missing in the request body")
            }

        conn = DatabaseManager.get_db_connection()
        with conn.cursor() as cur:
            args = (user_name, encrypt_password(user_password))
            cur.callproc('SP_CHECK_LOGIN', args)
            row_headers = [x[0] for x in cur.description]
            rv = cur.fetchall()
            print("Result from database query:", rv)

            json_data = []
            for result in rv:
                json_data.append(dict(zip(row_headers, result)))
                print(json_data)

            if not rv:
                return {
                    "statusCode": 404,
                    "headers": {
                        "Content-Type": "application/json",
                        "Access-Control-Allow-Headers": "Content-Type",
                        "Access-Control-Allow-Origin": "*",
                        "Access-Control-Allow-Methods": "OPTIONS,POST,GET,PUT,DELETE"
                    },
                    "body": json.dumps("User Not Found In Database", default=json_util.default)
                }
            else:
                json_data = []
                for result in rv:
                    json_data.append(dict(zip(row_headers, result)))

                print(json_data)
                jwt_secret = get_jwt_secret()
                jwt_token = generate_jwt_token(request_id=user_name, mobile_number=json_data[0]['Mobile_Number'], jwt_secret=jwt_secret)
                json_data.append({"token": jwt_token})

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
        print("except", e)
        return {
            "statusCode": 500,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Headers": "Content-Type",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "OPTIONS,POST,GET,PUT,DELETE"
            },
            "body": json.dumps("invalid username and password", cls=CustomJSONEncoder)
        }
    finally:
        if conn:
            conn.close()
if __name__ == "__main__":
    events = {
        "queryStringParameters": {
            "username": "johndoe@example.com",
            "password": "1234",
            # "status_id": "1"
        }
    }
    lambda_handler(event=events, context="")
