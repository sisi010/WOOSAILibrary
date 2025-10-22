"""
MongoDB Database Connection - Flask Sync Version
WoosAI Backend API Server
"""

from pymongo import MongoClient
import os
import ssl
import certifi

# Global variables for connection
_client = None
_db = None

def get_db():
    """
    Get MongoDB database instance
    Returns the database object
    """
    global _client, _db
    
    if _db is None:
        # Debug: Check environment variables
        print("=" * 50)
        print("🔍 DATABASE CONNECTION DEBUG")
        print("=" * 50)
        
        # Get MongoDB URL from environment
        mongodb_url = os.getenv('MONGODB_URL')
        db_name = os.getenv('DATABASE_NAME', 'woosai')
        
        print(f"📌 DATABASE_NAME: {db_name}")
        print(f"📌 MONGODB_URL exists: {mongodb_url is not None}")
        
        if mongodb_url:
            # Show partial URL for security
            url_preview = mongodb_url[:30] + "..." if len(mongodb_url) > 30 else mongodb_url
            print(f"📌 MONGODB_URL preview: {url_preview}")
        else:
            print("❌ MONGODB_URL is None or empty!")
            print("\n🔍 Checking all environment variables with 'MONGO' or 'DATABASE':")
            found = False
            for key in os.environ.keys():
                if 'MONGO' in key.upper() or 'DATABASE' in key.upper():
                    print(f"   ✓ {key} = {os.environ[key][:30]}...")
                    found = True
            if not found:
                print("   ⚠️ No MongoDB-related environment variables found!")
            
            print("\n💡 Available environment variable keys:")
            env_keys = list(os.environ.keys())
            print(f"   Total: {len(env_keys)} variables")
            print(f"   Sample: {env_keys[:5]}")
            
            raise ValueError("MONGODB_URL is not configured in environment variables")
        
        # Create client and get database
        print(f"\n🔌 Attempting to connect to MongoDB...")
        try:
            # Parse connection string to remove SSL parameters
            import urllib.parse
            
            # Create connection with minimal SSL configuration
            _client = MongoClient(
                mongodb_url,
                serverSelectionTimeoutMS=30000,
                connectTimeoutMS=30000,
                socketTimeoutMS=30000,
                retryWrites=True,
                w='majority'
            )
            _db = _client[db_name]
            
            # Test connection
            _client.admin.command('ping')
            print(f"✅ Successfully connected to MongoDB: {db_name}")
            print("=" * 50)
        except Exception as e:
            print(f"❌ MongoDB connection failed: {str(e)}")
            print("=" * 50)
            raise
    
    return _db


def get_collection(collection_name):
    """
    Get a specific collection from the database
    
    Args:
        collection_name (str): Name of the collection (users, licenses, payments, etc.)
        
    Returns:
        pymongo.collection.Collection: The collection object
    """
    db = get_db()
    return db[collection_name]


def close_db():
    """
    Close database connection
    """
    global _client, _db
    
    if _client is not None:
        _client.close()
        _client = None
        _db = None
        print("👋 MongoDB disconnected")