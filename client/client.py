from dbr.dbr import DBR
from enums import Placement
from query.get_query import GetQuery as GetQ
from query.set_query import SetQuery as SetQ
import time


def double(env):
    env |= {"new_val": env[b"key3"] + env[b"key3"]}
    return env    

def change(env):
    env |= {"new_val": env["new_val"] + b"hithere!"}
    return env

def run():
    INITIALIZATION_PORT = "50054"
    server_url = f"http://apirani2@sp25-cs525-0301.cs.illinois.edu:{INITIALIZATION_PORT}"

    get_q = GetQ(b"key3")
    dbr = DBR(name="TestDBR", placement=Placement.DEFAULT)
    dbr.add_query(get_q)
    dbr = dbr.then(double).then(change)

    start_time = time.time()
    env = dbr.execute(server_url)
    end_time = time.time()
    print(f"Execution time: {end_time - start_time} seconds")   
    print(env)


if __name__ == '__main__':
    run()