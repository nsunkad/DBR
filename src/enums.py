from enum import IntEnum


class Placement(IntEnum):
    """
    Default placement: next to client
    Smart placement: optimized
    """

    DEFAULT = 0
    SMART = 1
    BRUTE = 2


class DBRStatus(IntEnum):
    """
    Lifecycle status of DBR
    """
    DBR_CREATED = 1
    DBR_RUNNING = 2
    DBR_SUCCESS = 3
    DBR_FAILED = 4


class QueryType(IntEnum):
    
    """
    Type of query.
    """
    GET = 1
    SET = 2


class QueryStatus(IntEnum):
    """
    Lifecycle status of query
    """
    QUERY_CREATED = 1
    QUERY_RUNNING = 2
    QUERY_SUCCESS = 3
    QUERY_FAILED = 4
