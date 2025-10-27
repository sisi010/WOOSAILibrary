"""
Authentication Helper Functions - FastAPI Version
JWT token generation and verification
"""

import jwt
from datetime import datetime, timedelta
from fastapi import HTTPException, status, Header
from typing import Optional
import os

SECRET_KEY = os.getenv('SECRET_KEY', 'woosai-secret-key-2025')


def generate_token(user_id, email):
    """Generate JWT token"""
    payload = {
        'user_id': str(user_id),
        'email': email,
        'exp': datetime.utcnow() + timedelta(days=7)  # Token expires in 7 days
    }
    
    token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
    return token


def verify_token(token: str):
    """Verify JWT token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        return True, payload
    except jwt.ExpiredSignatureError:
        return False, {'error': 'Token expired'}
    except jwt.InvalidTokenError:
        return False, {'error': 'Invalid token'}


async def get_current_user(authorization: Optional[str] = Header(None)):
    """
    FastAPI dependency for token authentication
    Usage: current_user = Depends(get_current_user)
    """
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Authorization header is missing',
            headers={'WWW-Authenticate': 'Bearer'}
        )
    
    try:
        # Extract token from "Bearer TOKEN"
        scheme, token = authorization.split()
        
        if scheme.lower() != 'bearer':
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='Invalid authentication scheme',
                headers={'WWW-Authenticate': 'Bearer'}
            )
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Invalid authorization header format',
            headers={'WWW-Authenticate': 'Bearer'}
        )
    
    # Verify token
    is_valid, payload = verify_token(token)
    
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=payload.get('error', 'Invalid token'),
            headers={'WWW-Authenticate': 'Bearer'}
        )
    
    return payload