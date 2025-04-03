from uuid import uuid4
from abc import ABC, abstractmethod

from generated.dbr_pb2_grpc import DBRMsgStub


class BaseQuery(ABC):
    """
    Abstract query class
    """

    def __init__(self):
        self.id = uuid4()
        self.dbr = None

    @abstractmethod
    def execute(self):
        """Method to execute the query. Implemented in subclasses."""
        if not self.dbr:
            raise ValueError("Cannot execute a query not associated with a DBR")
        
