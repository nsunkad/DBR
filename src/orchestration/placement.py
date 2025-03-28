# Placement Service
from application.utils.enums import Placement
def placeDBR(dbr, place: Placement):
    if place == Placement.DEFAULT:
        # return client IP, predecessor location
        return dbr.predecessor_location 
    else:
        shard_locs = getQueryLocs()
        if place == Placement.SMART:
        # candidate locations approach
        # compares all access locs + client/prev dbr loc for best 
            return 1
        elif place == Placement.BRUTE:
        # compares each possible reigion latency to access locs
        # vectorization for speed up?
            return 2

# TODO: Convert dbr.queries into database locations
# extract keys, rpc db for Read/Write Regions 
def getQueryLocs(): 
    return None