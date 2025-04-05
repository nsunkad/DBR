from enums import Placement
import grpc
from constants import (
    DATABASE_ADDR,
    LOCAL_HOSTNAME,
    REGION_LATENCIES,
    HOSTNAME_REGIONS
)

import socket
from utils import load_latencies, load_hostname_regions
from generated import database_pb2, database_pb2_grpc

DB_CHANNEL = grpc.insecure_channel(DATABASE_ADDR)
DB_STUB = database_pb2_grpc.DatabaseStub(DB_CHANNEL)

def get_candidate_locations(placement_mode: Placement, dbr, hostname_to_region, shard_locations):
    local_region = hostname_to_region[LOCAL_HOSTNAME]
    print(local_region, dbr.predecessor_location)
    previous_location = dbr.predecessor_location or local_region
    
    candidate_locations = set([previous_location])
    
    # return client IP, predecessor location
    if placement_mode == Placement.DEFAULT:
        pass
    
    # NOTE: this is for the very first invocation from an external client ip
    # where the "predecessor" needs to be the hostname of the orchestrator itself
    if placement_mode == Placement.SMART:
        print("smart placement")
        # candidate locations approach, all hosts
        # compares all access locs + client/prev dbr loc for best 
        candidate_locations.update(shard_locations)

    if placement_mode == Placement.BRUTE:
        print("brute placement")
        # TODO: compares each possible reigion latency to access locs
        # vectorization for speed up?
        candidate_locations = set(hostname_to_region.values())

    print("candidate locations: ", candidate_locations)
    assert len(candidate_locations) > 0
    print("PREV LOC", previous_location)
    return candidate_locations, previous_location


# TEST: with read replicas after csv filled in
def placeDBR(dbr, place: Placement):
    region_latencies = REGION_LATENCIES
    hostname_regions = HOSTNAME_REGIONS
    hostname_to_region = {h: r for h, r in hostname_regions}
    
    shard_hostnames = get_shard_hostnames(dbr.queries)
    print("shard hostnames: ", shard_hostnames)
    shard_locations = set((hostname_to_region[host] for host in shard_hostnames if host in hostname_to_region))
    assert len(shard_locations) > 0

    print("shard locations: ", shard_locations)

    candidate_locations, previous_location = get_candidate_locations(place, dbr, hostname_to_region, shard_locations)
    print("candidate locations: ", candidate_locations)

    best_locations = []
    best_latency = float("inf")
    for candidate_location in candidate_locations:
        curr_latency = region_latencies[candidate_location][previous_location]
        # a: prev DBR/client to DBR 
        # NOTE: assumes symmetric RTT latency which gets factored out 
        max_query_latency = 0

        for shard_location in shard_locations:
            curr_query_latency = region_latencies[candidate_location][shard_location]
            max_query_latency = max(curr_query_latency, max_query_latency)
            print("curr query latency: ", curr_query_latency, "max query latency: ", max_query_latency)

        curr_latency += max_query_latency

        if curr_latency < best_latency:
            best_locations = [candidate_location]
            best_latency = curr_latency
        elif curr_latency == best_latency:
            best_locations.append(candidate_location)
    return best_locations

# Returns all UNIQUE locations for queries of a DBR
def get_shard_hostnames(queries): 
    print("getting locations", queries)
    locations = set()
    for query in queries: 
        location = query_to_location(query)
        locations.update(location)
    print("locations: ", locations)
    return locations

def query_to_location(query):
    print("IN QUERY TO LOCATION")
    query_type = query.WhichOneof('query_type')
    if query_type == "get_query":
        request = database_pb2.RegionRequest(key=query.get_query.key)
        response = DB_STUB.GetReadRegions(request)
        return response.regions
    
    if query_type == "set_query":
        request = database_pb2.RegionRequest(key=query.set_query.key)
        response = DB_STUB.GetWriteRegion(request)
        return [response.region]
    
    raise ValueError("Unsupported query type")