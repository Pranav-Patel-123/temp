from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
from config.db import customers_collection
import random
import string
import jwt
from jwt import encode, decode
import datetime
from passlib.context import CryptContext
from typing import Optional

customer_auth_router = APIRouter()

# ✅ JWT Secret & Algorithm
SECRET_KEY = "your_secret_key"  # Change this in production
ALGORITHM = "HS256"

# ✅ Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# ✅ Function to generate unique customer ID
def generate_customer_id():
    """Generate a random 8-character alphanumeric customer ID."""
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

# ✅ Function to create a JWT token
def create_jwt_token(data: dict):
    """Generate a JWT token."""
    payload = {
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=24),
        "iat": datetime.datetime.utcnow(),
        "sub": data
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

# ✅ Customer Registration Model
class RegisterRequest(BaseModel):
    name: str
    email: EmailStr
    password: str
    gst_required: bool = False
    gst_number: Optional[str] = None
    company_name: Optional[str] = None
    billing_address: Optional[str] = None

# ✅ Customer Login Model
class LoginRequest(BaseModel):
    email: EmailStr
    password: str

# ✅ Customer Registration Endpoint
@customer_auth_router.post("/register")
async def customer_register(data: RegisterRequest):
    existing_user = await customers_collection.find_one({"email": data.email})

    if existing_user:
        raise HTTPException(status_code=400, detail="User with this email already exists")

    customer_id = generate_customer_id()  # Generate unique customer ID

    new_customer = {
        "name": data.name,
        "email": data.email,
        "customer_id": customer_id,
        "password": pwd_context.hash(data.password),  # Hash password
        "gst_required": data.gst_required,
        "gst_number": data.gst_number if data.gst_required else None,
        "company_name": data.company_name if data.gst_required else None,
        "billing_address": data.billing_address if data.gst_required else None,
    }

    await customers_collection.insert_one(new_customer)

    token = create_jwt_token({"customer_id": customer_id, "email": data.email})

    return {
        "message": "Registration successful",
        "customer_id": customer_id,
        "token": token
    }

# ✅ Customer Login Endpoint
@customer_auth_router.post("/login")
async def customer_login(data: LoginRequest):
    user = await customers_collection.find_one({"email": data.email})

    if not user or not pwd_context.verify(data.password, user["password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_jwt_token({"customer_id": user["customer_id"], "email": user["email"]})

    return {
        "message": "Login successful",
        "customer_id": user["customer_id"],
        "token": token
    }
