"""
Lemon Squeezy Payment Router with Webhook & MongoDB Integration
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
from datetime import datetime, timedelta
from motor.motor_asyncio import AsyncIOMotorClient

router = APIRouter(tags=["payment"])
# Lemon Squeezy Configuration
LEMON_API_KEY = os.getenv("LEMON_API_KEY")
LEMON_STORE_ID = os.getenv("LEMON_STORE_ID")
LEMON_VARIANT_ID = os.getenv("LEMON_VARIANT_ID")
LEMON_WEBHOOK_SECRET = os.getenv("LEMON_WEBHOOK_SECRET")
LEMON_API_URL = "https://api.lemonsqueezy.com/v1"

# MongoDB Configuration
MONGODB_URL = os.getenv("MONGODB_URL")
DATABASE_NAME = os.getenv("DATABASE_NAME", "woosai")

# MongoDB Client
mongo_client = None
db = None


# Initialize MongoDB
async def get_database():
    """Get MongoDB database instance"""
    global mongo_client, db
    if db is None:
        mongo_client = AsyncIOMotorClient(MONGODB_URL)
        db = mongo_client[DATABASE_NAME]
    return db


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
    mongodb_connected: bool


class SubscriptionResponse(BaseModel):
    success: bool
    subscription: Optional[dict] = None
    detail: Optional[str] = None


# Health Check
@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Check Lemon Squeezy payment service health"""
    
    # Check MongoDB connection
    mongodb_connected = False
    try:
        database = await get_database()
        await database.command("ping")
        mongodb_connected = True
    except Exception as e:
        print(f"MongoDB connection error: {e}")
    
    return HealthResponse(
        success=True,
        service="payment",
        provider="lemon_squeezy",
        status="ok",
        api_key_configured=bool(LEMON_API_KEY),
        variant_id_configured=bool(LEMON_VARIANT_ID),
        mongodb_connected=mongodb_connected
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
                            "license_key": request.license_key,
                            "user_email": request.email
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
                    "variant": {
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
            print("❌ Invalid webhook signature")
            raise HTTPException(status_code=401, detail="Invalid signature")
    
    # Parse webhook data
    try:
        data = json.loads(body)
        event_name = data.get("meta", {}).get("event_name")
        
        # FIXED: Only log event name, not full data
        print(f"✅ Webhook: {event_name}")
        
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
        else:
            print(f"⚠️ Unhandled event: {event_name}")
        
        return {"success": True}
    
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON")
    except Exception as e:
        print(f"❌ Webhook error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


async def handle_order_created(data: dict):
    """Handle order_created event"""
    try:
        attributes = data.get("data", {}).get("attributes", {})
        
        # Try multiple possible field names for order_id
        order_id = (attributes.get("order_id") or 
                   attributes.get("id") or
                   data.get("data", {}).get("id"))
        
        email = (attributes.get("user_email") or 
                attributes.get("customer_email") or
                attributes.get("email"))
        
        # FIXED: Only log essential info
        print(f"✅ Order created: {order_id} - {email}")
        
        # Get MongoDB
        database = await get_database()
        orders_collection = database["orders"]
        
        # Save order
        order_doc = {
            "order_id": str(order_id),
            "email": email,
            "status": attributes.get("status", "pending"),
            "total": attributes.get("total", 0),
            "currency": attributes.get("currency", "USD"),
            "created_at": datetime.utcnow(),
            "lemon_data": attributes
        }
        
        await orders_collection.insert_one(order_doc)
        print(f"💾 Order saved: {order_id}")
        
    except Exception as e:
        print(f"❌ Error handling order_created: {str(e)}")


async def handle_subscription_created(data: dict):
    """Handle subscription_created event"""
    try:
        attributes = data.get("data", {}).get("attributes", {})
        
        # Try multiple possible field names
        subscription_id = (attributes.get("subscription_id") or 
                          attributes.get("id") or
                          data.get("data", {}).get("id"))
        
        email = (attributes.get("user_email") or 
                attributes.get("customer_email") or
                attributes.get("email"))
        
        # FIXED: Only log essential info
        print(f"✅ Subscription created: {subscription_id} - {email}")
        
        # Get MongoDB
        database = await get_database()
        subscriptions_collection = database["subscriptions"]
        users_collection = database["users"]
        
        # Save subscription
        subscription_doc = {
            "subscription_id": str(subscription_id),
            "email": email,
            "status": attributes.get("status", "active"),
            "product_id": attributes.get("product_id"),
            "variant_id": attributes.get("variant_id"),
            "created_at": datetime.utcnow(),
            "renews_at": attributes.get("renews_at"),
            "ends_at": attributes.get("ends_at"),
            "trial_ends_at": attributes.get("trial_ends_at"),
            "lemon_data": attributes
        }
        
        await subscriptions_collection.insert_one(subscription_doc)
        
        # Update user
        await users_collection.update_one(
            {"email": email},
            {
                "$set": {
                    "plan": "premium",
                    "subscription_id": str(subscription_id),
                    "subscription_status": "active",
                    "upgraded_at": datetime.utcnow()
                }
            },
            upsert=True
        )
        
        print(f"💾 Subscription saved: {subscription_id}")
        
    except Exception as e:
        print(f"❌ Error handling subscription_created: {str(e)}")


async def handle_subscription_updated(data: dict):
    """Handle subscription_updated event"""
    try:
        attributes = data.get("data", {}).get("attributes", {})
        
        # Try multiple possible field names
        subscription_id = (attributes.get("subscription_id") or 
                          attributes.get("id") or
                          data.get("data", {}).get("id"))
        
        status = attributes.get("status", "unknown")
        
        print(f"✅ Subscription updated: {subscription_id} - {status}")
        
        # Get MongoDB
        database = await get_database()
        subscriptions_collection = database["subscriptions"]
        users_collection = database["users"]
        
        # Update subscription
        await subscriptions_collection.update_one(
            {"subscription_id": str(subscription_id)},
            {
                "$set": {
                    "status": status,
                    "renews_at": attributes.get("renews_at"),
                    "ends_at": attributes.get("ends_at"),
                    "updated_at": datetime.utcnow(),
                    "lemon_data": attributes
                }
            }
        )
        
        # Update user status
        subscription = await subscriptions_collection.find_one(
            {"subscription_id": str(subscription_id)}
        )
        
        if subscription:
            email = subscription.get("email")
            await users_collection.update_one(
                {"email": email},
                {"$set": {"subscription_status": status}}
            )
        
        print(f"💾 Subscription updated: {subscription_id}")
        
    except Exception as e:
        print(f"❌ Error handling subscription_updated: {str(e)}")


async def handle_subscription_cancelled(data: dict):
    """Handle subscription_cancelled event"""
    try:
        attributes = data.get("data", {}).get("attributes", {})
        
        # Try multiple possible field names
        subscription_id = (attributes.get("subscription_id") or 
                          attributes.get("id") or
                          data.get("data", {}).get("id"))
        
        print(f"✅ Subscription cancelled: {subscription_id}")
        
        # Get MongoDB
        database = await get_database()
        subscriptions_collection = database["subscriptions"]
        users_collection = database["users"]
        
        # Update subscription status
        await subscriptions_collection.update_one(
            {"subscription_id": str(subscription_id)},
            {
                "$set": {
                    "status": "cancelled",
                    "cancelled_at": datetime.utcnow()
                }
            }
        )
        
        # Downgrade user to Free
        subscription = await subscriptions_collection.find_one(
            {"subscription_id": subscription_id}
        )
        
        if subscription:
            email = subscription.get("email")
            await users_collection.update_one(
                {"email": email},
                {
                    "$set": {
                        "plan": "free",
                        "subscription_status": "cancelled",
                        "downgraded_at": datetime.utcnow()
                    }
                }
            )
            
            print(f"💾 User downgraded to Free: {email}")
        
    except Exception as e:
        print(f"❌ Error handling subscription_cancelled: {str(e)}")


async def handle_payment_success(data: dict):
    """Handle subscription_payment_success event"""
    try:
        # FIXED: Removed full data logging
        attributes = data.get("data", {}).get("attributes", {})
        
        # Try multiple possible field names
        subscription_id = (attributes.get("subscription_id") or 
                          attributes.get("id") or
                          data.get("data", {}).get("id"))
        
        print(f"✅ Payment success: {subscription_id}")
        
        # Get MongoDB
        database = await get_database()
        subscriptions_collection = database["subscriptions"]
        users_collection = database["users"]
        
        # Extend subscription period
        subscription = await subscriptions_collection.find_one(
            {"subscription_id": subscription_id}
        )
        
        if subscription:
            email = subscription.get("email")
            
            # Update next billing date (add 30 days)
            await subscriptions_collection.update_one(
                {"subscription_id": subscription_id},
                {
                    "$set": {
                        "last_payment": datetime.utcnow(),
                        "next_billing": datetime.utcnow() + timedelta(days=30),
                        "status": "active"
                    }
                }
            )
            
            # Ensure user is still Premium
            await users_collection.update_one(
                {"email": email},
                {
                    "$set": {
                        "plan": "premium",
                        "subscription_status": "active",
                        "last_payment": datetime.utcnow()
                    }
                }
            )
            
            print(f"💾 Subscription renewed: {subscription_id}")
        
    except Exception as e:
        print(f"❌ Error handling payment_success: {str(e)}")


async def handle_license_key_created(data: dict):
    """Handle license_key_created event"""
    try:
        # FIXED: Removed full data logging
        attributes = data.get("data", {}).get("attributes", {})
        
        # Try multiple possible field names
        license_key = (attributes.get("key") or 
                      attributes.get("license_key"))
        
        email = (attributes.get("customer_email") or 
                attributes.get("user_email") or
                attributes.get("email"))
        
        # Get order_id to find email if not in license data
        order_id = attributes.get("order_id")
        
        print(f"✅ License created: {license_key[:8]}... - {email}")
        
        # Get MongoDB
        database = await get_database()
        licenses_collection = database["licenses"]
        users_collection = database["users"]
        
        # If email is None, try to find it from order_id
        if not email and order_id:
            orders_collection = database["orders"]
            order = await orders_collection.find_one({"order_id": str(order_id)})
            if order:
                email = order.get("email")
                print(f"📧 Found email from order: {email}")
        
        # Save license key
        license_doc = {
            "license_key": license_key,
            "email": email,
            "status": "active",
            "activation_limit": attributes.get("activation_limit", 5),
            "activations_count": 0,
            "created_at": datetime.utcnow(),
            "lemon_data": attributes
        }
        
        await licenses_collection.insert_one(license_doc)
        
        # Update user with license key
        await users_collection.update_one(
            {"email": email},
            {
                "$set": {
                    "license_key": license_key,
                    "license_status": "active"
                }
            },
            upsert=True
        )
        
        print(f"💾 License saved: {license_key[:8]}...")
        
    except Exception as e:
        print(f"❌ Error handling license_key_created: {str(e)}")


# Get User Subscriptions
@router.get("/subscriptions/{email}", response_model=SubscriptionResponse)
async def get_subscriptions(email: str):
    """Get user's subscription information"""
    
    try:
        # Check MongoDB first
        database = await get_database()
        subscriptions_collection = database["subscriptions"]
        
        subscription = await subscriptions_collection.find_one(
            {"email": email, "status": {"$in": ["active", "on_trial", "past_due"]}}
        )
        
        if subscription:
            # Remove MongoDB _id
            subscription.pop("_id", None)
            return SubscriptionResponse(
                success=True,
                subscription=subscription
            )
        
        # If not in MongoDB, check Lemon Squeezy API
        if not LEMON_API_KEY:
            raise HTTPException(status_code=500, detail="Lemon Squeezy not configured")
        
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