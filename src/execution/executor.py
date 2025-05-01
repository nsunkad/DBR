import base64
import json
import asyncio
import dill
import grpc
import requests
from constants import DATABASE_PORT, INITIALIZATION_PORT, LOCAL_HOSTNAME, LOCAL_REGION, ORCHESTRATION_PORT
from database_pb2 import GetRequest, SetRequest
from database_pb2_grpc import DatabaseStub
from dbr_pb2 import EnvEntry
import dbr_pb2_grpc
import pickle
from utils import convert_dbr_to_proto

from enums import DBRStatus, Placement
from custom_types import DBR, DBREnvironment, ExecuteFunction, GetQuery, SetQuery, TransformFunction

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
            asyncio.create_task(self.execute_dbr(dbr))

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

        env = {e.key: e.value for e in dbr.environment.environment}

        for query, result in zip(dbr.queries, query_results):
            if result is None:
                self.handle_failure(dbr.client_location, dbr.id)
                return
                
            if query.WhichOneof('query_type') == "get_query":
                env[query.get_query.key] = result.value
            
            if query.WhichOneof('query_type') == "set_query":
                env[query.set_query.key] = query.set_query.value
                
        print("ENV POST QUERIES", env)

        # Execute all the transform functions that are passed in, then re-schedule chained DBR
        print("ENV BEFORE TRANSFORM FUNCTIONS", env)
        while dbr.logic_functions and dbr.logic_functions[0].WhichOneof('logic_function_type') == "transform_function":
            logic_function = dbr.logic_functions[0]
            dbr.logic_functions.pop(0)
            
            b = bytes.fromhex(logic_function.transform_function.f)
            logic_function = dill.loads(b)
            print(logic_function)
            env = logic_function(env)
        print("ENV AFTER TRANSFORM FUNCTIONS", env)
            
        # Contains a chained DBR, execute it
        if dbr.logic_functions:
            logic_function = dbr.logic_functions[0]
            dbr.logic_functions.pop(0)

            b = bytes.fromhex(logic_function.execute_function.f)
            f = dill.loads(b)
            print("EXECUTE FUNCTION", f)

            f.__globals__['GetQuery'] = GetQuery
            f.__globals__['SetQuery'] = SetQuery
            f.__globals__['DBR'] = DBR
            f.__globals__['Placement'] = Placement

            new_dbr: DBR = f(env)
            print(new_dbr)
            
            new_dbr.id = dbr.id
            new_dbr.name = dbr.name
            new_dbr.predecessor_location = LOCAL_REGION
            new_dbr.client_location = dbr.client_location

            if dbr.placement == Placement.DEFAULT.value:
                new_dbr.placement = Placement.DEFAULT
            if dbr.placement == Placement.SMART.value:
                new_dbr.placement = Placement.SMART
            if dbr.placement == Placement.BRUTE.value:
                new_dbr.placement = Placement.BRUTE


            new_dbr.environment = DBREnvironment()
            for key, value in env.items():
                new_dbr.environment.env[key] = value

            for logic_function in dbr.logic_functions:
                if logic_function.WhichOneof('logic_function_type') == "transform_function":
                    f = TransformFunction(f=logic_function.transform_function.f)
                    new_dbr.logic_functions.append(logic_function)
                    continue
                
                if logic_function.WhichOneof('logic_function_type') == "execute_function":
                    f = ExecuteFunction(f=logic_function.execute_function.f)
                    new_dbr.logic_functions.append(logic_function)

            print(new_dbr)
            new_proto_dbr = convert_dbr_to_proto(new_dbr)

            # Schedule DBR at the new orchestration address
            url = f"{LOCAL_HOSTNAME}:{ORCHESTRATION_PORT}"
            
            if url in self.connection_cache:
                channel = self.connection_cache[url]
            else:
                channel = grpc.insecure_channel(url)
                self.connection_cache[url] = channel

            stub = dbr_pb2_grpc.DBReqServiceStub(channel)
            response = stub.Schedule(new_proto_dbr)
            print(response)

            data = {"id": dbr.id, "local_region": LOCAL_REGION, "functions_remaining": len(dbr.logic_functions)}
            base_url = dbr.client_location if dbr.client_location != LOCAL_HOSTNAME else LOCAL_HOSTNAME
            res = requests.post(f"http://{base_url}:{INITIALIZATION_PORT}/dump", json=data)
            print("DUMP RES", res)
            return
        
        print("DBR execution complete")
        
        url = f"http://{dbr.client_location}:{INITIALIZATION_PORT}/set_dbr_status"
        body = {
            "id": dbr.id,
            "status": DBRStatus.DBR_SUCCESS,
            "env": base64.b64encode(pickle.dumps(env)).decode('utf-8'),
        }

        response = requests.post(url, json=json.dumps(body))
        print(response)
        return
    
    def handle_failure(target, id):
        print("DBR execution failed")

        url = f"http://{target}:{INITIALIZATION_PORT}/set_dbr_status"
        body = {
            "id": id,
            "status": DBRStatus.DBR_FAILED,
            "env": {},
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
        print("EXECUTING GET", request)
        response = self.database.Get(request)
        return response.value

    def execute_set(self, set_query):
        request = SetRequest(key=set_query.key, value=set_query.value)
        print("EXECUTING SET", request)
        response = self.database.Set(request)
        return response.success
        