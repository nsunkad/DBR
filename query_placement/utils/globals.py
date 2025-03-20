from query_placement.utils.enums import Placement
from query_placement.utils.logger import Logger
from query_placement.utils.latencies import fetch_latencies

# smart placement by default
PLACEMENT = Placement.SMART
LOGGER = Logger()
CLIENT_LOCATION = "east"
REGION_LATENCIES: dict = fetch_latencies()
