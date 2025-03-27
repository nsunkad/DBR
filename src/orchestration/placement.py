# Placement Service
from application.utils.enums import Placement
def placeDBR(place: Placement):
    if place == Placement.DEFAULT:
        # return client IP, predecessor location
        return 0 

    # these are very similar to could also be collapsed
    # into a single else statement and then SMART/BRUTE
    # just decides # of candidate points (few or all) 
    elif place == Placement.SMART:
        # candidate locations approach
        # compares all access locs + client/prev dbr loc for best 
        return 1
    elif place == Placement.BRUTE:
        # compares each possible reigion latency to access locs
        # vectorization for speed up?
        return 2

