# Listen for DBRs
# Once DBR recieved, smart placement [placement.py]
import sys
import os
import grpc
import signal
from concurrent import futures

from orchestration.placement import placeDBR

# Add the src directory to the Python path
# import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'generated')))

# Now import from generated
from generated import dbr_pb2, dbr_pb2_grpc 
from application.utils.enums import Placement

class DBRServicer(dbr_pb2_grpc.DBRMsgServicer):
    
    def __init__(self):
        self.placement_setting = Placement.BRUTE
        self.placement_host = "localhost"
        self.placement_port = ":50053"
    
    def Send(self, request):
        print("Processing DBR")
        # returns a success message to requsting app server
        # self.placement_host = placeDBR(request, example_setting) # TODO, uncomment this back in
        self._forward_dbr_to_placement(request)
        return dbr_pb2.DBRReply(success=True)

    def _forward_dbr_to_placement(self, dbr):
         # Forward DBR to placement location
        placement = self.placement_host + self.placement_port
        print("Placement: ", placement)
        
        # Placement
        with grpc.insecure_channel(placement) as application_channel:
            stub = dbr_pb2_grpc.DBRMsgStub(application_channel)
            response = stub.Send(dbr) # Send DBR to placement server

def serve():
    # NOTE: Is 10 correct/ok to be hard coded?
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))

    dbr_pb2_grpc.add_DBRMsgServicer_to_server(DBRServicer(), server)
    port = 50052 
    server.add_insecure_port(f'127.0.0.1:{port}')
    server.start()
    print(f"Orchestration server started, listening on port {port}")

    # Block until server is terminated, graceful shutdown
    server.wait_for_termination()

if __name__ == '__main__':
    serve()