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
