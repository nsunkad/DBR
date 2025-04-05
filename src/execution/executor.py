import asyncio

import grpc
from constants import DATABASE_PORT, LOCAL_HOSTNAME

from database_pb2 import GetRequest, SetRequest
from dbr_pb2 import GetQuery, SetQuery
from database_pb2_grpc import DatabaseStub


class Executor:
    def __init__(self, queue):
        local_database = f"{LOCAL_HOSTNAME}:{DATABASE_PORT}"
        DB_CHANNEL = grpc.insecure_channel(local_database)
        self.database = DatabaseStub(DB_CHANNEL)
        self.queue = queue

    async def run(self):
        print("Executor started")
        while True:
            print("Executor waiting for DBR")
            dbr = await self.queue.get()
            print("Executor received DBR, now placing in thread", dbr)
            # await asyncio.to_thread(self.execute_dbr, dbr)
            asyncio.create_task(self.execute_dbr(dbr))
            # await self.execute_dbr(dbr)

    def execute_query(self, query):
        query_type = query.WhichOneof('query_type')
        if query_type == "get_query":
            return self.execute_get(query.get_query)
        
        if query_type == "set_query":
            return self.execute_set(query.set_query)
        
        raise ValueError("Unsupported query type")    
    
    async def execute_dbr(self, dbr):
        print("Executing DBR")
        loop = asyncio.get_running_loop()
        query_results = await asyncio.gather(*[
            loop.run_in_executor(None, self.execute_query, query) for query in dbr.queries
        ])
        results = {self.get_query_key(query): result for query, result in zip(dbr.queries, query_results)}
        print("Results: ", results)
        # TODO: Send results back to client/next layer

    def get_query_key(self, query):
        query_type = query.WhichOneof('query_type')
        
        if query_type == "get_query":
            return query.get_query.key
        if query_type == "set_query":
            return query.set_query.key
        
        raise ValueError("Unsupported query type")            
 

    def execute_get(self, get_query):
        request = GetRequest(key=get_query.key)
        response = self.database.Get(request)
        return response.value

    def execute_set(self, set_query):
        request = SetRequest(key=set_query.key, value=set_query.value)
        response = self.database.Set(request)
        return response.success
        