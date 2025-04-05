import json
import requests
from uuid import uuid4, UUID
from typing import Dict, Optional
from pydantic import BaseModel, Field
from query.base_query import BaseQuery
from dbr.dbr_environment import DBREnvironment
from enums import DBRStatus


# DBR references BaseQuery in its queries field using a forward reference.
class DBR(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    name: str = ""
    queries: Dict[UUID, BaseQuery] = Field(default_factory=dict)  # Reference to BaseQuery
    status: DBRStatus = DBRStatus.DBR_CREATED
    predecessor_location: Optional[str] = None
    successor: "Optional[DBR]" = None  # Recursive reference using forward declaration
    environment: DBREnvironment = Field(default_factory=DBREnvironment)
    location: Optional[str] = None

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
        print(data)
        response = requests.post(f"{server_url}/execute", json=data)
        print(response)
        return response

