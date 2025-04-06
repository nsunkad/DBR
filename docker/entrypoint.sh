#!/bin/bash
set -e
cd $ROOT_DIR

python3 -m venv $ROOT_DIR/venv
. $ROOT_DIR/venv/bin/activate
pip3 install --upgrade pip
pip3 install --upgrade setuptools
pip3 install wheel
pip3 install -r requirements.txt


cd $ROOT_DIR/src

# Run the latency configuration script (adjust parameters as needed)
python3 -m scripts.gen_protos
python3 -m scripts.set_latencies --interface eth0
echo "Latency configuration applied. Container will now remain running."

python3 -m execution.service &
python3 -m orchestration.service &
echo "Execution and orchestration servers started. Container will now remain running."

# # Keep the container alive indefinitely
tail -f /dev/null
