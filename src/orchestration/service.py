# Listen for DBRs
# Once DBR recieved, smart placement [placement.py]
import sys
import os

from orchestration.placement import placeDBR

# Add the src directory to the Python path
# import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'generated')))

# Now import from generated
from generated import dbr_pb2 
from application.utils.enums import Placement

# -------------------------------------------------------
# this is what application layer would be doing
# and then sending the .serialized over RPC
dbr = dbr_pb2.DBR()
dbr.id = "dbr-1234"
dbr.name = "TestDBR"
dbr.status = dbr_pb2.DBRStatus.DBR_CREATED

query = dbr.queries.add()
query.key = b"user:123"
query.status = dbr_pb2.QueryStatus.QUERY_CREATED

dbr.predecessor_location = "127.0.0.1"
dbr.successor = "DBR-2345"

kv = dbr.environment.add()
kv.key = b"env_key"
kv.value = b"env_value"
serialized_dbr = dbr.SerializeToString()
# -------------------------------------------------------
# need to add networking/listening code
# but jist is service.py recieves serialized_dbr
received_dbr = dbr_pb2.DBR()
received_dbr.ParseFromString(serialized_dbr)
example_setting = Placement.DEFAULT
print(placeDBR(received_dbr, example_setting))