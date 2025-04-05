import os
import socket
import sys

from logger import Logger
from utils import load_latencies

ROOT_DIR = os.environ.get("ROOT_DIR", None)
if ROOT_DIR is None:
    print("Error: ROOT_DIR environment variable not set.")
    sys.exit(1)

LOGGER = Logger()
REGION_LATENCIES = load_latencies(os.path.join(ROOT_DIR, "config/region_latencies.csv"))

DATABASE_PORT = "50051"
ORCHESTRATION_PORT = "50052"
APPLICATION_PORT = "50053"

DATABASE_URL = "localhost"
ORCHESTRATION_URL = "localhost"
APPLICATION_URL = "localhost"

DATABASE_ADDR = f"{DATABASE_URL}:{DATABASE_PORT}"
ORCHESTRATION_ADDR = f"{ORCHESTRATION_URL}:{ORCHESTRATION_PORT}"
APPLICATION_ADDR = f"{APPLICATION_URL}:{APPLICATION_PORT}"

LOCAL_HOSTNAME = socket.getfqdn()