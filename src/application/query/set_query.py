from application.query.base_query import BaseQuery
from application.utils.enums import QueryStatus, QueryType


class SetQuery(BaseQuery):
    """Set query"""

    def __init__(self, key):
        super().__init__()
        self.key = key
        self.status = QueryStatus.QUERY_CREATED
        self.query_type = QueryType.SET
        self.dbts = []

    def execute(self):
        """Executes a set query and returns the corresponding value"""
        