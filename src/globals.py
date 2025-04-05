from logger import Logger
from utils import load_latencies

LOGGER = Logger()
REGION_LATENCIES: dict = load_latencies()

DATABASE_PORT = "50051"
ORCHESTRATION_PORT = "50052"
APPLICATION_PORT = "50053"

DATABASE_URL = "localhost"
ORCHESTRATION_URL = "localhost"
APPLICATION_URL = "localhost"

DATABASE_ADDR = f"{DATABASE_URL}:{DATABASE_PORT}"
ORCHESTRATION_ADDR = f"{ORCHESTRATION_URL}:{ORCHESTRATION_PORT}"
APPLICATION_ADDR = f"{APPLICATION_URL}:{APPLICATION_PORT}"
