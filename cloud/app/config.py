"""
Database Configuration
MongoDB connection setup - Flask Context Version
"""

from app.database import get_collection

def get_users_collection():
    """Get users collection"""
    return get_collection('users')

def get_licenses_collection():
    """Get licenses collection"""
    return get_collection('licenses')

def get_payments_collection():
    """Get payments collection"""
    return get_collection('payments')

def get_api_keys_collection():
    """Get API keys collection"""
    return get_collection('api_keys')