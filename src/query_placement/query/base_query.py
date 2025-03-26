from uuid import uuid4
from abc import ABC, abstractmethod


class BaseQuery(ABC):
    """
    Abstract query class
    """

    def __init__(self):
        self.id = uuid4()

    @abstractmethod
    def execute(self):
        """Method to execute the query. Implemented in subclasses."""
