#!/bin/bash

# Define DATA_PATH relative to the script's location
export DATA_PATH="$(dirname "$0")/../../data"

# Check if DATA_PATH exists
if [ ! -d "$DATA_PATH" ]
then
    # Create DATA_PATH
    mkdir -p "$DATA_PATH"
fi

# Navigate to the scripts directory
cd "$(dirname "$0")"

# Check if .venv exists
if [ ! -d "../.venv" ]
then
    # Create a virtual environment
    python3 -m venv ../.venv
fi

# Activate the virtual environment
source ../.venv/bin/activate

# Install the requirements
pip install -r ../requirements.txt

# Run the FastAPI application with uvicorn
cd ..
pwd
uvicorn --host 0.0.0.0 --port 8003 app:app --reload