import json
import boto3
from datetime import datetime, timedelta, date
from DB_manager import DatabaseManager
import logging
import pymysql
import pybase64
import uuid
import random
import string
import hashlib

#json parser for parsing json
class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (date, datetime)):
            return obj.isoformat()
        return super().default(obj)

logger = logging.getLogger()
logger.setLevel(logging.INFO)

#using boto connection to s3 buckets
s3 = boto3.client('s3')

# Define the length of your referral code
code_length = 6  # You can adjust this as needed

# Generate a random referral code
def generate_referral_code(length):
    characters = string.ascii_letters + string.digits  # Include letters and digits
    referral_code = ''.join(random.choice(characters) for _ in range(length))
    return referral_code

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
    
    try:
        conn = DatabaseManager.get_db_connection()
        data = json.loads(event['body'])  
        referral_code = generate_referral_code(code_length)
        pass_word= sha1_hash_password(data['Password'])
        imgdata = pybase64.b64decode(data['Id_Proof_Image'])
        requestid=uuid.uuid4()
        filename = 'assets/partner/id_proof/{}.PNG'.format(requestid)
       
        s3.put_object(Bucket='leads-management-system', Key=filename, Body=imgdata)
        partner_data = [data['First_Name'],data['Last_Name'],data['Email_Id'],data['Mobile_Number'],referral_code,data['PAN_Number'],filename,
                        pass_word,data['Terms_and_Condition_Status'],data['Profile_Status_Id'],data['User_Role_Id']]
        print(partner_data)
        sql_partner_data_ins = '''INSERT INTO LMS.User (First_Name,Last_Name,Email_Id,Mobile_Number,Referral_Code,PAN_Number,Id_Proof_Image,
        Password,Terms_and_Condition_Status,Profile_Status_Id,User_Role_Id)values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'''
        with conn.cursor() as cur:
            cur.execute(sql_partner_data_ins, partner_data)
            division_data_id = conn.insert_id()
            print("id: ", division_data_id)
            conn.commit()
            
            return {
                "statusCode": 200,
                "headers": {
                "Content-Type": "application/json",
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'OPTIONS,POST,GET,PUT,DELETE'
                },
                "body": json.dumps({"status": "success", "division_id":division_data_id})
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
        

