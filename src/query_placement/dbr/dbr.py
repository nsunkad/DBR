import time
from uuid import uuid4
from pprint import pformat
from asyncio import TaskGroup
from query_placement.dbr.dbr_environment import DBREnvironment
from query_placement.utils.enums import DBRStatus
from query_placement.utils.globals import LOGGER, CLIENT_LOCATION


# TODO: add static typing
class DBR:
    """
    A DBR (DBRequest) is recursively defined as a chain of DBRs. A single DBR is the largest subset of parallelizable tasks in the program
    """

    def __init__(
        self,
        name=None,
        predecessor_location=None,
        successor=None,
        environment=None,
    ):
        """

        Initialize a DBRequest

        """
        self.id = uuid4()
        self.name = name
        self.status = DBRStatus.DBR_CREATED
        self.queries = {}
        self.predecessor_location = predecessor_location
        self.successor = successor
        self.environment = environment
        self.location = None

    def add_query(self, query) -> None:
        """
        Adds query to associated DBR. DBTs are constructed by the query
        """
        self.queries[query.id] = query

    def remove_query(self, query) -> None:
        """
        Removes query from associated DBR
        """
        if query.id in self.queries:
            self.queries.pop(query.id)

    async def execute(self):
        self.status = DBRStatus.DBR_RUNNING
        start_time = time.time()
        # TODO: Set query locations
        # TODO: Smart placement, set self.location for DBR
        
        async with TaskGroup() as tg:
            dbtasks = [tg.create_task(query.execute()) for _, query in self.queries.items()]

        end_time = time.time()
        results = {
            dbt.query.key: dbt.result() for dbt in dbtasks if dbt.result() is not None
        }
        self.environment |= DBREnvironment(results)
        
        # TODO: Decide successor placement here, immediately after current DBR fetches query results
        # (now we know the input environment for sucessor and can determine which shards successor needs to access)

        time_difference = end_time - start_time
        LOGGER.info("Execution time: %s", time_difference)

        if self.successor:
            self.successor.environment = self.environment
            self.successor.predecessor_location = self.location
        # TODO: Handle sink DBR case
        
        self.status = DBRStatus.DBR_SUCCESS
        LOGGER.info("DBR: %s, %s", self.name, self.status)
        
    def _get_default_placement(self):
         # Default placement
        default_placement = CLIENT_LOCATION
        
        default_placement = (
            self.predecessor_location
        )
        return default_placement

    def _get_smart_placement(self):
        # TODO: determine which candidate location to schedule DBR from, considering all predecessors and successors
        # candidate_locations = self._get_candidate_locations()
        raise NotImplementedError("Not implemented")
    
    def _get_candidate_locations(self):
        # TODO: select candidate locations from default placement location and self.queries
        # default_placement = self._get_default_placement()
        # candidate_locations = [default_placement]
        raise NotImplementedError("Not implemented")
        

    def __repr__(self):
        return f"DBR(tasks={pformat(self.queries)})"
