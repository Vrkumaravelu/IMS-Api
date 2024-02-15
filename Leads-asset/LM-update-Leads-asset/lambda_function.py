# import json
# import boto3
# from datetime import datetime, timedelta, date
# from DB_manager import DatabaseManager
# import logging
# import pymysql
# import pybase64
# import uuid
# import random
# import string
# import hashlib

# # json parser for parsing json
# class CustomJSONEncoder(json.JSONEncoder):
#     def default(self, obj):
#         if isinstance(obj, (date, datetime)):
#             return obj.isoformat()
#         return super().default(obj)

# logger = logging.getLogger()
# logger.setLevel(logging.INFO)

# # using boto connection to s3 buckets
# s3 = boto3.client('s3')
# print(s3)

# def lambda_handler(event, context):
#     try:
#         print(event)
#         conn = DatabaseManager.get_db_connection()
#         data = json.loads(event['body'])
#         print(data)

#         imgdata = pybase64.b64decode(data['leads_Image'])
#         asset_type = data['asset_type']
#         requestid=uuid.uuid4()
#         filename = 'assets/leads/{}/{}.{}'.format(data['Lead_detail_id'],requestid,asset_type)

#         s3.put_object(Bucket='leads-management-system', Key=filename, Body=imgdata)
#         # leads_data = [data['asset_name'], filename, data['Lead_detail_id']]
#         # print(leads_data)
#         update_leads_assets = """
#             UPDATE LMS.Leads_asset
#             SET
#                 asset_name=%s
#                 WHERE Lead_detail_id=%s and Leads_asset_id = %s
#         """

#         with conn.cursor() as cur:
#             conn.begin()

#             cur.execute(update_leads_assets, (
#                 data['asset_name'],
#                 int(data['Lead_detail_id']),
#                 int(data['Leads_asset_id'])
#             ))


#             print("Executed Successfully")
#             conn.commit()

#             return {
#                 "statusCode": 200,
#                 "headers": {
#                     "Content-Type": "application/json",
#                     'Access-Control-Allow-Headers': 'Content-Type',
#                     'Access-Control-Allow-Origin': '*',
#                     'Access-Control-Allow-Methods': 'OPTIONS,POST,GET,PUT,DELETE'
#                 },
#                "body": json.dumps({
#                 "status": "200",
#                 "Message": "Updated Successfully"
#         })
#             }

#     except pymysql.Error as e:
#         print(e)
#     finally:
#         if conn:
#             conn.close()


# # if __name__  == "__main__":
# #     events = { 

# # "body": json.dumps({

# #   "Lead_detail_id": "25",
# #   "Leads_asset_id": "1",
# #   "asset_name": "pan",
# #   "asset_path": "test/image",
# #   "leads_Image":"iVBORw0KGgoAAAANSUhEUgAAAAgAAAAIAQMAAAD+wSzIAAAABlBMVEX///+/v7+jQ3Y5AAAADklEQVQI12P4AIX8EAgALgAD/aNpbtEAAAAASUVORK5CYII=="
  
# # }) }
# # lambda_handler(event=events, context="")
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

# json parser for parsing json
class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (date, datetime)):
            return obj.isoformat()
        return super().default(obj)

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# using boto connection to s3 buckets
s3 = boto3.client('s3')
print(s3)

def lambda_handler(event, context):
    try:
        print(event)
        conn = DatabaseManager.get_db_connection()
        data = json.loads(event['body'])
        print(data)

        imgdata = pybase64.b64decode(data['leads_Image'])
        asset_type = data['asset_type']
        print(asset_type)
        requestid=uuid.uuid4()
        filename = 'assets/leads/{}/{}.{}'.format(data['Lead_detail_id'],requestid,asset_type)
        print(filename)

        s3.put_object(Bucket='leads-management-system', Key=filename, Body=imgdata)
        # leads_data = [data['asset_name'], filename, data['Lead_detail_id']]
        # print(leads_data)
        update_leads_assets = f"""UPDATE LMS.Leads_asset SET asset_name={data['asset_name']}WHERE Lead_detail_id={int(data['Lead_detail_id'])} 
        and Leads_asset_id = {int(data['Leads_asset_id'])}"""
        
        print(update_leads_assets)
        with conn.cursor() as cur:
            #conn.begin()
            cur.execute(update_leads_assets)
            # cur.execute(update_leads_assets, (
            #     data['asset_name'],
            #     int(data['Lead_detail_id']),
            #     int(data['Leads_asset_id'])
            # ))


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
               "body": json.dumps({
                "status": "200",
                "Message": "Updated Successfully"
        })
            }

    except pymysql.Error as e:
        print(e)
    finally:
        if conn:
            conn.close()


# if __name__  == "__main__":
#     events = { 

# "body": json.dumps({

#   "Lead_detail_id": "25",
#   "Leads_asset_id": "1",
#   "asset_name": "pan",
#   "asset_path": "test/image",
#   "leads_Image":"iVBORw0KGgoAAAANSUhEUgAAAAgAAAAIAQMAAAD+wSzIAAAABlBMVEX///+/v7+jQ3Y5AAAADklEQVQI12P4AIX8EAgALgAD/aNpbtEAAAAASUVORK5CYII=="
  
# }) }
# lambda_handler(event=events, context="")
