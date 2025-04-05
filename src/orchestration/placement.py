# Placement Service
from enums import Placement
import sys
import os
import grpc
from globals import (
    DATABASE_ADDR
)

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'generated')))
from generated import database_pb2, database_pb2_grpc

DB_CHANNEL = grpc.insecure_channel(DATABASE_ADDR)
DB_STUB = database_pb2_grpc.DatabaseStub(DB_CHANNEL)

def placeDBR(dbr, place: Placement):
    if place == Placement.DEFAULT:
        # return client IP, predecessor location
        return dbr.predecessor_location 
    shard_locs = QuerytoLocs(dbr.queries)
    if place == Placement.SMART:
        # candidate locations approach
        # TODO: compares all access locs + client/prev dbr loc for best 
        return shard_locs[0]
    if place == Placement.BRUTE:
        # TODO: compares each possible reigion latency to access locs
        # vectorization for speed up?
        
        # TODO: hardcoded to return first shard location, fix
        return shard_locs[0]

def QuerytoLocs(queries): 
    locations = []
    for query in queries:
        query_type = query.WhichOneof('query_type')
        if query_type == 'get_query':
            key = query.get_query.key
            regions = KeyToLoc(key, write=False)
            locations.extend(regions)
        elif query_type == 'set_query':
            key = query.set_query.key
            region = KeyToLoc(key, write=True)
            # TEST: Do we need to narrow down to exact read region?
            locations.append(region)
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