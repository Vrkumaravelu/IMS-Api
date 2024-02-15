import os
import json
import pymysql
import boto3
import logging

# Set up logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

class DatabaseManager:
    
    @staticmethod
    def get_db_connection():
        try:
            connection = pymysql.connect(
                host= 'plaz-dev-db.cp38dsvtanhf.ap-south-1.rds.amazonaws.com',
                user= 'admin',
                passwd= 'plazdb!SV',
                db= 'LMS',
                connect_timeout=5
            )
            logger.info("Successfully connected to the database RDS Proxy.")
            return connection
        except Exception as e:
            logger.error(f"Error connecting to the database: {e}")
            raise  # Re-raise the exception to ensure Lambda function execution stops

