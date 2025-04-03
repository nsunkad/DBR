# Listen for DBRs
# Once DBR recieved, smart placement [placement.py]
import sys
import os
import grpc
import asyncio
from application.utils.globals import (
    LOGGER,
    APPLICATION_PORT,
    APPLICATION_ADDR
)
from concurrent import futures

# Add the src directory to the Python path
# import sys, os
sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), "./generated"))
)

# Now import from generated
from application.dbr.dbr import DBR
from application.dbr.dbr_environment import DBREnvironment
# from application.query.get_query import GetQuery
# from application.query.set_query import SetQuery
from generated import dbr_pb2, dbr_pb2_grpc


class ApplicationService(dbr_pb2_grpc.DBRMsgServicer):
    def Schedule(self, request, context):
        try:
            dbr = self._unmarshal_dbreq(request)
            asyncio.run(dbr.execute_queries())
        except Exception as e:
            LOGGER.exception(e)
            return dbr_pb2.DBRReply(success=False)
        else:
            request.successor.execute()
        return dbr_pb2.DBRReply(success=True)

    # TODO: perhaps rethink design
    def _unmarshal_dbreq(self, dbreq):
        breakpoint()
        dbreq_queries = self._unmarshal_queries(dbreq.queries)
        updated_environment = DBREnvironment({pair.key: pair.value for pair in dbreq.environment})
        dbr = DBR(
            dbreq.id,
            dbreq.name,
            dbreq.status,
            dbreq_queries,
            dbreq.predecessor_location,
            successor=None,
            environment=updated_environment,
        ) # pylint: disable=redundant-keyword-arg

        if not dbreq.successor:
            return dbr

        dbr.successor = self._unmarshal_dbreq(dbreq.successor)
        return dbr

    def _unmarshal_queries(self, dbreq_queries):
        # TODO: Unimplemented
        raise NotImplementedError
        
        
        
def serve():
    application_server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))

    dbr_pb2_grpc.add_DBRMsgServicer_to_server(ApplicationService(), application_server)

    # TODO: these channels should not be insecure
    application_server.add_insecure_port(APPLICATION_ADDR)
    application_server.start()
    print(f"Application server started, listening on port {APPLICATION_PORT}")

    # Block until server is terminated, graceful shutdown
    application_server.wait_for_termination()


if __name__ == "__main__":
    serve()
