# app/routers/payment.py (FastAPI version)

"""
Lemon Squeezy Payment Integration for WoosAI Backend (FastAPI)

Handles Premium subscription payments through Lemon Squeezy
"""

from fastapi import APIRouter, Request, HTTPException, Header
from pydantic import BaseModel, EmailStr
from typing import Optional
import requests
import os
import hmac
import hashlib
from datetime import datetime

router = APIRouter(
    prefix="/api/payment",
    tags=["payment"]
)

# Lemon Squeezy configuration
LEMON_API_KEY = os.getenv('LEMON_API_KEY')
LEMON_STORE_ID = os.getenv('LEMON_STORE_ID')
LEMON_PRODUCT_ID = os.getenv('LEMON_PRODUCT_ID')
LEMON_WEBHOOK_SECRET = os.getenv('LEMON_WEBHOOK_SECRET')

LEMON_API_BASE = "https://api.lemonsqueezy.com/v1"


# Pydantic models
class CheckoutRequest(BaseModel):
    email: EmailStr
    license_key: str


class CancelSubscriptionRequest(BaseModel):
    subscription_id: str


def get_headers():
    """Get authorization headers for Lemon Squeezy API"""
    return {
        "Authorization": f"Bearer {LEMON_API_KEY}",
        "Content-Type": "application/vnd.api+json",
        "Accept": "application/vnd.api+json"
    }


@router.post("/create-checkout")
async def create_checkout(checkout_req: CheckoutRequest):
    """
    Create Lemon Squeezy checkout session for Premium upgrade
    
    Request body:
        {
            "email": "user@example.com",
            "license_key": "WOOSAI-FREE-xxx"
        }
    
    Returns:
        {
            "success": true,
            "url": "https://woosai.lemonsqueezy.com/checkout/..."
        }
    """
    try:
        if not LEMON_API_KEY or not LEMON_PRODUCT_ID:
            raise HTTPException(
                status_code=500,
                detail="Payment system not configured"
            )
        
        # Create checkout session
        checkout_data = {
            "data": {
                "type": "checkouts",
                "attributes": {
                    "checkout_data": {
                        "email": checkout_req.email,
                        "custom": {
                            "license_key": checkout_req.license_key
                        }
                    },
                    "expires_at": None,
                    "preview": False
                },
                "relationships": {
                    "store": {
                        "data": {
                            "type": "stores",
                            "id": LEMON_STORE_ID
                        }
                    } if LEMON_STORE_ID else None,
                    "variant": {
                        "data": {
                            "type": "variants",
                            "id": LEMON_PRODUCT_ID
                        }
                    }
                }
            }
        }
        
        # Remove store relationship if not provided
        if not LEMON_STORE_ID:
            del checkout_data["data"]["relationships"]["store"]
        
        response = requests.post(
            f"{LEMON_API_BASE}/checkouts",
            headers=get_headers(),
            json=checkout_data
        )
        
        if response.status_code in [200, 201]:
            result = response.json()
            checkout_url = result['data']['attributes']['url']
            
            return {
                "success": True,
                "url": checkout_url,
                "checkout_id": result['data']['id']
            }
        else:
            raise HTTPException(
                status_code=response.status_code,
                detail=f"Lemon Squeezy error: {response.text}"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/webhook")
async def lemon_webhook(
    request: Request,
    x_signature: Optional[str] = Header(None)
):
    """
    Handle Lemon Squeezy webhook events
    
    Events:
        - order_created: New Premium subscription
        - subscription_updated: Subscription changes
        - subscription_cancelled: Cancel Premium
    """
    try:
        # Get raw body
        body = await request.body()
        
        # Verify webhook signature
        if LEMON_WEBHOOK_SECRET and x_signature:
            expected_signature = hmac.new(
                LEMON_WEBHOOK_SECRET.encode(),
                body,
                hashlib.sha256
            ).hexdigest()
            
            if not hmac.compare_digest(x_signature, expected_signature):
                raise HTTPException(status_code=401, detail="Invalid signature")
        
        # Parse event
        event = await request.json()
        event_name = event.get('meta', {}).get('event_name')
        event_data = event.get('data', {})
        
        # Handle events
        if event_name == 'order_created':
            # New Premium subscription
            customer_email = event_data.get('attributes', {}).get('user_email')
            print(f"✅ Premium subscription created: {customer_email}")
            # TODO: Upgrade license to Premium in database
            
        elif event_name == 'subscription_updated':
            # Subscription renewed or updated
            print(f"🔄 Subscription updated")
            
        elif event_name == 'subscription_cancelled':
            # Subscription cancelled
            print(f"❌ Subscription cancelled")
            # TODO: Downgrade to Free in database
        
        return {"success": True}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/get-price")
async def get_price():
    """
    Get current Premium price
    
    Returns:
        {
            "success": true,
            "price": 9.00,
            "currency": "USD",
            "interval": "month"
        }
    """
    try:
        if not LEMON_PRODUCT_ID or not LEMON_API_KEY:
            # Fallback to hardcoded price
            return {
                "success": True,
                "price": 9.0,
                "currency": "USD",
                "interval": "month",
                "name": "Premium Plan"
            }
        
        # Fetch product from Lemon Squeezy
        response = requests.get(
            f"{LEMON_API_BASE}/variants/{LEMON_PRODUCT_ID}",
            headers=get_headers()
        )
        
        if response.status_code == 200:
            variant = response.json()['data']
            price = variant['attributes']['price'] / 100  # Convert cents to dollars
            
            return {
                "success": True,
                "price": price,
                "currency": "USD",
                "interval": "month",
                "name": "Premium Plan"
            }
        else:
            # Fallback to hardcoded price
            return {
                "success": True,
                "price": 9.0,
                "currency": "USD",
                "interval": "month",
                "name": "Premium Plan"
            }
            
    except Exception:
        # Fallback to hardcoded price
        return {
            "success": True,
            "price": 9.0,
            "currency": "USD",
            "interval": "month",
            "name": "Premium Plan"
        }


@router.get("/subscriptions/{email}")
async def get_subscription(email: str):
    """
    Get subscription status for a customer
    
    Args:
        email: Customer email
        
    Returns:
        {
            "success": true,
            "subscription": {
                "status": "active",
                "plan": "premium",
                "renews_at": "2025-11-23"
            }
        }
    """
    try:
        # TODO: Query Lemon Squeezy API for subscriptions
        # For now, return mock data
        
        return {
            "success": True,
            "subscription": {
                "status": "active",
                "plan": "premium",
                "renews_at": "2025-11-23"
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/cancel-subscription")
async def cancel_subscription(cancel_req: CancelSubscriptionRequest):
    """
    Cancel Premium subscription
    
    Request body:
        {
            "subscription_id": "12345"
        }
    
    Returns:
        {
            "success": true,
            "message": "Subscription cancelled"
        }
    """
    try:
        if not cancel_req.subscription_id:
            raise HTTPException(
                status_code=400,
                detail="subscription_id required"
            )
        
        # Cancel subscription via API
        response = requests.delete(
            f"{LEMON_API_BASE}/subscriptions/{cancel_req.subscription_id}",
            headers=get_headers()
        )
        
        if response.status_code in [200, 204]:
            return {
                "success": True,
                "message": "Subscription cancelled successfully"
            }
        else:
            raise HTTPException(
                status_code=500,
                detail="Failed to cancel subscription"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def health():
    """Health check endpoint"""
    return {
        "success": True,
        "service": "payment",
        "provider": "lemon_squeezy",
        "status": "ok",
        "api_key_configured": bool(LEMON_API_KEY),
        "product_id_configured": bool(LEMON_PRODUCT_ID)
    }