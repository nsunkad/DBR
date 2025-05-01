from dbr.dbr import DBR
from enums import Placement
from dbr.query import GetQuery, SetQuery
import time
import requests

def new_dbr():
    set_q = SetQuery(b"key3", b"val3new")
    dbr = DBR()
    dbr.name = "TestDBR"
    dbr.add_query(set_q)
    return dbr

def double(env):
    env |= {"new_val": env[b"key3"] + env[b"key3"]}
    return env    

def double_newval(env):
    env |= {"new_val": env["new_val"] + env["new_val"]}
    return env    

def change(env):
    env |= {"new_val": env["new_val"] + b"hithere!"}
    return env

def set_val(env):
    key = bytes(env["new_val"])
    set_q = SetQuery(key, b"chained_key")
    dbr = DBR()
    dbr.add_query(set_q)
    return dbr

def get_val(env):
    key = bytes(env["new_val"])
    get_q = GetQuery(key)
    dbr = DBR()
    dbr.add_query(get_q)
    return dbr

def run():
    INITIALIZATION_PORT = "50054"

    # base_url = "localhost"
    base_url = "apirani2@sp25-cs525-0301.cs.illinois.edu"

    server_url = f"http://{base_url}:{INITIALIZATION_PORT}"

    get_q = SetQuery(b"key3", b"val3")
    dbr = DBR()
    dbr.name = "TestDBR"
    dbr.placement = Placement.SMART
    dbr.add_query(get_q)
    dbr = dbr.then_transform(double).then_transform(double_newval).then_execute(set_val).then_execute(get_val)

    start_time = time.time()
    env = dbr.execute(server_url)
    end_time = time.time()
    print(f"Execution time: {end_time - start_time} seconds")   
    print(env)

    logs = requests.get(f"{server_url}/read-dump?id={dbr.id}").json()["data"]
    print(logs)


if __name__ == '__main__':
    run()