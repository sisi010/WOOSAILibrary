"""
License Router - FastAPI Version
Handles license creation and verification
"""

from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime
from bson.objectid import ObjectId

from app.database import get_db
from app.models import License
from app.auth import get_current_user

# Create router
router = APIRouter()


# Request Models
class GenerateLicenseRequest(BaseModel):
    plan: str = "free"
    duration_days: int = 30


class FreeLicenseRequest(BaseModel):
    email: EmailStr


class VerifyLicenseRequest(BaseModel):
    license_key: str


# Response Models
class LicenseInfo(BaseModel):
    id: Optional[str] = None
    license_key: str
    plan: str
    expires_at: str
    status: str
    created_at: Optional[str] = None


class LicenseResponse(BaseModel):
    message: str
    license: LicenseInfo


class FreeLicenseResponse(BaseModel):
    success: bool
    license_key: str
    plan: str
    expires_at: str
    message: str


class VerifyResponse(BaseModel):
    valid: bool
    message: str
    license: Optional[dict] = None


class MyLicensesResponse(BaseModel):
    licenses: List[LicenseInfo]
    count: int


@router.post("/generate", response_model=LicenseResponse, status_code=status.HTTP_201_CREATED)
async def generate_license(
    data: GenerateLicenseRequest,
    current_user: dict = Depends(get_current_user)
):
    """Generate new license for authenticated user"""
    try:
        # Validate plan
        if data.plan not in ['free', 'premium']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Invalid plan'
            )
        
        # Get database
        db = get_db()
        licenses_collection = db.licenses
        users_collection = db.users
        
        # Create license
        user_id = current_user['user_id']
        license_data = License.create(user_id, data.plan, data.duration_days)
        
        # Save to database
        result = licenses_collection.insert_one(license_data)
        
        # Update user plan
        users_collection.update_one(
            {'_id': ObjectId(user_id)},
            {'$set': {'plan': data.plan}}
        )
        
        return {
            'message': 'License generated successfully',
            'license': {
                'id': str(result.inserted_id),
                'license_key': license_data['license_key'],
                'plan': license_data['plan'],
                'expires_at': license_data['expires_at'].isoformat(),
                'status': license_data['status']
            }
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f'Failed to generate license: {str(e)}'
        )


@router.post("/request-free", response_model=FreeLicenseResponse, status_code=status.HTTP_201_CREATED)
async def request_free_license(data: FreeLicenseRequest):
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
        email = data.email.lower().strip()
        
        # Get database
        db = get_db()
        users_collection = db.users
        licenses_collection = db.licenses
        
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
                return {
                    'success': True,
                    'license_key': existing_license['license_key'],
                    'plan': existing_license['plan'],
                    'expires_at': existing_license['expires_at'].isoformat(),
                    'message': 'Using existing active free license'
                }
            
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
        
        return {
            'success': True,
            'license_key': license_data['license_key'],
            'plan': license_data['plan'],
            'expires_at': license_data['expires_at'].isoformat(),
            'message': 'Free license generated successfully'
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f'Failed to generate free license: {str(e)}'
        )


@router.post("/verify", response_model=VerifyResponse)
async def verify_license(data: VerifyLicenseRequest):
    """Verify license key"""
    try:
        license_key = data.license_key
        
        # Verify format and signature
        is_valid, message = License.verify(license_key)
        
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=message
            )
        
        # Check in database
        db = get_db()
        licenses_collection = db.licenses
        license_doc = licenses_collection.find_one({'license_key': license_key})
        
        if not license_doc:
            return {
                'valid': False,
                'message': 'License not found',
                'license': None
            }
        
        if license_doc['status'] != 'active':
            return {
                'valid': False,
                'message': 'License is not active',
                'license': None
            }
        
        return {
            'valid': True,
            'message': 'License is valid',
            'license': {
                'plan': license_doc['plan'],
                'expires_at': license_doc['expires_at'].isoformat(),
                'status': license_doc['status']
            }
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f'Verification failed: {str(e)}'
        )


@router.get("/my-licenses", response_model=MyLicensesResponse)
async def get_my_licenses(current_user: dict = Depends(get_current_user)):
    """Get all licenses for current user"""
    try:
        user_id = current_user['user_id']
        
        # Get database
        db = get_db()
        licenses_collection = db.licenses
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
        
        return {
            'licenses': license_list,
            'count': len(license_list)
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f'Failed to get licenses: {str(e)}'
        )