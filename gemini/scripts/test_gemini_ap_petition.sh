#!/bin/bash

# Check if an argument was provided
if [ $# -eq 0 ]
then
    echo "No arguments provided. Please provide a subject for the podcast."
    exit 1
fi

# The subject of the podcast
subject=$1

# The user ID (change this to the actual user ID)
user_id="user1"

# The URL of the FastAPI application
url="http://0.0.0.0:8002/generate_script"

# Make a POST request to the /generate_script endpoint
curl -X POST -H "Content-Type: application/json" -d "{\"subject\": \"$subject\", \"user_id\": \"$user_id\"}" $url