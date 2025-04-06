from uuid import uuid4, UUID
from typing import Optional
from abc import ABC, abstractmethod
from pydantic import BaseModel, Field
from enums import QueryType

# Define BaseQuery with a forward reference to DBR
class BaseQuery(BaseModel, ABC):
    id: UUID = Field(default_factory=uuid4)
    query_type: QueryType = Field(default_factory=QueryType)
    key: bytes = None
    value: Optional[bytes] = None
