from uuid import uuid4


class DBT:
    
    """
    A query spins up one or more DBTs (DB Tasks) for query execution
    """
    
    def __init__(self, query=None, location=None):
        """
        Initialize a DBTask
        """
        self.id = uuid4()
        self.dbr = None
        self.query = query
        self.location = location
        
    async def execute(self):
        if not self.dbr:
            raise ValueError(
                "DBT cannot be executed because it is not affiliated with a DBR"
            )

        # map self.dbr.environment into local memory
        raise NotImplementedError("This method has not been implemented yet")
