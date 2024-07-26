# app.py
from fastapi import FastAPI, HTTPException
from fastapi.responses import Response
from src.log import setup_logger
from src.audio import generate_podcast
from src.models import Podcast
from src.storage import FirebaseStorage
import os

os.environ["CUDA_VISIBLE_DEVICES"] = "-1"

app = FastAPI()
logger = setup_logger("uvicorn")
firebase_storage = FirebaseStorage()

if not os.path.exists("voices"):
    os.makedirs("voices")

if not os.listdir("voices"):
    firebase_storage.download_voices()

@app.post("/api/audio")
async def read_audio(podcast: Podcast):
    if not podcast.user_id or not podcast.podcast_id or not podcast.podcast_name:
        logger.error(f"Invalid request body: {podcast}")
        raise HTTPException(status_code=400, detail="Invalid request body")

    logger.info("Generating podcast")

    try:
        generate_podcast(podcast)
    except Exception as e:
        logger.error(f"Error generating podcast: {e}")
        raise HTTPException(status_code=500, detail="Error generating podcast")

    audio = firebase_storage.get_audio(podcast.user_id, podcast.podcast_id)
    if audio is None:
        logger.error(f"Podcast not found: {podcast.podcast_id}")
        raise HTTPException(status_code=404, detail="Podcast not found")

    return {"response_code": 200, "message": "Podcast generated successfully", "podcast": podcast}

@app.get("/audio/{user_id}/{podcast_id}")
def read_audio(user_id: str, podcast_id: str):
    logger.info(f"Retrieving podcast: {podcast_id} for user: {user_id}")
    audio = firebase_storage.get_audio(user_id, podcast_id)
    if audio is None:
        logger.error(f"Podcast not found: {podcast_id}")
        raise HTTPException(status_code=404, detail="Podcast not found")
    return Response(content=audio, media_type="audio/wav")