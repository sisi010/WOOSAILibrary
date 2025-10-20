# app/routers/admin.py

from fastapi import APIRouter, HTTPException
from app.database import accounts_collection, profiles_collection, usage_collection
from app.auth import generate_api_key
from app.models import AccountCreate
from datetime import datetime

router = APIRouter(prefix="/v1/admin", tags=["admin"])


@router.post("/accounts")
async def create_account(account_data: AccountCreate):
    """
    Create new account and generate API key
    
    ⚠️ In production, this should be protected with admin authentication!
    
    Args:
        account_data: Account creation data
    
    Returns:
        Created account with API key
    """
    # Check if email exists
    existing = await accounts_collection.find_one({"email": account_data.email})
    if existing:
        raise HTTPException(400, "Email already registered")
    
    # Generate API key
    api_key = generate_api_key()
    
    # Set max users based on plan
    max_users_map = {
        "free": 1000,
        "pro": 10000,
        "enterprise": 999999999
    }
    
    # Create account document
    account = {
        "api_key": api_key,
        "email": account_data.email,
        "plan": account_data.plan,
        "max_users": max_users_map.get(account_data.plan, 1000),
        "is_active": True,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    result = await accounts_collection.insert_one(account)
    account["_id"] = str(result.inserted_id)
    
    return account


@router.get("/accounts/{api_key}")
async def get_account(api_key: str):
    """
    Get account info by API key
    
    Args:
        api_key: API key to lookup
    
    Returns:
        Account information
    """
    account = await accounts_collection.find_one({"api_key": api_key})
    
    if not account:
        raise HTTPException(404, "Account not found")
    
    # Get profile count
    profile_count = await profiles_collection.count_documents({
        "account_id": str(account["_id"])
    })
    
    # Get usage stats
    today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    usage = await usage_collection.find_one({
        "account_id": str(account["_id"]),
        "date": today
    })
    
    account["_id"] = str(account["_id"])
    account["profile_count"] = profile_count
    account["today_usage"] = {
        "profile_saves": usage.get("profile_saves", 0) if usage else 0,
        "profile_loads": usage.get("profile_loads", 0) if usage else 0
    }
    
    return account


@router.get("/stats")
async def get_stats():
    """
    Get overall system statistics
    
    Returns:
        System statistics
    """
    total_accounts = await accounts_collection.count_documents({})
    total_profiles = await profiles_collection.count_documents({})
    active_accounts = await accounts_collection.count_documents({"is_active": True})
    
    # Get plan distribution
    plans = {}
    cursor = accounts_collection.find({})
    async for account in cursor:
        plan = account.get("plan", "free")
        plans[plan] = plans.get(plan, 0) + 1
    
    return {
        "total_accounts": total_accounts,
        "active_accounts": active_accounts,
        "total_profiles": total_profiles,
        "plan_distribution": plans
    }