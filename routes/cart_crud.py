from fastapi import APIRouter, HTTPException, Depends
from models.cart import Cart, CartItem, PyObjectId
from config.db import cart_collection
from bson import ObjectId
from typing import List
from datetime import datetime


cart_router = APIRouter()


# Get Customer Cart
@cart_router.get("/cart/{customer_id}", response_model=Cart)
async def get_cart(customer_id: str):
    cart = cart_collection.find_one({"customer_id": ObjectId(customer_id)})
    if not cart:
        return Cart(customer_id=ObjectId(customer_id), items=[], total_price=0.0)
    return cart


# Add Item to Cart
@cart_router.post("/cart/{customer_id}/add")
async def add_to_cart(customer_id: str, item: CartItem):
    cart = cart_collection.find_one({"customer_id": ObjectId(customer_id)})

    if not cart:
        new_cart = Cart(
            customer_id=ObjectId(customer_id),
            items=[item],
            total_price=item.price * item.quantity,
            created_at=datetime.utcnow().isoformat(),
            updated_at=datetime.utcnow().isoformat()
        )
        cart_collection.insert_one(new_cart.dict(by_alias=True))
        return {"message": "Cart created and item added"}

    # Check if item exists, update quantity
    found = False
    for cart_item in cart["items"]:
        if cart_item["product_id"] == str(item.product_id):
            cart_item["quantity"] += item.quantity
            found = True
            break

    if not found:
        cart["items"].append(item.dict(by_alias=True))

    cart["total_price"] = sum(i["price"] * i["quantity"] for i in cart["items"])
    cart["updated_at"] = datetime.utcnow().isoformat()
    
    cart_collection.update_one({"customer_id": ObjectId(customer_id)}, {"$set": cart})
    
    return {"message": "Item added to cart"}


# Update Item Quantity in Cart
@cart_router.put("/cart/{customer_id}/update/{product_id}")
async def update_cart_item(customer_id: str, product_id: str, quantity: int):
    cart = cart_collection.find_one({"customer_id": ObjectId(customer_id)})
    
    if not cart:
        raise HTTPException(status_code=404, detail="Cart not found")

    for item in cart["items"]:
        if item["product_id"] == product_id:
            item["quantity"] = quantity
            break
    else:
        raise HTTPException(status_code=404, detail="Product not found in cart")

    cart["total_price"] = sum(i["price"] * i["quantity"] for i in cart["items"])
    cart["updated_at"] = datetime.utcnow().isoformat()

    cart_collection.update_one({"customer_id": ObjectId(customer_id)}, {"$set": cart})

    return {"message": "Cart updated"}


# Remove Item from Cart
@cart_router.delete("/cart/{customer_id}/remove/{product_id}")
async def remove_cart_item(customer_id: str, product_id: str):
    cart = cart_collection.find_one({"customer_id": ObjectId(customer_id)})

    if not cart:
        raise HTTPException(status_code=404, detail="Cart not found")

    cart["items"] = [item for item in cart["items"] if item["product_id"] != product_id]
    cart["total_price"] = sum(i["price"] * i["quantity"] for i in cart["items"])
    cart["updated_at"] = datetime.utcnow().isoformat()

    cart_collection.update_one({"customer_id": ObjectId(customer_id)}, {"$set": cart})

    return {"message": "Item removed from cart"}


# Clear Entire Cart
@cart_router.delete("/cart/{customer_id}/clear")
async def clear_cart(customer_id: str):
    cart_collection.delete_one({"customer_id": ObjectId(customer_id)})
    return {"message": "Cart cleared"}
