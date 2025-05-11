import base64
import pickle
import requests
from requests.adapters import HTTPAdapter
from uuid import uuid4, UUID
from typing import Callable, Dict, Optional, List
from pydantic import BaseModel, Field, field_serializer
from dbr.query import BaseQuery, GetQuery, SetQuery
from dbr.function import Function, TransformFunction, ExecuteFunction
from dbr.dbr_environment import DBREnvironment
from enums import DBRStatus, Placement, FunctionType
from typing import Callable, Optional
import dill
import time




# DBR references BaseQuery in its queries field using a forward reference.
class DBR(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    name: str = ""
    queries: Dict[UUID, BaseQuery] = Field(default_factory=dict)  # Reference to BaseQuery
    status: DBRStatus = DBRStatus.DBR_CREATED
    predecessor_location: Optional[str] = None
    environment: DBREnvironment = Field(default_factory=DBREnvironment)
    logic_functions: List[Function] = []
    placement: Placement = Field(default=Placement.DEFAULT)

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
        # print(data)
        adapter = HTTPAdapter(max_retries=1)
        
        session = requests.Session()
        session.mount('http://', adapter)
        response = session.post(f"{server_url}/execute", json=data)
        id = str(self.id)
        # res = requests.get(f"{server_url}/check?id={id}")
        attempts = 0
        while attempts < 1000:
            response = session.get(f"{server_url}/check?id={id}")
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
            attempts += 1
        print("FAILED")
        return {}

    def transform(self, logic_function: Callable[[DBREnvironment], DBREnvironment]):
        self.logic_functions.append(TransformFunction(f=logic_function))
        return self
    
    def then(self, function: Function):
        self.logic_functions.append(function)
        return self

    def then_transform(self, logic_function: Callable[[DBREnvironment], DBREnvironment]):
        return self.transform(logic_function)
    
    def then_execute(self, f: Callable[[], "DBR"]):
        self.logic_functions.append(ExecuteFunction(f=f))
        return self

