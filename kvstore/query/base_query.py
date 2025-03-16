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

    @abstractmethod
    def _get_nearest_read_replica(self, key):
        """Method that analyzes region latencies and returns the IP address for the best read replica"""

    @abstractmethod
    def _get_all_read_replicas(self, key):
        """Method that returns a list of IP addresses for all read replicas for a given key"""

    @abstractmethod
    def _get_write_replica(self, key):
        """Method that returns leader for a specific key"""
