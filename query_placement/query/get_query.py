from query_placement.query.base_query import BaseQuery
from query_placement.utils.enums import QueryStatus, QueryType


class GetQuery(BaseQuery):
    """Get query"""

    def __init__(self, key):
        super().__init__()
        self.key = key
        self.status = QueryStatus.QUERY_CREATED
        self.query_type = QueryType.GET

    def execute(self):
        """Executes a get query and returns the corresponding value"""

        # Look up which read replica to read from
        raise NotImplementedError("Not yet implemented")
