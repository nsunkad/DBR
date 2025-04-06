import base64
import json
import asyncio
import dill
import grpc
import requests
from constants import DATABASE_PORT, INITIALIZATION_PORT, LOCAL_HOSTNAME, ORCHESTRATION_PORT
from database_pb2 import GetRequest, SetRequest
from database_pb2_grpc import DatabaseStub
from dbr_pb2 import EnvEntry
import dbr_pb2_grpc
import pickle

from enums import DBRStatus

class Executor:
    connection_cache = {}

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
        print("Executing DBR", dbr,)
        loop = asyncio.get_running_loop()
        query_results = await asyncio.gather(*[
            loop.run_in_executor(None, self.execute_query, query) for query in dbr.queries
        ])

        env = {self.get_query_key(query): result for query, result in zip(dbr.queries, query_results)}
        
        for entry in dbr.environment.environment:
            key = entry.key
            value = entry.value
            env[key] = value

        if dbr.logic_functions:
            print("Executing logic function")
            b = bytes.fromhex(dbr.logic_functions[0])
            logic_function = dill.loads(b)
            print("BEFORE ENV", env)
            env = logic_function(env)  # Use the deserialized function here
            print("AFTER ENV", env)
            dbr.logic_functions.pop(0)
            for key, value in env.items():
                dbr.environment.environment.append(EnvEntry(key=key, value=value))
        
        print("Results: ", env)
        # TODO: Send results back to client/next layer
        if dbr.logic_functions:
            print("more logic functions remain")
            url = f"localhost:{ORCHESTRATION_PORT}"
            
            if url in self.connection_cache:
                channel = self.connection_cache[url]
            else:
                channel = grpc.insecure_channel(url)
                self.connection_cache[url] = channel

            stub = dbr_pb2_grpc.DBReqServiceStub(channel)
            response = stub.Schedule(dbr)
            print(response)
            return
        
        print("DBR execution complete")
        print("TODO: Send results back to client", dbr.client_location)
        
        url = f"http://{dbr.client_location}:{INITIALIZATION_PORT}/set_dbr_status"
        body = {
            "id": dbr.id,
            "status": DBRStatus.DBR_SUCCESS,
            "env": base64.b64encode(pickle.dumps(env)).decode('utf-8'),
        }
        print("DATA", url, body)

        response = requests.post(url, json=json.dumps(body))
        print(response)
        return
        
            

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
        