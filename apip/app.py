import os
import json
import httpx
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Dict, List
import logging
from colorama import Fore, Style

app = FastAPI()

# Global variables
Env = "local"  # Default environment

# Logging
class ColorLogger:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
        self.logger.addHandler(handler)

    def debug(self, msg, *args, **kwargs):
        self.logger.debug(f"{Fore.CYAN}{msg}{Style.RESET_ALL}", *args, **kwargs)

    def info(self, msg, *args, **kwargs):
        self.logger.info(f"{Fore.BLUE}{msg}{Style.RESET_ALL}", *args, **kwargs)

    def warn(self, msg, *args, **kwargs):
        self.logger.warning(f"{Fore.YELLOW}{msg}{Style.RESET_ALL}", *args, **kwargs)

    def error(self, msg, *args, **kwargs):
        self.logger.error(f"{Fore.RED}{msg}{Style.RESET_ALL}", *args, **kwargs)

logger = ColorLogger()

# Configuration
class Config(BaseModel):
    TTS_IP: str
    TTS_Port: str
    API_Port: str
    GEMINI_IP: str
    GEMINI_Port: str

def load_config() -> Config:
    # with open(f"config/{Env}.json") as f:
    #     return Config(**json.load(f))
    config = Config(
        TTS_IP=os.getenv("TTS_IP"), 
        TTS_Port=os.getenv("TTS_PORT"), 
        API_Port=os.getenv("API_PORT"), 
        GEMINI_IP=os.getenv("GEMINI_IP"), 
        GEMINI_Port=os.getenv("GEMINI_PORT")
    )

    return config

config = load_config()
# TODO Arreglar esto
# config = Config(TTS_IP="0.0.0.0", TTS_Port="8001", API_Port="8000", GEMINI_Port="8002")

# Models
class Item(BaseModel):
    id: str
    name: str
    price: float

class RequestBody(BaseModel):
    user_id: str
    podcast_id: str

class GenerateScriptRequest(BaseModel):
    user_id: str
    subject: str
    podcast_name: str

class GeneratePodcastRequest(BaseModel):
    user_id: str
    subject: str
    podcast_name: str

# Global variables
items: List[Item] = []

@app.get("/api/items")
async def get_items():
    return items

@app.post("/api/items")
async def create_item(item: Item):
    items.append(item)
    return item

@app.post("/api/audio")
async def get_audio(body: RequestBody):
    """
    Endpoint to get audio for a given podcast.
    
    Args:
        body (RequestBody): The request body containing user_id and podcast_id.
    
    Returns:
        JSONResponse: A response indicating success or failure.
    """
    logger.info("API called with user_id: %s and podcast_id: %s", body.user_id, body.podcast_id)

    # Get the data path from environment variables
    data_path = os.getenv("DATA_PATH")
    if not data_path:
        logger.error("DATA_PATH environment variable not set")
        raise HTTPException(status_code=500, detail="Server configuration error")

    # Load names from the JSON file
    try:
        with open(f"{data_path}/names.json") as f:
            names = json.load(f)
    except FileNotFoundError:
        logger.error(f"names.json file not found in {data_path}")
        raise HTTPException(status_code=500, detail="Server configuration error")
    except json.JSONDecodeError:
        logger.error("Error decoding names.json")
        raise HTTPException(status_code=500, detail="Server configuration error")

    # Get the podcast name from the names dictionary
    podcast_name = names.get(body.podcast_id)
    if not podcast_name:
        logger.error(f"Name not found for podcast ID: {body.podcast_id}")
        raise HTTPException(status_code=404, detail="Podcast not found")

    # Prepare the payload for the TTS service
    payload = {
        "user_id": body.user_id,
        "podcast_name": podcast_name,
        "podcast_id": body.podcast_id,
    }

    # Make an asynchronous request to the TTS service
    try:
        async with httpx.AsyncClient(timeout=600.0) as client:  # Set timeout to 600 seconds (10 minutes)
            response = await client.post(f"http://{config.TTS_IP}:{config.TTS_Port}/api/audio", json=payload)
    except httpx.TimeoutException:
        logger.error("The request to the TTS service timed out")
        raise HTTPException(status_code=504, detail="The request to the TTS service timed out")
    except httpx.RequestError as exc:
        logger.error(f"An error occurred while requesting audio: {exc}")
        raise HTTPException(status_code=500, detail="Error communicating with TTS service")

    # Check the response status code
    if response.status_code == 200:
        logger.info("Received 200 OK from TTS service")
        return JSONResponse(status_code=200, content={})
    else:
        logger.error(f"Received non-OK response: {response.status_code}")
        raise HTTPException(status_code=response.status_code, detail="Error getting audio")
    


@app.post("/api/generate_script")
async def generate_script(body: GenerateScriptRequest):
    logger.info("Generating script")

    if not body.podcast_name:
        body.podcast_name = body.subject

    payload = {
        "user_id": body.user_id,
        "subject": body.subject,
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(f"http://{config.GEMINI_IP}:{config.GEMINI_Port}/generate_script", json=payload)

    if response.status_code != 200:
        logger.error(f"Unable to generate script: {response.status_code}")
        raise HTTPException(status_code=response.status_code, detail="Error generating script")

    script_id = response.json().get("script_id")
    if not script_id:
        logger.error("script_id not found in response")
        raise HTTPException(status_code=500, detail="Script ID not found")

    data_path = os.getenv("DATA_PATH")
    if not data_path:
        logger.error("DATA_PATH environment variable is not set")
        raise HTTPException(status_code=500, detail="DATA_PATH not set")

    script_path = f"{data_path}/names.json"
    try:
        with open(script_path, "r+") as f:
            existing_data = json.load(f)
            existing_data[script_id] = body.podcast_name
            f.seek(0)
            json.dump(existing_data, f)
            f.truncate()
    except Exception as e:
        logger.error(f"Unable to write to file: {e}")
        raise HTTPException(status_code=500, detail="Error saving script")

    logger.info("Script generated successfully")
    return {"podcast_id": script_id}

@app.post("/api/scripts")
async def get_scripts(body: Dict[str, str]):
    logger.info("Getting scripts")

    data_path = os.getenv("DATA_PATH")
    scripts_path = f"{data_path}/{body['user_id']}/scripts/"

    try:
        entries = os.listdir(scripts_path)
    except Exception as e:
        logger.error(f"Unable to read directory: {e}")
        raise HTTPException(status_code=500, detail="Unable to read scripts directory")

    scripts = []
    for entry in entries:
        if os.path.isdir(os.path.join(scripts_path, entry)):
            continue

        podcast_id = entry.replace("script_", "").replace(".json", "")

        try:
            with open(f"{data_path}/names.json") as f:
                names = json.load(f)
        except Exception as e:
            logger.error(f"Unable to open names file: {e}")
            continue

        podcast_name = names.get(podcast_id)
        if not podcast_name:
            logger.error(f"Name not found for podcast ID: {podcast_id}")
            continue

        scripts.append({"id": podcast_id, "name": podcast_name})

    return scripts

@app.post("/api/generate_podcast")
async def generate_podcast(body: GeneratePodcastRequest):
    logger.info("Generating podcast")

    if not body.podcast_name:
        body.podcast_name = body.subject

    # Generate script
    script_payload = {
        "user_id": body.user_id,
        "subject": body.subject,
    }

    async with httpx.AsyncClient(timeout=600.0) as client:  # Set timeout to 600 seconds (10 minutes)
        try:
            script_response = await client.post(f"http://{config.GEMINI_IP}:{config.GEMINI_Port}/generate_script", json=script_payload)

        except httpx.TimeoutException:
            logger.error("The request to the TTS service timed out")
            raise HTTPException(status_code=504, detail="The request to the TTS service timed out")
        
        except httpx.RequestError as exc:
            logger.error(f"An error occurred while requesting the script: {exc}")
            raise HTTPException(status_code=500, detail="Error communicating with the TTS service")

    if script_response.status_code != 200:
        logger.error(f"Unable to generate script: {script_response.status_code}")
        raise HTTPException(status_code=script_response.status_code, detail="Error generating script")

    script_id = script_response.json().get("script_id")
    if not script_id:
        logger.error("script_id not found in response")
        raise HTTPException(status_code=500, detail="Script ID not found")

    # Save podcast name
    data_path = os.getenv("DATA_PATH")
    if not data_path:
        logger.error("DATA_PATH environment variable is not set")
        raise HTTPException(status_code=500, detail="DATA_PATH not set")

    script_path = f"{data_path}/names.json"
    if not os.path.exists(script_path):
        with open(script_path, "w") as f:
            f.write("{}")
    
    # Read file and get data
    existing_data = {}
    try:
        with open(script_path, "r") as f:
            existing_data = json.load(f)
    except Exception as e:
        logger.error(f"Unable to read file: {e}")
        raise HTTPException(status_code=500, detail="Error reading script file")
    
    # Add new data
    existing_data[script_id] = body.podcast_name
    try:
        with open(script_path, "w") as f:
            json.dump(existing_data, f)
    except Exception as e:
        logger.error(f"Unable to write to file: {e}")
        raise HTTPException(status_code=500, detail="Error saving script")

    logger.info("Script generated successfully")

    # Generate audio
    audio_payload = {
        "user_id": body.user_id,
        "podcast_name": body.podcast_name,
        "podcast_id": script_id,
    }

    async with httpx.AsyncClient(timeout=600.0) as client:  # Set timeout to 600 seconds (10 minutes)
        try:
            audio_response = await client.post(f"http://{config.TTS_IP}:{config.TTS_Port}/api/audio", json=audio_payload)
        except httpx.TimeoutException:
            logger.error("The request to the TTS service timed out")
            raise HTTPException(status_code=504, detail="The request to the TTS service timed out")
        except httpx.RequestError as exc:
            logger.error(f"An error occurred while requesting audio: {exc}")
            raise HTTPException(status_code=500, detail="Error communicating with TTS service")

    if audio_response.status_code != 200:
        logger.error(f"Received non-OK response from audio generation: {audio_response.status_code}")
        raise HTTPException(status_code=audio_response.status_code, detail="Error generating audio")

    logger.info("Audio generated successfully")
    return {"podcast_id": script_id}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(config.API_Port))