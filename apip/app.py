from io import BytesIO
import os
import json
import httpx
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Dict, List
import logging
from colorama import Fore, Style
from src.storage import firebase_storage

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

class GetPocastsRequest(BaseModel):
    user_id: str

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

@app.post("/api/scripts")
async def get_scripts(body: Dict[str, str]):
    logger.info("Getting scripts")
    scripts = firebase_storage.list_scripts(body['user_id'])
    return scripts

@app.post("/api/podcasts")
async def get_podcasts_from_user(body: GetPocastsRequest):
    logger.info("Getting podcasts")
    podcasts = firebase_storage.get_user_podcasts(body.user_id)
    return podcasts

@app.post("/api/get_audio")
async def get_audio(body: RequestBody):
    logger.info("Getting audio")
    audio = firebase_storage.get_audio(body.user_id, body.podcast_id)
    if not audio:
        logger.error("Audio not found")
        raise HTTPException(status_code=404, detail="Audio not found")
    
    # Ensure the audio is in bytes
    if isinstance(audio, bytes):
        def audio_stream():
            yield audio
        
        return StreamingResponse(audio_stream(), media_type="audio/mpeg")
    
    else:
        logger.error("Audio is not in bytes format")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.post("/api/get_image")
async def get_image(body: RequestBody):
    logger.info("Getting image")
    image_url = firebase_storage.get_image(body.user_id, body.podcast_id)
    if not image_url:
        logger.error("Image not found")
        return JSONResponse(status_code=404, content={"detail": "Image not found"})
    return {"image_url": image_url}


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

    async with httpx.AsyncClient(timeout=1200.0) as client:  # Set timeout to 1200 seconds (20 minutes)
        try:
            script_response = await client.post(f"http://{config.GEMINI_IP}:{config.GEMINI_Port}/generate_script", json=script_payload)

        except httpx.TimeoutException:
            logger.error("The request to the gemini service timed out")
            raise HTTPException(status_code=504, detail="The request to the gemini service timed out")
        
        except httpx.RequestError as exc:
            logger.error(f"An error occurred while requesting the script: {exc}")
            raise HTTPException(status_code=500, detail="Error communicating with the TTS service")

    if script_response.status_code != 200:
        logger.error(f"Unable to generate script: {script_response.status_code}")
        raise HTTPException(status_code=script_response.status_code, detail="Error generating script")

    podcast_id = script_response.json().get("podcast_id")
    if not podcast_id:
        logger.error("podcast_id not found in response")
        raise HTTPException(status_code=500, detail="Script ID not found")
    
    logger.info("Script generated successfully")

    # Firebase
    firebase_storage.save_podcast_name(podcast_id, body.podcast_name, body.subject)
    logger.info("Podcast name saved to Firebase")

    # Generate audio
    logger.info("Generating audio")
    audio_payload = {
        "user_id": body.user_id,
        "podcast_name": body.podcast_name,
        "podcast_id": podcast_id,
    }

    async with httpx.AsyncClient(timeout=1200.0) as client:
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
    return {"podcast_id": podcast_id}


class AudioRequest(BaseModel):
    podcast_id: str
    user_id: str
    podcast_name: str
    subject: str

@app.post("/api/generate_audio")
async def generate_audio(body: AudioRequest):
    podcast_id = body.podcast_id

    # Generate audio
    logger.info("Generating audio")
    audio_payload = {
        "user_id": body.user_id,
        "podcast_name": body.podcast_name,
        "podcast_id": podcast_id,
    }

    async with httpx.AsyncClient(timeout=1200.0) as client:
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
    return {"podcast_id": podcast_id}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(config.API_Port))