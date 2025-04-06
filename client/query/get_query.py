from pydantic import Field
from enums import QueryStatus, QueryType
from dbr.dbr import BaseQuery

class GetQuery(BaseQuery):
    key: bytes

    def __init__(self, key):
        super().__init__(key=key, query_type=QueryType.GET)
    