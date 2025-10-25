"""
Lemon Squeezy Payment Router
Handles Premium subscription payments via Lemon Squeezy
"""

from fastapi import APIRouter, HTTPException, Request, Header
from pydantic import BaseModel, EmailStr
from typing import Optional
import os
import httpx
import hmac
import hashlib
import json
from datetime import datetime

router = APIRouter(prefix="/api/payment", tags=["payment"])

# Lemon Squeezy Configuration
LEMON_API_KEY = os.getenv("LEMON_API_KEY")
LEMON_STORE_ID = os.getenv("LEMON_STORE_ID")
LEMON_VARIANT_ID = os.getenv("LEMON_VARIANT_ID")  # ← Variant ID!
LEMON_WEBHOOK_SECRET = os.getenv("LEMON_WEBHOOK_SECRET")
LEMON_API_URL = "https://api.lemonsqueezy.com/v1"


# Request/Response Models
class CheckoutRequest(BaseModel):
    email: EmailStr
    license_key: str


class CheckoutResponse(BaseModel):
    success: bool
    url: Optional[str] = None
    detail: Optional[str] = None


class PriceResponse(BaseModel):
    success: bool
    price: float
    currency: str
    interval: str
    name: str


class HealthResponse(BaseModel):
    success: bool
    service: str
    provider: str
    status: str
    api_key_configured: bool
    variant_id_configured: bool


class SubscriptionResponse(BaseModel):
    success: bool
    subscription: Optional[dict] = None
    detail: Optional[str] = None


# Health Check
@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Check Lemon Squeezy payment service health"""
    return HealthResponse(
        success=True,
        service="payment",
        provider="lemon_squeezy",
        status="ok",
        api_key_configured=bool(LEMON_API_KEY),
        variant_id_configured=bool(LEMON_VARIANT_ID)
    )


# Get Premium Price
@router.get("/get-price", response_model=PriceResponse)
async def get_price():
    """Get Premium plan pricing information"""
    return PriceResponse(
        success=True,
        price=9.0,
        currency="USD",
        interval="month",
        name="Premium Plan"
    )


# Create Checkout Session
@router.post("/create-checkout", response_model=CheckoutResponse)
async def create_checkout(request: CheckoutRequest):
    """Create Lemon Squeezy checkout session for Premium upgrade"""
    
    if not all([LEMON_API_KEY, LEMON_STORE_ID, LEMON_VARIANT_ID]):
        raise HTTPException(
            status_code=500,
            detail="Lemon Squeezy configuration incomplete"
        )
    
    try:
        # Prepare checkout data
        checkout_data = {
            "data": {
                "type": "checkouts",
                "attributes": {
                    "checkout_data": {
                        "email": request.email,
                        "custom": {
                            "license_key": request.license_key
                        }
                    }
                },
                "relationships": {
                    "store": {
                        "data": {
                            "type": "stores",
                            "id": LEMON_STORE_ID
                        }
                    },
                    "variant": {  # ← Use Variant!
                        "data": {
                            "type": "variants",
                            "id": LEMON_VARIANT_ID
                        }
                    }
                }
            }
        }
        
        # Call Lemon Squeezy API
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{LEMON_API_URL}/checkouts",
                headers={
                    "Accept": "application/vnd.api+json",
                    "Content-Type": "application/vnd.api+json",
                    "Authorization": f"Bearer {LEMON_API_KEY}"
                },
                json=checkout_data,
                timeout=30.0
            )
            
            if response.status_code != 201:
                error_detail = response.json() if response.text else "Unknown error"
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Lemon Squeezy error: {error_detail}"
                )
            
            result = response.json()
            checkout_url = result["data"]["attributes"]["url"]
            
            return CheckoutResponse(
                success=True,
                url=checkout_url
            )
    
    except httpx.RequestError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Network error: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error creating checkout: {str(e)}"
        )


# Webhook Handler
@router.post("/webhook")
async def webhook_handler(
    request: Request,
    x_signature: Optional[str] = Header(None)
):
    """Handle Lemon Squeezy webhooks"""
    
    # Get raw body
    body = await request.body()
    
    # Verify signature if secret is configured
    if LEMON_WEBHOOK_SECRET and x_signature:
        expected_signature = hmac.new(
            LEMON_WEBHOOK_SECRET.encode(),
            body,
            hashlib.sha256
        ).hexdigest()
        
        if not hmac.compare_digest(expected_signature, x_signature):
            raise HTTPException(status_code=401, detail="Invalid signature")
    
    # Parse webhook data
    try:
        data = json.loads(body)
        event_name = data.get("meta", {}).get("event_name")
        
        # Handle different events
        if event_name == "order_created":
            await handle_order_created(data)
        elif event_name == "subscription_created":
            await handle_subscription_created(data)
        elif event_name == "subscription_updated":
            await handle_subscription_updated(data)
        elif event_name == "subscription_cancelled":
            await handle_subscription_cancelled(data)
        elif event_name == "subscription_payment_success":
            await handle_payment_success(data)
        elif event_name == "license_key_created":
            await handle_license_key_created(data)
        
        return {"success": True, "event": event_name}
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Webhook processing error: {str(e)}"
        )


# Webhook Event Handlers
async def handle_order_created(data: dict):
    """Handle order_created event"""
    print(f"Order created: {data}")


async def handle_subscription_created(data: dict):
    """Handle subscription_created event"""
    print(f"Subscription created: {data}")


async def handle_subscription_updated(data: dict):
    """Handle subscription_updated event"""
    print(f"Subscription updated: {data}")


async def handle_subscription_cancelled(data: dict):
    """Handle subscription_cancelled event"""
    print(f"Subscription cancelled: {data}")


async def handle_payment_success(data: dict):
    """Handle subscription_payment_success event"""
    print(f"Payment success: {data}")


async def handle_license_key_created(data: dict):
    """Handle license_key_created event"""
    print(f"License key created: {data}")


# Get User Subscriptions
@router.get("/subscriptions/{email}", response_model=SubscriptionResponse)
async def get_subscriptions(email: str):
    """Get user's subscription information"""
    
    if not LEMON_API_KEY:
        raise HTTPException(status_code=500, detail="Lemon Squeezy not configured")
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{LEMON_API_URL}/subscriptions",
                headers={
                    "Accept": "application/vnd.api+json",
                    "Authorization": f"Bearer {LEMON_API_KEY}"
                },
                params={"filter[user_email]": email},
                timeout=30.0
            )
            
            if response.status_code == 200:
                result = response.json()
                subscriptions = result.get("data", [])
                
                if subscriptions:
                    return SubscriptionResponse(
                        success=True,
                        subscription=subscriptions[0]
                    )
                else:
                    return SubscriptionResponse(
                        success=True,
                        subscription=None,
                        detail="No active subscription found"
                    )
            else:
                raise HTTPException(
                    status_code=response.status_code,
                    detail="Failed to fetch subscriptions"
                )
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching subscriptions: {str(e)}"
        )


# Cancel Subscription
@router.post("/cancel-subscription")
async def cancel_subscription(subscription_id: str):
    """Cancel a subscription"""
    
    if not LEMON_API_KEY:
        raise HTTPException(status_code=500, detail="Lemon Squeezy not configured")
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.delete(
                f"{LEMON_API_URL}/subscriptions/{subscription_id}",
                headers={
                    "Accept": "application/vnd.api+json",
                    "Authorization": f"Bearer {LEMON_API_KEY}"
                },
                timeout=30.0
            )
            
            if response.status_code in [200, 204]:
                return {"success": True, "detail": "Subscription cancelled"}
            else:
                raise HTTPException(
                    status_code=response.status_code,
                    detail="Failed to cancel subscription"
                )
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error cancelling subscription: {str(e)}"
        )