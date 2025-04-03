import os
import sys
import grpc
from uuid import uuid4
from pprint import pformat
from asyncio import TaskGroup
from application.dbr.dbr_environment import DBREnvironment
from application.utils.enums import DBRStatus
from application.utils.globals import (
    LOGGER,
    DATABASE_ADDR,
    ORCHESTRATION_ADDR,
)

from generated import dbr_pb2
from generated import dbr_pb2_grpc
from dbclient.database_pb2_grpc import DatabaseStub

# sys.path.insert(
#     0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../", "generated"))
# )

# Now import from generated


# TODO: add static typing
class DBR:
    """
    A DBR (DBRequest) is recursively defined as a chain of DBRs. A single DBR is the largest subset of parallelizable tasks in the program
    """

    def __init__(
        self,
        id=None,
        name=None,
        status=DBRStatus.DBR_CREATED,
        queries={},
        predecessor_location=None,
        successor=None,
        environment=None,
    ):
        """

        Initialize a DBRequest

        """
        self.id = uuid4()
        self.name = name
        self.status = status
        self.queries = queries
        self.predecessor_location = predecessor_location
        self.successor = successor
        self.environment = DBREnvironment()
        self.location = None

        # Because we don't want the additional overhead of connecting to the
        # local database channel on every parallel query, this
        # connection is kept alive and maintained at the DBR level
        self.database_connection = grpc.insecure_channel(DATABASE_ADDR)
        self.database_stub = DatabaseStub(self.database_connection)

    def add_query(self, query) -> None:
        """
        Adds query to associated DBR. DBTs are constructed by the query
        """
        query.dbr = self  # Back pointer for accessing database connection
        self.queries[query.id] = query

    def remove_query(self, query) -> None:
        """
        Removes query from associated DBR
        """
        if query.id in self.queries:
            self.queries.pop(query.id)

    def execute(self):
        self.status = DBRStatus.DBR_RUNNING
        # Send DBR over orchestration channel for placement
        with grpc.insecure_channel(ORCHESTRATION_ADDR) as orchestration_channel:
            orchestration_stub = dbr_pb2_grpc.DBRMsgStub(orchestration_channel)

            dbreq = self._marshal_dbr(self)
            response = orchestration_stub.Send(dbreq)

            if not response.success:
                print("DBR orchestration failed")
            
            return response

    # TODO: perhaps rethink design
    def _marshal_dbr(self, dbr):
        dbreq = dbr_pb2.DBReq()
        dbreq.id = dbr.id
        dbreq.name = dbr.name
        dbreq.status = dbr.status
        dbreq.queries = dbr.queries
        dbreq.predecessor_location = dbr.predecessor_location
        if not self.successor:
            dbreq.successor = ""
            return dbreq
        
        dbreq.successor = self._marshal_dbr(self.successor)
        return dbreq

    async def execute_queries(self):
        async with TaskGroup() as tg:
            dbtasks = [
                tg.create_task(query.execute()) for _, query in self.queries.items()
            ]

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
        return f"DBR(queries={pformat(self.queries)})"

    def __del__(self):
        self.database_connection.close()
