from dbr.dbr import DBR
from enums import Placement
from query.get_query import GetQuery
from query.set_query import SetQuery
import time

def set(env):
    set_q = SetQuery(b"key3", b"val3")
    dbr = DBR()
    dbr.name = "TestDBR"
    dbr.placement = Placement.DEFAULT
    dbr.add_query(set_q)
    env |= dbr.execute_inner()
    return env

def double(env):
    env |= {"new_val": env[b"key3"] + env[b"key3"]}
    return env    

def change(env):
    env |= {"new_val": env["new_val"] + b"hithere!"}
    return env

def run():
    INITIALIZATION_PORT = "50054"
    # server_url = f"http://apirani2@sp25-cs525-0301.cs.illinois.edu:{INITIALIZATION_PORT}"
    server_url = f"http://localhost:{INITIALIZATION_PORT}"

    get_q = GetQuery(b"key3")
    dbr = DBR()
    dbr.name = "TestDBR"
    dbr.placement = Placement.DEFAULT
    dbr.add_query(get_q)
    dbr = dbr.then(set).then(double).then(change)

    start_time = time.time()
    env = dbr.execute(server_url)
    end_time = time.time()
    print(f"Execution time: {end_time - start_time} seconds")   
    print(env)


if __name__ == '__main__':
    run()