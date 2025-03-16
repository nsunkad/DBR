from kvstore.query.base_query import BaseQuery
from kvstore.utils.enums import QueryStatus, QueryType


class GetQuery(BaseQuery):
    """Get query"""

    def __init__(self, key):
        super().__init__()
        self.key = key
        self.status = QueryStatus.QUERY_CREATED
        self.query_type = QueryType.GET
        self.dbts = []

    def execute(self):
        """Executes a get query and returns the corresponding value"""

        # Look up which read replica to read from
        raise NotImplementedError("Not yet implemented")

    def _get_nearest_read_replica(self, key):
        """
        Given a key, return the best read replica location
        """

    def _get_all_read_replicas(self, key):
        """
        Given a key, return all the possible locations where the values associated with the key are
        """
        raise NotImplementedError("Not yet implemented")
