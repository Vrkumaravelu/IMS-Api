import json
import jwt
from botocore.exceptions import ClientError
import secret_manager

def lambda_handler(event, context):

    if 'authorizationToken' in event:

        # Split the authorizationToken by space and check if there are at least two parts
        token_parts = event['authorizationToken'].split(' ')
        if len(token_parts) == 2 and token_parts[0] == 'Bearer':
            # Extract the token part
            token = token_parts[1]
            #token = event['authorizationToken'].split(' ')[1]  # Expected token format: "Bearer <token>"
            # Retrieve JWT Secret from AWS Secrets Manager
            jwt_secret = get_jwt_secret()

            try:
                # Validate the token
                payload = jwt.decode(token, jwt_secret, algorithms=['HS256'])

                # Create IAM policy
                return generate_policy(payload['sub'], 'Allow', event['methodArn'])

            except jwt.ExpiredSignatureError:
                # Token is expired
                print("Token is expired")
                return generate_policy('user', 'Deny', event['methodArn'])
            except (jwt.DecodeError, jwt.InvalidTokenError):
                print("Token is invalid")
                # Token is invalid
                return generate_policy('user', 'Deny', event['methodArn'])
            except Exception as e:
                print(e)
                print("Error")
                return generate_policy('user', 'Deny', event['methodArn'])
        
    # If 'authorizationToken' is missing or not in the expected format
    return {
        'statusCode': 401,
        'body': 'Unauthorized. Invalid token format.'
    }


def generate_policy(principal_id, effect, resource):
    # Generate an IAM policy
    auth_response = {}
    auth_response['principalId'] = principal_id
    if effect and resource:
        policy_document = {
            'Version': '2012-10-17',
            'Statement': [
                {
                    'Action': 'execute-api:Invoke',
                    'Effect': effect,
                    'Resource': resource
                }
            ]
        }
        auth_response['policyDocument'] = policy_document
    return auth_response

def get_jwt_secret():
    secret_name =secret_manager.JWT_SECRET_KEY
    #client = boto3.client('secretsmanager')
    try:
        #get_secret_value_response = client.get_secret_value(SecretId=secret_name)
        return secret_name
    except ClientError as e:
        print(f"Error retrieving secret: {e}")
        raise e
