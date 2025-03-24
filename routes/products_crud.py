from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from typing import List
from models.product import ProductUpdate
from config.db import products_collection
from bson import ObjectId
from datetime import datetime
import cloudinary.uploader

# Initialize Router
product_router = APIRouter()

# ------------------------------
# Product Endpoints
# ------------------------------

@product_router.get("/products")
async def get_products():
    """Retrieve all products with full details."""
    products = [
        {**product, "_id": str(product["_id"])}  # Convert ObjectId to string
        for product in await products_collection.find({}).to_list(length=100)
    ]
    return products


@product_router.post("/products")
async def create_product(
    name: str = Form(...),
    price: float = Form(...),
    quantity: int = Form(...),
    category: str = Form(""),
    brand: str = Form(""),
    images: List[UploadFile] = File(...)
):
    """Upload multiple images to Cloudinary and store product details in MongoDB"""

    # Cloudinary folder for product images
    cloudinary_folder = f"ph-products/{name.replace(' ', '-')}"  # Avoid spaces in folder names

    # Upload multiple images to Cloudinary
    image_urls = []
    for image in images:
        try:
            result = cloudinary.uploader.upload(image.file, folder=cloudinary_folder)
            image_urls.append(result["secure_url"])
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Cloudinary upload failed: {str(e)}")

    # Prepare product data
    product_data = {
        "name": name,
        "price": price,
        "quantity": quantity,
        "images": image_urls,  # Store multiple image URLs
        "category": category,
        "brand": brand,
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat(),
    }

    result = await products_collection.insert_one(product_data)
    return {"_id": str(result.inserted_id), "image_urls": image_urls}


@product_router.put("/products/{product_id}")
async def update_product(product_id: str, product: ProductUpdate):
    """Modify an existing product by its ID."""
    if not ObjectId.is_valid(product_id):
        raise HTTPException(status_code=400, detail="Invalid Product ID")

    # Only include provided fields in the update
    product_dict = {k: v for k, v in product.dict(exclude_unset=True).items() if v is not None}

    # Convert HttpUrl objects to strings
    if "images" in product_dict:
        product_dict["images"] = [str(url) for url in product_dict["images"]]

    product_dict["updated_at"] = datetime.utcnow().isoformat()

    result = await products_collection.update_one(
        {"_id": ObjectId(product_id)}, {"$set": product_dict}
    )

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Product not found")

    return {"message": "Product updated successfully"}


@product_router.delete("/products/{product_id}")
async def delete_product(product_id: str):
    """Remove a product from the database."""
    if not ObjectId.is_valid(product_id):
        raise HTTPException(status_code=400, detail="Invalid Product ID")

    result = await products_collection.delete_one({"_id": ObjectId(product_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Product not found")

    return {"message": "Product deleted successfully"}
