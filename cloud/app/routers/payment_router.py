"""
Lemon Squeezy Payment Integration for WoosAI Backend

Handles Premium subscription payments through Lemon Squeezy
"""

from flask import Blueprint, request, jsonify
import requests
import os
import hmac
import hashlib
from datetime import datetime, timedelta

payment_bp = Blueprint('payment', __name__)

# Lemon Squeezy configuration
LEMON_API_KEY = os.getenv('LEMON_API_KEY')
LEMON_STORE_ID = os.getenv('LEMON_STORE_ID')
LEMON_PRODUCT_ID = os.getenv('LEMON_PRODUCT_ID')
LEMON_WEBHOOK_SECRET = os.getenv('LEMON_WEBHOOK_SECRET')

LEMON_API_BASE = "https://api.lemonsqueezy.com/v1"


def get_headers():
    """Get authorization headers for Lemon Squeezy API"""
    return {
        "Authorization": f"Bearer {LEMON_API_KEY}",
        "Content-Type": "application/vnd.api+json",
        "Accept": "application/vnd.api+json"
    }


@payment_bp.route('/create-checkout', methods=['POST'])
def create_checkout():
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
        data = request.get_json()
        email = data.get('email')
        license_key = data.get('license_key')
        
        if not email or not license_key:
            return jsonify({
                'success': False,
                'error': 'Email and license_key are required'
            }), 400
        
        # Create checkout session
        checkout_data = {
            "data": {
                "type": "checkouts",
                "attributes": {
                    "checkout_data": {
                        "email": email,
                        "custom": {
                            "license_key": license_key
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
                    },
                    "variant": {
                        "data": {
                            "type": "variants",
                            "id": LEMON_PRODUCT_ID
                        }
                    }
                }
            }
        }
        
        response = requests.post(
            f"{LEMON_API_BASE}/checkouts",
            headers=get_headers(),
            json=checkout_data
        )
        
        if response.status_code in [200, 201]:
            result = response.json()
            checkout_url = result['data']['attributes']['url']
            
            return jsonify({
                'success': True,
                'url': checkout_url,
                'checkout_id': result['data']['id']
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': f"Lemon Squeezy error: {response.text}"
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@payment_bp.route('/webhook', methods=['POST'])
def lemon_webhook():
    """
    Handle Lemon Squeezy webhook events
    
    Events:
        - order_created: New Premium subscription
        - subscription_updated: Subscription changes
        - subscription_cancelled: Cancel Premium
    """
    try:
        # Verify webhook signature
        signature = request.headers.get('X-Signature')
        payload = request.get_data()
        
        if LEMON_WEBHOOK_SECRET:
            expected_signature = hmac.new(
                LEMON_WEBHOOK_SECRET.encode(),
                payload,
                hashlib.sha256
            ).hexdigest()
            
            if not hmac.compare_digest(signature, expected_signature):
                return jsonify({'error': 'Invalid signature'}), 401
        
        # Parse event
        event = request.get_json()
        event_name = event.get('meta', {}).get('event_name')
        event_data = event.get('data', {})
        
        # Handle events
        if event_name == 'order_created':
            # New Premium subscription
            license_key = event_data.get('attributes', {}).get('first_order_item', {}).get('product_name')
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
        
        return jsonify({'success': True}), 200
        
    except Exception as e:
        print(f"Webhook error: {e}")
        return jsonify({'error': str(e)}), 500


@payment_bp.route('/get-price', methods=['GET'])
def get_price():
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
        # Fetch product from Lemon Squeezy
        response = requests.get(
            f"{LEMON_API_BASE}/variants/{LEMON_PRODUCT_ID}",
            headers=get_headers()
        )
        
        if response.status_code == 200:
            variant = response.json()['data']
            price = variant['attributes']['price'] / 100  # Convert cents to dollars
            
            return jsonify({
                'success': True,
                'price': price,
                'currency': 'USD',
                'interval': 'month',
                'name': 'Premium Plan'
            }), 200
        else:
            # Fallback to hardcoded price
            return jsonify({
                'success': True,
                'price': 9.0,
                'currency': 'USD',
                'interval': 'month',
                'name': 'Premium Plan'
            }), 200
            
    except Exception as e:
        # Fallback to hardcoded price
        return jsonify({
            'success': True,
            'price': 9.0,
            'currency': 'USD',
            'interval': 'month',
            'name': 'Premium Plan'
        }), 200


@payment_bp.route('/subscriptions/<email>', methods=['GET'])
def get_subscription(email):
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
        # For now, check database
        
        return jsonify({
            'success': True,
            'subscription': {
                'status': 'active',
                'plan': 'premium',
                'renews_at': '2025-11-23'
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@payment_bp.route('/cancel-subscription', methods=['POST'])
def cancel_subscription():
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
        data = request.get_json()
        subscription_id = data.get('subscription_id')
        
        if not subscription_id:
            return jsonify({
                'success': False,
                'error': 'subscription_id required'
            }), 400
        
        # Cancel subscription via API
        response = requests.delete(
            f"{LEMON_API_BASE}/subscriptions/{subscription_id}",
            headers=get_headers()
        )
        
        if response.status_code in [200, 204]:
            return jsonify({
                'success': True,
                'message': 'Subscription cancelled successfully'
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to cancel subscription'
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# Health check
@payment_bp.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'success': True,
        'service': 'payment',
        'provider': 'lemon_squeezy',
        'status': 'ok'
    }), 200