# Listen for DBRs
# Once DBR recieved, smart placement [placement.py]
import sys
import os
import grpc
import asyncio
from application.utils.globals import LOGGER, APPLICATION_PORT, APPLICATION_ADDR, ORCHESTRATION_PORT
from concurrent import futures

# Add the src directory to the Python path
# import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), './generated')))

# Now import from generated
from application.dbr.dbr import DBR
from application.dbr.dbr_environment import DBREnvironment
from generated import dbr_pb2, dbr_pb2_grpc 
class ApplicationService(dbr_pb2_grpc.DBRMsgServicer):
    def Schedule(self, request, context):
        try:
            queries = request.queries
            
            updated_environment = {pair.key: pair.value for pair in request.environment}
            dbr = DBR(request.id, request.name, request.status, request.predecessor_location,request.successor)
            dbr.environment = updated_environment
            asyncio.run(dbr.execute_queries())
        except Exception as e:
            LOGGER.exception(e)
            return dbr_pb2.DBRReply(success=False)
        else:
            request.successor.execute()
        return dbr_pb2.DBRReply(success=True)

def serve():
    application_server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))

    dbr_pb2_grpc.add_DBRMsgServicer_to_server(ApplicationService(), application_server)
    application_server.add_insecure_port(APPLICATION_ADDR)
    application_server.start()
    print(f"Application server started, listening on port {APPLICATION_PORT}")

    # Block until server is terminated, graceful shutdown
    application_server.wait_for_termination()

if __name__ == '__main__':
    serve()