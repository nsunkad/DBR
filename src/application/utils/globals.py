from application.utils.enums import Placement
from application.utils.logger import Logger
from application.utils.latencies import fetch_latencies

# smart placement by default
PLACEMENT = Placement.SMART
LOGGER = Logger()
CLIENT_LOCATION = "east"
REGION_LATENCIES: dict = fetch_latencies()
