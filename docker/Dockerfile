FROM ubuntu:20.04

# Install necessary packages: iproute2 for tc, python3, and any other needed tools.
RUN apt-get update && apt-get install -y iproute2 python3 python3-pip

# Copy the latency configuration script into the container.
COPY scripts/set_latencies.py /usr/local/bin/set_latencies.py
COPY docker/entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/set_latencies.py /usr/local/bin/entrypoint.sh

# Copy your CSV files into the container (or mount them later as volumes).
COPY config/region_latencies.csv /etc/latency/region_latencies.csv
COPY config/hostname_regions.csv /etc/latency/hostname_regions.csv

# Set the entrypoint to run the script.
ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]