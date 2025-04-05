import sys
import os

sys.path.insert( 0, os.path.abspath(os.path.join(os.path.dirname(__file__), "generated")))

from dbr.dbr import DBR
from dbr.dbr_environment import DBREnvironment
from query.get_query import GetQuery as GetQ
from query.set_query import SetQuery as SetQ

def run():
    INITIALIZATION_PORT = "50054"
    server_url = f"http://127.0.0.1:{INITIALIZATION_PORT}"

    get_q = GetQ(b"key3")
    # set_q = SetQ(b"key3", b"value2")
    # queries = {get_q.id: get_q, set_q.id: set_q}
    # queries = {set_q.id: set_q}

    # env.prefix = "abcd"

    # get_q2 = GetQ(bytes(env.prefix) + b"key2")


    dbr = DBR(name="TestDBR")
    dbr.add_query(get_q)

    response = dbr.execute(server_url)
    print(response)

if __name__ == '__main__':
    run()