from query.base_query import BaseQuery
from enums import QueryStatus, QueryType

class SetQuery(BaseQuery):
    key: bytes
    value: bytes

    def __init__(self, key, value):
        super().__init__(key=key, value=value, query_type=QueryType.SET)
