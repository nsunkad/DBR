from dbr.dbr import DBR
from enums import Placement
from dbr.query import GetQuery, SetQuery
import time

INITIALIZATION_PORT = "50054"
base_url = "apirani2@sp25-cs525-0301.cs.illinois.edu"
server_url = f"http://{base_url}:{INITIALIZATION_PORT}"


def new_dbr(env):
    set_q = SetQuery(b"key4", b"val3new")
    dbr = DBR()
    dbr.name = "TestDBR"
    dbr.add_query(set_q)
    return dbr

def double(env):
    env |= {"new_val": env[b"K"] + env[b"K"]}
    return env    

def double_newval(env):
    env |= {"new_val": env["new_val"] + env["new_val"]}
    return env    

def change(env):
    env |= {"new_val": env["new_val"] + b"hithere!"}
    return env

def set_val(env):
    key = bytes(env["new_val"])
    set_q1 = SetQuery(key, b"chained_key1")
    set_q2 = SetQuery(key, b"chained_key2")
    set_q3 = SetQuery(key, b"chained_key3")

    dbr = DBR()
    dbr.add_query(set_q1)
    dbr.add_query(set_q2)
    dbr.add_query(set_q3)
    return dbr

def get_val(env):
    key = bytes(env["new_val"])
    get_q = GetQuery(key)
    dbr = DBR()
    dbr.add_query(get_q)
    return dbr

def base_case(chain_length):
    get_q = SetQuery(b"K", b"V")
    dbr = DBR()
    dbr.name = "TestDBR"
    dbr.add_query(get_q)
    dbr.placement = Placement.SMART

    dbr = dbr.then_transform(double).then_transform(double_newval)
    for _ in range(chain_length):
        dbr = dbr.then_execute(set_val)
    
    return dbr



def run():
    def get_stats(test_steps, dbr, placement):
        total_time = 0.
        for i in range(test_steps):
            dbr.placement = placement
            start_time = time.time()
            _ = dbr.execute(server_url)
            end_time = time.time()
            total_time += end_time - start_time

            if i % 10 == 0:
                print(f"{i}-{i+9}:", total_time / (i + 1))
        return total_time / test_steps
    
    TEST_STEPS = 100
    CHAIN_LENGTH = 5


    print("MOVING ON TO DEFAULT")
    dbr = base_case(CHAIN_LENGTH)
    default_runtime = get_stats(TEST_STEPS, dbr, Placement.DEFAULT)

    print("MOVING ON TO SMART")
    dbr = base_case(CHAIN_LENGTH)
    smart_runtime = get_stats(TEST_STEPS, dbr, Placement.SMART)

    print("MOVING ON TO BRUTE")
    dbr = base_case(CHAIN_LENGTH)
    brute_runtime = get_stats(TEST_STEPS, dbr, Placement.BRUTE)

    print("Default runtime:", default_runtime)
    print("Brute runtime:", brute_runtime)
    print("Smart runtime:", smart_runtime)


if __name__ == '__main__':
    run()