# app/models.py

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
from bson import ObjectId


class PyObjectId(ObjectId):
    """Custom ObjectId for Pydantic"""
    @classmethod
    def __get_validators__(cls):
        yield cls.validate
    
    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)


class ProfileData(BaseModel):
    """Profile data model"""
    data: Dict[str, Any]
    
    class Config:
        json_schema_extra = {
            "example": {
                "data": {
                    "patterns": {"quality": 5, "economy": 3},
                    "usage_count": 15
                }
            }
        }


class AccountCreate(BaseModel):
    """Account creation model"""
    email: str
    plan: str = "free"
    
    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "plan": "free"
            }
        }