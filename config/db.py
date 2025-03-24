import os
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient

# Load environment variables
load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = "ph"  # Explicitly set the database name

if not MONGO_URI:
    raise ValueError("MONGO_URI is not set in .env file")

# Initialize MongoDB client (but don't connect immediately)
client = AsyncIOMotorClient(MONGO_URI)
database = client[DB_NAME]  # Connect to the 'ph' database

# Collections
customers_collection = database.get_collection("customers")
products_collection = database.get_collection("products")
orders_collection = database.get_collection("orders")
cart_collection = database.get_collection("carts")
counters_collection = database.get_collection("counters")
categories_collection = database.get_collection("categories")

print(f"✅ Connected to MongoDB database: {DB_NAME}")

# Function to close the MongoDB connection properly
async def close_mongo_connection():
    client.close()
    print("❌ MongoDB connection closed.")
