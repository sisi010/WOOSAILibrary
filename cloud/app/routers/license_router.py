"""
License Router
Handles license creation and verification
"""

from flask import Blueprint, request, jsonify
from app.config import get_licenses_collection, get_users_collection
from app.models import License, User
from app.auth import token_required
from bson.objectid import ObjectId
from datetime import datetime

license_bp = Blueprint('license', __name__)


@license_bp.route('/generate', methods=['POST'])
@token_required
def generate_license(current_user):
    """Generate new license for user"""
    try:
        data = request.get_json()
        
        # Get plan from request or user's current plan
        plan = data.get('plan', 'free')
        duration_days = data.get('duration_days', 30)
        
        # Validate plan
        if plan not in ['free', 'premium']:
            return jsonify({'error': 'Invalid plan'}), 400
        
        # Create license
        user_id = current_user['user_id']
        license_data = License.create(user_id, plan, duration_days)
        
        # Save to database
        licenses_collection = get_licenses_collection()
        result = licenses_collection.insert_one(license_data)
        
        # Update user plan
        users_collection = get_users_collection()
        users_collection.update_one(
            {'_id': ObjectId(user_id)},
            {'$set': {'plan': plan}}
        )
        
        return jsonify({
            'message': 'License generated successfully',
            'license': {
                'id': str(result.inserted_id),
                'license_key': license_data['license_key'],
                'plan': license_data['plan'],
                'expires_at': license_data['expires_at'].isoformat(),
                'status': license_data['status']
            }
        }), 201
    
    except Exception as e:
        return jsonify({'error': f'Failed to generate license: {str(e)}'}), 500


@license_bp.route('/request-free', methods=['POST'])
def request_free_license():
    """
    Request free license with email only (no login required)
    
    This endpoint allows users to get a free license immediately
    without going through registration/login process.
    
    Request body:
        {
            "email": "user@example.com"
        }
    
    Response:
        {
            "success": true,
            "license_key": "WOOSAI-FREE-20250122-abc123",
            "plan": "free",
            "expires_at": "2025-02-21T00:00:00",
            "message": "Free license generated successfully"
        }
    """
    try:
        data = request.get_json()
        
        # Validate email
        if not data or not data.get('email'):
            return jsonify({'error': 'Email is required'}), 400
        
        email = data.get('email').strip().lower()
        
        # Basic email validation
        if '@' not in email or '.' not in email:
            return jsonify({'error': 'Invalid email format'}), 400
        
        users_collection = get_users_collection()
        licenses_collection = get_licenses_collection()
        
        # Check if user exists
        user = users_collection.find_one({'email': email})
        
        if user:
            # User exists - check if they already have an active free license
            existing_license = licenses_collection.find_one({
                'user_id': str(user['_id']),
                'plan': 'free',
                'status': 'active',
                'expires_at': {'$gt': datetime.utcnow()}
            })
            
            if existing_license:
                # Return existing active license
                return jsonify({
                    'success': True,
                    'license_key': existing_license['license_key'],
                    'plan': existing_license['plan'],
                    'expires_at': existing_license['expires_at'].isoformat(),
                    'message': 'Using existing active free license'
                }), 200
            
            user_id = str(user['_id'])
        else:
            # Create new user (without password - library-only user)
            user_data = {
                'email': email,
                'name': email.split('@')[0],  # Use email prefix as name
                'plan': 'free',
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow(),
                'source': 'library'  # Mark as library user
            }
            
            result = users_collection.insert_one(user_data)
            user_id = str(result.inserted_id)
        
        # Generate free license (30 days)
        license_data = License.create(user_id, plan='free', duration_days=30)
        
        # Save license to database
        licenses_collection.insert_one(license_data)
        
        # Update user plan
        users_collection.update_one(
            {'_id': ObjectId(user_id)},
            {'$set': {'plan': 'free', 'updated_at': datetime.utcnow()}}
        )
        
        return jsonify({
            'success': True,
            'license_key': license_data['license_key'],
            'plan': license_data['plan'],
            'expires_at': license_data['expires_at'].isoformat(),
            'message': 'Free license generated successfully'
        }), 201
    
    except Exception as e:
        return jsonify({'error': f'Failed to generate free license: {str(e)}'}), 500


@license_bp.route('/verify', methods=['POST'])
def verify_license():
    """Verify license key"""
    try:
        data = request.get_json()
        
        if not data or not data.get('license_key'):
            return jsonify({'error': 'License key is required'}), 400
        
        license_key = data.get('license_key')
        
        # Verify format and signature
        is_valid, message = License.verify(license_key)
        
        if not is_valid:
            return jsonify({'valid': False, 'message': message}), 400
        
        # Check in database
        licenses_collection = get_licenses_collection()
        license_doc = licenses_collection.find_one({'license_key': license_key})
        
        if not license_doc:
            return jsonify({'valid': False, 'message': 'License not found'}), 404
        
        if license_doc['status'] != 'active':
            return jsonify({'valid': False, 'message': 'License is not active'}), 400
        
        return jsonify({
            'valid': True,
            'message': 'License is valid',
            'license': {
                'plan': license_doc['plan'],
                'expires_at': license_doc['expires_at'].isoformat(),
                'status': license_doc['status']
            }
        }), 200
    
    except Exception as e:
        return jsonify({'error': f'Verification failed: {str(e)}'}), 500


@license_bp.route('/my-licenses', methods=['GET'])
@token_required
def get_my_licenses(current_user):
    """Get all licenses for current user"""
    try:
        user_id = current_user['user_id']
        
        licenses_collection = get_licenses_collection()
        licenses = list(licenses_collection.find({'user_id': user_id}))
        
        license_list = []
        for lic in licenses:
            license_list.append({
                'id': str(lic['_id']),
                'license_key': lic['license_key'],
                'plan': lic['plan'],
                'status': lic['status'],
                'created_at': lic['created_at'].isoformat(),
                'expires_at': lic['expires_at'].isoformat()
            })
        
        return jsonify({
            'licenses': license_list,
            'count': len(license_list)
        }), 200
    
    except Exception as e:
        return jsonify({'error': f'Failed to get licenses: {str(e)}'}), 500