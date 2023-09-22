import http.client
import json
import datetime

def initiate_connection():
    username, password, installation_id = open_pw_file()
    conn = http.client.HTTPSConnection("vrmapi.victronenergy.com")
    payload = json.dumps({"username": username, "password": password})
    headers = {'Content-Type': "application/json"}
    conn.request("POST", "/v2/auth/login", payload, headers)
    print("API connection initiated")
    return conn, installation_id


def open_pw_file():
    file = open("password.txt", "r")
    uname, pw, installation_id = tuple(file.read().split('\n'))
    file.close()
    return uname, pw, installation_id


def get_token(conn, installation_id):
    # Connect and login
    res = conn.getresponse()
    data = res.read().decode("utf-8")
    toke = json.loads(data)["token"]
    return toke


def get_devices(conn, toke, installation_id):
    # Connected devices for a given installation
    headers = {'Content-Type': "application/json", 'x-authorization': "Bearer " + toke}
    conn.request("GET", f"/v2/installations/{installation_id}/system-overview", headers=headers)
    res = conn.getresponse()
    data = res.read().decode("utf-8")
    devi = json.loads(data)['records']
    return devi


def get_installation_data(conn, toke, data_url_selection, installation_id, data_out, scheduler):
    # data_url_selection sollte overall stats sein, da nur so das dictionary funktioniert
    scheduler.enter(10, 1, get_installation_data, (conn, toke, data_url_selection, installation_id, data_out, scheduler))
    headers = {'Content-Type': "application/json", 'x-authorization': "Bearer " + toke}

    day_beginning = datetime.datetime.combine(datetime.datetime.now(), datetime.time.min)
    timestamp = int(day_beginning.timestamp())

    conn.request("GET", f"/v2/installations/{installation_id}/{data_url_selection}start={timestamp}&interval=days", headers=headers)
    res = conn.getresponse()
    data = res.read().decode("utf-8")

    data_out[0] = json.loads(data)['records']['total_consumption'][0][1]




