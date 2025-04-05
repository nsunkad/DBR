import csv 

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
                latencies[region][col.strip()] = row[col].strip()
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
    hostname_regions = []
    with open(hostname_region_csv, newline="") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            hostname = row["hostname"].strip()
            region = row["region"].strip()
            hostname_regions.append((hostname, region))
    return hostname_regions


def import_protobuf():
    import sys
    import importlib.util
    from constants import ROOT_DIR

    def import_module(module_name, module_path, alias=""):
        spec = importlib.util.spec_from_file_location(module_name, module_path)
        if spec is None:
            print(f"Error: Could not create module specification for {module_path}")
            return None

        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module

        try:
            spec.loader.exec_module(module)
            if alias:
                sys.modules[alias] = module
            print(f"Module {module_name} imported successfully.")
        except Exception as e:
            print(f"Error: Failed to execute module {module_path}: {e}")
            del sys.modules[module_name]
            return None

    import_module("generated.database_pb2", f"{ROOT_DIR}/src/generated/database_pb2.py", alias="database_pb2")
    import_module("generated.database_pb2_grpc", f"{ROOT_DIR}/src/generated/database_pb2_grpc.py", alias="database_pb2_grpc")
    import_module("generated.dbr_pb2", f"{ROOT_DIR}/src/generated/dbr_pb2.py", alias="dbr_pb2")
    import_module("generated.dbr_pb2_grpc", f"{ROOT_DIR}/src/generated/dbr_pb2_grpc.py", alias="dbr_pb2_grpc")
