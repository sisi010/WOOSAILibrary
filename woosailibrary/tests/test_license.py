"""
Test license verification
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# 🆕 .env 파일 로드
from dotenv import load_dotenv
load_dotenv()  # .env 파일에서 환경 변수 로드

from woosailibrary import WoosAI


def test_free_plan():
    """Test free plan (no license)"""
    print("\n" + "="*60)
    print("Test 1: Free Plan")
    print("="*60)
    
    ai = WoosAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    assert ai.plan == "free"
    print("✅ Free plan initialized correctly")


def test_premium_with_valid_license():
    """Test premium plan with valid license"""
    print("\n" + "="*60)
    print("Test 2: Premium Plan (Valid License)")
    print("="*60)
    
    # Generate test license (30 days)
    from tools.license_generator import LicenseGenerator
    license_key = LicenseGenerator.generate("PREMIUM", 30)
    
    print(f"Test license: {license_key}")
    
    ai = WoosAI(
        api_key=os.getenv("OPENAI_API_KEY"),
        license_key=license_key
    )
    
    assert ai.plan == "premium"
    print("✅ Premium plan activated successfully")


def test_invalid_license():
    """Test invalid license"""
    print("\n" + "="*60)
    print("Test 3: Invalid License")
    print("="*60)
    
    ai = WoosAI(
        api_key=os.getenv("OPENAI_API_KEY"),
        license_key="WOOSAI-PREMIUM-20251120-INVALID"
    )
    
    assert ai.plan == "free"
    print("✅ Invalid license correctly rejected, fell back to free")


def test_expired_license():
    """Test expired license"""
    print("\n" + "="*60)
    print("Test 4: Expired License")
    print("="*60)
    
    # Generate expired license (negative days)
    from tools.license_generator import LicenseGenerator
    from datetime import datetime, timedelta
    
    # Create license that expired yesterday
    expired_date = (datetime.now() - timedelta(days=1)).strftime("%Y%m%d")
    import hashlib
    data = f"PREMIUM:{expired_date}:{LicenseGenerator.SECRET_KEY}"
    sig = hashlib.sha256(data.encode()).hexdigest()[:6].upper()
    expired_license = f"WOOSAI-PREMIUM-{expired_date}-{sig}"
    
    print(f"Expired license: {expired_license}")
    
    ai = WoosAI(
        api_key=os.getenv("OPENAI_API_KEY"),
        license_key=expired_license
    )
    
    assert ai.plan == "free"
    print("✅ Expired license correctly rejected")


if __name__ == "__main__":
    try:
        test_free_plan()
        test_premium_with_valid_license()
        test_invalid_license()
        test_expired_license()
        
        print("\n" + "="*60)
        print("✅ All license tests passed!")
        print("="*60)
        
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
    except Exception as e:
        print(f"\n❌ Error: {e}")