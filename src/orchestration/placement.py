# Placement Service
import sys
import os
from enums import Placement
import grpc
from constants import (
    DATABASE_ADDR,
)

import copy
import socket

from utils import load_latencies, load_hostname_regions
from generated import database_pb2, database_pb2_grpc

DB_CHANNEL = grpc.insecure_channel(DATABASE_ADDR)
DB_STUB = database_pb2_grpc.DatabaseStub(DB_CHANNEL)

# TEST: with read replicas after csv filled in
def placeDBR(dbr, place: Placement):
    if place == Placement.DEFAULT:
        # return client IP, predecessor location
        return dbr.predecessor_location 

    shard_locs = QuerytoLocs(dbr.queries)
    hostname_regions = load_hostname_regions("../config/hostname_regions.csv")
    host_to_region = {}
    for h, r in hostname_regions:
        host_to_region[h] = r
    # NOTE: this is for the very first invocation from an external client ip
    # where the "predecessor" needs to be the hostname of the orchestrator itself
    if dbr.predecessor_location not in host_to_region.keys():
        previous_loc = socket.fqdn()
    else:
        previous_loc = dbr.predecessor_location

    region_latencies = load_latencies("../config/region_latencies.csv")
    test_locs = set()
    if place == Placement.SMART:
        # candidate locations approach
        # compares all access locs + client/prev dbr loc for best 
        # all hosts
        test_locs.add(previous_loc)
        test_locs.update(shard_locs)

    if place == Placement.BRUTE:
        # TODO: compares each possible reigion latency to access locs
        # vectorization for speed up?
        test_locs = set(host_to_region.keys())
    best_host = None
    best_latency = float("inf")
    for candidate in test_locs:
        curr_latency = 0
        # a: prev DBR/client to DBR 
        curr_latency += int(region_latencies[host_to_region[candidate]][host_to_region[dbr.predecessor_location]])
        # NOTE: assumes symmetric RTT latency which gets factored out 
        max_query_latency = float("-inf")
        for loc in shard_locs:
            curr_query_latency = int(region_latencies[host_to_region[candidate]][host_to_region[loc]])
            max_query_latency = max(curr_query_latency, max_query_latency)

        curr_latency += max_query_latency
        # NOTE: chooses lexographically smaller in the event of a tie 
        if curr_latency < best_latency:
            best_host = candidate
            best_latency = curr_latency
        elif curr_latency == best_latency:
            best_host = candidate if candidate < best_host else best_host
    return best_host

# Returns all UNIQUE locations for queries of a DBR
def QuerytoLocs(queries): 
    locations = set()
    for query in queries:
        query_type = query.WhichOneof('query_type')
        if query_type == 'get_query':
            key = query.get_query.key
            regions = KeyToLoc(key, write=False)
            locations.update(regions)
        elif query_type == 'set_query':
            key = query.set_query.key
            region = KeyToLoc(key, write=True)
            # TEST: Do we need to narrow down to exact read region?
            locations.add(region)
        else:
            print('Unknown query type')
    return locations

def KeyToLoc(key, write: bool):
    request = database_pb2.RegionRequest(key=key)
    if write:
        response = DB_STUB.GetWriteRegion(request)
        return response.region
    response = DB_STUB.GetReadRegions(request)
    return response.regions