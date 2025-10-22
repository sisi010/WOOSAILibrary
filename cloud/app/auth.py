"""
Authentication Helper Functions
JWT token generation and verification
"""

import jwt
from datetime import datetime, timedelta
from flask import request, jsonify
from functools import wraps
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

def verify_token(token):
    """Verify JWT token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        return True, payload
    except jwt.ExpiredSignatureError:
        return False, {'error': 'Token expired'}
    except jwt.InvalidTokenError:
        return False, {'error': 'Invalid token'}

def token_required(f):
    """Decorator to require valid token"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # Get token from Authorization header
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(' ')[1]  # "Bearer TOKEN"
            except IndexError:
                return jsonify({'error': 'Invalid token format'}), 401
        
        if not token:
            return jsonify({'error': 'Token is missing'}), 401
        
        # Verify token
        is_valid, payload = verify_token(token)
        
        if not is_valid:
            return jsonify(payload), 401
        
        # Pass user info to the route
        return f(payload, *args, **kwargs)
    
    return decorated