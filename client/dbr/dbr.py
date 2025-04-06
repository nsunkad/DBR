import base64
import pickle
import requests
from uuid import uuid4, UUID
from typing import Dict, Optional, List
from pydantic import BaseModel, Field, field_serializer
from query.base_query import BaseQuery
from dbr.dbr_environment import DBREnvironment
from enums import DBRStatus, Placement
from typing import Callable, Optional
import dill


# DBR references BaseQuery in its queries field using a forward reference.
class DBR(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    name: str = ""
    queries: Dict[UUID, BaseQuery] = Field(default_factory=dict)  # Reference to BaseQuery
    status: DBRStatus = DBRStatus.DBR_CREATED
    predecessor_location: Optional[str] = None
    environment: DBREnvironment = Field(default_factory=DBREnvironment)
    logic_functions: List[Callable[[DBREnvironment], DBREnvironment]] = []
    placement: Placement = Placement.DEFAULT

    def add_query(self, query: BaseQuery) -> None:
        """
        Adds a query to the DBR and sets its back reference.
        """
        self.queries[query.id] = query

    def remove_query(self, query: BaseQuery) -> None:
        """
        Removes a query from the DBR.
        """
        self.queries.pop(query.id, None)

    def execute(self, server_url: str):
        """
        Executes the DBR by converting it to JSON.
        """
        self.status = DBRStatus.DBR_RUNNING
        data = self.model_dump_json(exclude_none=True)  # or use .json() if preferred
        response = requests.post(f"{server_url}/execute", json=data)

        id = str(self.id)
        while True:
            response = requests.get(f"{server_url}/check?id={id}")
            if response.status_code == 200:
                data = response.json()
                status = data["status"]
                if status == DBRStatus.DBR_SUCCESS:
                    env = data["env"]
                    env = base64.b64decode(env)
                    env = pickle.loads(env)
                    return env

                if status == DBRStatus.DBR_FAILED:
                    print("FAILED")
                    break

    @field_serializer("logic_functions")
    def serialize_logic_function(self, logic_functions: Callable[[DBREnvironment], DBREnvironment]) -> Optional[str]:
        serialized = []
        for logic_function in logic_functions:
            logic_function.__module__ = '__main__'
            dump = dill.dumps(logic_function).hex()
            serialized.append(dump)
        return serialized
        
    def then(self, logic_function: Callable[[DBREnvironment], DBREnvironment]):
        self.logic_functions.append(logic_function)
        return self