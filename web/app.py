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
from fastapi.responses import StreamingResponse
import asyncio
from httpx import Timeout
from io import BytesIO
from PIL import Image


app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")
DATA_PATH = os.getenv('DATA_PATH')
API_URL = os.getenv('API_URL')


class Podcast(BaseModel):
    id: str
    name: str
    image: str


@app.get("/")
async def root(request: Request):
    async with httpx.AsyncClient() as client:
        # Send a POST request to the scripts API
        response = await client.post(f'{API_URL}/api/podcasts', json={"user_id": "user1"})
        response.raise_for_status()
        podcasts_data = response.json()

        podcasts = [Podcast(id=data['id'], name=data['name'],
                            image=f'https://picsum.photos/seed/{data["name"]}/200') for data in podcasts_data]

        # get images for each podcast
        for podcast in podcasts:
            response = await client.post(f'{API_URL}/api/get_image', json={"user_id": "user1", "podcast_id": podcast.id})
            if response.status_code != 404:
                data = response.json()
                podcast.image = data.get("image_url")

    return templates.TemplateResponse("index.html", {"request": request, "podcasts": podcasts})


@app.get("/audio/{user_id}/{podcast_id}")
async def get_audio(user_id: str, podcast_id: str):
    async with httpx.AsyncClient() as client:
        response = await client.post(f'{API_URL}/api/get_audio', json={"user_id": user_id, "podcast_id": podcast_id})
        response.raise_for_status()
        audio_data = response.content
        if not audio_data:
            raise HTTPException(status_code=404, detail="Audio not found")
        else:
            return StreamingResponse(iter([audio_data]), media_type="audio/mpeg")



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
        response = await client.post(f'{API_URL}/api/generate_podcast', json=payload)
        if response.status_code != 200:
            raise HTTPException(
                status_code=response.status_code, detail=response.text)
        podcast_data = response.json()

    # Create a new Podcast object
    # new_podcast = Podcast(
    #     id=podcast_data['podcast_id'],
    #     name=request.name,
    #     image=f'https://picsum.photos/seed/{request.name}/200'
    # )

    # Get the updated list of podcasts
    # podcasts = await get_podcasts()
    # podcasts.append(new_podcast)

    # return templates.TemplateResponse("index.html", {"request": request, "podcasts": podcasts})
    return {"message": "Podcast generated successfully"}


@app.get("/generate-audio")
async def generate_audio():
    payload = {
        "podcast_id": "7a4599f3-306d-4611-b9a2-d9ec0ca916a8",
        "user_id": "user1",
        "podcast_name": "The Roman Podcast",
        "subject": "Roman History"
    }
    timeout = Timeout(90.0 * 600)
    # Send a POST request to the podcast generation API
    async with httpx.AsyncClient(timeout=timeout) as client:
        response = await client.post(f'{API_URL}/api/generate_audio', json=payload)
        if response.status_code != 200:
            raise HTTPException(
                status_code=response.status_code, detail=response.text)
        podcast_data = response.json()


async def get_podcasts():
    async with httpx.AsyncClient() as client:
        # Send a POST request to the scripts API
        response = await client.post(f'{API_URL}/api/podcasts', json={"user_id": "user1"})
        response.raise_for_status()
        podcasts_data = response.json()

        podcasts = [Podcast(id=data['id'], name=data['name'],
                            image=f'https://picsum.photos/seed/{data["name"]}/200') for data in podcasts_data]

        # get images for each podcast
        for podcast in podcasts:
            response = await client.post(f'{API_URL}/api/get_image', json={"user_id": "user1", "podcast_id": podcast.id})
            if response.status_code != 404:
                podcast.image = response.content

    return podcasts
