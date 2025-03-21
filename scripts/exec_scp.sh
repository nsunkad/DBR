#!/bin/bash
if [[ ! -n "$USER" ]]; then
    echo "Set user environment variable!"
    exit 1
fi

# Check if a command was provided as an argument.
if [ "$#" -eq 0 ]; then
    echo "Usage: $0 file"
    exit 1
fi

HOSTFILE="config/vms.dat"

# Check if the host file exists.
if [ ! -f "$HOSTFILE" ]; then
    echo "Host file '$HOSTFILE' not found!"
    exit 1
fi

# Loop through each host in the host file.
while IFS= read -r host; do
    # Skip empty lines.
    if [[ -n "$host" ]]; then
        TARGET="$USER@$host"
        echo "Executing on $host..."
        ssh-copy-id -i "$1" $TARGET
    fi
done < "$HOSTFILE"
