import json
import pymysql.cursors
import pymysql


def getOnline(request):
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
            if ('email' not in data_keys) or ('is_logout' not in data_keys):
                body["error"] = "Request missing parameters. One of ['email', 'is_logout']"
                return (json.dumps(body), 400, headers)
            email = data['email']
            is_logout = data['is_logout']
            print(email, is_logout)
            if is_logout:
                try:
                    print('Updating user status!')
                    cursor.execute(f"UPDATE user_state SET is_online = '{0}' WHERE email ='{email}';")
                    connection.commit()
                    connection.close()
                    body['message'] = "User offline!"
                    body['statusCode'] = 200
                    return (json.dumps(body), 200, headers)
                except Exception as e:
                    body['error'] = "RDS: " + str(e)
                    return json.dumps(body), 500, headers
            else:
                try:
                    print('Getting online users!')
                    cursor.execute(f"SELECT user_reg.name, user_reg.institute, user_reg.role, user_reg.email FROM user_state INNER JOIN user_reg ON user_state.email=user_reg.email WHERE is_online='{1}';")
                    online_users = cursor.fetchall()
                    result={
                        'active_users':online_users
                    }
                    connection.commit()
                    connection.close()
                    body['result'] = result
                    body['statusCode'] = 200
                    return (json.dumps(body), headers)
                except Exception as e:
                    body['error'] = "RDS: " + str(e)
                    return json.dumps(body), 500, headers
    except Exception as e:
        print(str(e))
        body['error'] = str(e)
        return (json.dumps(body), 500, headers)
