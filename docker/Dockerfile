FROM ubuntu:20.04

# Install necessary packages: iproute2 for tc, python3, and any other needed tools.
RUN apt-get update && apt-get install -y gcc libpq-dev iproute2 python3 python3-pip python3.8-venv python3-dev python3-pip python3-venv python3-wheel

COPY . /root

# Copy the latency configuration script into the container.
RUN chmod +x /root/docker/entrypoint.sh /root/src/scripts/set_latencies.py

EXPOSE 50051 50052 50053 50054

# Set the entrypoint to run the script.
ENTRYPOINT ["/root/docker/entrypoint.sh"]