from pydantic import BaseModel, Field
from typing import List, Optional
from bson import ObjectId

# Custom ObjectId Type for Pydantic
class PyObjectId(str):
    @classmethod
    def __get_pydantic_json_schema__(cls, schema):
        schema.update(type="string")

    @classmethod
    def validate(cls, value):
        if not ObjectId.is_valid(value):
            raise ValueError("Invalid ObjectId")
        return str(value)  # Always return as string

# Cart Item Schema
class CartItem(BaseModel):
    id: Optional[PyObjectId] = Field(None, alias="_id")
    product_id: PyObjectId
    name: str
    price: float
    quantity: int

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

# Cart Schema
class Cart(BaseModel):
    id: Optional[PyObjectId] = Field(None, alias="_id")
    customer_id: PyObjectId
    items: List[CartItem] = []
    total_price: float = 0.0
    created_at: Optional[str] = None  # ISO format timestamp
    updated_at: Optional[str] = None

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

# Schema for Partial Updates
class CartUpdate(BaseModel):
    items: Optional[List[CartItem]] = None
    total_price: Optional[float] = None
