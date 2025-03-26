from application.query.base_query import BaseQuery
from application.utils.enums import QueryStatus, QueryType


class RangeSetQuery(BaseQuery):
    """Range set query"""

    def __init__(self, range_start_key, range_end_key):
        super().__init__()
        self.range_start_key = range_start_key
        self.range_end_key = range_end_key
        self.status = QueryStatus.QUERY_CREATED
        self.query_type = QueryType.RANGE_SET

    def execute(self):
        """Executes a range get query and returns the corresponding value"""
        
        # TODO: check if range_start_key and range_end_key map to two different regions, handle accordingly
        raise NotImplementedError("Not yet implemented")
