#!/bin/bash

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# Check if SCRIPT_DIR is already in PYTHONPATH
if [[ ":$PYTHONPATH:" != *":$SCRIPT_DIR:"* ]]; then
    # If not, append SCRIPT_DIR to PYTHONPATH
    export PYTHONPATH="${PYTHONPATH}:${SCRIPT_DIR}"
    echo "Appended ${SCRIPT_DIR} to PYTHONPATH."
else
    echo "${SCRIPT_DIR} is already in PYTHONPATH."
fi

# Optionally, print the current PYTHONPATH
echo "Current PYTHONPATH: ${PYTHONPATH}"
