echo -e "\nTesting POST /api/audio"

package="{
    \"user_id\": \"user1\",
    \"podcast_id\": \"69fc8a1c-3e4d-42d3-a499-6c3c0c2357bc\"
}"

curl -i -o audio.mp3 -X POST -H "Content-Type: application/json" -d "$package" http://localhost:8000/api/audio