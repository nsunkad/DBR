from dbr.dbr import DBR
from dbr.dbr_environment import DBREnvironment
from query.get_query import GetQuery as GetQ
from query.set_query import SetQuery as SetQ

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

    # env = dbr.environment
    # dbr2 = DBR(name="TestDBR2")
    # # dbr2.add_query(SetQ(b"key4", b"value4"))
    # dbr2.add_query(SetQ(env[b"new_val"], b"value4"))

    # dbr.successor = dbr2

if __name__ == '__main__':
    run()