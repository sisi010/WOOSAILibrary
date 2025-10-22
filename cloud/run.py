"""
Run Flask Server
Start the WoosAI Backend API
"""

from app import create_app
import os
import sys

# Print Python version and environment info
print("=" * 60)
print("🐍 PYTHON ENVIRONMENT INFO")
print("=" * 60)
print(f"Python version: {sys.version}")
print(f"Python executable: {sys.executable}")
print(f"Current directory: {os.getcwd()}")
print("=" * 60)

# Print environment variables (MongoDB)
print("\n🔍 CHECKING ENVIRONMENT VARIABLES")
print("=" * 60)
mongodb_url = os.getenv('MONGODB_URL')
if mongodb_url:
    # Show partial URL for security
    url_preview = mongodb_url[:40] + "..." if len(mongodb_url) > 40 else mongodb_url
    print(f"✅ MONGODB_URL exists: {url_preview}")
else:
    print("❌ MONGODB_URL not found!")
print(f"✅ DATABASE_NAME: {os.getenv('DATABASE_NAME', 'not set')}")
print("=" * 60)

# Try to create app
print("\n🚀 CREATING FLASK APP")
print("=" * 60)

try:
    app = create_app()
    print("✅ Flask app created successfully!")
except Exception as e:
    print(f"❌ Error creating app: {str(e)}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

if __name__ == '__main__':
    # Get port from environment variable or use 5000
    port = int(os.getenv('PORT', 5000))
    
    # Run server
    print(f"\n🎯 STARTING SERVER")
    print(f"📍 Running on: http://0.0.0.0:{port}")
    print(f"📚 API Health: http://0.0.0.0:{port}/api/health")
    print("=" * 60)
    
    app.run(
        host='0.0.0.0',
        port=port,
        debug=False  # Production mode
    )