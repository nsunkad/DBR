from queryplacement.utils.enums import Placement
from queryplacement.utils.logger import Logger
from queryplacement.utils.latencies import fetch_latencies

# smart placement by default
PLACEMENT = Placement.SMART
LOGGER = Logger()
CLIENT_LOCATION = "east"
REGION_LATENCIES: dict = fetch_latencies()
