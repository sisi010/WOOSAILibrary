"""
Payment Router
Handles Stripe payment processing
"""

from flask import Blueprint, request, jsonify
import stripe
import os
from app.config import get_payments_collection, get_licenses_collection, get_users_collection
from app.models import Payment, License
from app.auth import token_required
from bson.objectid import ObjectId

payment_bp = Blueprint('payment', __name__)

# Configure Stripe
stripe.api_key = os.getenv('STRIPE_SECRET_KEY')

# Pricing (in cents)
PLANS = {
    'free': {'price': 0, 'name': 'Free Plan', 'duration_days': 365},
    'premium': {'price': 2900, 'name': 'Premium Plan', 'duration_days': 30}  # $29.00
}

@payment_bp.route('/create-checkout-session', methods=['POST'])
@token_required
def create_checkout_session(current_user):
    """Create Stripe checkout session"""
    try:
        data = request.get_json()
        plan = data.get('plan', 'premium')
        
        if plan not in PLANS:
            return jsonify({'error': 'Invalid plan'}), 400
        
        plan_info = PLANS[plan]
        
        if plan_info['price'] == 0:
            return jsonify({'error': 'Free plan does not require payment'}), 400
        
        # Create Stripe checkout session
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'product_data': {
                        'name': plan_info['name'],
                        'description': f'WoosAI {plan} plan - {plan_info["duration_days"]} days'
                    },
                    'unit_amount': plan_info['price'],
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=f'http://woos-ai.com/pricing.html?session_id={{CHECKOUT_SESSION_ID}}',
            cancel_url='http://woos-ai.com/pricing.html',
            metadata={
                'user_id': current_user['user_id'],
                'plan': plan
            }
        )
        
        # Save payment record
        payment_data = Payment.create(
            user_id=current_user['user_id'],
            amount=plan_info['price'] / 100,  # Convert to dollars
            plan=plan,
            stripe_payment_id=session.id
        )
        
        payments_collection = get_payments_collection()
        payments_collection.insert_one(payment_data)
        
        return jsonify({
            'session_id': session.id,
            'url': session.url
        }), 200
    
    except Exception as e:
        return jsonify({'error': f'Failed to create checkout session: {str(e)}'}), 500


@payment_bp.route('/webhook', methods=['POST'])
def stripe_webhook():
    """Handle Stripe webhook events"""
    payload = request.get_data()
    sig_header = request.headers.get('Stripe-Signature')
    
    # Note: In production, verify webhook signature
    # endpoint_secret = os.getenv('STRIPE_WEBHOOK_SECRET')
    
    try:
        event = stripe.Event.construct_from(
            request.get_json(), stripe.api_key
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 400
    
    # Handle the checkout.session.completed event
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        
        # Get user and plan from metadata
        user_id = session['metadata']['user_id']
        plan = session['metadata']['plan']
        
        # Update payment status
        payments_collection = get_payments_collection()
        payments_collection.update_one(
            {'stripe_payment_id': session['id']},
            {'$set': {'status': 'completed'}}
        )
        
        # Generate license
        plan_info = PLANS[plan]
        license_data = License.create(user_id, plan, plan_info['duration_days'])
        
        licenses_collection = get_licenses_collection()
        licenses_collection.insert_one(license_data)
        
        # Update user plan
        users_collection = get_users_collection()
        users_collection.update_one(
            {'_id': ObjectId(user_id)},
            {'$set': {'plan': plan}}
        )
    
    return jsonify({'status': 'success'}), 200


@payment_bp.route('/verify-session', methods=['POST'])
@token_required
def verify_session(current_user):
    """Verify payment session and generate license"""
    try:
        data = request.get_json()
        session_id = data.get('session_id')
        
        if not session_id:
            return jsonify({'error': 'Session ID is required'}), 400
        
        # Retrieve session from Stripe
        session = stripe.checkout.Session.retrieve(session_id)
        
        if session.payment_status != 'paid':
            return jsonify({'error': 'Payment not completed'}), 400
        
        # Check if license already generated
        licenses_collection = get_licenses_collection()
        existing_license = licenses_collection.find_one({
            'user_id': current_user['user_id'],
            'stripe_session_id': session_id
        })
        
        if existing_license:
            return jsonify({
                'message': 'License already generated',
                'license_key': existing_license['license_key']
            }), 200
        
        # Generate license
        plan = session.metadata.get('plan', 'premium')
        plan_info = PLANS[plan]
        license_data = License.create(
            current_user['user_id'],
            plan,
            plan_info['duration_days']
        )
        license_data['stripe_session_id'] = session_id
        
        result = licenses_collection.insert_one(license_data)
        
        # Update user plan
        users_collection = get_users_collection()
        users_collection.update_one(
            {'_id': ObjectId(current_user['user_id'])},
            {'$set': {'plan': plan}}
        )
        
        return jsonify({
            'message': 'License generated successfully',
            'license_key': license_data['license_key'],
            'plan': plan,
            'expires_at': license_data['expires_at'].isoformat()
        }), 200
    
    except Exception as e:
        return jsonify({'error': f'Verification failed: {str(e)}'}), 500


@payment_bp.route('/my-payments', methods=['GET'])
@token_required
def get_my_payments(current_user):
    """Get payment history for current user"""
    try:
        payments_collection = get_payments_collection()
        payments = list(payments_collection.find({'user_id': current_user['user_id']}))
        
        payment_list = []
        for payment in payments:
            payment_list.append({
                'id': str(payment['_id']),
                'amount': payment['amount'],
                'plan': payment['plan'],
                'status': payment['status'],
                'created_at': payment['created_at'].isoformat()
            })
        
        return jsonify({
            'payments': payment_list,
            'count': len(payment_list)
        }), 200
    
    except Exception as e:
        return jsonify({'error': f'Failed to get payments: {str(e)}'}), 500