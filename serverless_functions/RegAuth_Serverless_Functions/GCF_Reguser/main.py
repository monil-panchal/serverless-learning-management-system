from google.cloud import datastore
import requests
import time
import json
import logging
import re
import os


def register_user(request):
    body = {}    
    response = {}
    headers = {
        'Access-Control-Allow-Headers': 'Origin, X-Requested-With, Content-Type, Accept, Authorization',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': '*',
        'Access-Control-Max-Age': '3600'
    }
    if request.method == 'OPTIONS':
        return '', 204, headers
    
    if request.method in ['GET','PUT','PATCH','DELETE']:
        body['message'] = 'Method not supported'        
        return (json.dumps(body), 405, headers)

    headers['Access-Control-Max-Age'] = '1296000'
    headers['Content-Type'] = 'application/json'

    LAMBDA_FUNCTION_URI = os.environ.get('LAMBDA_FUNCTION_URI')
    
    try:
        data = request.get_json()            
        if data:
            data_keys = data.keys()
            print('Dictinary keys: ',data_keys)
            if ('email' not in data_keys) or ('name' not in data_keys) or ('role' not in data_keys) or ('password' not in data_keys) or ('gender' not in data_keys) or ('question' not in data_keys) or ('answer' not in data_keys) or ('instituteName' not in data_keys):
                body["message"] = "Request missing parameters!"
                return (json.dumps(body), 400, headers)
            email = data['email']
            question = data['question']
            answer = data['answer']
            name = data['name']
            gender = data['gender']
            role = data['role']
            instituteName = data['instituteName']
            password = data['password']
            print('Data: ',data)
            if (email=='') or (name=='') or (password=='') or (gender=='') or (answer=='') or (role==''):
                body["message"] = "Form contains empty fields!"
                return (json.dumps(body), 400, headers)
            emailRex = re.compile('^([a-zA-Z0-9_\-\.]+)@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.)|(([a-zA-Z0-9\-]+\.)+))([a-zA-Z]{2,4}|[0-9]{1,3})(\]?)$')
            if emailRex.match(email)== None:
                body["message"] =  'Invalid Email format!'
                return (json.dumps(body), 422, headers)
            passwordRex = re.compile('^(?=.*[a-z])(?=.*[A-Z])(?=.*[0-9])(?=.*[!@#\$%\^&\*])(?=.{8,})')
            if passwordRex.match(password)==None:
                body["message"] = 'Password must contain: At least 1 uppercase, At least 1 lowercase, At least 1 special character, and a minimum length of 8!'
                return (json.dumps(body), 422, headers)
            reqData = {"email": email, "name": name, "password": password, "gender": gender, "question": question, "instituteName": instituteName, "role": role}
            print("Request data sent to Lambda: ",reqData)
            response = requests.post(LAMBDA_FUNCTION_URI, data=json.dumps(reqData), headers={'Content-Type': 'application/json'})
            response = response.json()
            print("Type of response: ",type(response))
            print("Response from lambda:",response)
            print('Keys in response', response.keys())
            print('Type of status code', type(response['statusCode']))
            if (response['statusCode'] >= 400):
                return response['body'], response['statusCode'], headers
            if 'message' in eval(response['body']).keys():
                try:
                    print('Inside try of DS!')
                    client = datastore.Client()
                    entity = datastore.Entity(key=client.key('user'))
                    entity.update({'email': email, 'question': question, 'answer': answer})
                    client.put(entity)
                    body['message'] = 'User registered successfully!'
                    return (json.dumps(body), 200, headers)
                except Exception as e:
                    print('Inside except of DS!')
                    print("ERR:", str(e))
                    body['message'] = str(e)
                    print('first')
                    return (json.dumps(body), 500, headers)
            else:
                print('Inside else of DS!')
                body['message'] = response['body']['error']
                return (json.dumps(body), 500, headers)
        else:
            body["error"] = "Request missing parameters one of ['email', 'name', 'password', 'gender', 'question', 'answer', instituteName', 'role']"
            return (json.dumps(body), 400, headers)
    except Exception as e:
        print("ERROR:", str(e))
        body['message'] = str(e)
        return (json.dumps(body), 500, headers)