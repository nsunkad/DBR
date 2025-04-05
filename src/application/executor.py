import asyncio
from generated import database_pb2
from generated.database_pb2 import GetRequest, SetRequest
from generated.dbr_pb2 import GetQuery, SetQuery

class Executor:
    def __init__(self, queue):
        self.database = database_pb2.DatabaseStub()
        self.queue = queue
    
    async def run(self):
        while True:
            dbr = await self.queue.get()
            asyncio.to_thread(self.execute_dbr, dbr)

    def execute_query(self, query):
        if isinstance(query, GetQuery):
            return self.execute_get(query)
        
        if isinstance(query, SetQuery):
            return self.execute_set(query)
        
        raise ValueError("Unsupported query type")    
    
    async def execute_dbr(self, dbr):
        query_results = await asyncio.gather(*[self.execute_query(query) for query in dbr.queries])
        results = {query.id: result for query, result in zip(dbr.queries, query_results)}
        print("Results: ", results)
        # TODO: Send results back to client/next layer
        return results

    def execute_get(self, get_query):
        request = GetRequest(key=get_query.key)
        response = self.database.get(request)
        return response.value

    def execute_set(self, set_query):
        request = SetRequest(key=set_query.key, value=set_query.value)
        response = self.database.set(request)
        return response.success
        