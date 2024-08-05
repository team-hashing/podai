import os
import httpx
from fastapi import APIRouter, HTTPException, Request, Form
from fastapi.responses import FileResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from src.log import setup_logger
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import pyrebase


logger = setup_logger("uvicorn")
router = APIRouter()

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


@router.get("/login")
async def login_page(request: Request):
    token = request.cookies.get("access_token")
    if token:
        response = RedirectResponse(url="/", status_code=303)
    return templates.TemplateResponse("login.html", {"request": request})


@router.post("/login")
async def login(request: Request, email: str = Form(...), password: str = Form(...)):
    try:
        user = auth.sign_in_with_email_and_password(email, password)
        id_token = user['idToken']
        response = RedirectResponse(url="/", status_code=303)
        response.set_cookie(key="access_token", value=id_token, httponly=True)
        response.set_cookie(key="user_id", value=user['localId'], httponly=False)
        response.set_cookie(key="page_transition", value="true", max_age=5)
        logger.info(f"User {email} logged in")
        return response
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        raise HTTPException(
            status_code=401,
            detail="Incorrect email or password",
        )


@router.get("/signup")
async def signup_page(request: Request):
    return templates.TemplateResponse("signup.html", {"request": request})


@router.post("/signup")
async def signup(username: str = Form(...), email: str = Form(...), password: str = Form(...)):
    try:
        # Create user with email and password
        user = auth.create_user_with_email_and_password(email, password)
        id_token = user['idToken']
        logger.info(f"User {email} signed up")

        # Register user in the main app
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{API_URL}/api/create_user", json={"username": username, "user_id": user['localId']})
            response.raise_for_status()
            logger.info(f"User {username} registered in main app")

        # Set the access token cookie
        response = RedirectResponse(url="/", status_code=303)
        response.set_cookie(key="access_token", value=id_token, httponly=True)
        response.set_cookie(key="user_id", value=user['localId'], httponly=False)
        response.set_cookie(key="page_transition", value="true", max_age=5)
        
        return response
    
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error occurred: {e}")
        raise HTTPException(
            status_code=e.response.status_code,
            detail="Unable to register user in main app",
        )
    except Exception as e:
        logger.error(f"Error during signup: {e}")
        raise HTTPException(
            status_code=400,
            detail="Unable to create account. Please check your information and try again.",
        )


@router.get("/logout")
async def logout(request: Request):
    response = RedirectResponse(url="/login")
    response.delete_cookie(key="access_token")
    response.delete_cookie(key="user_id")
    return response
