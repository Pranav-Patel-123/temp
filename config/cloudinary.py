import cloudinary
import cloudinary.uploader
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure Cloudinary
cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_URL").split("@")[-1],
    api_key=os.getenv("CLOUDINARY_URL").split("//")[-1].split(":")[0],
    api_secret=os.getenv("CLOUDINARY_URL").split(":")[-1].split("@")[0]
)
