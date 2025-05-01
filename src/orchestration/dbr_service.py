import asyncio
import threading
import grpc
import random
from constants import EXECUTION_PORT, LOCAL_HOSTNAME, REGION_HOSTNAME_MAPPINGS
from orchestration.placement import placeDBR
from generated import dbr_pb2, dbr_pb2_grpc 
from enums import Placement
from utils import start_background_loop

class DBRServicer(dbr_pb2_grpc.DBReqServiceServicer):
    def __init__(self, placement_host="localhost"):
        self.placement_host = placement_host
        self.connection_cache = {}

        self.loop = asyncio.new_event_loop()
        self.thread = threading.Thread(target=start_background_loop, args=(self.loop,), daemon=True)
        self.thread.start()

        asyncio.run_coroutine_threadsafe(self._start_worker(), self.loop)
        # asyncio.create_task(self.queue_worker())

    async def _start_worker(self):
        self.queue = asyncio.Queue()
        asyncio.create_task(self.queue_worker())
    
    def Schedule(self, dbreq, context):
        # self.loop.call_soon_threadsafe(self.queue.put_nowait, dbreq)
        # self.queue.put_nowait(dbreq)
        self.loop.call_soon_threadsafe(self.queue.put_nowait, dbreq)
        print("Received DBR")
        return dbr_pb2.DBRReply(success=True)

    async def queue_worker(self):
        print("in queue")
        while True:
            print("in loop")
            dbreq = await self.queue.get()
            print("Popped DBR!", dbreq)
            # await asyncio.create_task(self._handle_dbr(dbreq))
            await asyncio.to_thread(self._handle_dbr, dbreq)
        
    def _handle_dbr(self, dbreq):
        print("Handling DBR", dbreq)
        locations = placeDBR(dbreq, dbreq.placement)
        print(locations)
        hostnames = []
        for loc in locations:
            hostnames.extend(REGION_HOSTNAME_MAPPINGS[loc])

        if LOCAL_HOSTNAME in hostnames:
            url = f"{LOCAL_HOSTNAME}:{EXECUTION_PORT}"
            return self._forward_dbr(dbreq, url)

        selected_hostname = random.choice(hostnames)

        url = f"{selected_hostname}:{EXECUTION_PORT}"
        self._forward_dbr(dbreq, url)
        return

    def _forward_dbr(self, dbr, url):
        if url not in self.connection_cache:
            channel = grpc.insecure_channel(url)
            self.connection_cache[url] = channel
        else:
            channel = self.connection_cache[url]
        
        stub = dbr_pb2_grpc.DBReqServiceStub(channel)
        response = stub.Schedule(dbr) # Send DBR to placement server
        if response.success:
            print(f"Placed DBR at {url} via {dbr.placement} placement mode")


dbr_servicer = DBRServicer()