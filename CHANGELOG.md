# Changelog

All notable changes to WoosAI Library will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [1.1.0] - 2025-10-23

### Added
- ✨ **Usage Statistics Tracking**
  - Daily, monthly, and total statistics
  - Real-time cost savings tracking
  - Token usage monitoring
  - `get_today_stats()`, `get_monthly_stats()`, `get_total_stats()` methods
  - `display_stats()` for formatted output

- 💾 **Advanced Caching System**
  - LRU (Least Recently Used) eviction policy
  - TTL (Time To Live) support
  - Configurable cache size limits
  - Automatic periodic cleanup
  - Pattern-based cache deletion with regex support
  - `CacheManager` class with full cache lifecycle management

- 🧹 **Cache Management Methods**
  - `clear_cache()` - Clear all cache entries
  - `clear_cache_by_pattern(pattern)` - Remove entries matching regex
  - `clear_expired_cache()` - Remove only expired entries
  - `clear_old_cache(days)` - Remove entries older than N days
  - `get_cache_info()` - Get detailed cache information
  - `get_cache_stats()` - Get cache performance statistics
  - `display_cache_stats()` - Display formatted cache statistics

- 📊 **New Configuration Options**
  - `cache` - Enable/disable caching
  - `cache_ttl` - Cache time-to-live in hours
  - `max_cache_size` - Maximum number of cached entries
  - `auto_cleanup_interval` - Automatic cleanup frequency

- 📁 **New Core Modules**
  - `woosailibrary/core/stats_tracker.py` - Statistics tracking
  - `woosailibrary/core/cache_manager.py` - Cache management

### Changed
- 🔄 Updated `__init__.py` to v1.1.0
- 📝 Enhanced `WoosAI` class with statistics and caching support
- 🎨 Improved initialization messages with cache status
- 📦 Updated dependencies in `setup.py`

### Improved
- ⚡ Better performance with caching
- 🛡️ Enhanced error handling
- 📈 More detailed usage analytics
- 💰 Additional cost savings through caching

### Fixed
- 🐛 Minor bug fixes in input compression
- 🔧 Improved error messages
- 📝 Better documentation

---

## [1.0.1] - 2025-10-15

### Added
- 🎫 Automatic free license generation
- 🔐 License management system
- 🌐 Backend API integration

### Changed
- 📝 Updated documentation
- 🎨 Improved user onboarding flow

### Fixed
- 🐛 Fixed license verification issues
- 🔧 Improved error handling

---

## [1.0.0] - 2025-10-01

### Added
- 🚀 Initial release
- ⚡ Input compression (Korean idioms, numbers, patterns)
- 🎯 Output optimization (prompt engineering)
- 💰 Up to 78.5% cost reduction
- 🏃 Up to 79% speed improvement
- 📦 Core optimization modules:
  - `LightweightInputCompressor`
  - `PromptOptimizer`
- 🔧 OpenAI API integration
- 📝 Basic documentation
- ✅ Unit tests
- 🌐 PyPI package

### Features
- Input text compression
- Output token reduction
- Prompt optimization
- Strategy patterns (SPEED, BALANCED, MAXIMUM)
- OpenAI client wrapper

---

## Upgrade Guide

### From v1.0.1 to v1.1.0

1. **Update package:**
   ```bash
   pip install --upgrade woosailibrary
   ```

2. **No breaking changes** - All v1.0.1 code will continue to work

3. **New features available:**
   ```python
   from woosailibrary import WoosAI
   
   # Enable caching (optional)
   client = WoosAI(cache=True)
   
   # View statistics (new)
   client.display_stats()
   
   # Manage cache (new)
   client.display_cache_stats()
   client.clear_expired_cache()
   ```

4. **Configuration files:**
   - New files will be created in `~/.woosai/`:
     - `stats.json` - Usage statistics
     - `cache/responses.json` - Cached responses
   
5. **Benefits:**
   - ✅ Track your cost savings
   - ✅ Reduce costs further with caching
   - ✅ Monitor usage patterns
   - ✅ Better cache management

---

## Roadmap

### v1.2.0 (Planned)
- [ ] Web dashboard for visualizations
- [ ] Multi-model support (Claude, Gemini)
- [ ] Batch processing API
- [ ] A/B testing framework
- [ ] Enhanced analytics

### v1.3.0 (Future)
- [ ] Team collaboration features
- [ ] Custom optimization strategies
- [ ] Advanced reporting
- [ ] CLI tools
- [ ] Slack/Discord integration

---

## Migration Notes

### v1.0.x to v1.1.0
- **Fully backward compatible**
- No code changes required
- New features are opt-in
- Existing functionality unchanged

---

## Support

For questions or issues:
- 📧 Email: contact@woos-ai.com
- 🐛 Issues: [GitHub Issues](https://github.com/woosai/woosailibrary/issues)
- 📖 Docs: [Documentation](https://github.com/woosai/woosailibrary#readme)

---

**Last Updated:** 2025-10-23