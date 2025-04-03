from dataclasses import dataclass


@dataclass
class DBREnvironment:
    """
    Wrapper for a dictionary mapping between fetched keys and associated values
"""
    def __init__(self, env):
        self.env = env

    def __getitem__(self, key):
        """Fetches value for associated key in environment

        Args:
            key (any): A key for a KV pair stored in the database
        """
        if key in self.env:
            return self.env[key]
        else:
            raise KeyError(f"Key '{key}' not found in the dictionary.")

    def __ior__(self, other):
        if isinstance(other, DBREnvironment):
            self.env |= other.env
        elif isinstance(other, dict):
            self.env |= other
        else:
            raise TypeError("Not a DBREnvironment")
