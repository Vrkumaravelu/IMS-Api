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
    print("event" , event)
    
    data = json.loads(event['body'])
    print(data)
    try:
        update_leads_details = """
            UPDATE LMS.Lead_Details
            SET
                First_Name=%s,
                Last_Name=%s,
                Mobile_No=%s,
                Company_Name=%s,
                Company_Type_Id=%s,
                Salary=%s,
                Loan_Amount=%s,
                Bank_Id=%s,
                Loan_Type_Id=%s,
                Loan_Process_Status_Id=%s,
                Payslip_Image_Path=%s,
                Generated_Partner=%s,
                Generated_By=%s,
                Lead_Status=%s,
                Generated_On=%s,
                Street=%s,
                State=%s,
                Pincode=%s,
                City=%s,
                Email=%s
           
            WHERE Lead_Details_Id=%s
        """
        update_leads_assets = """
            UPDATE LMS.Leads_asset
            SET
                asset_name=%s,
                asset_path=%s
                WHERE Lead_detail_id=%s and Leads_asset_id = %s 
        """

        conn = DatabaseManager.get_db_connection()
        with conn.cursor() as cur:
            conn.begin()
            cur.execute(update_leads_details, (
                data['First_Name'],
                data['Last_Name'],
                data['Mobile_No'],
                data['Company_Name'],
                data['Company_Type_Id'],
                data['Salary'],
                data['Loan_Amount'],
                data['Bank_Id'],
                data['Loan_Type_Id'],
                data['Loan_Process_Status_Id'],
                data['Payslip_Image_Path'],
                data['Generated_Partner'],
                data['Generated_By'],
                data['Lead_Status'],
                data['Generated_On'],
                data['Street'],
                data['State'],
                data['Pincode'],
                data['City'],
                data['Email'],
                int(data['Lead_Details_Id'])  
            ))
            cur.execute(update_leads_assets, (
                data['asset_name'],
                data['asset_path'],
                int(data['Lead_Details_Id']),
                int(data['Leads_asset_id'])
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
            "body": json.dumps({"status": "success", "lead_detail_id": data['Lead_Details_Id']})
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
  "Bank_Id": "<integer>",
  "City": "<string>",
  "Company_Name": "<string>",
  "Company_Type_Id": "<integer>",
  "Door_no": "<string>",
  "First_Name": "<string>",
  "Generated_By": "<integer>",
  "Generated_On": "<string>",
  "Generated_Partner": "<integer>",
  "Last_Name": "<string>",
  "Lead_Details_Id": 33,
  "Lead_Status": "<integer>",
  "Loan_Amount": "<integer>",
  "Loan_Process_Status_Id": "<integer>",
  "Loan_Type_Id": "<integer>",
  "Mobile_No": "<string>",
  "Payslip_Image_Path": "<string>",
  "Pincode": "<string>",
  "Salary": "<integer>",
  "State": "<string>",
  "Street": "<string>",
  "asset_name" :"testfinal",
  "asset_path" : "testfinal",
  "Leads_asset_id" : "5",
  "Email":"test@gmail.com"
}
) }
lambda_handler (event=events,context="")