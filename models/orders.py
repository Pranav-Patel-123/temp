from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class OrderItem(BaseModel):
    product_id: str
    name: str
    price: float
    quantity: int

class Order(BaseModel):
    order_id: Optional[str] = None  # Sequential order ID
    customer_id: str  # Only customers are linked to orders
    items: List[OrderItem]
    total_price: float = Field(..., gt=0)
    status: str = "pending"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
