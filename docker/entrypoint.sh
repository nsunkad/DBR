#!/bin/bash
set -e

# Run the latency configuration script (adjust parameters as needed)
python3 /usr/local/bin/set_latencies.py \
    --interface eth0 \
    --latencies-csv /etc/latency/region_latencies.csv \
    --hostname-region-csv /etc/latency/hostname_regions.csv

echo "Latency configuration applied. Container will now remain running."

# Keep the container alive indefinitely
tail -f /dev/null
