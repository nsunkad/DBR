#!/usr/bin/env python3
import csv
import argparse
import subprocess
import sys
import socket

def run_command(cmd):
    """Helper function to run a shell command and print it."""
    print("Running:", cmd)
    result = subprocess.run(cmd, shell=True)
    if result.returncode != 0:
        print(f"Command failed: {cmd}", file=sys.stderr)

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

def resolve_hostname(hostname):
    """Resolve a hostname to a list of IP addresses."""
    try:
        # gethostbyname_ex returns (hostname, aliaslist, ipaddrlist)
        _, _, ipaddrlist = socket.gethostbyname_ex(hostname)
        return ipaddrlist
    except socket.gaierror as e:
        print(f"Error resolving {hostname}: {e}", file=sys.stderr)
        return []

def main():
    parser = argparse.ArgumentParser(
        description="Assign latencies based on region mapping using tc/netem. "
                    "Local region is determined from your hostname and mapping CSV."
    )
    parser.add_argument(
        "--interface", required=True, help="Network interface (e.g., eth0)"
    )
    parser.add_argument(
        "--latencies-csv",
        required=True,
        help="CSV file with a latency matrix (regions vs regions)",
    )
    parser.add_argument(
        "--hostname-region-csv",
        required=True,
        help="CSV file mapping hostnames to their region (headers: hostname,region)",
    )
    args = parser.parse_args()

    # Load CSV files
    try:
        latencies = load_latencies(args.latencies_csv)
    except Exception as e:
        print(f"Error loading latencies CSV: {e}", file=sys.stderr)
        sys.exit(1)
    
    try:
        hostname_regions = load_hostname_regions(args.hostname_region_csv)
    except Exception as e:
        print(f"Error loading hostname-region CSV: {e}", file=sys.stderr)
        sys.exit(1)

    # Determine the local region by comparing the local hostname to the mapping.
    local_hostname = socket.getfqdn()
    local_region = None
    for host, region in hostname_regions:
        if host == local_hostname:
            local_region = region
            break

    if local_region is None:
        print(f"Local hostname '{local_hostname}' not found in the hostname-region mapping. "
              "Please add it or specify your region manually.", file=sys.stderr)
        sys.exit(1)
    
    print(f"Determined local region as '{local_region}' for hostname '{local_hostname}'.")

    # Validate that the local region exists in the latencies matrix
    if local_region not in latencies:
        print(f"Local region '{local_region}' not found in latencies CSV", file=sys.stderr)
        sys.exit(1)

    # Clear existing tc settings on the interface
    run_command(f"tc qdisc del dev {args.interface} root || true")
    run_command(f"tc qdisc add dev {args.interface} root handle 1: htb default 9999")
    run_command(f"tc class add dev {args.interface} parent 1: classid 1:9999 htb rate 100mbit")

    # Use a counter to assign unique class IDs for each rule
    counter = 10

    # Apply tc rules for all hostnames except the local host
    for hostname, region in hostname_regions:
        if hostname == local_hostname:
            continue  # Skip local host

        ips = resolve_hostname(hostname)
        if not ips:
            continue

        if region not in latencies[local_region]:
            print(f"Region '{region}' not found for local region '{local_region}' in latencies CSV", file=sys.stderr)
            continue

        delay = latencies[local_region][region]
        print(f"Configuring hostname '{hostname}' (region: {region}) with {delay}ms delay "
              f"(from local region '{local_region}'). Resolved IPs: {ips}")

        # Create a new HTB class for this hostname
        run_command(f"tc class add dev {args.interface} parent 1: classid 1:{counter} htb rate 100mbit")
        # Attach a netem qdisc to add the delay. The handle uses the counter (e.g., 10 becomes 100:)
        run_command(f"tc qdisc add dev {args.interface} parent 1:{counter} handle {counter}0: netem delay {delay}ms")
        # For each resolved IP, add a filter to match traffic destined to that IP.
        for ip in ips:
            run_command(f"tc filter add dev {args.interface} protocol ip parent 1:0 prio 1 u32 match ip dst {ip}/32 flowid 1:{counter}")
        counter += 1

if __name__ == "__main__":
    main()
