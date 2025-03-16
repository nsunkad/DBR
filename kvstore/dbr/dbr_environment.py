from dataclasses import dataclass


@dataclass
class DBREnvironment:
    def __init__(self, env):
        self.env = env

    def lookup_env(self, key):
        """Fetches value for associated key in environment

        Args:
            key (any): A key for a KV pair stored in the database
        """
        if key in self.env:
            return self.env[key]
        else:
            raise KeyError(f"Key '{key}' not found in the dictionary.")

    def __or__(self, other):
        return
