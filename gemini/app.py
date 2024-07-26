import logging
from uuid import uuid4
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings
import uvicorn
from fastapi.responses import JSONResponse

from src.gemini import PodcastGenerator
from src.storage import FirebaseStorage
from src.script_processor import standardize_script_format
from src.image_generation import generate_image

# Configuration
class Settings(BaseSettings):
    app_name: str = "Podcast Script Generator"
    debug: bool = False


    class Config:
        env_file = ".env"

settings = Settings()

# Logging setup
logging.basicConfig(level=logging.DEBUG if settings.debug else logging.INFO)
logger = logging.getLogger(__name__)

# Models
class PodcastRequest(BaseModel):
    subject: str = Field(..., min_length=3, max_length=200)
    user_id: str = Field(..., min_length=1)

class ScriptResponse(BaseModel):
    message: str
    podcast_id: str

# App initialization
app = FastAPI(title=settings.app_name)

# Exception handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    logger.error(f"HTTP error occurred: {exc.detail}")
    return JSONResponse(status_code=exc.status_code, content={"error": exc.detail})

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    logger.exception("An unexpected error occurred")
    return JSONResponse(status_code=500, content={"error": "An unexpected error occurred"})


# Routes
@app.post("/generate_script", response_model=ScriptResponse)
async def generate_script(
    request: PodcastRequest
):
    firebase_storage = FirebaseStorage()
    logger.info(f"Generating script for subject: {request.subject}")
    try:
        # Generate podcast script
        pg = PodcastGenerator()
        script = await pg.generate_podcast_script(request.subject)
        if script is None:
            raise ValueError("Script generation failed")

        # Generate script ID
        podcast_id = str(uuid4())

        # Standardize script format
        standardized_script = standardize_script_format(script)

        # Save script to Firebase Storage
        await firebase_storage.save_podcast(request.user_id, podcast_id, standardized_script)

        # Generate image
        image_data = generate_image(request.subject)
        await firebase_storage.save_image(request.user_id, podcast_id, image_data)

        logger.info(f"Script generated successfully. ID: {podcast_id}")
        return ScriptResponse(message="Script generated successfully", podcast_id=podcast_id)

    # Error handling
    except ValueError as ve:
        logger.error(f"Script generation failed: {str(ve)}")
        raise HTTPException(status_code=500, detail=str(ve))

    except Exception as e:
        logger.exception("An unexpected error occurred during script generation")
        raise HTTPException(status_code=500, detail="An unexpected error occurred during script generation")


# Lifecycle events
@app.on_event("startup")
async def startup_event():
    logger.info("Starting up the application")
    # You can add any startup tasks here, like initializing database connections


@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down the application")
    # You can add any cleanup tasks here


if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8002, reload=settings.debug)