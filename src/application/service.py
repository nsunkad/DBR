# Listen for DBRs
# Once DBR recieved, smart placement [placement.py]
import sys
import os
import grpc
from application.utils.globals import LOGGER
from concurrent import futures

# Add the src directory to the Python path
# import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'generated')))

# Now import from generated
from generated import dbr_pb2, dbr_pb2_grpc 
from application.utils.enums import Placement

class DBRServicer(dbr_pb2_grpc.DBRMsgServicer):
    def ReceiveDBR(self, dbr):
        try:
            dbr.execute_queries()
        except Exception as e:
            LOGGER.exception(e)
            return dbr_pb2.DBRReply(success=False)
        else:
            dbr.successor.execute()
            
        return dbr_pb2.DBRReply(success=True)

def serve():
    # NOTE: Is 10 correct/ok to be hard coded?
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))

    dbr_pb2_grpc.add_DBRMsgServicer_to_server(DBRServicer(), server)
    port = 50053
    server.add_insecure_port(f'127.0.0.1:{port}')
    server.start()
    print(f"Application server started, listening on port {port}")

    # Block until server is terminated, graceful shutdown
    server.wait_for_termination()

if __name__ == '__main__':
    serve()