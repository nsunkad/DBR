from uuid import uuid4
from abc import ABC, abstractmethod

from generated.dbr_pb2_grpc import DBRMsgStub
from dbclient.database_pb2 import RegionRequest, GetRequest, SetRequest


class BaseQuery(ABC):
    """
    Abstract query class
    """

    def __init__(self):
        self.id = uuid4()
        self.dbr = None

    @abstractmethod
    def execute(self):
        if not self.dbr:
            raise ValueError("Cannot execute a query not associated with a DBR")
        
        """Method to execute the query. Implemented in subclasses."""
