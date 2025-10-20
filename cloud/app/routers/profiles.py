# app/routers/profiles.py

from fastapi import APIRouter, Depends, HTTPException
from app.database import profiles_collection, usage_collection
from app.auth import verify_api_key, check_user_limit
from app.models import ProfileData
from datetime import datetime
from typing import Dict, Any

router = APIRouter(prefix="/v1/profiles", tags=["profiles"])


@router.put("/{user_id}")
async def save_profile(
    user_id: str,
    profile_data: ProfileData,
    account: dict = Depends(verify_api_key)
):
    """
    Save or update user profile
    
    Args:
        user_id: User identifier
        profile_data: Profile data to save
        account: Account from API key
    
    Returns:
        Success message
    """
    # Check user limit
    if not await check_user_limit(account, user_id):
        raise HTTPException(
            403,
            detail=f"User limit exceeded. Your plan allows {account['max_users']} users. Please upgrade."
        )
    
    account_id = str(account["_id"])
    
    # Upsert profile (update or insert)
    await profiles_collection.update_one(
        {"account_id": account_id, "user_id": user_id},
        {
            "$set": {
                "data": profile_data.data,
                "updated_at": datetime.utcnow()
            },
            "$setOnInsert": {
                "account_id": account_id,
                "user_id": user_id,
                "created_at": datetime.utcnow()
            }
        },
        upsert=True
    )
    
    # Track usage
    today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    await usage_collection.update_one(
        {"account_id": account_id, "date": today},
        {"$inc": {"profile_saves": 1}},
        upsert=True
    )
    
    return {"status": "ok", "message": "Profile saved"}


@router.get("/{user_id}")
async def load_profile(
    user_id: str,
    account: dict = Depends(verify_api_key)
) -> Dict[str, Any]:
    """
    Load user profile
    
    Args:
        user_id: User identifier
        account: Account from API key
    
    Returns:
        Profile data
    """
    account_id = str(account["_id"])
    
    # Find profile
    profile = await profiles_collection.find_one({
        "account_id": account_id,
        "user_id": user_id
    })
    
    if not profile:
        raise HTTPException(404, "Profile not found")
    
    # Track usage
    today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    await usage_collection.update_one(
        {"account_id": account_id, "date": today},
        {"$inc": {"profile_loads": 1}},
        upsert=True
    )
    
    # Return only data (not metadata)
    return profile["data"]


@router.delete("/{user_id}")
async def delete_profile(
    user_id: str,
    account: dict = Depends(verify_api_key)
):
    """
    Delete user profile (GDPR compliance)
    
    Args:
        user_id: User identifier
        account: Account from API key
    
    Returns:
        Success message
    """
    account_id = str(account["_id"])
    
    result = await profiles_collection.delete_one({
        "account_id": account_id,
        "user_id": user_id
    })
    
    if result.deleted_count == 0:
        raise HTTPException(404, "Profile not found")
    
    return {"status": "ok", "message": "Profile deleted"}


@router.get("/")
async def list_profiles(
    account: dict = Depends(verify_api_key),
    limit: int = 10,
    skip: int = 0
):
    """
    List all profiles for this account
    
    Args:
        account: Account from API key
        limit: Number of profiles to return
        skip: Number of profiles to skip
    
    Returns:
        List of profiles
    """
    account_id = str(account["_id"])
    
    # Get profiles
    cursor = profiles_collection.find(
        {"account_id": account_id}
    ).limit(limit).skip(skip)
    
    profiles = []
    async for profile in cursor:
        profiles.append({
            "user_id": profile["user_id"],
            "created_at": profile.get("created_at"),
            "updated_at": profile.get("updated_at")
        })
    
    # Get total count
    total = await profiles_collection.count_documents({
        "account_id": account_id
    })
    
    return {
        "profiles": profiles,
        "total": total,
        "limit": limit,
        "skip": skip
    }