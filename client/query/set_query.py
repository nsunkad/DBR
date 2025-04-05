from query.base_query import BaseQuery
from enums import QueryStatus, QueryType
from generated import dbr_pb2

class SetQuery(BaseQuery):
    """Set query"""

    def __init__(self, key, value):
        super().__init__()
        self.key = key
        self.value = value
        self.status = QueryStatus.QUERY_CREATED
        self.query_type = QueryType.SET

    def marshal(self):
        msg = dbr_pb2.SetQuery()
        msg.id = str(self.id)
        msg.status = int(self.status)
        msg.key = self.key
        msg.value = self.value
        query = dbr_pb2.Query(set_query=msg)
        return query
        