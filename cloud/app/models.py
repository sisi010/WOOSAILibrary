"""
Database Models
Data structures for MongoDB collections
"""

from datetime import datetime, timedelta
import bcrypt
import secrets

class User:
    """User model"""
    
    @staticmethod
    def create(email, password, name=None):
        """Create new user"""
        # Hash password
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        
        user_data = {
            'email': email,
            'password': hashed_password,
            'name': name,
            'plan': 'free',  # free or premium
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }
        
        return user_data
    
    @staticmethod
    def verify_password(stored_password, provided_password):
        """Verify password"""
        return bcrypt.checkpw(provided_password.encode('utf-8'), stored_password)


class License:
    """License model"""
    
    @staticmethod
    def create(user_id, plan, duration_days=30):
        """Create new license"""
        import hashlib
        
        # Generate license key
        # Format: WOOSAI-PLAN-YYYYMMDD-HASH
        expiry_date = datetime.utcnow() + timedelta(days=duration_days)
        expiry_str = expiry_date.strftime('%Y%m%d')
        
        # Create signature
        secret_key = "WOOSAI_SECRET_2025_V1"
        signature_base = f"{plan}:{expiry_str}:{secret_key}"
        signature = hashlib.sha256(signature_base.encode()).hexdigest()[:6]
        
        license_key = f"WOOSAI-{plan.upper()}-{expiry_str}-{signature}"
        
        license_data = {
            'license_key': license_key,
            'user_id': user_id,
            'plan': plan,  # free, premium
            'status': 'active',  # active, expired, revoked
            'created_at': datetime.utcnow(),
            'expires_at': expiry_date,
            'updated_at': datetime.utcnow()
        }
        
        return license_data
    
    @staticmethod
    def verify(license_key):
        """Verify license key format and signature"""
        import hashlib
        
        try:
            parts = license_key.split('-')
            if len(parts) != 4 or parts[0] != 'WOOSAI':
                return False, "Invalid license format"
            
            plan = parts[1]
            expiry_str = parts[2]
            signature = parts[3]
            
            # Check expiry
            expiry_date = datetime.strptime(expiry_str, '%Y%m%d')
            if expiry_date < datetime.utcnow():
                return False, "License expired"
            
            # Verify signature
            secret_key = "WOOSAI_SECRET_2025_V1"
            signature_base = f"{plan}:{expiry_str}:{secret_key}"
            expected_signature = hashlib.sha256(signature_base.encode()).hexdigest()[:6]
            
            if signature != expected_signature:
                return False, "Invalid signature"
            
            return True, "Valid license"
        
        except Exception as e:
            return False, f"Verification error: {str(e)}"


class Payment:
    """Payment model"""
    
    @staticmethod
    def create(user_id, amount, plan, stripe_payment_id=None):
        """Create payment record"""
        payment_data = {
            'user_id': user_id,
            'amount': amount,
            'plan': plan,
            'status': 'pending',  # pending, completed, failed
            'stripe_payment_id': stripe_payment_id,
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }
        
        return payment_data


class APIKey:
    """API Key model"""
    
    @staticmethod
    def create(user_id):
        """Create new API key"""
        # Generate random API key
        api_key = f"wai_{secrets.token_urlsafe(32)}"
        
        api_key_data = {
            'api_key': api_key,
            'user_id': user_id,
            'status': 'active',  # active, revoked
            'usage_count': 0,
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }
        
        return api_key_data