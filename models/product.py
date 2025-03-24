from pydantic import BaseModel, Field, HttpUrl, field_validator
from pydantic_core.core_schema import ValidationInfo
from typing import List, Optional
from bson import ObjectId

# Custom ObjectId Type for Pydantic v2
class PyObjectId(str):
    @classmethod
    def __get_pydantic_core_schema__(cls, source_type, handler):
        return handler(str)  # Ensure ObjectId is treated as a string

    @classmethod
    def validate(cls, value):
        if not ObjectId.is_valid(value):
            raise ValueError("Invalid ObjectId")
        return str(value)  # Always return as a string

# Dimensions Schema
class Dimensions(BaseModel):
    height: float
    width: float
    depth: float

# Product Schema
class Product(BaseModel):
    id: Optional[PyObjectId] = Field(None, alias="_id")
    name: str
    description: Optional[str] = None
    images: List[HttpUrl] = []
    price: float
    quantity: int
    category: Optional[str] = None
    brand: Optional[str] = None
    dimensions: Optional[Dimensions] = None
    created_at: Optional[str] = None  # ISO format timestamp
    updated_at: Optional[str] = None

    @field_validator("id", mode="before")
    @classmethod
    def validate_objectid(cls, v, info: ValidationInfo):
        if v is None:
            return None
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return str(v)

    class Config:
        populate_by_name = True
        json_encoders = {ObjectId: str}

# Schema for Partial Updates
class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    images: Optional[List[HttpUrl]] = None
    price: Optional[float] = None
    quantity: Optional[int] = None
    category: Optional[str] = None
    brand: Optional[str] = None
    dimensions: Optional[Dimensions] = None
