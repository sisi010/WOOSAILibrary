"""
Authentication Router - FastAPI Version
Handles user registration and login
"""

from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
from bson.objectid import ObjectId

from app.database import get_db
from app.models import User

# Create router
router = APIRouter()


# Request Models
class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    name: Optional[str] = ""


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


# Response Models
class UserResponse(BaseModel):
    id: str
    email: str
    name: str
    plan: str


class AuthResponse(BaseModel):
    message: str
    token: str
    user: UserResponse


@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def register(data: RegisterRequest):
    """User registration endpoint"""
    try:
        db = get_db()
        users_collection = db.users
        
        # Check if user already exists
        existing_user = users_collection.find_one({'email': data.email})
        
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Email already registered'
            )
        
        # Create new user
        user_data = User.create(data.email, data.password, data.name)
        result = users_collection.insert_one(user_data)
        
        # Generate token (simple version - you can enhance this)
        from app.auth import generate_token
        token = generate_token(result.inserted_id, data.email)
        
        return {
            'message': 'User registered successfully',
            'token': token,
            'user': {
                'id': str(result.inserted_id),
                'email': data.email,
                'name': data.name,
                'plan': 'free'
            }
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f'Registration failed: {str(e)}'
        )


@router.post("/login", response_model=AuthResponse)
async def login(data: LoginRequest):
    """User login endpoint"""
    try:
        db = get_db()
        users_collection = db.users
        
        # Find user
        user = users_collection.find_one({'email': data.email})
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='Invalid email or password'
            )
        
        # Verify password
        if not User.verify_password(user['password'], data.password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='Invalid email or password'
            )
        
        # Generate token
        from app.auth import generate_token
        token = generate_token(user['_id'], data.email)
        
        return {
            'message': 'Login successful',
            'token': token,
            'user': {
                'id': str(user['_id']),
                'email': user['email'],
                'name': user.get('name', ''),
                'plan': user.get('plan', 'free')
            }
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f'Login failed: {str(e)}'
        )


@router.get("/me", response_model=UserResponse)
async def get_current_user():
    """Get current user info - placeholder for token authentication"""
    # TODO: Implement proper token authentication with Depends
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail='Token authentication not yet implemented'
    )


@router.post("/logout")
async def logout():
    """User logout endpoint"""
    # In JWT, logout is handled on client side by deleting the token
    return {'message': 'Logged out successfully'}