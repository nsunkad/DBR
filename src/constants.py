import os
import socket
import sys

from logger import Logger
from utils import load_latencies, load_hostname_regions

ROOT_DIR = os.environ.get("ROOT_DIR", None)
if ROOT_DIR is None:
    print("Error: ROOT_DIR environment variable not set.")
    sys.exit(1)

LOGGER = Logger()
REGION_LATENCIES = load_latencies(os.path.join(ROOT_DIR, "config/region_latencies.csv"))
HOSTNAME_REGION_MAPPINGS, REGION_HOSTNAME_MAPPINGS = load_hostname_regions(os.path.join(ROOT_DIR, "config/hostname_regions.csv"))

DATABASE_PORT = "50051"
ORCHESTRATION_PORT = "50052"
EXECUTION_PORT = "50053"
INITIALIZATION_PORT = "50054"

LOCAL_HOSTNAME = socket.getfqdn()
if LOCAL_HOSTNAME not in HOSTNAME_REGION_MAPPINGS:
    LOCAL_HOSTNAME = "localhost"

LOCAL_REGION = HOSTNAME_REGION_MAPPINGS[LOCAL_HOSTNAME]