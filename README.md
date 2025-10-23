# 🚀 WoosAI Library

**Reduce your OpenAI API costs by up to 88%!**

WoosAI Library is a powerful Python library that optimizes OpenAI API calls through intelligent input compression, output optimization, advanced caching, and real-time statistics tracking.

[![PyPI version](https://badge.fury.io/py/woosailibrary.svg)](https://badge.fury.io/py/woosailibrary)
[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## ✨ Features

### 🎯 Core Features
- **Input Optimization** - Compress user inputs without losing meaning
- **Output Optimization** - Get concise, relevant responses
- **Advanced Caching** - LRU cache with pattern-based deletion
- **Usage Statistics** - Track costs, tokens, and savings in real-time
- **Auto License** - Free license auto-generated on first use

### 💰 Cost Savings
- **Up to 88%** cost reduction on OpenAI API calls
- **Real-time tracking** of cost savings
- **Cache system** eliminates repeated API calls

### 📊 Statistics & Monitoring
- Daily, monthly, and total usage statistics
- Token usage tracking
- Cost comparison (with/without WoosAI)
- Cache hit rate monitoring

### 💾 Advanced Caching
- **LRU Eviction** - Automatic removal of least-used entries
- **TTL Support** - Auto-expire old cache entries
- **Pattern Deletion** - Remove cache by regex pattern
- **Auto Cleanup** - Periodic automatic maintenance

---

## 🚀 Quick Start

### Installation

```bash
pip install woosailibrary
```

### Basic Usage

```python
import os
from woosailibrary import WoosAI

# Set your OpenAI API key
os.environ['OPENAI_API_KEY'] = 'your-openai-api-key'

# Initialize WoosAI (auto-generates free license on first use)
client = WoosAI()

# Make optimized API call
response = client.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "Explain AI in simple terms"}]
)

print(response.choices[0].message.content)
```

### With Caching

```python
# Enable caching for repeated queries
client = WoosAI(
    cache=True,              # Enable caching
    cache_ttl=24,            # Cache expires after 24 hours
    max_cache_size=1000,     # Store up to 1000 entries
    auto_cleanup_interval=100 # Auto cleanup every 100 operations
)

# First call - hits OpenAI API
response1 = client.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "What is AI?"}]
)

# Second call - returns from cache (FREE!)
response2 = client.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "What is AI?"}]
)
```

---

## 📊 Statistics & Monitoring

### View Statistics

```python
# Display all statistics
client.display_stats()

# Get specific stats
today = client.get_today_stats()
monthly = client.get_monthly_stats()
total = client.get_total_stats()

print(f"Today's savings: {today['cost_saved']}")
print(f"Monthly savings: {monthly['cost_saved']}")
print(f"Total savings: {total['cost']['saved']}")
```

**Example Output:**
```
============================================================
📊 WoosAI Usage Statistics
============================================================

📅 Today (2025-10-23):
  Requests: 15
  Cost Saved: $2.50
  Tokens Saved: 3,500

📆 This Month (2025-10):
  Requests: 450
  Cost Saved: $75.00
  Projected Monthly: $225.00

🎯 Total (All Time):
  Requests: 1,200
  Cost Saved: $210.00
  Savings: 88.0%

============================================================
```

---

## 💾 Cache Management

### View Cache Statistics

```python
# Display cache statistics
client.display_cache_stats()

# Get cache info
cache_info = client.get_cache_info()
print(f"Cache size: {cache_info['size_usage']}")
```

**Example Output:**
```
============================================================
💾 Advanced Cache Statistics
============================================================

📊 Performance:
  Cache Hits: 450
  Cache Misses: 150
  Hit Rate: 75.0%
  LRU Evictions: 50

💰 Savings:
  Cost Saved (from cache): $22.50

📦 Storage:
  Cached Entries: 850/1000 (85.0%)
  Active: 800
  Expired: 50

============================================================
```

### Cache Management

```python
# Clear expired cache entries
client.clear_expired_cache()

# Clear cache by pattern (e.g., weather-related queries)
client.clear_cache_by_pattern("weather|날씨")

# Clear cache older than 7 days
client.clear_old_cache(days=7)

# Clear all cache
client.clear_cache()
```

---

## 🎯 Use Cases

### 1. FAQ Chatbot
```python
client = WoosAI(cache=True, cache_ttl=168)  # 1 week cache

# Same questions = FREE responses!
for question in faq_questions:
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": question}]
    )
```

### 2. Customer Support Bot
```python
client = WoosAI(cache=True, max_cache_size=5000)

response = client.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "How do I reset my password?"}]
)
```

---

## 📖 API Reference

### WoosAI Client

```python
client = WoosAI(
    api_key=None,              # OpenAI API key
    license_key=None,          # WoosAI license
    cache=False,               # Enable caching
    cache_ttl=24,              # Cache TTL in hours
    max_cache_size=1000,       # Maximum cache entries
    auto_cleanup_interval=100  # Auto cleanup frequency
)
```

### Statistics Methods

```python
client.get_today_stats()      # Get today's statistics
client.get_monthly_stats()    # Get monthly statistics
client.get_total_stats()      # Get total statistics
client.display_stats()        # Display statistics
```

### Cache Methods

```python
client.get_cache_info()              # Get cache info
client.display_cache_stats()         # Display cache stats
client.clear_cache()                 # Clear all cache
client.clear_cache_by_pattern(regex) # Clear by pattern
client.clear_expired_cache()         # Clear expired
client.clear_old_cache(days=7)       # Clear old entries
```

---

## 🔧 Configuration

### Configuration Files

WoosAI stores data in:
- **Windows:** `C:\Users\<username>\.woosai\`
- **Linux/Mac:** `~/.woosai/`

Files:
- `config.json` - License information
- `stats.json` - Usage statistics
- `cache/responses.json` - Cached responses

---

## 🔗 Links

- **Website:** [https://woos-ai.com](https://woos-ai.com)
- **PyPI:** [https://pypi.org/project/woosailibrary/](https://pypi.org/project/woosailibrary/)
- **Support:** contact@woos-ai.com

---

## 📄 License

MIT License

---

**Made with ❤️ by WoosAI Team**