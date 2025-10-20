"""
Basic functionality tests
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from dotenv import load_dotenv
load_dotenv()

from woosailibrary import WoosAI
from tools.license_generator import LicenseGenerator


def test_import():
    """Test basic import"""
    print("\n" + "="*60)
    print("Test 1: Import Test")
    print("="*60)
    
    from woosailibrary import WoosAI, chat, __version__
    
    print(f"✅ WoosAI imported successfully")
    print(f"   Version: {__version__}")


def test_initialization():
    """Test initialization without API call"""
    print("\n" + "="*60)
    print("Test 2: Initialization Test")
    print("="*60)
    
    # Free plan
    ai_free = WoosAI(api_key=os.getenv("OPENAI_API_KEY"))
    assert ai_free.plan == "free"
    print("✅ Free plan initialization successful")
    
    # Premium plan
    license_key = LicenseGenerator.generate("PREMIUM", 30)
    ai_premium = WoosAI(
        api_key=os.getenv("OPENAI_API_KEY"),
        license_key=license_key
    )
    assert ai_premium.plan == "premium"
    print("✅ Premium plan initialization successful")


def test_plan_info():
    """Test plan information methods"""
    print("\n" + "="*60)
    print("Test 3: Plan Info Test")
    print("="*60)
    
    ai = WoosAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    # Get plan info
    info = ai.get_plan_info()
    assert "name" in info
    assert "savings" in info
    print("✅ get_plan_info() works")
    
    # Get usage
    usage = ai.get_usage()
    assert "used" in usage
    assert "limit" in usage
    print("✅ get_usage() works")


def test_chat_free():
    """Test chat with free plan"""
    print("\n" + "="*60)
    print("Test 4: Free Plan Chat Test")
    print("="*60)
    
    ai = WoosAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    response = ai.chat("테스트")
    
    assert response["error"] is None
    assert response["content"] is not None
    assert response["stats"]["plan"] == "무료 플랜"
    assert response["stats"]["strategy_used"] == "starter"
    
    print("✅ Free plan chat successful")
    print(f"   Output: {response['stats']['tokens']['output']} tokens")


def test_chat_premium():
    """Test chat with premium plan"""
    print("\n" + "="*60)
    print("Test 5: Premium Plan Chat Test")
    print("="*60)
    
    license_key = LicenseGenerator.generate("PREMIUM", 30)
    ai = WoosAI(
        api_key=os.getenv("OPENAI_API_KEY"),
        license_key=license_key
    )
    
    response = ai.chat("테스트 질문입니다")
    
    assert response["error"] is None
    assert response["content"] is not None
    assert response["stats"]["plan"] == "프리미엄 플랜"
    assert response["stats"]["auto_optimized"] == True
    
    print("✅ Premium plan chat successful")
    print(f"   Strategy: {response['stats']['strategy_used']}")
    print(f"   Output: {response['stats']['tokens']['output']} tokens")


if __name__ == "__main__":
    try:
        test_import()
        test_initialization()
        test_plan_info()
        test_chat_free()
        test_chat_premium()
        
        print("\n" + "="*60)
        print("✅ All basic tests passed!")
        print("="*60)
        
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
    except Exception as e:
        print(f"\n❌ Error: {e}")