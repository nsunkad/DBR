# Listen for DBRs
# Once DBR recieved, smart placement [placement.py]
import sys
import os
import grpc

from concurrent import futures

from constants import APPLICATION_PORT, ORCHESTRATION_PORT, ORCHESTRATION_ADDR, ROOT_DIR
from orchestration.placement import placeDBR

# Add the src directory to the Python path
sys.path.insert(0, (os.path.join(ROOT_DIR, "src", "generated")))

# Now import from generated
from generated import dbr_pb2, dbr_pb2_grpc 
from enums import Placement

class DBRServicer(dbr_pb2_grpc.DBRMsgServicer):
    
    def __init__(self, placement_host="localhost", placement_mode=Placement.DEFAULT):
        self.placement_mode = placement_mode
        self.placement_host = placement_host
    
    def Send(self, request, context):
        print("Processing DBR")
        # returns a success message to requsting app server
        # self.placement_host = placeDBR(request, example_setting) # TODO, uncomment this back in
        self._forward_dbr_to_placement(request)
        return dbr_pb2.DBRReply(success=True)

    def _forward_dbr_to_placement(self, dbr):
        placement = self.placement_host + APPLICATION_PORT
        print("Placement: ", placement)
        
        # Schedule DBR at the selected placement location
        with grpc.insecure_channel(placement) as application_channel:
            stub = dbr_pb2_grpc.DBRMsgStub(application_channel)
            response = stub.Schedule(dbr) # Send DBR to placement server
            if response.success:
                print("Placed DBR at {placement} via the {self.placement_mode} placement mode")

def serve():
    # NOTE: Is 10 correct/ok to be hard coded?
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))

    dbr_pb2_grpc.add_DBRMsgServicer_to_server(DBRServicer(), server)
    server.add_insecure_port(ORCHESTRATION_ADDR)
    server.start()
    print(f"Orchestration server started, listening on port {ORCHESTRATION_PORT}")

    # Block until server is terminated, graceful shutdown
    server.wait_for_termination()

if __name__ == '__main__':
    serve()