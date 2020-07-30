import json
import pymysql
import pymysql.cursors
import sys
import hmac
import hashlib
import base64
import boto3
import botocore.exceptions

COGNITO_USER_POOL_ID = 'us-east-1_KINLM8PpJ'
COGNITO_APP_CLIENT_ID = '3dbln0qqhfdvdh2ca8ar7q53o6'
COGNITO_APP_CLIENT_SECRET = '1i6ri5acd5kp1l7nvjmpvculhsbr0i1kea5i5nvuuu37b09tl88q'


def get_secret_hash(username):
    msg = username + COGNITO_APP_CLIENT_ID
    dig = hmac.new(str(COGNITO_APP_CLIENT_SECRET).encode('utf-8'), msg=str(msg).encode('utf-8'), digestmod=hashlib.sha256).digest()
    d2 = base64.b64encode(dig).decode()
    return d2


def lambda_handler(event, context):
    body = {}
    headers = {}
    headers['Access-Control-Allow-Origin'] = '*'
    headers['Content-Type'] = 'application/json'
    try:
        connection = pymysql.connect(host='serverless.cljjsiiqwmmz.us-east-1.rds.amazonaws.com', user='admin', password='Test1234', db='serverless', charset='utf8mb4')
    except Exception as e:
        print(e)
        body['error'] = str(e)
        return {"statusCode": 500, "headers": headers, "body": json.dumps(body)}
    print(type(event))
    data = event
    email = data['email']
    name = data['name']
    password = data['password']
    gender = data['gender']
    question = data['question']
    role = data['role']
    instituteName = data['instituteName']

    print(data)
    
    try:
        print('cognito request initiated')
        client = boto3.client('cognito-idp')
        client.sign_up(ClientId=COGNITO_APP_CLIENT_ID, SecretHash=get_secret_hash(email), Username=email, Password=password,  UserAttributes=[{'Name': "email", 'Value': email}, {'Name': 'name', 'Value': name}, {'Name': 'gender', 'Value': gender}, {'Name': 'custom:question', 'Value': question}], ValidationData=[{'Name': "email", 'Value': email}])
        print('cognito request completed')
        
    except client.exceptions.UsernameExistsException as e:
        print('client.exceptions.UsernameExistsException', str(e))
        body['error'] = "The user already exists!"
        return {"statusCode": 409, "headers": headers, "body": json.dumps(body)}
        
    except client.exceptions.InvalidPasswordException as e:
        print('client.exceptions.InvalidPasswordException', str(e))
        body['error'] = "Invalid Password!"
        return {"statusCode": 422, "headers": headers, "body": json.dumps(body)}
        
    except client.exceptions.UserLambdaValidationException as e:
        print('client.exceptions.UserLambdaValidationException', str(e))
        body['error'] = str(e)
        return {"statusCode": 409, "headers": headers, "body": json.dumps(body)}
        
    except Exception as e:
        print('Error', str(e))
        body['error'] = str(e)
        return {"statusCode": 500, "headers": headers, "body": json.dumps(body)}
        
    try:
        print('inside try')
        with connection.cursor() as cursor:
            sql = "INSERT INTO `user_reg` (`name`, `email`, `institute`, `gender`, `role`) VALUES (%s, %s, %s, %s, %s)"
            cursor.execute(sql, (name, email, instituteName, gender, role))
            connection.commit()
            body["message"] = "Successfully Registered User!"
        connection.close()
        return {"statusCode": 200, "headers": headers, "body": json.dumps(body)}
    except Exception as e:
        body['error'] = "RDS: " + str(e)
        return {"statusCode": 500, "headers": headers, "body": json.dumps(body)}
