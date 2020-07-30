import json
import pymysql.cursors
import pymysql


def getUserFiles(request):
    print('BEGIN', request)
    body = {}
    headers = {}
    headers['Access-Control-Allow-Headers'] = 'Origin, X-Requested-With, Content-Type, Accept, Authorization'
    headers['Access-Control-Allow-Origin'] = '*'
    headers['Access-Control-Allow-Methods'] = '*'
    headers['Access-Control-Max-Age'] = '3600'

    if request.method == 'OPTIONS':
        return ('', 204, headers)

    if request.method in ['GET', 'PUT', 'PATCH', 'DELETE']:
        body['error'] = 'Method not supported'
        return (json.dumps(body), 405, headers)

    headers['Access-Control-Max-Age'] = '1296000'
    headers['Content-Type'] = 'application/json'
    try:
        connection = pymysql.connect(host='serverless.cljjsiiqwmmz.us-east-1.rds.amazonaws.com', user='admin', password='Test1234', db='serverless', charset='utf8mb4', cursorclass=pymysql.cursors.
                               DictCursor)
        cursor = connection.cursor()
        print('------------------Connected to RDS MySQL successfully------------------')
    except Exception as e:
        print(e)
        body['error'] = str(e)
        return (json.dumps(body), 500, headers)
    try:
        data = request.get_json()
        if data:
            print('DATA', data)
            data_keys = data.keys()
            print('dict keys:')
            print(data_keys)
            if ('email' not in data_keys) or ('file_name' not in data_keys) or ('is_upload' not in data_keys):
                body["error"] = "Request missing parameters. One of ['email', 'is_upload', 'file_name']"
                return (json.dumps(body), 400, headers)
            email = data['email']
            file_name = data['file_name']
            is_upload = data['is_upload']
            print(email, is_upload)
            if is_upload:
                try:
                    print('Getting the user...')
                    cursor.execute(f"SELECT * FROM user_reg where email='{email}';")
                    user = cursor.fetchall()
                    print(user)
                    connection.commit()
                    email = user[0]['email']
                    name = user[0]['name']
                    gender = user[0]['gender']
                    institute = user[0]['institute']
                    role = user[0]['role']
                    cursor.execute(f"INSERT INTO user_files (email, name, file_name, role, institute) VALUES ('{email}','{name}','{file_name}','{role}','{institute}');")
                    connection.commit()
                    connection.close()
                    body['result'] = user
                    body['message'] = "Successfully inserted"
                    body['statusCode'] = 200
                    return (json.dumps(body), headers)
                except Exception as e:
                    body['error'] = "RDS: " + str(e)
                    return (json.dumps(body), 500, headers)
            else:
                try:
                    cursor.execute(f"SELECT * FROM user_files where email='{email}';")
                    user = cursor.fetchall()
                    print('{} file(s) found for the user!'.format(len(user)))
                    connection.commit()
                    connection.close()
                    body['result'] = user
                    body['message'] = "Successfully retrieved!"
                    body['statusCode'] = 200
                    return (json.dumps(body), headers)
                except Exception as e:
                    body['error'] = "RDS: " + str(e)
                    return (json.dumps(body), 500, headers)
                
    except Exception as e:
        print(str(e))
        body['error'] = str(e)
        return (json.dumps(body), 500, headers)

                
                