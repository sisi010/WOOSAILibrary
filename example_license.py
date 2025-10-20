"""
WoosAI License Usage Examples
"""

from woosailibrary import WoosAI
import os
from dotenv import load_dotenv
load_dotenv()

def example_free():
    """Example: Free plan usage"""
    print("\n" + "="*60)
    print("Example 1: Free Plan")
    print("="*60)
    
    ai = WoosAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    response = ai.chat("AI란 무엇인가요?")
    
    # 🆕 전체 response 출력해서 확인
    print(f"\n전체 응답: {response}")
    
    if response.get("error"):
        print(f"\n❌ 에러 발생: {response['error']}")
    elif response.get("content"):
        print(f"\n답변: {response['content']}")
        print(f"플랜: {response['stats']['plan']}")
        print(f"절감: {response['stats']['savings']}")


def example_premium():
    """Example: Premium plan with license"""
    print("\n" + "="*60)
    print("Example 2: Premium Plan (With License)")
    print("="*60)
    
    # Generate test license
    from tools.license_generator import LicenseGenerator
    license_key = LicenseGenerator.generate("PREMIUM", 30)
    
    print(f"Using license: {license_key}\n")
    
    ai = WoosAI(
        api_key=os.getenv("OPENAI_API_KEY"),
        license_key=license_key
    )
    
    # Test different question lengths
    questions = [
        "AI란?",  # Short
        "인공지능 기술을 설명해주세요",  # Medium
        "인공지능 기술의 발전 역사와 현재 활용 사례, 그리고 향후 10년간의 전망에 대해 자세히 설명해주세요"  # Long
    ]
    
    for q in questions:
        response = ai.chat(q)
        
        if response.get("error"):
            print(f"\n❌ 에러: {response['error']}")
            continue
        
        print(f"\n질문: {q[:30]}...")
        print(f"전략: {response['stats']['strategy_used']}")
        print(f"절감: {response['stats']['savings']}")
        print(f"출력: {response['stats']['tokens']['output']}토큰")


def example_env_variable():
    """Example: Using environment variable"""
    print("\n" + "="*60)
    print("Example 3: Using Environment Variable")
    print("="*60)
    
    print("Set in .env file:")
    print("  WOOSAI_LICENSE=WOOSAI-PREMIUM-20251120-ABC123")
    print("\nThen simply:")
    print("  ai = WoosAI()  # Auto-loads license from env")


def example_plan_comparison():
    """Example: Compare plans"""
    print("\n" + "="*60)
    print("Example 4: Plan Comparison")
    print("="*60)
    
    ai = WoosAI(api_key=os.getenv("OPENAI_API_KEY"))
    ai.compare_plans()


if __name__ == "__main__":
    example_free()
    example_premium()
    example_env_variable()
    example_plan_comparison()