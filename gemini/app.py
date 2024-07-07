from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
import json
from pathlib import Path
from src.gemini import generate_podcast_script
import uvicorn
from uuid import uuid4


app = FastAPI()

class PodcastRequest(BaseModel):
    subject: str
    user_id: str

@app.post("/generate_script")
async def generate_script(request: PodcastRequest):
    script = generate_podcast_script(request.subject)
    if script is None:
        raise HTTPException(status_code=500, detail="Script generation failed")

    data_path = os.getenv("DATA_PATH", "/data")
    directory = f"{data_path}/{request.user_id}/scripts"
    Path(directory).mkdir(parents=True, exist_ok=True)

    # Generate a unique script_id using uuid
    script_id = str(uuid4())
    filename = f"script_{script_id}"
    script = standardize_script_format(script)

    with open(f"{directory}/{filename}.json", "w") as script_file:
        script_file.write(json.dumps(script))

    return {"message": "Script generated successfully", "file_path": f"{directory}/{filename}.json", "script_id": script_id}

def standardize_script_format(script):
    # Define a mapping from non-standard speaker names to standard speaker names
    speaker_mapping = {
        "Male Host": "male_host",
        "Female Host": "female_host",
        "male host": "male_host",
        "female host": "female_host",
        "Male_Host": "male_host",
        "Female_Host": "female_host",
        "male_host": "male_host",
        "female_host": "female_host",
    }

    # Iterate over the script
    for section, lines in script.items():
        for line in lines:
            # Get the non-standard speaker name
            non_standard_speaker = line.pop("speaker", None)
            if non_standard_speaker is None:
                continue

            # Get the standard speaker name
            standard_speaker = speaker_mapping.get(non_standard_speaker, "unknown_speaker")

            # Replace the non-standard speaker name with the standard speaker name
            line[standard_speaker] = line.pop(non_standard_speaker, "")

    return script

if __name__ == "__main__":
    try:
        uvicorn.run(app, host="0.0.0.0", port=8002)
    except KeyboardInterrupt:
        pass
