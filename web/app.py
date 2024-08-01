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

logger = setup_logger("uvicorn")

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")
DATA_PATH = os.getenv('DATA_PATH')
API_URL = os.getenv('API_URL')


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

@app.get("/login")
async def login_page(request: Request):
    token = request.cookies.get("access_token")
    if token:
        return RedirectResponse(url="/")
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login")
async def login(request: Request, email: str = Form(...), password: str = Form(...)):
    token = request.cookies.get("access_token")
    if token:
        return RedirectResponse(url="/")
    
    try:
        user = auth.sign_in_with_email_and_password(email, password)
        id_token = user['idToken']
        response = RedirectResponse(url="/")
        response.set_cookie(key="access_token", value=id_token, httponly=True)
        logger.info(f"User {email} logged in")
        return response
    except:
        raise HTTPException(
            status_code=401,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

@app.get("/signup")
async def signup_page(request: Request):
    return templates.TemplateResponse("signup.html", {"request": request})

@app.post("/signup")
async def signup(username: str = Form(...), email: str = Form(...), password: str = Form(...)):
    try:
        # Create user with email and password
        user = auth.create_user_with_email_and_password(email, password)
        id_token = user['idToken']
        logger.info(f"User {email} signed up")
        logger.info(f"AAAAAAAAAAAAAAAAAAAAAAAAAA {user}")


        # Register user in the main app
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{API_URL}/api/create_user", json={"username": username, "user_id": user['localId']})
            response.raise_for_status()
            logger.info(f"User {username} registered in main app")

        # Set the access token cookie
        response = RedirectResponse(url="/")
        response.set_cookie(key="access_token", value=id_token, httponly=True)
        # Set a cookie with the user's id
        response.set_cookie(key="user_id", value=user['localId'], httponly=True)
        return response
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error occurred: {e}")
        raise HTTPException(
            status_code=e.response.status_code,
            detail="Unable to register user in main app",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        logger.error(f"Error during signup: {e}")
        raise HTTPException(
            status_code=400,
            detail="Unable to create account",
            headers={"WWW-Authenticate": "Bearer"},
        )

@app.get("/logout")
async def logout(request: Request):
    response = RedirectResponse(url="/login")
    response.delete_cookie(key="access_token")
    return response


@app.post("/")
async def root_post(request: Request):
    token = request.cookies.get("access_token")
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

    return templates.TemplateResponse("index.html", {"request": request, "podcasts": podcasts, "token": token})


@app.get("/")
async def root(request: Request):
    token = request.cookies.get("access_token")
    if not token:
        return RedirectResponse(url="/login")
    
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

    return templates.TemplateResponse("index.html", {"request": request, "podcasts": podcasts, "token": token})


@app.get("/audio/{user_id}/{podcast_id}")
async def get_audio(user_id: str, podcast_id: str):
    timeout = 120.0
    async with httpx.AsyncClient(timeout=timeout) as client:
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
