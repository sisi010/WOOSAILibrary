# -*- coding: utf-8 -*-
"""
WOOSAILibrary - AI Output Token Optimizer
Version: 1.1.0

Features:
- Input/Output optimization
- Advanced caching with LRU
- Usage statistics tracking
- Up to 88% cost savings
"""

import os
import json
import requests
import tiktoken
from pathlib import Path
from typing import Optional, Dict, Any
from openai import OpenAI

# Import core modules
from .core.lightweight_input import get_compressor
from .core.prompt_optimizer import get_prompt_optimizer
from .core.stats_tracker import StatsTracker
from .core.cache_manager import CacheManager

__version__ = "1.1.0"
__all__ = ['WoosAI', '__version__']


class LicenseManager:
    """Manage WoosAI license locally"""
    
    CONFIG_DIR = Path.home() / '.woosai'
    CONFIG_FILE = CONFIG_DIR / 'config.json'
    API_BASE_URL = 'https://woosai-backend-production.up.railway.app/api'
    
    def __init__(self):
        self.config_dir = self.CONFIG_DIR
        self.config_file = self.CONFIG_FILE
        self.api_base_url = self.API_BASE_URL
        self.config_dir.mkdir(parents=True, exist_ok=True)
    
    def load_license(self) -> Optional[Dict[str, Any]]:
        """Load license from file"""
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
        """Save license to file"""
        try:
            config = {'license': license_data, 'version': __version__}
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2)
            return True
        except Exception as e:
            print(f"Warning: Failed to save license: {e}")
            return False
    
    def request_free_license(self, email: str) -> Optional[Dict[str, Any]]:
        """Request free license from API"""
        try:
            url = f"{self.api_base_url}/licenses/request-free"
            response = requests.post(url, json={'email': email}, timeout=10)
            
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
        except Exception as e:
            print(f"Error requesting license: {e}")
            return None
    
    def get_or_create_license(self) -> Optional[Dict[str, Any]]:
        """Get existing license or create new one"""
        license_data = self.load_license()
        
        if license_data:
            print(f"✓ Loaded license: {license_data['plan'].upper()}")
            return license_data
        
        print("\n" + "="*60)
        print("🎉 Welcome to WoosAI Library!")
        print("="*60)
        print("\nGenerating FREE license...\n")
        
        while True:
            email = input("📧 Enter your email: ").strip()
            
            if not email or '@' not in email:
                print("❌ Invalid email. Try again.\n")
                continue
            
            print("\n⏳ Generating license...")
            license_data = self.request_free_license(email)
            
            if license_data:
                self.save_license(license_data)
                print("\n✅ SUCCESS! License generated!")
                print(f"📋 Key: {license_data['license_key']}")
                print(f"💾 Saved to: {self.config_file}\n")
                return license_data
            else:
                retry = input("Try again? (y/n): ").strip().lower()
                if retry != 'y':
                    return None


class WoosAI:
    """
    WoosAI - AI Cost Optimization Library
    
    Usage:
        client = WoosAI(cache=True)
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": "Hello"}]
        )
    """
    
    def __init__(self, 
                 api_key: Optional[str] = None, 
                 license_key: Optional[str] = None,
                 cache: bool = False,
                 cache_ttl: int = 24,
                 max_cache_size: int = 1000,
                 auto_cleanup_interval: int = 100):
        """
        Initialize WoosAI
        
        Args:
            api_key: OpenAI API key
            license_key: WoosAI license key
            cache: Enable caching (default: False)
            cache_ttl: Cache TTL in hours (default: 24)
            max_cache_size: Max cache entries (default: 1000)
            auto_cleanup_interval: Auto cleanup interval (default: 100)
        """
        # License
        self.license_manager = LicenseManager()
        if license_key:
            self.license_data = {'license_key': license_key, 'plan': 'unknown'}
        else:
            self.license_data = self.license_manager.get_or_create_license()
            if not self.license_data:
                raise Exception("Failed to initialize license")
        
        # OpenAI
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError("OpenAI API key not found")
        self.client = OpenAI(api_key=self.api_key)
        
        # Optimizers
        self.compressor = get_compressor()
        self.prompt_optimizer = get_prompt_optimizer()
        
        # Stats
        self.stats_tracker = StatsTracker()
        
        # Cache
        self.cache_enabled = cache
        self.cache_manager = None
        if cache:
            self.cache_manager = CacheManager(
                ttl_hours=cache_ttl,
                max_size=max_cache_size,
                auto_cleanup_interval=auto_cleanup_interval
            )
        
        # Chat wrapper
        self.chat = ChatCompletions(self)
        
        cache_status = "ENABLED" if cache else "DISABLED"
        print(f"✓ WoosAI v{__version__} initialized (Cache: {cache_status})")
    
    def get_plan(self) -> str:
        """Get current plan"""
        return self.license_data.get('plan', 'free')
    
    # Stats methods
    def get_today_stats(self):
        """Get today's stats"""
        return self.stats_tracker.get_today_stats()
    
    def get_monthly_stats(self):
        """Get monthly stats"""
        return self.stats_tracker.get_monthly_stats()
    
    def get_total_stats(self):
        """Get total stats"""
        return self.stats_tracker.get_total_stats()
    
    def display_stats(self):
        """Display stats"""
        self.stats_tracker.display_stats()
    
    # Cache methods
    def get_cache_info(self):
        """Get cache info"""
        if not self.cache_enabled:
            print("⚠️  Cache disabled")
            return None
        return self.cache_manager.get_cache_info()
    
    def get_cache_stats(self):
        """Get cache stats"""
        if not self.cache_enabled:
            print("⚠️  Cache disabled")
            return None
        return self.cache_manager.get_stats()
    
    def display_cache_stats(self):
        """Display cache stats"""
        if not self.cache_enabled:
            print("⚠️  Cache disabled")
            return
        self.cache_manager.display_stats()
    
    def clear_cache(self):
        """Clear all cache"""
        if self.cache_enabled:
            self.cache_manager.clear()
    
    def clear_cache_by_pattern(self, pattern: str):
        """Clear cache by pattern"""
        if self.cache_enabled:
            return self.cache_manager.clear_by_pattern(pattern)
    
    def clear_expired_cache(self):
        """Clear expired cache"""
        if self.cache_enabled:
            return self.cache_manager.clear_expired()
    
    def clear_old_cache(self, days: int = 7):
        """Clear old cache"""
        if self.cache_enabled:
            return self.cache_manager.clear_old_entries(days)


class ChatCompletions:
    """Chat completions wrapper"""
    
    def __init__(self, woosai_client):
        self.woosai = woosai_client
        self.completions = self
    
    def create(self, 
               model: str,
               messages: list,
               optimize_input: bool = True,
               optimize_output: bool = True,
               **kwargs) -> Any:
        """Create chat completion"""
        
        # Check cache
        if self.woosai.cache_enabled:
            cached = self.woosai.cache_manager.get(model, messages, **kwargs)
            if cached:
                from types import SimpleNamespace
                return SimpleNamespace(**cached)
        
        # Calculate original tokens
        try:
            encoder = tiktoken.encoding_for_model(model)
            original_content = ' '.join([msg.get('content', '') for msg in messages if msg.get('role') == 'user'])
            original_tokens = len(encoder.encode(original_content))
        except:
            original_tokens = 0
        
        # Optimize input
        if optimize_input:
            optimized_messages = []
            for msg in messages:
                if msg['role'] == 'user':
                    compressed, _ = self.woosai.compressor.compress(msg['content'])
                    optimized_messages.append({'role': msg['role'], 'content': compressed})
                else:
                    optimized_messages.append(msg)
        else:
            optimized_messages = messages
        
        # Optimize output
        if optimize_output:
            system_prompt = self.woosai.prompt_optimizer.get_system_prompt()
            optimized_messages.insert(0, {'role': 'system', 'content': system_prompt})
            
            if 'max_tokens' not in kwargs:
                kwargs['max_tokens'] = self.woosai.prompt_optimizer.get_max_tokens()
            if 'temperature' not in kwargs:
                kwargs['temperature'] = self.woosai.prompt_optimizer.get_temperature()
        
        # Call API
        response = self.woosai.client.chat.completions.create(
            model=model,
            messages=optimized_messages,
            **kwargs
        )
        
        # Record stats
        try:
            tokens_input = response.usage.prompt_tokens
            tokens_output = response.usage.completion_tokens
            tokens_saved = max(0, original_tokens - tokens_input) if optimize_input else 0
            
            if 'gpt-4' in model.lower():
                input_rate, output_rate = 0.03, 0.06
            else:
                input_rate, output_rate = 0.0015, 0.002
            
            cost_without = (original_tokens * input_rate + tokens_output * output_rate) / 1000
            cost_with = (tokens_input * input_rate + tokens_output * output_rate) / 1000
            
            self.woosai.stats_tracker.record_request(
                tokens_input=tokens_input,
                tokens_output=tokens_output,
                tokens_saved=tokens_saved,
                cost_without=cost_without,
                cost_with=cost_with,
                strategy="basic"
            )
            
            # Cache response
            if self.woosai.cache_enabled:
                self.woosai.cache_manager.set(model, messages, response, cost_with, **kwargs)
        
        except Exception as e:
            print(f"Warning: Stats/cache error: {e}")
        
        return response


def create_client(api_key: Optional[str] = None, license_key: Optional[str] = None) -> WoosAI:
    """Create WoosAI client"""
    return WoosAI(api_key=api_key, license_key=license_key)