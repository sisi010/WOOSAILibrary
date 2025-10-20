# storage/cloud_storage.py

import requests
from typing import Optional, Dict, Any


class CloudStorage:
    """
    WoosAI Cloud Storage
    Stores user profiles in MongoDB Atlas via WoosAI Cloud API
    """
    
    def __init__(self, api_key: str, base_url: str = "http://localhost:8000/v1"):
        """Initialize CloudStorage"""
        if not api_key:
            raise ValueError("API key is required")
        if not api_key.startswith("woosai_"):
            raise ValueError("Invalid API key format")
        
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        
        print(f"CloudStorage initialized")
        print(f"API: {self.base_url}")
    
    def _get_headers(self):
        """Get HTTP headers with authentication"""
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    def save_profile(self, user_id: str, profile_data: dict):
        """Save user profile to cloud"""
        url = f"{self.base_url}/profiles/{user_id}"
        response = requests.put(
            url,
            headers=self._get_headers(),
            json={"data": profile_data},
            timeout=10
        )
        response.raise_for_status()
    
    def load_profile(self, user_id: str):
        """Load user profile from cloud"""
        url = f"{self.base_url}/profiles/{user_id}"
        response = requests.get(
            url,
            headers=self._get_headers(),
            timeout=10
        )
        if response.status_code == 404:
            return None
        response.raise_for_status()
        return response.json()
    
    def delete_profile(self, user_id: str):
        """Delete user profile from cloud"""
        url = f"{self.base_url}/profiles/{user_id}"
        response = requests.delete(
            url,
            headers=self._get_headers(),
            timeout=10
        )
        response.raise_for_status()