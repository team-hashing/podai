# main.py
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from src.log import setup_logger
from src.audio import generate_podcast
from src.models import Podcast
import os

os.environ["CUDA_VISIBLE_DEVICES"] = "-1"
PODCAST_DIR = "podcasts"

app = FastAPI()
logger = setup_logger("uvicorn")



@app.post("/api/audio")
async def read_audio(podcast: Podcast):
    if not podcast.user_id or not podcast.script or not podcast.podcast_name:
        logger.error(f"Invalid request body: {podcast}")
        raise HTTPException(status_code=400, detail="Invalid request body")

    logger.info("Generating podcast")
    generate_podcast(podcast)

    # Check if podcast exists
    if not os.path.exists(f"{PODCAST_DIR}/{podcast.user_id}/{podcast.podcast_name}.wav"):
        logger.error(f"Podcast not found: {podcast}")
        raise HTTPException(status_code=404, detail="Podcast not found")

    return FileResponse(f"{PODCAST_DIR}/{podcast.user_id}/{podcast.podcast_name}.wav", media_type="audio/mpeg")

@app.get("/audio")
def read_audio():
    logger.info("Generating podcast")
    generate_podcast("script.json")
    return FileResponse("{PODCAST_DIR}/{podcast.user_id}/{podcast.podcast_name}.wav", media_type="audio/mpeg")