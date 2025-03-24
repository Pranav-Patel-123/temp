import os
import jwt
import datetime
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

owner_auth_router = APIRouter()

# JWT Secret & Algorithm from .env
SECRET_KEY = os.getenv("SECRET_KEY", "your_default_secret_key")
ALGORITHM = "HS256"

# Owner credentials from .env
OWNER_EMAIL = os.getenv("OWNER_EMAIL")
OWNER_PASSWORD = os.getenv("OWNER_PASSWORD")  # Plain text password

# Request Model for Owner Login
class OwnerLoginRequest(BaseModel):
    email: str
    password: str

def create_jwt_token(data: dict):
    """Generate a JWT token for the owner."""
    payload = {
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=24),
        "iat": datetime.datetime.utcnow(),
        "sub": data
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

@owner_auth_router.post("/login")
async def owner_login(data: OwnerLoginRequest):
    """Owner login endpoint using plain-text credentials from .env"""
    print(OWNER_EMAIL, OWNER_PASSWORD)
    print(data.email, data.password)

    # Check if email matches
    if data.email != OWNER_EMAIL or data.password != OWNER_PASSWORD:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # Generate JWT token
    token = create_jwt_token({"email": OWNER_EMAIL})

    return {
        "message": "Login successful",
        "email": OWNER_EMAIL,
        "token": token
    }
