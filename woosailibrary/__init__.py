# -*- coding: utf-8 -*-
"""
WOOSAILibrary - AI Cost Optimization Made Simple
License-based Premium Features

Plans:
  - Free: Basic optimization (17% savings)
  - Premium: Full AUTO optimization (up to 61% savings)

Usage:
    # Free plan
    ai = WoosAI(api_key="sk-...")
    
    # Premium plan (with license)
    ai = WoosAI(
        api_key="sk-...",
        license_key="WOOSAI-PREMIUM-20251120-ABC123"
    )

Get Premium License:
    Visit https://woosai.com/premium

Author: WoosAI Team
Created: 2025-10-20
Version: 1.0.0
"""

# Add current directory to Python path
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Now import core modules
from core.lightweight_input import get_compressor
from core.prompt_optimizer import get_prompt_optimizer
from openai import OpenAI
import hashlib
from datetime import datetime


class WoosAI:
    """
    Simple AI cost optimization with license-based premium features
    
    Free Plan:
        - Basic optimization (STARTER strategy)
        - 17% cost savings
        - 1,000 requests/month
    
    Premium Plan (License Required):
        - Full AUTO optimization
        - Up to 61% cost savings
        - 50,000 requests/month
        - Automatic strategy selection
    
    Example:
        # Free
        ai = WoosAI(api_key="sk-...")
        
        # Premium
        ai = WoosAI(
            api_key="sk-...",
            license_key="WOOSAI-PREMIUM-20251120-ABC123"
        )
        
        response = ai.chat("Your question")
    """
    
    PLAN_INFO = {
        "free": {
            "name": "무료 플랜",
            "name_en": "Free Plan",
            "description": "기본 자동 최적화",
            "savings": "17%",
            "monthly_limit": 1000,
            "price": "무료",
            "features": [
                "기본 자동 최적화 (STARTER)",
                "17% 비용 절감",
                "월 1,000개 요청",
                "입력 압축"
            ]
        },
        "premium": {
            "name": "프리미엄 플랜",
            "name_en": "Premium Plan",
            "description": "완전 자동 최적화 (AUTO)",
            "savings": "최대 61%",
            "monthly_limit": 50000,
            "price": "$20/월",
            "features": [
                "완전 자동 최적화 (AUTO)",
                "질문별 최적 전략 자동 선택",
                "최대 61% 비용 절감",
                "월 50,000개 요청",
                "입력 압축",
                "상세 분석 리포트"
            ]
        }
    }
    
    # Secret key for license verification (keep this secret!)
    _SECRET_KEY = "WOOSAI_SECRET_2025_V1"
    
    def __init__(self, 
                 api_key: str = None,
                 license_key: str = None):
        """
        Initialize WoosAI
        
        Args:
            api_key: OpenAI API key (or use OPENAI_API_KEY env var)
            license_key: Premium license key (or use WOOSAI_LICENSE env var)
                        Format: WOOSAI-PREMIUM-YYYYMMDD-SIGNATURE
        
        Example:
            # Free plan
            ai = WoosAI(api_key="sk-...")
            
            # Premium plan
            ai = WoosAI(
                api_key="sk-...",
                license_key="WOOSAI-PREMIUM-20251120-ABC123"
            )
            
            # Using environment variables
            # .env file:
            # OPENAI_API_KEY=sk-...
            # WOOSAI_LICENSE=WOOSAI-PREMIUM-20251120-ABC123
            ai = WoosAI()  # Auto-loads from env
        """
        # Get API key
        self.openai_api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.openai_api_key:
            raise ValueError(
                "OpenAI API key required. "
                "Provide api_key parameter or set OPENAI_API_KEY environment variable."
            )
        
        # Get license key
        license = license_key or os.getenv("WOOSAI_LICENSE")
        
        # Verify license and determine plan
        if license:
            self.plan, self.license_info = self._verify_license(license)
        else:
            self.plan = "free"
            self.license_info = None
        
        # Print plan info
        self._print_welcome()
        
        # Initialize internal components
        self._compressor = get_compressor()
        self._prompt_optimizer = get_prompt_optimizer()
        self._client = OpenAI(api_key=self.openai_api_key)
        
        # Get encoder from compressor (handle different attribute names)
        import tiktoken
        self._encoder = tiktoken.get_encoding("cl100k_base")
        
        # Request counter
        self._request_count = 0
    
    def _verify_license(self, license_key: str) -> tuple:
        """
        Verify license key
        
        License format: WOOSAI-PLAN-EXPIRY-SIGNATURE
        Example: WOOSAI-PREMIUM-20251120-A8F3D9
        
        Args:
            license_key: License key string
        
        Returns:
            tuple: (plan, license_info) or ("free", None) if invalid
        """
        try:
            # Parse license key
            parts = license_key.strip().split('-')
            
            if len(parts) != 4:
                print("⚠️  Invalid license key format")
                print("    Expected format: WOOSAI-PLAN-YYYYMMDD-SIGNATURE")
                return ("free", None)
            
            prefix, plan, expiry, signature = parts
            
            # Check prefix
            if prefix != "WOOSAI":
                print("⚠️  Invalid license key prefix")
                return ("free", None)
            
            # Check plan
            plan = plan.upper()
            if plan not in ["FREE", "PREMIUM"]:
                print("⚠️  Invalid plan in license key")
                return ("free", None)
            
            # Check expiry date
            try:
                expiry_date = datetime.strptime(expiry, "%Y%m%d")
                if datetime.now() > expiry_date:
                    print("⚠️  License expired")
                    print(f"    Expired on: {expiry_date.strftime('%Y-%m-%d')}")
                    print("    Please renew at: https://woosai.com/renew")
                    return ("free", None)
            except ValueError:
                print("⚠️  Invalid expiry date format")
                return ("free", None)
            
            # Verify signature
            expected_sig = self._generate_signature(plan, expiry)
            if signature.upper() != expected_sig:
                print("⚠️  Invalid license signature")
                print("    This license key may be tampered or fake")
                return ("free", None)
            
            # All checks passed!
            license_info = {
                "plan": plan,
                "expiry": expiry_date,
                "days_remaining": (expiry_date - datetime.now()).days
            }
            
            return (plan.lower(), license_info)
            
        except Exception as e:
            print(f"⚠️  License verification error: {e}")
            return ("free", None)
    
    def _generate_signature(self, plan: str, expiry: str) -> str:
        """
        Generate license signature
        
        Args:
            plan: Plan name (FREE or PREMIUM)
            expiry: Expiry date (YYYYMMDD)
        
        Returns:
            6-character signature
        """
        data = f"{plan}:{expiry}:{self._SECRET_KEY}"
        return hashlib.sha256(data.encode()).hexdigest()[:6].upper()
    
    def _print_welcome(self):
        """Print welcome message with plan info"""
        if self.plan == "premium" and self.license_info:
            days = self.license_info["days_remaining"]
            expiry = self.license_info["expiry"].strftime("%Y-%m-%d")
            print(f"✅ WoosAI Premium License Valid")
            print(f"   Expires: {expiry} ({days} days remaining)")
            print(f"   Plan: {self.PLAN_INFO['premium']['name']}")
        else:
            print(f"✅ WoosAI - {self.PLAN_INFO['free']['name']}")
            print(f"   Upgrade to Premium: https://woosai.com/premium")
    
    def _select_strategy(self, input_tokens: int) -> str:
        """
        Select optimization strategy based on plan and input length
        
        Free: Always STARTER
        Premium: AUTO (STARTER/PRO/PREMIUM based on length)
        
        Args:
            input_tokens: Number of input tokens
        
        Returns:
            Strategy name
        """
        if self.plan == "free":
            return "starter"
        
        # Premium: Full AUTO
        if input_tokens < 18:
            return "starter"
        elif input_tokens < 60:
            return "pro"
        else:
            return "premium"
    
    def chat(self, message: str, compress: bool = True) -> dict:
        """
        Send a message and get optimized response
        
        Args:
            message: Your question or message
            compress: Enable input compression (default: True)
        
        Returns:
            dict containing:
                - content: AI response text
                - stats: Optimization statistics
                - error: Error message (if any)
        
        Example:
            response = ai.chat("Explain AI technology")
            print(response["content"])
            print(f"Saved: {response['stats']['savings']}")
        """
        # Check monthly limit
        self._request_count += 1
        limit = self.PLAN_INFO[self.plan]["monthly_limit"]
        
        if self._request_count > limit:
            return {
                "error": f"월 {limit}개 제한 초과. 플랜 업그레이드가 필요합니다.",
                "content": None,
                "stats": None
            }
        
        try:
            # 1. Compress input
            if compress:
                compressed_text, comp_info = self._compressor.compress(message)
                tokens_saved = comp_info.get("tokens_saved", 0)
            else:
                compressed_text = message
                tokens_saved = 0
            
            # 2. Count input tokens
            input_tokens = len(self._encoder.encode(compressed_text))
            
            # 3. Select strategy (AUTO for premium, STARTER for free)
            strategy = self._select_strategy(input_tokens)
            
            # 4. Get optimized system prompt
            system_prompt = self._prompt_optimizer.get_system_prompt(
                strategy=strategy
            )
            
            # 5. Get optimization parameters
            if strategy == "starter":
                max_tokens = 2000
                temperature = 0.7
            elif strategy == "pro":
                max_tokens = 1300
                temperature = 0.5
            else:  # premium strategy
                max_tokens = 700
                temperature = 0.3
            
            # 6. Call OpenAI API
            response = self._client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": compressed_text}
                ],
                max_tokens=max_tokens,
                temperature=temperature
            )
            
            # 7. Calculate costs
            output_tokens = response.usage.completion_tokens
            total_tokens = response.usage.total_tokens
            
            input_cost = input_tokens * 0.150 / 1_000_000
            output_cost = output_tokens * 0.600 / 1_000_000
            total_cost = input_cost + output_cost
            
            # 8. Estimate savings
            if strategy == "starter":
                savings_percent = "17%"
            elif strategy == "pro":
                savings_percent = "43%"
            else:
                savings_percent = "61%"
            
            # 9. Return result
            return {
                "content": response.choices[0].message.content,
                "stats": {
                    "plan": self.PLAN_INFO[self.plan]["name"],
                    "auto_optimized": self.plan == "premium",
                    "strategy_used": strategy,
                    "savings": savings_percent,
                    "tokens": {
                        "input": input_tokens,
                        "output": output_tokens,
                        "total": total_tokens,
                        "saved": tokens_saved
                    },
                    "cost": {
                        "input": f"${input_cost:.6f}",
                        "output": f"${output_cost:.6f}",
                        "total": f"${total_cost:.6f}"
                    },
                    "usage": f"{self._request_count}/{limit}"
                },
                "error": None
            }
            
        except Exception as e:
            return {
                "error": str(e),
                "content": None,
                "stats": None
            }
    
    def get_plan_info(self) -> dict:
        """
        Get current plan information
        
        Returns:
            dict with plan details
        """
        info = self.PLAN_INFO[self.plan].copy()
        
        if self.license_info:
            info["license"] = {
                "expiry": self.license_info["expiry"].strftime("%Y-%m-%d"),
                "days_remaining": self.license_info["days_remaining"]
            }
        
        return info
    
    def compare_plans(self) -> None:
        """Display comparison between Free and Premium plans"""
        if self.plan == "free":
            print("""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  플랜 비교
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🆓 무료 플랜 (현재)
  ✅ 기본 자동 최적화 (STARTER)
  ✅ 17% 비용 절감
  ✅ 월 1,000개 요청
  ✅ 입력 압축
  💵 무료

⭐ 프리미엄 플랜
  ✅ 완전 자동 최적화 (AUTO)
  ✅ 최대 61% 비용 절감
  ✅ 질문별 최적 전략 자동 선택
  ✅ 월 50,000개 요청
  ✅ 입력 압축
  ✅ 상세 분석 리포트
  💵 $20/월

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💡 프리미엄으로 업그레이드하면 44% 더 절감!
   👉 https://woosai.com/premium
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
            """)
        else:
            days = self.license_info["days_remaining"]
            expiry = self.license_info["expiry"].strftime("%Y-%m-%d")
            print(f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  현재 플랜
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⭐ 프리미엄 플랜 (현재)
  ✅ 완전 자동 최적화 (AUTO) 사용 중
  ✅ 최대 61% 비용 절감
  ✅ 질문별 최적 전략 자동 선택
  ✅ 월 50,000개 요청
  
  📅 만료일: {expiry} ({days}일 남음)
  
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎉 최적의 비용 절감 효과를 누리고 있습니다!
   갱신: https://woosai.com/renew
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
            """)
    
    def get_usage(self) -> dict:
        """
        Get current usage statistics
        
        Returns:
            dict with usage info
        """
        limit = self.PLAN_INFO[self.plan]["monthly_limit"]
        return {
            "used": self._request_count,
            "limit": limit,
            "remaining": limit - self._request_count,
            "percentage": (self._request_count / limit * 100) if limit > 0 else 0,
            "plan": self.plan
        }


# Quick access function
def chat(message: str, api_key: str = None, license_key: str = None) -> str:
    """
    Quick one-liner for simple usage
    
    Example:
        from woosailibrary import chat
        
        response = chat("What is AI?", api_key="sk-...")
        print(response)
    
    Args:
        message: Your question
        api_key: OpenAI API key
        license_key: Premium license key (optional)
    
    Returns:
        AI response text
    """
    ai = WoosAI(api_key=api_key, license_key=license_key)
    result = ai.chat(message)
    return result.get("content") or result.get("error", "Unknown error")


# Version info
__version__ = "1.0.0"
__author__ = "WoosAI Team"
__license__ = "MIT"