# app/database.py

from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

# Load environment variables from parent directory
from pathlib import Path
env_path = Path(__file__).parent.parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

MONGODB_URL = os.getenv("MONGODB_URL")
DATABASE_NAME = os.getenv("DATABASE_NAME", "woosai")

print(f"🔌 Connecting to MongoDB Atlas...")
print(f"📊 Database: {DATABASE_NAME}")

# Async client
client = AsyncIOMotorClient(MONGODB_URL)
database = client[DATABASE_NAME]

# Collections
accounts_collection = database["accounts"]
profiles_collection = database["profiles"]
usage_collection = database["usage"]


async def init_db():
    """Initialize database with indexes"""
    try:
        # Test connection
        await client.admin.command('ping')
        print("✅ MongoDB Atlas connected successfully!")
        
        # Create indexes
        await accounts_collection.create_index("api_key", unique=True)
        await accounts_collection.create_index("email", unique=True)
        
        await profiles_collection.create_index([
            ("account_id", 1),
            ("user_id", 1)
        ], unique=True)
        
        await usage_collection.create_index([
            ("account_id", 1),
            ("date", -1)
        ])
        
        print("✅ MongoDB indexes created")
        
    except Exception as e:
        print(f"❌ MongoDB connection failed: {e}")
        raise


async def close_db():
    """Close database connection"""
    client.close()
    print("👋 MongoDB disconnected")