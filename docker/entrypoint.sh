#!/bin/bash
set -e

echo "ROOT_DIR is: $ROOT_DIR"
cd $ROOT_DIR

python -m venv $ROOT_DIR/venv
. $ROOT_DIR/venv/bin/activate
pip install --upgrade pip
pip install --upgrade setuptools
pip install wheel
pip install -r requirements.txt

cd $ROOT_DIR/src

# Run the latency configuration script (adjust parameters as needed)
python -m scripts.gen_protos
python -m scripts.set_latencies --interface eth0
echo "Latency configuration applied. Container will now remain running."


cd $ROOT_DIR/src/database && cargo run $ROOT_DIR/config/vms.dat&
python -u -m execution.service &
python -u -m orchestration.service &
echo "Execution and orchestration servers started. Container will now remain running."

# # Keep the container alive indefinitely
tail -f /dev/null
