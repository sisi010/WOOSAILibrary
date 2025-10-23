# WOOSAILibrary

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![PyPI version](https://badge.fury.io/py/woosailibrary.svg)](https://pypi.org/project/woosailibrary/)

🚀 AI 비용 최적화 라이브러리 - OpenAI API 비용을 최대 88% 절감

**✨ v1.0.1 NEW: 이메일만으로 즉시 무료 라이선스 자동 발급!**

## 🎯 주요 기능

- 🆓 **무료 자동 발급**: 이메일 입력만으로 즉시 사용 가능!
- ⚡ **간편한 시작**: 설치 → import → 이메일 입력 → 완료!
- 💰 **FREE 플랜**: STARTER 전략으로 20% 비용 절감
- ⭐ **PREMIUM 플랜**: PRO/PREMIUM 전략으로 최대 88% 절감
- 🔄 **자동 라이선스 관리**: 로컬 저장 및 자동 로드
- 📊 **실시간 통계**: 토큰 사용량, 비용, 절감률 확인

## 💰 비용 절감 효과

```python
# 일반 OpenAI API
월 10,000개 요청 × $0.001/요청 = $10.00

# WOOSAILibrary FREE 플랜
월 10,000개 요청 × $0.0008/요청 = $8.00 (20% 절감)

# WOOSAILibrary PREMIUM 플랜  
월 10,000개 요청 × $0.00012/요청 = $1.20 (88% 절감)

→ 월 $8.80 절약! 연간 $105.60 절약!
```

## 📦 설치

```bash
pip install woosailibrary
```

## 🚀 빠른 시작

### ✨ 첫 실행 (자동 라이선스 발급)

```python
from woosailibrary import WoosAI

# 첫 실행 시 이메일 입력 프롬프트가 나타납니다
client = WoosAI()

# ============================================================
# 🎉 Welcome to WoosAI Library!
# ============================================================
# 
# To get started, we'll generate a FREE license for you.
# This takes just a few seconds and requires only your email.
#
# 📧 Enter your email: your@email.com
#
# ⏳ Generating free license...
#
# ============================================================
# ✅ SUCCESS! Free license generated!
# ============================================================
# 
# 📋 License Key: WOOSAI-FREE-20251122-xxxxxx
# 📅 Valid until: 2025-11-22
# 💳 Plan: FREE
#
# 💾 License saved to: C:\Users\...\config.json
#
# 🚀 You're all set! Starting WoosAI...

# 이제 바로 사용 가능!
response = client.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "AI란 무엇인가요?"}],
    strategy="starter"
)

print(response.choices[0].message.content)
```

### 🔄 두 번째 실행 (자동 로드)

```python
from woosailibrary import WoosAI

# 저장된 라이선스가 자동으로 로드됩니다
client = WoosAI()
# ✓ Loaded license: FREE

# 바로 사용!
response = client.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "Hello!"}]
)
```

### 🎓 OpenAI API 키 설정

```python
import os

# 방법 1: 환경 변수 설정
os.environ['OPENAI_API_KEY'] = 'sk-your-openai-api-key'

from woosailibrary import WoosAI
client = WoosAI()

# 방법 2: 직접 전달
from woosailibrary import WoosAI
client = WoosAI(api_key='sk-your-openai-api-key')

# 방법 3: .env 파일 사용 (추천)
# .env 파일에 OPENAI_API_KEY=sk-your-key 저장
```

## 📊 플랜 비교

| 기능 | FREE | PREMIUM |
|------|------|----------|
| **가격** | 무료 | $9/월 |
| **라이선스 발급** | ✅ 자동 | ✅ 웹사이트 |
| **비용 절감** | ~20% | 최대 88% |
| **사용 전략** | STARTER | PRO + PREMIUM |
| **최적화 방식** | 기본 | 완전 AUTO |
| **지원** | 커뮤니티 | 우선 지원 |

## 🎯 최적화 전략

### FREE 플랜 (STARTER)
```python
client = WoosAI()

response = client.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "질문"}],
    strategy="starter"  # FREE 플랜에서 사용 가능
)
# → 약 20% 비용 절감
```

### PREMIUM 플랜 (PRO + PREMIUM)
```python
client = WoosAI()  # Premium 라이선스 키 사용

# PRO 전략 (균형잡힌 최적화)
response = client.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "질문"}],
    strategy="pro"
)
# → 약 58% 비용 절감

# PREMIUM 전략 (최대 절감)
response = client.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "질문"}],
    strategy="premium"
)
# → 약 88% 비용 절감
```

## 🔐 PREMIUM 업그레이드

FREE 플랜에서 PRO/PREMIUM 전략을 사용하려고 하면:

```python
client = WoosAI()  # FREE 플랜

response = client.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "질문"}],
    strategy="premium"  # Premium 전략 시도
)

# ⚠️  'premium' strategy requires Premium plan.
#     Using 'starter' strategy instead.
#
# ============================================================
# 🚀 Upgrade to Premium
# ============================================================
# 
# 📊 Free Plan Limitations:
#   • Strategy: STARTER only
#   • Savings: ~20%
#   • Support: Community
# 
# ✨ Premium Plan Benefits:
#   • Strategy: PRO + PREMIUM
#   • Savings: Up to 88%
#   • Support: Priority
#   • Price: $9 /month
# 
# 🔗 Upgrade now: https://woos-ai.com/upgrade
# ============================================================
```

**업그레이드 방법:**
1. https://woos-ai.com/upgrade 방문
2. Premium 플랜 구매
3. 발급받은 라이선스 키 입력

```python
# Premium 라이선스로 업그레이드
client = WoosAI(license_key="WOOSAI-PREMIUM-...")

# 이제 모든 전략 사용 가능!
response = client.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "질문"}],
    strategy="premium"  # ✅ 작동!
)
```

## 📚 API 문서

### WoosAI 클래스

```python
WoosAI(api_key=None, license_key=None)
```

**Parameters:**
- `api_key` (str, optional): OpenAI API 키. 제공하지 않으면 `OPENAI_API_KEY` 환경 변수 사용
- `license_key` (str, optional): WoosAI 라이선스 키. 제공하지 않으면 자동 발급

### chat.completions.create()

OpenAI SDK와 호환되는 인터페이스:

```python
client.chat.completions.create(
    model="gpt-4",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Hello!"}
    ],
    strategy="starter",        # "starter", "pro", "premium"
    optimize_input=True,       # 입력 압축 (기본값: True)
    optimize_output=True,      # 출력 최적화 (기본값: True)
    max_tokens=2000,           # 최대 토큰 수
    temperature=0.7            # 응답 다양성
)
```

**Returns:** OpenAI ChatCompletion 응답 객체

### 편의 메서드

```python
# 플랜 정보 확인
plan = client.get_plan()  # "free" or "premium"

# 업그레이드 정보 표시
client.upgrade_info()
```

## 🛠️ 고급 사용법

### 입력 압축만 사용

```python
response = client.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "긴 질문..."}],
    optimize_input=True,   # 입력 압축 활성화
    optimize_output=False  # 출력 최적화 비활성화
)
```

### 출력 최적화만 사용

```python
response = client.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "질문"}],
    optimize_input=False,  # 입력 압축 비활성화
    optimize_output=True   # 출력 최적화 활성화
)
```

### 최적화 없이 사용

```python
# OpenAI SDK와 동일하게 사용
from openai import OpenAI

client = OpenAI(api_key="sk-your-key")
response = client.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "Hello"}]
)
```

## 🔧 로컬 라이선스 관리

라이선스는 다음 위치에 저장됩니다:
```
Windows: C:\Users\[username]\.woosai\config.json
Mac/Linux: ~/.woosai/config.json
```

**라이선스 파일 예시:**
```json
{
  "license": {
    "license_key": "WOOSAI-FREE-20251122-xxxxxx",
    "plan": "free",
    "expires_at": "2025-11-22T00:00:00",
    "email": "your@email.com"
  },
  "version": "1.0.1"
}
```

**라이선스 재설정:**
```python
# 라이선스 파일 삭제 후 다시 실행하면 새로 발급됩니다
import os
from pathlib import Path

config_file = Path.home() / '.woosai' / 'config.json'
if config_file.exists():
    os.remove(config_file)
    print("License reset. Run WoosAI() again to generate new license.")
```

## 🧪 테스트

```bash
# 기본 기능 테스트
python tests/test_basic.py

# 라이선스 시스템 테스트
python tests/test_license.py
```

## 📝 변경 이력

### v1.0.1 (2025-10-23)
- ✨ **NEW:** 이메일만으로 무료 라이선스 자동 발급
- ✨ **NEW:** 로컬 라이선스 자동 관리 (~/.woosai/config.json)
- ✨ **NEW:** Premium 업그레이드 안내 기능
- 🔧 개선: OpenAI SDK 호환 인터페이스
- 🔧 개선: 사용자 경험 개선

### v1.0.0 (2025-01-03)
- 🎉 초기 릴리스
- 입력/출력 최적화 기능
- 3가지 최적화 전략 (STARTER, PRO, PREMIUM)

## 📄 라이선스

MIT License

## 👥 제작

WoosAI Team

## 🔗 링크

- 🌐 웹사이트: https://woos-ai.com
- 📦 PyPI: https://pypi.org/project/woosailibrary/
- 💎 Premium 구매: https://woos-ai.com/upgrade
- 📖 문서: https://woos-ai.com/docs
- 🐛 이슈: https://github.com/sisi010/WOOSAILibrary/issues
- ⭐ GitHub: https://github.com/sisi010/WOOSAILibrary

## 💡 기여

기여를 환영합니다! Pull Request를 보내주세요.

## 📧 문의

support@woosai.com

---

**Made with ❤️ by WoosAI Team**