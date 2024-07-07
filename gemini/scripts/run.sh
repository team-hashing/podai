#!/bin/bash

# Define DATA_PATH relative to the script's location
DATA_PATH="$(dirname "$0")/../../data"

# Check if DATA_PATH exists
if [ ! -d "$DATA_PATH" ]
then
    # Create DATA_PATH
    mkdir -p "$DATA_PATH"
fi

# Export DATA_PATH so it's available to child processes
export DATA_PATH

# Check if .venv exists
if [ ! -d ".venv" ]
then
    # Create a virtual environment
    python3 -m venv .venv
fi

# Activate the virtual environment
source .venv/bin/activate

# Install the requirements
pip install -r requirements.txt

# Check if uvicorn is installed
if ! pip freeze | grep -q uvicorn
then
    # Install uvicorn
    pip install uvicorn
fi

# Run the FastAPI application with uvicorn
uvicorn app:app --host 0.0.0.0 --port 8002