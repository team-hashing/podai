import os
import httpx
from fastapi import FastAPI, HTTPException, Request, Depends, Form
from fastapi.responses import FileResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from fastapi.staticfiles import StaticFiles
from fastapi.responses import StreamingResponse
import asyncio
from httpx import Timeout
from io import BytesIO
from PIL import Image
import pyrebase
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import json
import logging
from src.log import setup_logger
from typing import Optional
from src.auth import router as auth_router
import aiohttp

logger = setup_logger("uvicorn")

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")
DATA_PATH = os.getenv('DATA_PATH')
API_URL = os.getenv('API_URL')


# Routes
app.include_router(auth_router, prefix="")

def load_firebase_config():
    firebase_config = {
        "apiKey": "AIzaSyBBt3PTdctzq1dGbKP0UxLDaDaSApqU_lg",
        "authDomain": "podai-425012.firebaseapp.com",
        "databaseURL": "",
        "projectId": "podai-425012",
        "storageBucket": "podai-425012.appspot.com",
        "messagingSenderId": "197233010794",
        "appId": "1:197233010794:web:b6f71e4ab2d989b5710213",
        "measurementId": "G-11VMLCSB72"
    }

    logger.info("Firebase config loaded")
    return firebase_config


firebase_config = load_firebase_config()
firebase = pyrebase.initialize_app(firebase_config)
auth = firebase.auth()

security = HTTPBearer()


class Podcast(BaseModel):
    id: str
    name: str
    image: str
    status: str = "ready"
    author: str = "Unknown"
    likes: int = 0

class UserInfo(BaseModel):
    username: str
    email: str
    age: Optional[int] = None


async def get_current_user(token: HTTPAuthorizationCredentials = Depends(security)):
    try:
        user = auth.get_account_info(token.credentials)
        return user['users'][0]['email']
    except:
        raise HTTPException(
            status_code=401,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )



async def get_user_info(user_id: str):
    async with httpx.AsyncClient() as client:
        # get user info
        response = await client.post(f'{API_URL}/api/get_user_info', json={"user_id": user_id})
        response.raise_for_status()
        user_info = response.json()
        
        return user_info

async def is_image_url(url):
    async with aiohttp.ClientSession() as session:
        async with session.head(url) as response:
            content_type = response.headers.get('Content-Type', '')
            return content_type.startswith('image/')


async def get_user_podcasts(user_id: str, page: int = 0, per_page: int = 5):
    async with httpx.AsyncClient() as client:

        # Send a POST request to the scripts API with pagination parameters
        response = await client.post(f'{API_URL}/api/podcasts', json={"user_id": user_id, "page": page, "per_page": per_page})
        response.raise_for_status()
        if page != 0:
            data = response.json()
            podcasts_data = data['podcasts']
            total_pages = data['total_pages']
            
        else:
            podcasts_data = response.json()
            total_pages = 1
        


        podcasts = [
            Podcast(
                id=data['id'],
                name=data['name'],
                image=f'https://picsum.photos/seed/podcast/200',
                status=data.get('status', 'ready'),
                author=data.get('username', 'Unknown'),
                likes=data.get('likes', 0)
            )
            for data in podcasts_data if not 'status' in data.keys() or data['status'] != "error"
        ]


        # get images for each podcast
        for podcast in podcasts:
            response = await client.post(f'{API_URL}/api/get_image', json={"user_id": user_id, "podcast_id": podcast.id})
            if response.status_code != 404:
                data = response.json()
                image_url = data.get("image_url")
                if await is_image_url(image_url):
                    podcast.image = image_url
                else:
                    podcast.image = 'static/images/placeholder2.png'

            else:
                podcast.image = 'static/images/placeholder2.png'

        return podcasts, total_pages

async def get_podcasts_by_likes(user_id: str, page: int = 0, per_page: int = 5):
    async with httpx.AsyncClient() as client:

        response = await client.post(f'{API_URL}/api/podcasts_by_likes', json={"user_id": user_id, "page": page, "per_page": per_page})
        response.raise_for_status()
        if page != 0:
            data = response.json()
            podcasts_data = data['podcasts']
            total_pages = data['total_pages']
        else:
            podcasts_data = response.json()
            total_pages = 1



        
        podcasts = [
            Podcast(
                id=data['id'],
                name=data['name'],
                image=f'https://picsum.photos/seed/podcast/200',
                status=data.get('status', 'ready'),
                author=data.get('username', 'Unknown'),
                likes=data.get('likes', 0)
            )
            for data in podcasts_data if not 'status' in data.keys() or data['status'] != "error"
        ]

        for podcast in podcasts:
            response = await client.post(f'{API_URL}/api/get_image', json={"user_id": user_id, "podcast_id": podcast.id})
            if response.status_code != 404:
                data = response.json()
                image_url = data.get("image_url")
                if await is_image_url(image_url):
                    podcast.image = image_url
                else:
                    podcast.image = 'static/images/placeholder2.png'

            else:
                podcast.image = 'static/images/placeholder2.png'

        return podcasts, total_pages

async def get_liked_podcasts(user_id: str, page: int = 0, per_page: int = 12):
    async with httpx.AsyncClient() as client:
        # Get liked podcasts
        response = await client.post(f'{API_URL}/api/get_liked_podcasts', json={"user_id": user_id, "page": page, "per_page": per_page})
        response.raise_for_status()
        if page != 0:
            data = response.json()
            podcasts_data = data['podcasts']
            total_pages = data['total_pages']
        else:
            podcasts_data = response.json()
            total_pages = 1


        
        podcasts = [
            Podcast(
                id=data['id'],
                name=data['name'],
                image=f'https://picsum.photos/seed/podcast/200',
                status=data.get('status', 'ready'),
                author=data.get('username', 'Unknown'),
                likes=data.get('likes', 0)
            )
            for data in podcasts_data if not 'status' in data.keys() or data['status'] != "error"
        ]

        # get images for each liked podcast
        for podcast in podcasts:
            response = await client.post(f'{API_URL}/api/get_image', json={"user_id": user_id, "podcast_id": podcast.id})
            if response.status_code != 404:
                data = response.json()
                image_url = data.get("image_url")
                if await is_image_url(image_url):
                    podcast.image = image_url
                else:
                    podcast.image = 'static/images/placeholder2.png'

            else:
                podcast.image = 'static/images/placeholder2.png'

        return podcasts, total_pages


@app.get("/")
async def root(request: Request, user_page: int = 1, likes_page: int = 1, liked_page: int = 1, per_page: int = 5):
    token = request.cookies.get("access_token")
    user_id = request.cookies.get("user_id")
    if not token:
        logger.info("User not logged in")
        return RedirectResponse(url="/login")
    if not user_id:
        raise HTTPException(
            status_code=400, detail="User ID not found in cookies")
    
    user_info                        = await get_user_info(user_id)
    user_podcasts, user_pages        = await get_user_podcasts(user_id, page=user_page, per_page=per_page)
    podcasts_by_likes, likes_pages   = await get_podcasts_by_likes(user_id, page=likes_page, per_page=per_page)
    liked_podcasts, liked_pages      = await get_liked_podcasts(user_id, page=liked_page, per_page=per_page)

    
    response = templates.TemplateResponse("index.html", {
        "request": request,
        "podcasts": user_podcasts,
        "podcasts_by_likes": podcasts_by_likes,
        "liked_podcasts": liked_podcasts,
        "token": token,
        "user_pages": user_pages,
        "likes_pages": likes_pages,
        "liked_pages": liked_pages,
        "user_page": user_page,
        "likes_page": likes_page,
        "liked_page": liked_page,
        "user_info": user_info
    })

    response.set_cookie(key="user_info", value=json.dumps(user_info), httponly=False)
    return response


@app.get("/audio/{podcast_id}")
async def get_audio(request: Request, podcast_id: str):
    # Extract user_id from cookies
    user_id = request.cookies.get("user_id")
    if not user_id:
        raise HTTPException(
            status_code=400, detail="User ID not found in cookies")

    timeout = 120.0
    async with httpx.AsyncClient(timeout=timeout) as client:
        response = await client.post(f'{API_URL}/api/get_audio', json={"user_id": user_id, "podcast_id": podcast_id})
        response.raise_for_status()
        audio_data = response.content
        if not audio_data:
            raise HTTPException(status_code=404, detail="Audio not found")
        else:
            return StreamingResponse(iter([audio_data]), media_type="audio/mpeg")


@app.get("/like_podcast/{podcast_id}")
async def like_podcast(request: Request, podcast_id: str):
    # Extract user_id from cookies
    user_id = request.cookies.get("user_id")
    if not user_id:
        raise HTTPException(
            status_code=400, detail="User ID not found in cookies")

    async with httpx.AsyncClient() as client:
        response = await client.post(f'{API_URL}/api/like_podcast', json={"user_id": user_id, "podcast_id": podcast_id})
        response.raise_for_status()
        return RedirectResponse(url="/")

@app.get("/unlike_podcast/{podcast_id}")
async def unlike_podcast(request: Request, podcast_id: str):
    # Extract user_id from cookies
    user_id = request.cookies.get("user_id")
    if not user_id:
        raise HTTPException(
            status_code=400, detail="User ID not found in cookies")

    async with httpx.AsyncClient() as client:
        response = await client.post(f'{API_URL}/api/unlike_podcast', json={"user_id": user_id, "podcast_id": podcast_id})
        response.raise_for_status()
        return RedirectResponse(url="/")


@app.get("/check-podcast-status/{podcast_id}")
async def check_podcast_status(request: Request, podcast_id: str):
    # Extract user_id from cookies
    user_id = request.cookies.get("user_id")
    if not user_id:
        raise HTTPException(
            status_code=400, detail="User ID not found in cookies")

    async with httpx.AsyncClient() as client:
        response = await client.post(f'{API_URL}/api/get_podcast_status', json={"user_id": user_id, "podcast_id": podcast_id})
        response.raise_for_status()
        return response.json()
    

@app.get("/get-podcast-details/{podcast_id}")
async def get_podcast_details(request: Request, podcast_id: str):
    # Extract user_id from cookies
    user_id = request.cookies.get("user_id")
    if not user_id:
        raise HTTPException(
            status_code=400, detail="User ID not found in cookies")

    async with httpx.AsyncClient() as client:
        response = await client.post(f'{API_URL}/api/get_podcast_info', json={"user_id": user_id, "podcast_id": podcast_id})
        response.raise_for_status()
        return response.json()
    

class PodcastGenerationRequest(BaseModel):
    name: str
    subject: str


@app.post("/generate-podcast")
async def generate_podcast(request: Request, podcast_request: PodcastGenerationRequest):
    # Extract user_id from cookies
    user_id = request.cookies.get("user_id")
    if not user_id:
        raise HTTPException(
            status_code=400, detail="User ID not found in cookies")

    # Define the payload for the podcast generation API
    payload = {
        "user_id": user_id,
        "subject": podcast_request.subject,
        "podcast_name": podcast_request.name
    }
    # Set a 90-minute timeout
    timeout = Timeout(90.0 * 60)

    # Send a POST request to the podcast generation API
    async with httpx.AsyncClient(timeout=timeout) as client:
        response = await client.post(f'{API_URL}/api/generate_podcast', json=payload)
        if response.status_code != 200:
            raise HTTPException(
                status_code=response.status_code, detail=response.detail)
        podcast_data = response.json()

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
