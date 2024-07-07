#!/bin/bash

# Define the API endpoint
API_ENDPOINT="http://localhost:8000/api/generate_script"

# Define the user_id
USER_ID="user1"

# Check the number of arguments
if [ $# -eq 1 ]; then
    SUBJECT="$1"
    PODCAST_NAME=""
elif [ $# -eq 2 ]; then
    PODCAST_NAME="$1"
    SUBJECT="$2"
else
    SUBJECT="Pasta"
    PODCAST_NAME=""
fi

# Send a POST request to the API endpoint
curl -X POST -H "Content-Type: application/json" -d "{\"user_id\": \"$USER_ID\", \"subject\": \"$SUBJECT\", \"podcast_name\": \"$PODCAST_NAME\"}" $API_ENDPOINT