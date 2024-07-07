import os
import httpx
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from fastapi.staticfiles import StaticFiles
from fastapi import FastAPI, Request, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import asyncio

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")
DATA_PATH = os.getenv('DATA_PATH')

class Podcast(BaseModel):
    id: str
    name: str
    image: str

@app.get("/")
async def root(request: Request):
    # Send a POST request to the scripts API
    async with httpx.AsyncClient() as client:
        response = await client.post('http://localhost:8000/api/scripts', json={"user_id": "user1"})
        response.raise_for_status()
        podcasts_data = response.json()

    # Create a list of Podcast objects from the response data
    podcasts = [Podcast(id=data['id'], name=data['name'], image=f'https://picsum.photos/seed/{data["name"]}/200') for data in podcasts_data]

    return templates.TemplateResponse("index.html", {"request": request, "podcasts": podcasts})

@app.get("/audio/{user_id}/{podcast_id}")
async def get_audio(user_id: str, podcast_id: str):
    audio_path = f"{DATA_PATH}/{user_id}/audios/{podcast_id}.wav"
    if os.path.exists(audio_path):
        return {"audioUrl": f"/stream-audio/{user_id}/{podcast_id}"}
    else:
        raise HTTPException(status_code=404, detail="Audio file not found")

@app.get("/stream-audio/{user_id}/{podcast_id}")
async def stream_audio(user_id: str, podcast_id: str):
    audio_path = f"{DATA_PATH}/{user_id}/audios/{podcast_id}.wav"
    if os.path.exists(audio_path):
        return FileResponse(audio_path, media_type="audio/wav")
    else:
        raise HTTPException(status_code=404, detail="Audio file not found")
    
class PodcastGenerationRequest(BaseModel):
    name: str
    subject: str

@app.post("/generate-podcast")
async def generate_podcast(request: PodcastGenerationRequest):
    
    # Send a POST request to the scripts API
    async with httpx.AsyncClient() as client:
        response = await client.post('http://localhost:8000/api/scripts', json={"user_id": "user1"})
        response.raise_for_status()
        podcasts_data = response.json()

    # Create a list of Podcast objects from the response data
    podcasts = [Podcast(id=data['id'], name=data['name'], image=f'https://picsum.photos/seed/{data["name"]}/200') for data in podcasts_data]


    # Simulate a long-running process
    await asyncio.sleep(5)
    
    # In a real scenario, you would generate the podcast here
    new_podcast = Podcast(
        id=str(len(podcasts) + 1),
        name=request.name,
        image="/static/images/generated_podcast.jpg"  # Use a default image or generate one
    )
    podcasts.append(new_podcast)
    return templates.TemplateResponse("index.html", {"request": request, "podcasts": podcasts})
    