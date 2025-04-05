import grpc
from uuid import uuid4
from pprint import pformat
from dbr.dbr_environment import DBREnvironment
from enums import DBRStatus

from generated import dbr_pb2
from generated import dbr_pb2_grpc
from generated.database_pb2_grpc import DatabaseStub


# TODO: add static typing
class DBR:
    """
    A DBR (DBRequest) is recursively defined as a chain of DBRs. A single DBR is the largest subset of parallelizable tasks in the program
    """
    def __init__(
        self,
        name=None,
        status=DBRStatus.DBR_CREATED,
        queries={},
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
        self.predecessor_location = None
        self.successor = successor
        self.environment = DBREnvironment()
        self.location = None

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

    def execute(self, server_url):
        self.status = DBRStatus.DBR_RUNNING
        # Send DBR over orchestration channel for placement
        with grpc.insecure_channel(server_url) as orchestration_channel:
            orchestration_stub = dbr_pb2_grpc.DBReqServiceStub(orchestration_channel)

            request = self._marshal_dbr(self)
            response = orchestration_stub.Schedule(request)

            if not response.success:
                print("DBR orchestration failed")
            
        return response

    def _marshal_dbr(self, dbr):
        dbreq = dbr_pb2.DBReq()
        dbreq.id = str(dbr.id)
        dbreq.name = dbr.name
        dbreq.status = int(dbr.status)
        
        for query in self.queries.values():
            dbreq.queries.append(query.marshal())
        
        if self.predecessor_location:
            dbreq.predecessor_location = self.predecessor_location

        if self.successor:
            dbreq.successor = self._marshal_dbr(self.successor)
        return dbreq

    def __repr__(self):
        return f"DBR(queries={pformat(self.queries)})"
