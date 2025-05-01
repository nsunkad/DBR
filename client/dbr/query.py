from uuid import uuid4, UUID
from typing import Optional
from abc import ABC, abstractmethod
from pydantic import BaseModel, Field
from enums import QueryType

# Define BaseQuery with a forward reference to DBR
class BaseQuery(BaseModel, ABC):
    id: UUID = Field(default_factory=uuid4)
    query_type: QueryType
    key: bytes = None
    value: Optional[bytes] = None

class GetQuery(BaseQuery):
    key: bytes

    def __init__(self, key):
        super().__init__(key=key, query_type=QueryType.GET)

class SetQuery(BaseQuery):
    key: bytes
    value: bytes

    def __init__(self, key, value):
        super().__init__(key=key, value=value, query_type=QueryType.SET)
