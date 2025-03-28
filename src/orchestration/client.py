# this is what application layer will be doing

import sys
import os
import grpc

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'generated')))

# Now import from generated
from generated import dbr_pb2, dbr_pb2_grpc

def run():
    # gRPC channel
    with grpc.insecure_channel('localhost:50052') as channel:
        stub = dbr_pb2_grpc.DBRMsgStub(channel)
        dbr = dbr_pb2.DBR()
        dbr.id = "dbr-1234"
        dbr.name = "TestDBR"
        dbr.status = dbr_pb2.DBRStatus.DBR_CREATED

        query = dbr.queries.add()
        query.key = b"user:123"
        query.status = dbr_pb2.QueryStatus.QUERY_CREATED

        dbr.predecessor_location = "127.0.0.1"
        dbr.successor = "DBR-2345"

        kv = dbr.environment.add()
        kv.key = b"env_key"
        kv.value = b"env_value"
        response = stub.Send(dbr)

if __name__ == '__main__':
    run()
