import json
import boto3
import botocore.exceptions
import hmac
import hashlib
import base64
import re

COGNITO_USER_POOL_ID = 'us-east-1_KINLM8PpJ'
COGNITO_APP_CLIENT_ID = '3dbln0qqhfdvdh2ca8ar7q53o6'
COGNITO_APP_CLIENT_SECRET = '1i6ri5acd5kp1l7nvjmpvculhsbr0i1kea5i5nvuuu37b09tl88q'


def get_secret_hash(username):
    msg = username + COGNITO_APP_CLIENT_ID
    dig = hmac.new(str(COGNITO_APP_CLIENT_SECRET).encode('utf-8'), msg=str(msg).encode('utf-8'), digestmod=hashlib.sha256).digest()
    d2 = base64.b64encode(dig).decode()
    return d2

def lambda_handler(event, context):
    print(event)
    data = event
    keys = data.keys()
    body={}
    
    # check request body for email and password fields
    if ('email' not in keys) or ('password' not in keys):
        return {'statusCode': 400, "headers":{'Access-Control-Allow-Origin': '*'}, 'body': json.dumps({'message': "Request missing parameters. Oneof ['email', 'password']"})}
        
    email = data['email']
    password = data['password']
    
    # check for empty fields
    if (email == '') or (password == ''):
        message = "Form contains empty fields!"
        return {'statusCode': 400, "headers":{'Access-Control-Allow-Origin': '*'}, 'body': json.dumps({'message': message })}

    try:
        client = boto3.client('cognito-idp')
        print('1')
        authenticate = {'USERNAME': email, 'PASSWORD': password, "SECRET_HASH": get_secret_hash(email)}
        print('2')
        response = client.initiate_auth(AuthFlow='USER_PASSWORD_AUTH', AuthParameters=authenticate, ClientId=COGNITO_APP_CLIENT_ID)
        print('3')
        print('response:', response)
        
        accessToken = response['AuthenticationResult']['AccessToken']
        userData = client.get_user(AccessToken=accessToken)
        
        # fetching user's email and security question
        user = {}
        for obj in userData['UserAttributes']:
            key = obj['Name']
            value = obj['Value']
            user[key] = value
        
        user = {'email': user['email'], 'question': user['custom:question']}
        return {'statusCode': 200, "headers":{'Access-Control-Allow-Origin': '*'}, "body": json.dumps({'accessToken': accessToken, 'user': user})}
        
    except client.exceptions.NotAuthorizedException as e:
        print("client.exceptions.NotAuthorizedException:", str(e))
        body['error'] = "Not authorized!"
        body['statusCode'] = 401
        print(body)
        print("Returning response!")
        return {'body': json.dumps({"statusCode": "401","headers": {"Access-Control-Allow-Origin": "*"}})}
        
    except Exception as e:
        print("Error:", str(e))
        body['error'] = str(e)
        body['statusCode'] = 500
        return {'statusCode': 500, "headers":{'Access-Control-Allow-Origin': '*'}}