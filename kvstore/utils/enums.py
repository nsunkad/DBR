from enum import Enum


class Placement(Enum):
    """
    Default placement: next to client
    Smart placement: optimized
    """

    DEFAULT = 1
    SMART = 2


class DBRStatus(Enum):
    DBR_CREATED = 1
    DBR_RUNNING = 2
    DBR_SUCCESS = 3
    DBR_FAILED = 4


class DBTStatus(Enum):
    DBT_CREATED = 1
    DBT_STARTED = 2
    DBT_SUCCESS = 3
    DBT_FAILED = 4


class QueryType(Enum):
    GET = 1
    SET = 2
    RANGE_GET = 3
    RANGE_SET = 4


class QueryStatus(Enum):
    QUERY_CREATED = 1
    QUERY_RUNNING = 2
    QUERY_SUCCESS = 3
    QUERY_FAILED = 4
