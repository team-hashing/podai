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
from httpx import Timeout


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
    podcasts = [Podcast(id=data['id'], name=data['name'],
                        image=f'https://picsum.photos/seed/{data["name"]}/200') for data in podcasts_data]

    return templates.TemplateResponse("index.html", {"request": request, "podcasts": podcasts})


@app.get("/audio/{user_id}/{podcast_id}")
async def get_audio(user_id: str, podcast_id: str):
    # print all files in the directory
    print(os.listdir(f"{DATA_PATH}/{user_id}/audios"))
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
    # Define the payload for the podcast generation API
    payload = {
        "user_id": "user1",
        "subject": request.subject,
        "podcast_name": request.name
    }

    # Set a 90-minute timeout
    timeout = Timeout(90.0 * 60)

    # Send a POST request to the podcast generation API
    async with httpx.AsyncClient(timeout=timeout) as client:
        response = await client.post('http://localhost:8000/api/generate_podcast', json=payload)
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=response.text)
        podcast_data = response.json()

    # Create a new Podcast object
    new_podcast = Podcast(
        id=podcast_data['podcast_id'],
        name=request.name,
        image=f'https://picsum.photos/seed/{request.name}/200'
    )

    # Get the updated list of podcasts
    podcasts = await get_podcasts()
    podcasts.append(new_podcast)

    return templates.TemplateResponse("index.html", {"request": request, "podcasts": podcasts})

async def get_podcasts():
    # Send a POST request to the scripts API
    async with httpx.AsyncClient() as client:
        response = await client.post('http://localhost:8000/api/scripts', json={"user_id": "user1"})
        response.raise_for_status()
        podcasts_data = response.json()

    # Create a list of Podcast objects from the response data
    podcasts = [Podcast(id=data['id'], name=data['name'],
                        image=f'https://picsum.photos/seed/{data["name"]}/200') for data in podcasts_data]
    
    return podcasts

"""
@app.post("/generate-podcast")
async def generate_podcast(request: PodcastGenerationRequest):

    # Send a POST request to the scripts API
    async with httpx.AsyncClient() as client:
        response = await client.post('http://localhost:8000/api/scripts', json={"user_id": "user1"})
        response.raise_for_status()
        podcasts_data = response.json()

    # Create a list of Podcast objects from the response data
    podcasts = [Podcast(id=data['id'], name=data['name'],
                        image=f'https://picsum.photos/seed/{data["name"]}/200') for data in podcasts_data]

    # Simulate a long-running process
    await asyncio.sleep(5)

    # In a real scenario, you would generate the podcast here
    new_podcast = Podcast(
        id=str(len(podcasts) + 1),
        name=request.name,
        # Use a default image or generate one
        image="/static/images/generated_podcast.jpg"
    )
    podcasts.append(new_podcast)
    return templates.TemplateResponse("index.html", {"request": request, "podcasts": podcasts})
"""

