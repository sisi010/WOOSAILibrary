# -*- coding: utf-8 -*-
"""
WOOSAILibrary - AI Output Token Optimizer
Reduce AI API costs by optimizing input/output tokens

Main Features:
- Input compression (Korean idioms, numbers, patterns)
- Output optimization (prompt engineering, structured outputs)
- Cost reduction: Up to 78.5% savings
- Speed improvement: Up to 79% faster

Usage:
    from woosai import WoosAI
    
    # First time - auto license generation
    client = WoosAI()  # Will prompt for email, auto-generate free license
    
    # Optimize OpenAI API call
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": "Your question"}],
        strategy="starter"  # or "pro", "premium"
    )

Author: WoosAI Team
Version: 1.0.1
"""

import os
import json
import requests
from pathlib import Path
from typing import Optional, Dict, Any
from openai import OpenAI

# Import optimizers
# Import optimizers
from .core.lightweight_input import get_compressor
from .core.prompt_optimizer import get_prompt_optimizer

__version__ = "1.0.1"
__all__ = ['WoosAI', '__version__']


class LicenseManager:
    """
    Manage WoosAI license locally
    
    Features:
    - Auto-generate free license with email only
    - Save license to local config file (~/.woosai/config.json)
    - Auto-load license on next use
    - Verify license with backend API
    """
    
    CONFIG_DIR = Path.home() / '.woosai'
    CONFIG_FILE = CONFIG_DIR / 'config.json'
    API_BASE_URL = 'https://woosai-backend-production.up.railway.app/api'
    
    def __init__(self):
        """Initialize license manager"""
        self.config_dir = self.CONFIG_DIR
        self.config_file = self.CONFIG_FILE
        self.api_base_url = self.API_BASE_URL
        
        # Create config directory if not exists
        self.config_dir.mkdir(parents=True, exist_ok=True)
    
    def load_license(self) -> Optional[Dict[str, Any]]:
        """
        Load license from local config file
        
        Returns:
            dict: License data or None if not found
        """
        if not self.config_file.exists():
            return None
        
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
                return config.get('license')
        except Exception as e:
            print(f"Warning: Failed to load license: {e}")
            return None
    
    def save_license(self, license_data: Dict[str, Any]) -> bool:
        """
        Save license to local config file
        
        Args:
            license_data: License information to save
            
        Returns:
            bool: True if successful
        """
        try:
            config = {
                'license': license_data,
                'version': __version__
            }
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2)
            
            return True
        except Exception as e:
            print(f"Warning: Failed to save license: {e}")
            return False
    
    def request_free_license(self, email: str) -> Optional[Dict[str, Any]]:
        """
        Request free license from backend API
        
        Args:
            email: User email address
            
        Returns:
            dict: License data or None if failed
        """
        try:
            url = f"{self.api_base_url}/licenses/request-free"
            response = requests.post(
                url,
                json={'email': email},
                timeout=10
            )
            
            if response.status_code in [200, 201]:
                data = response.json()
                if data.get('success'):
                    return {
                        'license_key': data['license_key'],
                        'plan': data['plan'],
                        'expires_at': data['expires_at'],
                        'email': email
                    }
            else:
                error_msg = response.json().get('error', 'Unknown error')
                print(f"Error: {error_msg}")
                return None
        
        except requests.exceptions.RequestException as e:
            print(f"Network error: {e}")
            print("Please check your internet connection and try again.")
            return None
        except Exception as e:
            print(f"Error requesting license: {e}")
            return None
    
    def verify_license(self, license_key: str) -> bool:
        """
        Verify license with backend API
        
        Args:
            license_key: License key to verify
            
        Returns:
            bool: True if valid
        """
        try:
            url = f"{self.api_base_url}/licenses/verify"
            response = requests.post(
                url,
                json={'license_key': license_key},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get('valid', False)
            else:
                return False
        
        except Exception:
            # If verification fails, allow offline usage
            return True
    
    def get_or_create_license(self) -> Optional[Dict[str, Any]]:
        """
        Get existing license or create new one
        
        Returns:
            dict: License data or None if failed
        """
        # Try to load existing license
        license_data = self.load_license()
        
        if license_data:
            print(f"✓ Loaded license: {license_data['plan'].upper()}")
            return license_data
        
        # No license found - request email and generate
        print("\n" + "="*60)
        print("🎉 Welcome to WoosAI Library!")
        print("="*60)
        print("\nTo get started, we'll generate a FREE license for you.")
        print("This takes just a few seconds and requires only your email.\n")
        
        while True:
            email = input("📧 Enter your email: ").strip()
            
            if not email:
                print("❌ Email cannot be empty. Please try again.\n")
                continue
            
            if '@' not in email or '.' not in email:
                print("❌ Invalid email format. Please try again.\n")
                continue
            
            print("\n⏳ Generating free license...")
            license_data = self.request_free_license(email)
            
            if license_data:
                # Save license locally
                self.save_license(license_data)
                
                print("\n" + "="*60)
                print("✅ SUCCESS! Free license generated!")
                print("="*60)
                print(f"\n📋 License Key: {license_data['license_key']}")
                print(f"📅 Valid until: {license_data['expires_at'][:10]}")
                print(f"💳 Plan: {license_data['plan'].upper()}")
                print(f"\n💾 License saved to: {self.config_file}")
                print("\n🚀 You're all set! Starting WoosAI...\n")
                
                # Premium 안내 추가
                print("="*60)
                print("💎 Want MORE Savings?")
                print("="*60)
                print("\n📊 Your FREE Plan:")
                print("  ✓ STARTER strategy")
                print("  ✓ ~20% cost savings")
                print("  ✓ Perfect for getting started!\n")
                print("🌟 Upgrade to PREMIUM ($9/month):")
                print("  ⚡ PRO + PREMIUM strategies")
                print("  ⚡ Up to 88% cost savings")
                print("  ⚡ Priority support")
                print("  ⚡ ROI: 2,900% for app developers\n")
                print("🔗 Upgrade now: https://woos-ai.com/upgrade")
                print("="*60 + "\n")
                
                return license_data
            else:
                print("\n❌ Failed to generate license. Please try again.\n")
                retry = input("Try again? (y/n): ").strip().lower()
                if retry != 'y':
                    return None


class WoosAI:
    """
    WoosAI Client - Optimized OpenAI API Wrapper
    
    Features:
    - Auto license management (free tier)
    - Input compression
    - Output optimization
    - Cost reduction: Up to 78.5%
    - Speed improvement: Up to 79%
    
    Usage:
        from woosai import WoosAI
        
        client = WoosAI()  # Auto license generation
        
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": "Hello"}],
            strategy="starter"
        )
    """
    
    def __init__(self, api_key: Optional[str] = None, license_key: Optional[str] = None):
        """
        Initialize WoosAI client
        
        Args:
            api_key: OpenAI API key (if not provided, uses OPENAI_API_KEY env var)
            license_key: WoosAI license key (if not provided, auto-generates free license)
        """
        # Initialize license manager
        self.license_manager = LicenseManager()
        
        # Get or create license
        if license_key:
            self.license_data = {'license_key': license_key, 'plan': 'unknown'}
        else:
            self.license_data = self.license_manager.get_or_create_license()
            
            if not self.license_data:
                raise Exception("Failed to initialize license. Please try again.")
        
        # Initialize OpenAI client
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError(
                "OpenAI API key not found. Please provide it via:\n"
                "1. WoosAI(api_key='your-key')\n"
                "2. Environment variable: OPENAI_API_KEY"
            )
        
        self.client = OpenAI(api_key=self.api_key)
        
        # Initialize optimizers
        self.compressor = get_compressor()
        self.prompt_optimizer = get_prompt_optimizer()
        
        # Create chat completions wrapper
        self.chat = ChatCompletions(self)
    
    def get_plan(self) -> str:
        """Get current plan (free/premium)"""
        return self.license_data.get('plan', 'free')
    
    def upgrade_info(self):
        """Show upgrade information"""
        print("\n" + "="*60)
        print("🚀 Upgrade to Premium")
        print("="*60)
        print("\n📊 Free Plan Limitations:")
        print("  • Strategy: STARTER only")
        print("  • Savings: ~20%")
        print("  • Support: Community")
        print("\n✨ Premium Plan Benefits:")
        print("  • Strategy: PRO + PREMIUM")
        print("  • Savings: Up to 88%")
        print("  • Support: Priority")
        print("  • Price: $9.99/month")
        print("\n🔗 Upgrade now: https://woos-ai.com/upgrade")
        print("="*60 + "\n")


class ChatCompletions:
    """
    Chat completions wrapper with optimization
    """
    
    def __init__(self, woosai_client):
        """Initialize with WoosAI client"""
        self.woosai = woosai_client
        self.completions = self  # For compatibility with OpenAI SDK
    
    def create(self, 
               model: str,
               messages: list,
               strategy: str = "starter",
               optimize_input: bool = True,
               optimize_output: bool = True,
               **kwargs) -> Any:
        """
        Create chat completion with optimization
        
        Args:
            model: OpenAI model name (e.g., "gpt-4", "gpt-3.5-turbo")
            messages: Chat messages list
            strategy: Optimization strategy ("starter", "pro", "premium")
            optimize_input: Enable input compression
            optimize_output: Enable output optimization
            **kwargs: Additional OpenAI API parameters
            
        Returns:
            OpenAI ChatCompletion response
        """
        # Check plan restrictions
        plan = self.woosai.get_plan()
        
        if strategy in ["pro", "premium"] and plan == "free":
            print(f"\n⚠️  '{strategy}' strategy requires Premium plan.")
            print("    Using 'starter' strategy instead.\n")
            self.woosai.upgrade_info()
            strategy = "starter"
        
        # Optimize input
        if optimize_input:
            optimized_messages = []
            for msg in messages:
                if msg['role'] == 'user':
                    compressed_content, _ = self.woosai.compressor.compress(
                        msg['content'],
                        strategy=strategy
                    )
                    optimized_messages.append({
                        'role': msg['role'],
                        'content': compressed_content
                    })
                else:
                    optimized_messages.append(msg)
        else:
            optimized_messages = messages
        
        # Optimize output
        if optimize_output:
            # Add system prompt for output optimization
            system_prompt = self.woosai.prompt_optimizer.get_system_prompt(
                strategy=strategy
            )
            
            # Insert system message at beginning
            optimized_messages.insert(0, {
                'role': 'system',
                'content': system_prompt
            })
            
            # Set max_tokens if not provided
            if 'max_tokens' not in kwargs:
                kwargs['max_tokens'] = self.woosai.prompt_optimizer.get_max_tokens(strategy)
            
            # Set temperature if not provided
            if 'temperature' not in kwargs:
                kwargs['temperature'] = self.woosai.prompt_optimizer.get_temperature(strategy)
        
        # Call OpenAI API
        response = self.woosai.client.chat.completions.create(
            model=model,
            messages=optimized_messages,
            **kwargs
        )
        
        return response


# Module-level convenience function
def create_client(api_key: Optional[str] = None, license_key: Optional[str] = None) -> WoosAI:
    """
    Create WoosAI client (convenience function)
    
    Args:
        api_key: OpenAI API key
        license_key: WoosAI license key
        
    Returns:
        WoosAI client instance
    """
    return WoosAI(api_key=api_key, license_key=license_key)