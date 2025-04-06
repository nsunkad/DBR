import base64
import pickle
from uuid import uuid4, UUID
from typing import Dict, Optional, Any, List
from pydantic import BaseModel, Field, field_validator
import requests
from constants import INITIALIZATION_PORT
from enums import DBRStatus, QueryType, Placement
from abc import ABC
import dill

class DBREnvironment(BaseModel):
    """
    Wrapper for a dictionary mapping between fetched keys and associated values.
    """
    env: Dict[str, Any] = Field(default_factory=dict)

class BaseQuery(BaseModel, ABC):
    id: UUID = Field(default_factory=uuid4)
    query_type: QueryType = Field(default_factory=QueryType)
    key: bytes = None
    value: Optional[bytes] = None

class GetQuery(BaseQuery):
    key: bytes
    query_type: QueryType = QueryType.GET
    def __init__(self, key, query_type=QueryType.GET, id=None):
        if id is None:
            id = uuid4()
        super().__init__(id=id, key=key, query_type=query_type)

class SetQuery(BaseQuery):
    key: bytes
    value: bytes
    query_type: QueryType = QueryType.SET
    def __init__(self, key, value, query_type=QueryType.SET, id=None):
        if id is None:
            id = uuid4()
        super().__init__(id=id, key=key, value=value, query_type=query_type)

class DBR(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    name: str = ""
    queries: Dict[UUID, BaseQuery] = Field(default_factory=dict)
    status: DBRStatus = DBRStatus.DBR_CREATED
    predecessor_location: Optional[str] = None
    environment: DBREnvironment = Field(default_factory=DBREnvironment)
    logic_functions: List[str] = []
    placement: Placement = Field(default=Placement.DEFAULT)

    @field_validator("queries", mode="before")
    @classmethod
    def validate_queries(cls, v: dict) -> dict:
        new_queries = {}
        for key, query_data in v.items():
            # Convert key from str to UUID if needed.
            key_uuid = UUID(key) if isinstance(key, str) else key
            if isinstance(query_data, dict):
                qt = query_data.get("query_type")
                if qt == QueryType.GET:
                    new_queries[key_uuid] = GetQuery.model_validate(query_data)
                elif qt == QueryType.SET:
                    new_queries[key_uuid] = SetQuery.model_validate(query_data)
                else:
                    raise ValueError(f"Unknown query_type: {qt}")
            else:
                new_queries[key_uuid] = query_data
        return new_queries

    def add_query(self, query: BaseQuery) -> None:
        self.queries[query.id] = query

    def remove_query(self, query: BaseQuery) -> None:
        self.queries.pop(query.id, None)

    def execute_inner(self):
        url = f"http://localhost:{INITIALIZATION_PORT}"

        self.status = DBRStatus.DBR_RUNNING
        data = self.model_dump_json(exclude_none=True)  # or use .json() if preferred
        print(data)
        response = requests.post(f"{url}/execute", json=data)

        id = str(self.id)
        while True:
            response = requests.get(f"{url}/check?id={id}")
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
        return {}
