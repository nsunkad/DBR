import threading
import grpc
from concurrent import futures
from constants import ORCHESTRATION_PORT, INITIALIZATION_PORT
from generated import dbr_pb2_grpc 
from orchestration.dbr_service import dbr_servicer
from orchestration.rest_api import app

def serve():
    rest_thread = threading.Thread(
        target=lambda: app.run(host="0.0.0.0", port=INITIALIZATION_PORT, debug=False, use_reloader=False)
    )
    rest_thread.start()

    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    dbr_pb2_grpc.add_DBReqServiceServicer_to_server(dbr_servicer, server)
    orchestration_address = f"0.0.0.0:{ORCHESTRATION_PORT}"
    server.add_insecure_port(orchestration_address)
    server.start()
    print(f"Orchestration server started, listening on port {ORCHESTRATION_PORT}")

    # Block until server is terminated, graceful shutdown
    server.wait_for_termination()

if __name__ == '__main__':
    serve()