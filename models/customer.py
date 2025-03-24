from pydantic import BaseModel, Field, EmailStr
from bson import ObjectId
from typing import Optional

class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)

    @classmethod
    def __get_pydantic_json_schema__(cls, handler):
        return {"type": "string", "format": "objectid"}

# ✅ Customer Model with GST Bill Fields
class CustomerLogin(BaseModel):
    customer_id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    name: str
    email: EmailStr
    password: str
    
    # ✅ GST Bill Fields (Optional)
    gst_required: bool = False  # True if GST bill is needed
    gst_number: Optional[str] = None  # GSTIN (if applicable)
    company_name: Optional[str] = None  # Business name
    billing_address: Optional[str] = None  # Address for the GST invoice

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
