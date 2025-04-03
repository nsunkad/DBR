import grpc
from application.utils.enums import Placement
from application.utils.logger import Logger
from application.utils.latencies import fetch_latencies

# smart placement by default
PLACEMENT = Placement.SMART
LOGGER = Logger()
CLIENT_LOCATION = "us-east-1"
REGION_LATENCIES: dict = fetch_latencies()
DATABASE_PORT = ":50051"
DATABASE_ADDR = "localhost:50051"

ORCHESTRATION_PORT = ":50052"
ORCHESTRATION_ADDR = "localhost:50052"

APPLICATION_PORT = ":50053"
APPLICATION_ADDR = "localhost:50053"
from generated.dbr_pb2_grpc import DBRMsgStub