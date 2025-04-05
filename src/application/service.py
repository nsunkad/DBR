# Listen for DBRs
# Once DBR recieved, smart placement [placement.py]
import sys
import os
import grpc
import asyncio
from application.executor import Executor
from constants import (
    LOGGER,
    APPLICATION_PORT,
    APPLICATION_ADDR,
    ROOT_DIR
)
from concurrent import futures

sys.path.insert(0, (os.path.join(ROOT_DIR, "src", "generated")))

from generated import dbr_pb2, dbr_pb2_grpc
from generated.dbr_pb2 import DBReq, DBREnvironment, DBReply

class ApplicationService(dbr_pb2_grpc.DBRMsgServicer):
    queue = asyncio.Queue()
    executor = Executor(queue)
    asyncio.create_task(executor.run())
    
    def Schedule(self, request, context):
        dbr = DBReq(request)
        self.queue.put_nowait(dbr)
        return dbr_pb2.DBRReply(success=True)
        
def serve():
    application_server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))

    dbr_pb2_grpc.add_DBRMsgServicer_to_server(ApplicationService(), application_server)

    application_server.add_insecure_port(APPLICATION_ADDR)
    application_server.start()
    print(f"Application server started, listening on port {APPLICATION_PORT}")

    # Block until server is terminated, graceful shutdown
    application_server.wait_for_termination()


if __name__ == "__main__":
    serve()
