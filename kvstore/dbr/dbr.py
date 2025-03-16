import time
from uuid import uuid4
from pprint import pformat
from asyncio import TaskGroup
from kvstore.dbr.dbr_environment import DBREnvironment
from kvstore.utils.enums import DBRStatus
from kvstore.utils.globals import LOGGER, CLIENT_LOCATION


# add static typing w/ mypy and pylint
class DBR:
    """
    A DBR (DBRequest) is recursively defined as a chain of DBRs. A single DBR is the largest subset of parallelizable tasks in the program
    """

    def __init__(
        self,
        name=None,
        predecessor=None,
        successor=None,
        environment=None,
    ):
        """

        Initialize a DBRequest

        """
        self.id = uuid4()
        self.name = name
        self.status = DBRStatus.DBR_CREATED
        self.dbts = {}  # mapping between query ID and dbt
        self.predecessor = predecessor
        self.successor = successor
        self.environment = environment

        # Default placement
        self.location = CLIENT_LOCATION
        if self.predecessor:
            self.location = (
                self.predecessor.location
            )  # default scheduling next to predecessor, smart placement can change this

    def add_query(self, query) -> None:
        """
        Adds query to associated DBR. DBTs are constructed by the query
        """
        query.dbt.dbr = self
        self.dbts[query.id] = query.dbt

    def remove_query(self, query) -> None:
        """
        Removes query from associated DBR
        """
        if query.id in self.dbts:
            self.dbts.pop(query.id)

    async def execute(self):
        self.status = DBRStatus.DBR_RUNNING
        start_time = time.time()
        # TODO: Set DBT locations
        # TODO: Smart placement, set self.location for DBR

        async with TaskGroup() as tg:
            dbtasks = [tg.create_task(dbt.execute()) for dbt in self.dbts]

        end_time = time.time()
        results = {
            dbt.query.key: dbt.result() for dbt in dbtasks if dbt.result() is not None
        }

        results = results | self.environment
        output_environment = DBREnvironment(results)  # set union

        time_difference = end_time - start_time
        LOGGER.info("Execution time: %s", time_difference)

        if self.successor:
            self.successor.environment = output_environment

        # handle sink DBR case
        self.status = DBRStatus.DBR_SUCCESS
        LOGGER.info("DBR: %s, %s", self.name, self.status)

    def __repr__(self):
        return f"DBR(tasks={pformat(self.dbts)})"
