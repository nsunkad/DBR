from typing import Any, Dict
from pydantic import BaseModel, Field

class DBREnvironment(BaseModel):
    """
    Wrapper for a dictionary mapping between fetched keys and associated values.
    """
    env: Dict[str, Any] = Field(default_factory=dict)

    def __getitem__(self, key: str) -> Any:
        """Fetch the value associated with the key."""
        try:
            return self.env[key]
        except KeyError:
            raise KeyError(f"Key '{key}' not found in the dictionary.")

    def __ior__(self, other: Any):
        """
        Implements the in-place OR operator (|=) to merge environments.
        Merges another DBREnvironment or a dict into this environment.
        """
        if isinstance(other, DBREnvironment):
            self.env |= other.env
        elif isinstance(other, dict):
            self.env |= other
        else:
            raise TypeError("Operand must be a DBREnvironment or dict")
        return self
