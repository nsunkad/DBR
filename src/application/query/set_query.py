from application.query.base_query import BaseQuery
from application.utils.enums import QueryStatus, QueryType
from dbclient import database_pb2


class SetQuery(BaseQuery):
    """Set query"""

    def __init__(self, key, value):
        super().__init__()
        self.key = key
        self.value = value
        self.status = QueryStatus.QUERY_CREATED
        self.query_type = QueryType.SET

    def execute(self):
        """Executes a get query and returns the corresponding value"""
        request = database_pb2.SetRequest(key=bytes(self.key), value=bytes(self.value))
        response = self.dbr.database_stub.Set(request)
        print("SET response: ", response)
        
        