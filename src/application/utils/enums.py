from enum import Enum, IntEnum


class Placement(Enum):
    """
    Default placement: next to client
    Smart placement: optimized
    """

    DEFAULT = 1
    SMART = 2
    BRUTE = 3


class DBRStatus(IntEnum):
    """
    Lifecycle status of DBR
    """
    DBR_CREATED = 1
    DBR_RUNNING = 2
    DBR_SUCCESS = 3
    DBR_FAILED = 4


class QueryType(Enum):
    
    """
    Type of query.
    """
    GET = 1
    SET = 2


class QueryStatus(Enum):
    """
    Lifecycle status of query
    """
    QUERY_CREATED = 1
    QUERY_RUNNING = 2
    QUERY_SUCCESS = 3
    QUERY_FAILED = 4
