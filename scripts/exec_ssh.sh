#!/bin/bash

if [[ ! -n "$USER" ]]; then
    echo "Set user environment variable!"
    exit 1
fi


# Check if a command was provided as an argument.
if [ "$#" -eq 0 ]; then
    echo "Usage: $0 <command to execute>"
    exit 1
fi

HOSTFILE="vms.dat"

# Check if the host file exists.
if [ ! -f "$HOSTFILE" ]; then
    echo "Host file '$HOSTFILE' not found!"
    exit 1
fi

# Combine all arguments to form the command.
command_to_execute="$*"

echo "Executing command: \"$command_to_execute\" on hosts listed in $HOSTFILE"
echo "-------------------------------------"

# Loop through each host in the host file.
while IFS= read -r host; do
    # Skip empty lines.
    if [[ -n "$host" ]]; then
        TARGET="$USER@$host"
        echo "Executing \"$command_to_execute\" on $TARGET:"
        ssh $TARGET "$command_to_execute" < /dev/null >> "out/$host.out"
    fi
done < "$HOSTFILE"
