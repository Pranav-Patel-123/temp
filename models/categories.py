from pydantic import BaseModel, Field, HttpUrl, field_validator
from pydantic_core.core_schema import ValidationInfo
from typing import Optional
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

# Category Schema
class Category(BaseModel):
    id: Optional[PyObjectId] = Field(None, alias="_id")
    name: str
    description: Optional[str] = None
    image: Optional[HttpUrl] = None  # Single image URL
    created_at: Optional[str] = None
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

# Schema for Partial Updates (Categories)
class CategoryUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    image: Optional[HttpUrl] = None  # Allow updating the image URL
