echo -e "\nTesting POST /api/audio"
# script is a JSON object in tests/data/script.json
script=$(cat tests/data/script.json | jq )

package="{
    \"user_id\": \"123\",
    \"script\": $script,
    \"podcast_name\": \"whales\"
}"

curl -i -o audio.mp3 -X POST -H "Content-Type: application/json" -d "$package" http://localhost:8000/api/audio

#echo $package
