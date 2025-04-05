from uuid import uuid4
from abc import ABC, abstractmethod

class BaseQuery(ABC):
    """
    Abstract query class
    """

    def __init__(self):
        self.id = uuid4()
        self.dbr = None

    """Method to marshal the query. Implemented in subclasses."""
    @abstractmethod
    def marshal(self):
        raise NotImplementedError
        
