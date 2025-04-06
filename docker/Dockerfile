FROM python:3.13-slim

RUN apt-get update && apt-get install -y gcc libpq-dev iproute2 python3-dev python3-pip python3-wheel curl

# Install Rust via rustup (non-interactive mode)
RUN curl https://sh.rustup.rs -sSf | sh -s -- -y

# Add Cargo (Rust package manager) to the PATH
ENV PATH="/root/.cargo/bin:${PATH}"

COPY . /root
RUN chmod +x /root/docker/entrypoint.sh /root/src/scripts/set_latencies.py

EXPOSE 50051 50052 50053 50054

ENTRYPOINT ["/root/docker/entrypoint.sh"]