#!/bin/bash

export DATA_PATH="$(dirname "$0")/../../data"

echo "DATA_PATH: $DATA_PATH"

# Check if DATA_PATH exists
if [ ! -d "$DATA_PATH" ]
then
    # Create DATA_PATH
    mkdir -p "$DATA_PATH"
fi

cd "$(dirname "$0")/.."
go run main.go -env=local