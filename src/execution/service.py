import sys
import grpc
import asyncio
from execution.executor import Executor
from constants import (
    EXECUTION_PORT,
)
from concurrent import futures

from dbr_pb2 import DBReq, DBREnvironment, DBRReply
from dbr_pb2_grpc import DBReqService
import dbr_pb2_grpc

class ExecutionService(DBReqService):
    queue = asyncio.Queue()
    executor = Executor(queue)
    asyncio.to_thread(executor.run())
    
    def Schedule(self, dbreq, context):
        self.queue.put_nowait(dbreq)
        return DBRReply(success=True)
        
def serve():
    execution_server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))

    dbr_pb2_grpc.add_DBReqServiceServicer_to_server(ExecutionService(), execution_server)

    execution_address = f"0.0.0.0:{EXECUTION_PORT}"
    execution_server.add_insecure_port(execution_address)
    execution_server.start()
    print(f"Application server started, listening on port {EXECUTION_PORT}")

    # Block until server is terminated, graceful shutdown
    execution_server.wait_for_termination()


if __name__ == "__main__":
    serve()
