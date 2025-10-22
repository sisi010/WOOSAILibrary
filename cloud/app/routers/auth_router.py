"""
Authentication Router
Handles user registration and login
"""

from flask import Blueprint, request, jsonify
from app.config import get_users_collection
from app.models import User, APIKey
from app.auth import generate_token, token_required
from bson.objectid import ObjectId

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    """User registration endpoint"""
    try:
        data = request.get_json()
        
        # Validate input
        if not data or not data.get('email') or not data.get('password'):
            return jsonify({'error': 'Email and password are required'}), 400
        
        email = data.get('email')
        password = data.get('password')
        name = data.get('name', '')
        
        # Check if user already exists
        users_collection = get_users_collection()
        existing_user = users_collection.find_one({'email': email})
        
        if existing_user:
            return jsonify({'error': 'Email already registered'}), 400
        
        # Create new user
        user_data = User.create(email, password, name)
        result = users_collection.insert_one(user_data)
        
        # Generate token
        token = generate_token(result.inserted_id, email)
        
        return jsonify({
            'message': 'User registered successfully',
            'token': token,
            'user': {
                'id': str(result.inserted_id),
                'email': email,
                'name': name,
                'plan': 'free'
            }
        }), 201
    
    except Exception as e:
        return jsonify({'error': f'Registration failed: {str(e)}'}), 500


@auth_bp.route('/login', methods=['POST'])
def login():
    """User login endpoint"""
    try:
        data = request.get_json()
        
        # Validate input
        if not data or not data.get('email') or not data.get('password'):
            return jsonify({'error': 'Email and password are required'}), 400
        
        email = data.get('email')
        password = data.get('password')
        
        # Find user
        users_collection = get_users_collection()
        user = users_collection.find_one({'email': email})
        
        if not user:
            return jsonify({'error': 'Invalid email or password'}), 401
        
        # Verify password
        if not User.verify_password(user['password'], password):
            return jsonify({'error': 'Invalid email or password'}), 401
        
        # Generate token
        token = generate_token(user['_id'], email)
        
        return jsonify({
            'message': 'Login successful',
            'token': token,
            'user': {
                'id': str(user['_id']),
                'email': user['email'],
                'name': user.get('name', ''),
                'plan': user.get('plan', 'free')
            }
        }), 200
    
    except Exception as e:
        return jsonify({'error': f'Login failed: {str(e)}'}), 500


@auth_bp.route('/me', methods=['GET'])
@token_required
def get_current_user(current_user):
    """Get current user info"""
    try:
        users_collection = get_users_collection()
        user = users_collection.find_one({'_id': ObjectId(current_user['user_id'])})
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        return jsonify({
            'user': {
                'id': str(user['_id']),
                'email': user['email'],
                'name': user.get('name', ''),
                'plan': user.get('plan', 'free'),
                'created_at': user.get('created_at').isoformat() if user.get('created_at') else None
            }
        }), 200
    
    except Exception as e:
        return jsonify({'error': f'Failed to get user info: {str(e)}'}), 500


@auth_bp.route('/logout', methods=['POST'])
@token_required
def logout(current_user):
    """User logout endpoint"""
    # In JWT, logout is handled on client side by deleting the token
    # This endpoint is for future enhancements (e.g., token blacklist)
    return jsonify({'message': 'Logged out successfully'}), 200