from uuid import uuid4, UUID
from typing import Dict, Optional, Any, List
from pydantic import BaseModel, Field, field_validator
from enums import DBRStatus, QueryType
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

class SetQuery(BaseQuery):
    key: bytes
    value: bytes
    query_type: QueryType = QueryType.SET

class DBR(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    name: str = ""
    queries: Dict[UUID, BaseQuery] = Field(default_factory=dict)
    status: DBRStatus = DBRStatus.DBR_CREATED
    predecessor_location: Optional[str] = None
    environment: DBREnvironment = Field(default_factory=DBREnvironment)
    logic_functions: List[str]

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