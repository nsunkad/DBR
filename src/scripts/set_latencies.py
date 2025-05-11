#!/usr/bin/env python3
import argparse
import subprocess
import sys
import socket
from constants import LOCAL_HOSTNAME, LOCAL_REGION, REGION_LATENCIES, HOSTNAME_REGION_MAPPINGS

def run_command(cmd):
    """Helper function to run a shell command and print it."""
    #print("Running:", cmd)
    result = subprocess.run(cmd, shell=True)
    if result.returncode != 0:
        #print(f"Command failed: {cmd}", file=sys.stderr)
        pass

def resolve_hostname(hostname):
    """Resolve a hostname to a list of IP addresses."""
    try:
        # gethostbyname_ex returns (hostname, aliaslist, ipaddrlist)
        _, _, ipaddrlist = socket.gethostbyname_ex(hostname)
        return ipaddrlist
    except socket.gaierror as e:
        #print(f"Error resolving {hostname}: {e}", file=sys.stderr)
        return []

def main():
    parser = argparse.ArgumentParser(
        description="Assign latencies based on region mapping using tc/netem. "
                    "Local region is determined from your hostname and mapping CSV."
    )
    parser.add_argument(
        "--interface", required=True, help="Network interface (e.g., eth0)"
    )
    args = parser.parse_args()

    # Clear existing tc settings on the interface
    run_command(f"tc qdisc del dev {args.interface} root || true")
    run_command(f"tc qdisc add dev {args.interface} root handle 1: htb default 9999")
    run_command(f"tc class add dev {args.interface} parent 1: classid 1:9999 htb rate 100mbit")

    # Use a counter to assign unique class IDs for each rule
    counter = 10

    # Apply tc rules for all hostnames except the local host
    for hostname, region in HOSTNAME_REGION_MAPPINGS.items():
        if hostname == LOCAL_HOSTNAME:
            continue  # Skip local host

        ips = resolve_hostname(hostname)
        if not ips:
            continue
        if region not in REGION_LATENCIES[LOCAL_REGION]:
            #print(f"Region '{region}' not found for local region '{LOCAL_REGION}' in latencies CSV", file=sys.stderr)
            continue

        delay = REGION_LATENCIES[LOCAL_REGION][region]
        #print(f"Configuring hostname '{hostname}' (region: {region}) with {delay}ms delay "
            #   f"(from local region '{LOCAL_REGION}'). Resolved IPs: {ips}")

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
