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
    today = date.today()
    d1 = today.strftime("%d/%m/%Y")

    insert_lead_details = """
        INSERT INTO LMS.Lead_Details (
            First_Name,
            Last_Name,
            Mobile_No,
            Company_Name,
            Company_Type_Id,
            Salary,
            Loan_Amount,
            Bank_Id,
            Loan_Type_Id,
            Loan_Process_Status_Id,
            Payslip_Image_Path,
            Generated_Partner,
            Generated_By,
            Lead_Status,
            Generated_On,
            Street,
            State,
            City,
            Pincode,
            Door_no,
            Email
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,%s, %s, %s, %s, %s, %s)
    """

    conn = DatabaseManager.get_db_connection()
    with conn.cursor() as cur:
        cur.execute(insert_lead_details, (
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
            d1,
            data['Street'],
            data['State'],
            data['City'],
            data['Pincode'],
            data['Door_no'],
            data['Email']
        ))
        print("Executed Successfully")
        lead_detail_id = conn.insert_id()
        conn.commit()

    return {
    "statusCode": 200,
    "headers": {
        "Content-Type": "application/json"
    },
    "body": json.dumps({
        "status": "success",
        "lead_detail_id": lead_detail_id,
        "statusCode": 200,
        "responseMessage": "Lead Details INSERTED SUCCESSFULLY",
        "response": "Lead Details INSERTED SUCCESSFULLY"
    })
}

if __name__ == "__main__":
    events = {
        "body": json.dumps({
            'First_Name': 'kumar',
            'Last_Name': 'Doe',
            'Mobile_No': '223333332',
            'Company_Name': 'ABC Corp',
            'Company_Type_Id': '1',
            'Salary': '50000',
            'Loan_Amount': '100000',
            'Bank_Id': '12345',
            'Loan_Type_Id': '1',
            'Loan_Process_Status_Id': '2',
            'Payslip_Image_Path': '/path/to/image.png',
            'Generated_Partner': '1',
            'Generated_By': '2',
            'Lead_Status': '1',
            'Generated_On': '2023-01-01T12:00:00Z',
            'Street': 'StreetAddress',
            'State': 'State',
            'City': 'City',
            'Pincode': '12345',
            'Door_no': 'DoorNo',
            'Email':'kumaravelu@sv.com'
        })
    }
    lambda_handler(event=events, context="")
