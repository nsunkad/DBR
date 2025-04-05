import sys
import os

sys.path.insert( 0, os.path.abspath(os.path.join(os.path.dirname(__file__), "generated")))

from dbr.dbr import DBR
from query.get_query import GetQuery as GetQ
from query.set_query import SetQuery as SetQ
from constants import ORCHESTRATION_ADDR

def run():
    server_url = ORCHESTRATION_ADDR

    get_q = GetQ(b"key3")
    # set_q = SetQ(b"key3", b"value2")
    # queries = {get_q.id: get_q, set_q.id: set_q}
    queries = {get_q.id: get_q}
    # queries = {set_q.id: set_q}
    dbr = DBR(name="TestDBR", queries=queries)
    response = dbr.execute(server_url)
    print(response)

if __name__ == '__main__':
    run()