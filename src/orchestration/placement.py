from enums import Placement
import grpc
from constants import (
    DATABASE_ADDR,
    ROOT_DIR
)

import socket

from utils import load_latencies, load_hostname_regions
from generated import database_pb2, database_pb2_grpc

DB_CHANNEL = grpc.insecure_channel(DATABASE_ADDR)
DB_STUB = database_pb2_grpc.DatabaseStub(DB_CHANNEL)

def get_candidate_locations(placement_mode: Placement, dbr, hostname_to_region, shard_locations):
    candidate_locations = set()

    # return client IP, predecessor location
    # FIXME: Will return None if there is no predecessor location
    if placement_mode == Placement.DEFAULT:
        return set([dbr.predecessor_location])

    # NOTE: this is for the very first invocation from an external client ip
    # where the "predecessor" needs to be the hostname of the orchestrator itself
    if dbr.predecessor_location not in hostname_to_region:
        previous_loc = hostname_to_region[socket.getfqdn()]
    else:
        previous_loc = dbr.predecessor_location

    if placement_mode == Placement.SMART:
        # candidate locations approach, all hosts
        # compares all access locs + client/prev dbr loc for best 
        candidate_locs.add(previous_loc)
        candidate_locs.update(shard_locations)

    if placement_mode == Placement.BRUTE:
        # TODO: compares each possible reigion latency to access locs
        # vectorization for speed up?
        candidate_locs = set(hostname_to_region.keys())

    assert len(candidate_locations) > 0

    return candidate_locations


# TEST: with read replicas after csv filled in
def placeDBR(dbr, place: Placement):
    region_latencies = load_latencies(f"{ROOT_DIR}/config/region_latencies.csv")
    hostname_regions = load_hostname_regions(f"{ROOT_DIR}/config/hostname_regions.csv")
    hostname_to_region = {h: r for h, r in hostname_regions}
    shard_locations = QuerytoLocs(dbr.queries)

    test_locs = get_candidate_locations(place, dbr, hostname_to_region, shard_locations)

    best_host = None
    best_latency = float("inf")
    for candidate in test_locs:
        curr_latency = 0
        # a: prev DBR/client to DBR 
        curr_latency += int(region_latencies[hostname_to_region[candidate]][hostname_to_region[dbr.predecessor_location]])
        # NOTE: assumes symmetric RTT latency which gets factored out 
        max_query_latency = float("-inf")

        for loc in shard_locations:
            curr_query_latency = int(region_latencies[hostname_to_region[candidate]][hostname_to_region[loc]])
            max_query_latency = max(curr_query_latency, max_query_latency)

        curr_latency += max_query_latency
        # NOTE: chooses lexographically smaller in the event of a tie 
        if curr_latency < best_latency:
            best_host = candidate
            best_latency = curr_latency
        elif curr_latency == best_latency and candidate < best_host:
            best_host = candidate
    return best_host

# Returns all UNIQUE locations for queries of a DBR
def QuerytoLocs(queries): 
    locations = set()
    for query in queries:        
        location = query_to_location(query, write=False)
        locations.update(location)
    return locations

def query_to_location(query, write: bool):
    query_type = query.WhichOneof('query_type')
    if query_type == 'get_query':
        key = query.get_query.key
        regions = DB_STUB.GetReadRegions(key)
        return regions
    
    if query_type == 'set_query':
        key = query.set_query.key
        region = DB_STUB.GetWriteRegion(key)
        return region
    
    raise ValueError("Unsupported query type")