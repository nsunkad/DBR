import sys
import os
import grpc

sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../generated"))
)
# this is what application layer will be doing
from generated.dbr_pb2 import DBReq, DBRStatus, QueryStatus
from generated.dbr_pb2_grpc import DBRMsgStub


def run():
    # grpc channel
    with grpc.insecure_channel("localhost:50052") as orchestration_channel:

        # create a stub for the channel
        stub = DBRMsgStub(orchestration_channel)

        dbr = DBReq()
        dbr.id = "dbr-1234"
        dbr.name = "TestDBR"
        dbr.status = DBRStatus.DBR_CREATED

        query1 = dbr.queries.add()
        query1.get_query.key = b"key"
        query1.status = QueryStatus.QUERY_CREATED

        query2 = dbr.queries.add()
        query2.set_query.key = b"key2"
        query2.status = QueryStatus.QUERY_CREATED

        dbr.predecessor_location = "127.0.0.1"
        dbr.successor = "DBR-2345"

        kv = dbr.environment.add()
        kv.key = b"env_key"
        kv.value = b"env_value"
        response = stub.Send(dbr)


if __name__ == "__main__":
    run()
