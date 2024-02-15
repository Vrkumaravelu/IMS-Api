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
print(s3)

def lambda_handler(event, context):
    
    try:
        conn = DatabaseManager.get_db_connection()
        data = json.loads(event['body'])  
        
        imgdata = pybase64.b64decode(data['leads_Image'])
        asset_type = data['asset_type']
        requestid=uuid.uuid4()
        filename = 'assets/leads/{}/{}.{}'.format(data['Lead_detail_id'],requestid,asset_type)
       
        s3.put_object(Bucket='leads-management-system', Key=filename, Body=imgdata)
        leads_data = [data['asset_name'],filename,data['asset_status'],data['Lead_detail_id']]
        print(leads_data)
        sql_leads_data_ins = '''INSERT INTO LMS.Leads_asset (asset_name,asset_path,asset_status,Lead_detail_id) values (%s,%s,%s,%s)'''
        with conn.cursor() as cur:
            cur.execute(sql_leads_data_ins, leads_data)
            
            conn.commit()
            
            return {
                "statusCode": 200,
                "headers": {
                "Content-Type": "application/json",
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'OPTIONS,POST,GET,PUT,DELETE'
                },
                "body": json.dumps({"status": "success", "leads_details id":data['Lead_detail_id']})
            }

    except pymysql.Error as e:
        print(e)
    finally:
        if conn:
            conn.close()