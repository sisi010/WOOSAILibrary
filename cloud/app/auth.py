# app/auth.py

from fastapi import Header, HTTPException
from app.database import accounts_collection
import secrets


def generate_api_key() -> str:
    """Generate API key"""
    return f"woosai_{secrets.token_urlsafe(32)}"


async def verify_api_key(authorization: str = Header(...)) -> dict:
    """
    Verify API key from Authorization header
    
    Header format: "Bearer woosai_xxxxx"
    """
    if not authorization.startswith("Bearer "):
        raise HTTPException(401, "Invalid authorization header")
    
    api_key = authorization.replace("Bearer ", "")
    
    # Find account in MongoDB
    account = await accounts_collection.find_one({"api_key": api_key})
    
    if not account:
        raise HTTPException(401, "Invalid API key")
    
    if not account.get("is_active", True):
        raise HTTPException(403, "Account inactive")
    
    return account


async def check_user_limit(account: dict, user_id: str) -> bool:
    """Check if user limit exceeded"""
    from app.database import profiles_collection
    
    # Count unique users for this account
    user_count = await profiles_collection.count_documents({
        "account_id": str(account["_id"])
    })
    
    # Unlimited for enterprise
    if account.get("plan") == "enterprise":
        return True
    
    # Check limit
    max_users = account.get("max_users", 1000)
    return user_count < max_users