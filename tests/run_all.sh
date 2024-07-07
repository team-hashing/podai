#!/bin/bash

# Function to stop all background jobs
stop_jobs() {
    kill $(jobs -p)
}

# Catch SIGINT and stop all background jobs
trap stop_jobs SIGINT

# Navigate to the root directory
cd "$(dirname "$0")/.."

# Define DATA_PATH
DATA_PATH="/data"

# Run the main API
(
cd api
bash scripts/run_local.sh
) &

# Run the TTS API
(
cd tts
bash scripts/run.sh
) &

# Run the Gemini API
(
cd gemini
bash scripts/run.sh
) &

# Run the web app
(
cd web
bash scripts/run.sh
) &