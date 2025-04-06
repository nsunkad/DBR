import base64
import json
import pickle
from dbr.dbr import DBR
from dbr.dbr_environment import DBREnvironment
from enums import DBRStatus
from query.get_query import GetQuery as GetQ
from query.set_query import SetQuery as SetQ
import requests

def double(env):
    env |= {"new_val": env[b"key3"] + env[b"key3"]}
    return env    

def change(env):
    env |= {"new_val": env["new_val"] + b"hithere!"}
    return env

def run():
    INITIALIZATION_PORT = "50054"
    server_url = f"http://127.0.0.1:{INITIALIZATION_PORT}"

    get_q = GetQ(b"key3")
    dbr = DBR(name="TestDBR")
    dbr.add_query(get_q)
    dbr = dbr.then(double).then(change)
    print(dbr)

    response = dbr.execute(server_url)
    print(response)

    id = str(dbr.id)
    while True:
        response = requests.get(f"{server_url}/check?id={id}")
        if response.status_code == 200:
            data = response.json()
            status = data["status"]
            if status == DBRStatus.DBR_FAILED:
                print("FAILED")
                break
            
            if status == DBRStatus.DBR_SUCCESS:
                print("SUCCESS")
                env = data["env"]
                env = base64.b64decode(env)
                env = pickle.loads(env)
                print(env)
                break
    #     print(response)

    # dbr.successor = dbr2

if __name__ == '__main__':
    run()