import os
import sys
import time
from concurrent import futures
from uuid import uuid4
from pprint import pformat
from asyncio import TaskGroup
from application.dbr.dbr_environment import DBREnvironment
from application.utils.enums import DBRStatus
from application.utils.globals import LOGGER, CLIENT_LOCATION
from generated import dbr_pb2, dbr_pb2_grpc

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../', 'generated')))

# Now import from generated


# TODO: add static typing
class DBR:
    """
    A DBR (DBRequest) is recursively defined as a chain of DBRs. A single DBR is the largest subset of parallelizable tasks in the program
    """

    def __init__(
        self,
        name=None,
        predecessor_location=None,
        successor=None,
        environment=None,
    ):
        """

        Initialize a DBRequest

        """
        self.id = uuid4()
        self.name = name
        self.status = DBRStatus.DBR_CREATED
        self.queries = {}
        self.predecessor_location = predecessor_location
        self.successor = successor
        self.environment = environment
        self.location = None

    def add_query(self, query) -> None:
        """
        Adds query to associated DBR. DBTs are constructed by the query
        """
        self.queries[query.id] = query

    def remove_query(self, query) -> None:
        """
        Removes query from associated DBR
        """
        if query.id in self.queries:
            self.queries.pop(query.id)

    def execute(self):
        self.status = DBRStatus.DBR_RUNNING
        start_time = time.time()
        
        
        # Send DBR over orchestration channel for placement
        with grpc.insecure_channel('localhost:50052') as orchestration_channel:
            # create a stub for the channel
            stub = dbr_pb2_grpc.DBRMsgStub(orchestration_channel)
            
            dbr = dbr_pb2.DBR() # TODO: syntax
            dbr.id = self.id
            dbr.name = self.name
            dbr.status = self.status
            dbr.queries = self.queries
            dbr.predecessor_location = self.predecessor_location
            dbr.successor = self.successor
            response = stub.Send(dbr)
        
            if not response.success: 
                print("DBR orchestration failed")
    
    async def execute_queries(self):
        async with TaskGroup() as tg:
            dbtasks = [tg.create_task(query.execute()) for _, query in self.queries.items()]

        results = {
            dbt.query.key: dbt.result() for dbt in dbtasks if dbt.result() is not None
        }
        self.environment |= DBREnvironment(results)

        if self.successor:
            self.successor.environment = self.environment
            self.successor.predecessor_location = self.location
        # TODO: Handle sink DBR case
        
        self.status = DBRStatus.DBR_SUCCESS
        LOGGER.info("DBR: %s, %s", self.name, self.status)

    def __repr__(self):
        return f"DBR(tasks={pformat(self.queries)})"
