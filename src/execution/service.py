import sys
import threading
import grpc
import asyncio
from execution.executor import Executor
from constants import (
    EXECUTION_PORT,
)
from concurrent import futures

from dbr_pb2 import DBReq, DBREnvironment, DBRReply
import dbr_pb2_grpc
from utils import start_background_loop

class ExecutionService(dbr_pb2_grpc.DBReqServiceServicer):
    def __init__(self):
        self.loop = asyncio.new_event_loop()
        self.thread = threading.Thread(target=start_background_loop, args=(self.loop,), daemon=True)
        self.thread.start()
        
        asyncio.run_coroutine_threadsafe(self._start_worker(), self.loop)

    def Schedule(self, dbreq, context):
        self.loop.call_soon_threadsafe(self.queue.put_nowait, dbreq)
        return DBRReply(success=True)
    
    async def _start_worker(self):
        self.queue = asyncio.Queue()
        self.executor = Executor(self.queue)
        asyncio.create_task(self.executor.run())


def serve():
    execution_server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))

    dbr_pb2_grpc.add_DBReqServiceServicer_to_server(ExecutionService(), execution_server)

    execution_address = f"0.0.0.0:{EXECUTION_PORT}"
    execution_server.add_insecure_port(execution_address)
    execution_server.start()
    print(f"Execution server started, listening on port {EXECUTION_PORT}")

    # Block until server is terminated, graceful shutdown
    execution_server.wait_for_termination()


if __name__ == "__main__":
    serve()
