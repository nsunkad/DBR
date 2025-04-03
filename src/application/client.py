import sys
import os
import grpc
from application.dbr.dbr import DBR
from application.query.get_query import GetQuery as GetQ
from application.query.set_query import SetQuery as SetQ

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'generated')))

# Now import from generated
from generated import dbr_pb2, dbr_pb2_grpc
from application.utils.globals import (
    APPLICATION_ADDR
)

def run():
    # gRPC channel
    with grpc.insecure_channel(APPLICATION_ADDR) as application_channel:
        application_server = dbr_pb2_grpc.DBRMsgStub(application_channel)
        get = GetQ("key1")
        set = SetQ("key1", "value2")
        queries = {get.id: get, set.id: set}
        dbr = DBR(name="TestDBR", queries=queries, successor=None)
        response = dbr.execute()
        print(response)

if __name__ == '__main__':
    run()