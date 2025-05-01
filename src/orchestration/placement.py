from enums import Placement
import grpc
from constants import (
    DATABASE_PORT,
    LOCAL_HOSTNAME,
    HOSTNAME_REGION_MAPPINGS,
    REGION_HOSTNAME_MAPPINGS,
    REGION_LATENCIES,
    HOSTNAME_REGION_MAPPINGS,
    LOCAL_REGION
)

from generated import database_pb2, database_pb2_grpc

db_url = f"{LOCAL_HOSTNAME}:{DATABASE_PORT}"
DB_CHANNEL = grpc.insecure_channel(db_url)
DB_STUB = database_pb2_grpc.DatabaseStub(DB_CHANNEL)

def get_candidate_locations(placement_mode: Placement, dbr, shard_locations):
    print("IN", LOCAL_REGION, dbr.predecessor_location)
    previous_location = dbr.predecessor_location or LOCAL_REGION
    
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
        candidate_locations = set(REGION_HOSTNAME_MAPPINGS.keys())

    print("candidate locations: ", candidate_locations)
    assert len(candidate_locations) > 0
    print("PREV LOC", previous_location)
    return candidate_locations, previous_location


# TEST: with read replicas after csv filled in
def placeDBR(dbr, place: Placement):
    shard_locations = get_shard_locations(dbr.queries)
    shard_hostnames = set()

    for location in shard_locations:
        shard_hostnames.update(REGION_HOSTNAME_MAPPINGS[location])
    
    assert len(shard_locations) > 0
    assert len(shard_hostnames) > 0

    print("shard locations: ", shard_locations)
    print("shard hostnames: ", shard_hostnames)

    candidate_locations, previous_location = get_candidate_locations(place, dbr, shard_locations)
    print("candidate locations: ", candidate_locations)

    best_locations = []
    best_latency = float("inf")
    for candidate_location in candidate_locations:
        curr_latency = REGION_LATENCIES[candidate_location][previous_location]
        # a: prev DBR/client to DBR 
        # NOTE: assumes symmetric RTT latency which gets factored out 
        max_query_latency = 0

        for shard_location in shard_locations:
            curr_query_latency = REGION_LATENCIES[candidate_location][shard_location]
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
def get_shard_locations(queries): 
    print("getting locations", queries)
    locations = set()
    for query in queries: 
        location = query_to_location(query)
        locations.update(location)
    print("locations: ", locations)
    return locations

def query_to_location(query):
    # TODO: DEBUG
    return [LOCAL_REGION]

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