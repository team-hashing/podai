from io import BytesIO
import os
import json
from uuid import uuid4
import httpx
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Dict, List
import logging
from colorama import Fore, Style
from src.storage import firebase_storage
import asyncio
from src.log import setup_logger

app = FastAPI()

# Global variables
Env = "local"  # Default environment


logger = setup_logger("uvicorn")

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

class UserRequest(BaseModel):
    user_id: str

class GetPocastsRequest(BaseModel):
    user_id: str
    page: int = 0
    per_page: int = 5

class GenerateScriptRequest(BaseModel):
    user_id: str
    subject: str
    podcast_name: str

class GeneratePodcastRequest(BaseModel):
    user_id: str
    subject: str
    podcast_name: str

class UserCreateRequest(BaseModel):
    username: str
    user_id: str

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
    podcasts = firebase_storage.get_user_podcasts(body.user_id, body.page, body.per_page)
    return podcasts

@app.post("/api/podcasts_by_likes")
async def get_podcasts_by_likes(body: GetPocastsRequest):
    logger.info("Getting podcasts by likes")
    podcasts = firebase_storage.get_podcasts_by_likes(body.user_id, body.page, body.per_page)
    return podcasts

@app.post("/api/get_audio")
async def get_audio(body: RequestBody):
    logger.info("Getting audio")
    audio = firebase_storage.get_audio(body.user_id, body.podcast_id)
    if not audio:
        logger.error("Audio not found")
        name = firebase_storage.get_podcast_name(body.user_id, body.podcast_id)
        subject = firebase_storage.get_podcast_subject(body.user_id, body.podcast_id)
        if name and subject:
            audio_Petition = AudioRequest(podcast_id=body.podcast_id, user_id=body.user_id, podcast_name=name, subject=subject)
            await generate_audio(audio_Petition)
        return JSONResponse(status_code=404, content={"detail": "Audio not found"})
    
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
    
    # Check if enough tokens
    if not firebase_storage.use_token(body.user_id):
        logger.error("Not enough tokens")
        raise HTTPException(status_code=403, detail="Not enough tokens")

    podcast_id = str(uuid4())

    # Generate script
    script_payload = {
        "user_id": body.user_id,
        "subject": body.subject,
        "podcast_id": podcast_id
    }
    await firebase_storage.save_podcast(body.user_id, podcast_id, body.podcast_name, body.subject)

    # Return ok but continue with this function
    username = firebase_storage.get_username_from_id(body.user_id)
    response = {"podcast_id": podcast_id, "username": username}
    logger.info("Podcast saved to Firestore")

    async def continue_execution():
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

    # Start the background task
    asyncio.create_task(continue_execution())

    return response

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

@app.post("/api/like_podcast")
async def like_podcast(body: RequestBody):
    logger.info("Liking podcast")
    firebase_storage.like_podcast(body.user_id, body.podcast_id)
    return {"message": "Podcast liked successfully"}

@app.post("/api/unlike_podcast")
async def unlike_podcast(body: RequestBody):
    logger.info("Unliking podcast")
    firebase_storage.unlike_podcast(body.user_id, body.podcast_id)
    return {"message": "Podcast unliked successfully"}

@app.post("/api/get_liked_podcasts")
async def get_liked_podcasts(body: GetPocastsRequest):
    logger.info("Getting liked podcasts")
    podcasts = firebase_storage.get_liked_podcasts(body.user_id, body.page, body.per_page)
    return podcasts

@app.post("/api/get_user_info")
async def get_user_info(body: UserRequest):
    logger.info("Getting user info")
    user_info = firebase_storage.get_user_info(body.user_id)
    return user_info

@app.post("/api/create_user")
async def create_user(body: UserCreateRequest):
    logger.info("Creating user")
    firebase_storage.create_user(body.user_id, body.username)
    return {"message": "User created"}

@app.post("/api/get_podcast_info")
async def get_podcast_info(body: RequestBody):
    logger.info("Getting podcast info")
    podcast_info = firebase_storage.get_podcast_info(body.user_id, body.podcast_id)
    return podcast_info

@app.post("/api/get_podcast_status")
async def get_podcast_status(body: RequestBody):
    logger.info("Getting podcast status")
    status = firebase_storage.get_podcast_status(body.user_id, body.podcast_id)
    return status

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(config.API_Port))