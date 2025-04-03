from application.query.base_query import BaseQuery
from application.utils.enums import QueryStatus, QueryType
from generated import database_pb2


class GetQuery(BaseQuery):
    """Get query"""

    def __init__(self, key):
        super().__init__()
        self.key = key
        self.status = QueryStatus.QUERY_CREATED
        self.query_type = QueryType.GET

    def execute(self):
        """Executes a get query and returns the corresponding value"""
        request = database_pb2.GetRequest(bytes(self.key))
        response = self.dbr.database_stub.Get(request)
        print("GET response: ", "Key: ", self.key, "Response: ", response)
        
