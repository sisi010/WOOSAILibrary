"""
Advanced Response Cache Manager

Cache OpenAI API responses with advanced features:
- LRU (Least Recently Used) eviction
- Pattern-based cache deletion
- Automatic periodic cleanup
- Size limits
"""

import json
import hashlib
import re
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from collections import OrderedDict


class CacheManager:
    """
    Advanced cache manager with LRU, auto-cleanup, and pattern matching
    
    Features:
    - Cache responses by query hash
    - TTL (Time To Live) support
    - LRU eviction when size limit reached
    - Pattern-based cache deletion
    - Automatic cleanup on every N operations
    - Detailed cache statistics
    """
    
    def __init__(self, 
                 config_dir: Optional[Path] = None, 
                 ttl_hours: int = 24,
                 max_size: int = 1000,
                 auto_cleanup_interval: int = 100):
        """
        Initialize advanced cache manager
        
        Args:
            config_dir: Directory for storing cache (default: ~/.woosai)
            ttl_hours: Cache TTL in hours (default: 24)
            max_size: Maximum number of cache entries (default: 1000)
            auto_cleanup_interval: Auto cleanup every N operations (default: 100)
        """
        if config_dir is None:
            config_dir = Path.home() / '.woosai'
        
        self.config_dir = Path(config_dir)
        self.cache_dir = self.config_dir / 'cache'
        self.cache_file = self.cache_dir / 'responses.json'
        self.ttl_hours = ttl_hours
        self.max_size = max_size
        self.auto_cleanup_interval = auto_cleanup_interval
        self.operation_count = 0
        
        # Ensure directory exists
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Load cache
        self.cache = self._load_cache()
        
        # Clean expired entries
        self._cleanup_expired()
    
    def _load_cache(self) -> Dict[str, Any]:
        """Load cache from file"""
        if self.cache_file.exists():
            try:
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # Convert entries to OrderedDict for LRU
                    if "entries" in data:
                        data["entries"] = OrderedDict(data["entries"])
                    return data
            except Exception:
                pass
        
        # Default cache structure
        return {
            "entries": OrderedDict(),
            "stats": {
                "hits": 0,
                "misses": 0,
                "saves": 0,
                "evictions": 0,
                "total_cost_saved": 0.0
            },
            "config": {
                "ttl_hours": self.ttl_hours,
                "max_size": self.max_size
            }
        }
    
    def _save_cache(self):
        """Save cache to file"""
        try:
            # Convert OrderedDict to regular dict for JSON
            save_data = {
                "entries": dict(self.cache["entries"]),
                "stats": self.cache["stats"],
                "config": self.cache["config"]
            }
            
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(save_data, f, indent=2)
        except Exception as e:
            print(f"Warning: Failed to save cache: {e}")
    
    def _generate_key(self, model: str, messages: list, **kwargs) -> str:
        """Generate cache key from request parameters"""
        cache_input = {
            "model": model,
            "messages": messages,
            "temperature": kwargs.get("temperature", 0.7),
            "max_tokens": kwargs.get("max_tokens", 2000)
        }
        
        cache_str = json.dumps(cache_input, sort_keys=True)
        return hashlib.md5(cache_str.encode()).hexdigest()
    
    def _cleanup_expired(self):
        """Remove expired cache entries"""
        now = datetime.now()
        expired_keys = []
        
        for key, entry in list(self.cache["entries"].items()):
            expires_at = datetime.fromisoformat(entry["expires_at"])
            if now > expires_at:
                expired_keys.append(key)
        
        for key in expired_keys:
            del self.cache["entries"][key]
        
        if expired_keys:
            self._save_cache()
    
    def _enforce_size_limit(self):
        """Enforce max cache size using LRU eviction"""
        while len(self.cache["entries"]) > self.max_size:
            # Remove oldest (least recently used) entry
            oldest_key = next(iter(self.cache["entries"]))
            del self.cache["entries"][oldest_key]
            self.cache["stats"]["evictions"] += 1
    
    def _auto_cleanup(self):
        """Automatic cleanup every N operations"""
        self.operation_count += 1
        if self.operation_count >= self.auto_cleanup_interval:
            self._cleanup_expired()
            self.operation_count = 0
    
    def get(self, model: str, messages: list, **kwargs) -> Optional[Dict[str, Any]]:
        """Get cached response"""
        self._auto_cleanup()
        
        key = self._generate_key(model, messages, **kwargs)
        
        if key in self.cache["entries"]:
            entry = self.cache["entries"][key]
            expires_at = datetime.fromisoformat(entry["expires_at"])
            
            # Check if expired
            if datetime.now() > expires_at:
                del self.cache["entries"][key]
                self._save_cache()
                self.cache["stats"]["misses"] += 1
                return None
            
            # Move to end (most recently used)
            self.cache["entries"].move_to_end(key)
            
            # Cache hit!
            self.cache["stats"]["hits"] += 1
            self.cache["stats"]["total_cost_saved"] += entry.get("cost_saved", 0.0)
            self._save_cache()
            
            return entry["response"]
        
        # Cache miss
        self.cache["stats"]["misses"] += 1
        return None
    
    def set(self, model: str, messages: list, response: Any, cost_saved: float = 0.0, **kwargs):
        """Store response in cache"""
        self._auto_cleanup()
        
        key = self._generate_key(model, messages, **kwargs)
        expires_at = datetime.now() + timedelta(hours=self.ttl_hours)
        
        # Convert response to dict
        response_dict = {
            "id": getattr(response, 'id', ''),
            "object": getattr(response, 'object', 'chat.completion'),
            "created": getattr(response, 'created', 0),
            "model": getattr(response, 'model', model),
            "choices": [
                {
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": response.choices[0].message.content
                    },
                    "finish_reason": response.choices[0].finish_reason
                }
            ] if hasattr(response, 'choices') and len(response.choices) > 0 else [],
            "usage": {
                "prompt_tokens": getattr(response.usage, 'prompt_tokens', 0),
                "completion_tokens": getattr(response.usage, 'completion_tokens', 0),
                "total_tokens": getattr(response.usage, 'total_tokens', 0)
            } if hasattr(response, 'usage') else {}
        }
        
        # Get original query for pattern matching
        query_text = ' '.join([msg.get('content', '') for msg in messages if msg.get('role') == 'user'])
        
        self.cache["entries"][key] = {
            "response": response_dict,
            "query": query_text[:200],  # Store first 200 chars for pattern matching
            "cached_at": datetime.now().isoformat(),
            "expires_at": expires_at.isoformat(),
            "cost_saved": cost_saved,
            "access_count": 0
        }
        
        self.cache["stats"]["saves"] += 1
        
        # Enforce size limit (LRU eviction)
        self._enforce_size_limit()
        
        self._save_cache()
    
    def clear_by_pattern(self, pattern: str) -> int:
        """Clear cache entries matching a pattern"""
        removed_keys = []
        
        try:
            regex = re.compile(pattern, re.IGNORECASE)
            
            for key, entry in list(self.cache["entries"].items()):
                query = entry.get("query", "")
                if regex.search(query):
                    removed_keys.append(key)
            
            for key in removed_keys:
                del self.cache["entries"][key]
            
            if removed_keys:
                self._save_cache()
                print(f"✅ Removed {len(removed_keys)} entries matching pattern '{pattern}'")
            else:
                print(f"ℹ️  No entries found matching pattern '{pattern}'")
        
        except re.error as e:
            print(f"❌ Invalid regex pattern: {e}")
            return 0
        
        return len(removed_keys)
    
    def clear_expired(self) -> int:
        """Clear only expired entries"""
        before_count = len(self.cache["entries"])
        self._cleanup_expired()
        after_count = len(self.cache["entries"])
        removed = before_count - after_count
        
        if removed > 0:
            print(f"✅ Removed {removed} expired cache entries")
        else:
            print("ℹ️  No expired entries found")
        
        return removed
    
    def clear_old_entries(self, days: int = 7) -> int:
        """Clear entries older than specified days"""
        cutoff_date = datetime.now() - timedelta(days=days)
        removed_keys = []
        
        for key, entry in list(self.cache["entries"].items()):
            cached_at = datetime.fromisoformat(entry["cached_at"])
            if cached_at < cutoff_date:
                removed_keys.append(key)
        
        for key in removed_keys:
            del self.cache["entries"][key]
        
        if removed_keys:
            self._save_cache()
            print(f"✅ Removed {len(removed_keys)} entries older than {days} days")
        else:
            print(f"ℹ️  No entries older than {days} days found")
        
        return len(removed_keys)
    
    def get_cache_info(self) -> Dict[str, Any]:
        """Get detailed cache information"""
        total_entries = len(self.cache["entries"])
        expired_count = 0
        oldest_date = None
        newest_date = None
        
        now = datetime.now()
        for entry in self.cache["entries"].values():
            # Check expired
            expires_at = datetime.fromisoformat(entry["expires_at"])
            if now > expires_at:
                expired_count += 1
            
            # Track dates
            cached_at = datetime.fromisoformat(entry["cached_at"])
            if oldest_date is None or cached_at < oldest_date:
                oldest_date = cached_at
            if newest_date is None or cached_at > newest_date:
                newest_date = cached_at
        
        return {
            "total_entries": total_entries,
            "active_entries": total_entries - expired_count,
            "expired_entries": expired_count,
            "max_size": self.max_size,
            "size_usage": f"{total_entries}/{self.max_size} ({total_entries/self.max_size*100:.1f}%)" if self.max_size > 0 else "0/0",
            "oldest_entry": oldest_date.strftime("%Y-%m-%d %H:%M") if oldest_date else "N/A",
            "newest_entry": newest_date.strftime("%Y-%m-%d %H:%M") if newest_date else "N/A",
            "ttl_hours": self.ttl_hours,
            "auto_cleanup_interval": self.auto_cleanup_interval
        }
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        stats = self.cache["stats"]
        total_requests = stats["hits"] + stats["misses"]
        hit_rate = (stats["hits"] / total_requests * 100) if total_requests > 0 else 0
        
        return {
            "hits": stats["hits"],
            "misses": stats["misses"],
            "total_requests": total_requests,
            "hit_rate": f"{hit_rate:.1f}%",
            "cache_saves": stats["saves"],
            "evictions": stats["evictions"],
            "cached_entries": len(self.cache["entries"]),
            "cost_saved": f"${stats['total_cost_saved']:.2f}"
        }
    
    def clear(self):
        """Clear all cache entries"""
        count = len(self.cache["entries"])
        self.cache["entries"] = OrderedDict()
        self._save_cache()
        print(f"✅ Cleared all {count} cache entries")
    
    def display_stats(self):
        """Display formatted cache statistics"""
        stats = self.get_stats()
        info = self.get_cache_info()
        
        print("\n" + "="*60)
        print("💾 Advanced Cache Statistics")
        print("="*60)
        print(f"\n📊 Performance:")
        print(f"  Cache Hits: {stats['hits']}")
        print(f"  Cache Misses: {stats['misses']}")
        print(f"  Hit Rate: {stats['hit_rate']}")
        print(f"  LRU Evictions: {stats['evictions']}")
        print(f"\n💰 Savings:")
        print(f"  Cost Saved (from cache): {stats['cost_saved']}")
        print(f"\n📦 Storage:")
        print(f"  Cached Entries: {info['size_usage']}")
        print(f"  Active: {info['active_entries']}")
        print(f"  Expired: {info['expired_entries']}")
        print(f"\n⏰ Configuration:")
        print(f"  TTL: {info['ttl_hours']} hours")
        print(f"  Max Size: {info['max_size']} entries")
        print(f"  Auto Cleanup: Every {info['auto_cleanup_interval']} operations")
        print(f"\n📅 Timeline:")
        print(f"  Oldest Entry: {info['oldest_entry']}")
        print(f"  Newest Entry: {info['newest_entry']}")
        print("="*60 + "\n")