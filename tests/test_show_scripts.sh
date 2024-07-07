#!/bin/bash

# Define the API endpoint
API_ENDPOINT="http://localhost:8000/api/scripts"

# Define the user_id
USER_ID="user1"

# Send a POST request to the API endpoint
curl -X POST -H "Content-Type: application/json" -d "{\"user_id\": \"$USER_ID\"}" $API_ENDPOINT