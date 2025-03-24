from fastapi import APIRouter, HTTPException
from config.db import orders_collection, counters_collection
from models.orders import Order
from bson import ObjectId
from datetime import datetime
from typing import List
from fastapi import Query


order_router = APIRouter()

async def get_next_order_id():
    """Fetch the next sequential order ID, creating a counter if it doesn't exist."""
    counter = await counters_collection.find_one_and_update(
        {"_id": "order_id"},
        {"$inc": {"seq": 1}},
        upsert=True,  
        return_document=True
    )
    return counter["seq"]

# ✅ Place a new order with a sequential order ID
@order_router.post("/", response_model=Order)
async def create_order(order: Order):
    order_dict = order.dict()

    # Ensure counter exists
    if not await counters_collection.find_one({"_id": "order_id"}):
        await counters_collection.insert_one({"_id": "order_id", "seq": 0})

    # Generate sequential order ID
    next_order_id = await get_next_order_id()
    order_dict["order_id"] = f"ORD-{next_order_id:06d}"  # Format: "ORD-000001"

    order_dict["created_at"] = datetime.utcnow()
    result = await orders_collection.insert_one(order_dict)

    # ✅ Return response including order_id
    return {**order_dict, "_id": str(result.inserted_id)}


# ✅ Get all orders (FOR OWNER)
@order_router.get("/", response_model=List[Order])
async def get_all_orders():
    orders = await orders_collection.find().to_list(None)
    return [{**order, "_id": str(order["_id"]), "order_id": order["order_id"]} for order in orders]

# ✅ Get orders by customer ID (FOR CUSTOMER)
@order_router.get("/customer/{customer_id}", response_model=List[Order])
async def get_customer_orders(customer_id: str):
    orders = await orders_collection.find({"customer_id": customer_id}).to_list(None)
    if not orders:
        raise HTTPException(status_code=404, detail="No orders found for this customer")
    return [{**order, "_id": str(order["_id"]), "order_id": order["order_id"]} for order in orders]


# ✅ Update order status (OWNER ONLY)
@order_router.patch("/{order_id}")
async def update_order_status(order_id: str, status: str = Query(...)):
    if status not in ["pending", "shipped", "delivered", "cancelled"]:
        raise HTTPException(status_code=400, detail="Invalid order status")

    result = await orders_collection.update_one(
        {"order_id": order_id},  # ✅ Query by `order_id`, not `_id`
        {"$set": {"status": status, "updated_at": datetime.utcnow()}}
    )

    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Order not found")

    return {"message": "Order status updated successfully"}

