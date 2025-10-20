# test_cloud.py

import sys
import os

# Add current directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

from woosai.storage.cloud_storage import CloudStorage

def main():
    print("=" * 50)
    print("CloudStorage Test")
    print("=" * 50)
    
    # API Key
    API_KEY = "woosai_gD379MGezJZIy6Zm-hpDOciMb5czO2KkoC4qA1eZ5jQ"
    
    # Create storage
    print("\n1. Creating CloudStorage...")
    storage = CloudStorage(api_key=API_KEY)
    print("   OK!")
    
    # Test user
    test_user = "test_user_001"
    test_data = {
        "patterns": {"quality": 5, "economy": 3},
        "usage_count": 10
    }
    
    # Save
    print(f"\n2. Saving profile for '{test_user}'...")
    storage.save_profile(test_user, test_data)
    print("   OK!")
    
    # Load
    print(f"\n3. Loading profile...")
    loaded = storage.load_profile(test_user)
    print(f"   Data: {loaded}")
    
    # Verify
    print(f"\n4. Verifying...")
    if loaded == test_data:
        print("   MATCH!")
    else:
        print("   MISMATCH!")
    
    # Delete
    print(f"\n5. Deleting profile...")
    storage.delete_profile(test_user)
    print("   OK!")
    
    # Verify deletion
    print(f"\n6. Verify deletion...")
    deleted = storage.load_profile(test_user)
    if deleted is None:
        print("   DELETED!")
    else:
        print("   STILL EXISTS!")
    
    print("\n" + "=" * 50)
    print("All tests passed!")
    print("=" * 50)

if __name__ == "__main__":
    main()