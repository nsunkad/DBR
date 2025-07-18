import asyncio
import csv
from enums import QueryType, FunctionType
from generated import dbr_pb2

def load_latencies(latencies_csv):
    """
    Load the latencies CSV file.
    Assumes the first column is the region name, and the header row contains region names.
    Example CSV:
    region,us-east,us-west,eu
    us-east,0,50,100
    us-west,50,0,120
    eu,100,120,0
    """
    latencies = {}
    with open(latencies_csv, newline="") as csvfile:
        reader = csv.DictReader(csvfile)
        # The first column is assumed to be the row region identifier.
        region_key = reader.fieldnames[0]
        for row in reader:
            region = row[region_key].strip()
            latencies[region] = {}
            for col in reader.fieldnames[1:]:
                latencies[region][col.strip()] = float(row[col].strip())
    return latencies

def load_hostname_regions(hostname_region_csv):
    """
    Load the hostname-region CSV file.
    Assumes headers 'hostname' and 'region'.
    Example CSV:
    hostname,region
    server1.example.com,us-east
    server2.example.com,us-west
    server3.example.com,eu
    """
    hostname_regions_mappings = {}
    region_hostname_mappings = {}
    with open(hostname_region_csv, newline="") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            hostname = row["hostname"].strip()
            region = row["region"].strip()

            hostname_regions_mappings[hostname] = region
            if region not in region_hostname_mappings:
                region_hostname_mappings[region] = []
            region_hostname_mappings[region].append(hostname)

    return hostname_regions_mappings, region_hostname_mappings


def import_protobuf():
    import sys
    import importlib.util
    from constants import ROOT_DIR

    def import_module(module_name, module_path, alias=""):
        spec = importlib.util.spec_from_file_location(module_name, module_path)
        if spec is None:
            #print(f"Error: Could not create module specification for {module_path}")
            return None

        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module

        try:
            spec.loader.exec_module(module)
            if alias:
                sys.modules[alias] = module
            #print(f"Module {module_name} imported successfully.")
        except Exception as e:
            #print(f"Error: Failed to execute module {module_path}: {e}")
            del sys.modules[module_name]
            return None

    import_module("generated.database_pb2", f"{ROOT_DIR}/src/generated/database_pb2.py", alias="database_pb2")
    import_module("generated.database_pb2_grpc", f"{ROOT_DIR}/src/generated/database_pb2_grpc.py", alias="database_pb2_grpc")
    import_module("generated.dbr_pb2", f"{ROOT_DIR}/src/generated/dbr_pb2.py", alias="dbr_pb2")
    import_module("generated.dbr_pb2_grpc", f"{ROOT_DIR}/src/generated/dbr_pb2_grpc.py", alias="dbr_pb2_grpc")

def start_background_loop(loop):
    """Run an asyncio event loop in a background thread."""
    asyncio.set_event_loop(loop)
    loop.run_forever()


def convert_dbr_to_proto(dbr):
    #print("CONVERTING")
    proto_dbr = dbr_pb2.DBReq()
    proto_dbr.id = str(dbr.id)
    proto_dbr.name = dbr.name
    proto_dbr.status = dbr.status.value
    proto_dbr.client_location = dbr.client_location
    proto_dbr.placement = dbr.placement.value

    #print("PREDECESSOR")
    if dbr.predecessor_location is not None:
        proto_dbr.predecessor_location = dbr.predecessor_location
    
    #print("LOGIC FUNCTIONS")
    for logic_function in dbr.logic_functions:
        if logic_function.function_type == FunctionType.TRANSFORM:
            proto_function = dbr_pb2.TransformFunction(f=logic_function.f)
            proto_dbr.logic_functions.append(dbr_pb2.LogicFunction(transform_function=proto_function))
            continue
        
        if logic_function.function_type == FunctionType.EXECUTE:
            proto_function = dbr_pb2.ExecuteFunction(f=logic_function.f)
            proto_dbr.logic_functions.append(dbr_pb2.LogicFunction(execute_function=proto_function))
            continue

        raise ValueError("Unsupported function type")
        
    #print("env")
    for key, value in dbr.environment.env.items():
        proto_dbr.environment.environment.append(dbr_pb2.EnvEntry(key=key, value=value))

    #print("queries")
    for query in dbr.queries.values():
        #print(query)
        if query.query_type == QueryType.GET:
            proto_query = dbr_pb2.GetQuery(id=str(query.id), key=query.key)
            proto_dbr.queries.append(dbr_pb2.Query(get_query=proto_query))
            continue
        
        if query.query_type == QueryType.SET:
            proto_query = dbr_pb2.SetQuery(id=str(query.id), key=query.key, value=query.value)
            proto_dbr.queries.append(dbr_pb2.Query(set_query=proto_query))
            continue
        
        raise ValueError("Unsupported query type")

    #print("PROTO DBR", proto_dbr)
    return proto_dbr
