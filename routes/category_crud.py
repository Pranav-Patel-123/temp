from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from models.categories import CategoryUpdate
from config.db import categories_collection
from bson import ObjectId
from datetime import datetime
import cloudinary.uploader

# Initialize Router
category_router = APIRouter()

# ------------------------------
# Category Endpoints
# ------------------------------

@category_router.get("/categories")
async def get_categories():
    """Retrieve all categories"""
    categories = [
        {**category, "_id": str(category["_id"])}
        for category in await categories_collection.find({}).to_list(length=100)
    ]
    return categories


@category_router.post("/categories")
async def create_category(
    name: str = Form(...),
    description: str = Form(""),
    image: UploadFile = File(None)  # Image upload is optional
):
    """Create a new category with an image upload"""

    # Cloudinary folder for category images
    cloudinary_folder = f"ph-categories/{name.replace(' ', '-')}"  # Avoid spaces in folder names

    # Upload image if provided
    image_url = None
    if image:
        try:
            result = cloudinary.uploader.upload(image.file, folder=cloudinary_folder)
            image_url = result["secure_url"]
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Cloudinary upload failed: {str(e)}")

    # Prepare category data
    category_data = {
        "name": name,
        "description": description,
        "image": image_url,  # Store single image URL
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat(),
    }

    result = await categories_collection.insert_one(category_data)
    return {"_id": str(result.inserted_id), "image_url": image_url}


@category_router.put("/categories/{category_id}")
async def update_category(
    category_id: str,
    name: str = Form(None),
    description: str = Form(None),
    image: UploadFile = File(None)  # Image upload is optional
):
    """Update an existing category with optional image upload"""
    if not ObjectId.is_valid(category_id):
        raise HTTPException(status_code=400, detail="Invalid Category ID")

    update_data = {}

    # Update text fields
    if name:
        update_data["name"] = name
    if description:
        update_data["description"] = description

    # Upload new image if provided
    if image:
        cloudinary_folder = f"ph-categories/{name.replace(' ', '-') if name else 'updated-category'}"
        try:
            result = cloudinary.uploader.upload(image.file, folder=cloudinary_folder)
            update_data["image"] = result["secure_url"]
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Cloudinary upload failed: {str(e)}")

    update_data["updated_at"] = datetime.utcnow().isoformat()

    result = await categories_collection.update_one(
        {"_id": ObjectId(category_id)}, {"$set": update_data}
    )

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Category not found")

    return {"message": "Category updated successfully"}


@category_router.delete("/categories/{category_id}")
async def delete_category(category_id: str):
    """Delete a category"""
    if not ObjectId.is_valid(category_id):
        raise HTTPException(status_code=400, detail="Invalid Category ID")

    result = await categories_collection.delete_one({"_id": ObjectId(category_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Category not found")

    return {"message": "Category deleted successfully"}
