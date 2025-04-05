from query.base_query import BaseQuery
from enums import QueryStatus, QueryType
from generated import dbr_pb2

class GetQuery(BaseQuery):
    """Get query"""

    def __init__(self, key):
        super().__init__()
        self.key = key
        self.status = QueryStatus.QUERY_CREATED
        self.query_type = QueryType.GET

    def marshal(self):
        msg = dbr_pb2.GetQuery()
        msg.id = str(self.id)
        msg.status = int(self.status)
        msg.key = self.key
        query = dbr_pb2.Query(get_query=msg)
        return query
