# WOOSAILibrary

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![GitHub Stars](https://img.shields.io/github/stars/sisi010/WOOSAILibrary.svg)](https://github.com/sisi010/WOOSAILibrary/stargazers)

🚀 AI 비용 최적화 라이브러리 - OpenAI API 비용을 최대 61% 절감
...
## 🎯 주요 기능

- 🆓 **무료 플랜**: 기본 최적화로 17% 비용 절감
- ⭐ **프리미엄 플랜**: 완전 AUTO 최적화로 최대 43% 비용 절감
- 🤖 **자동 전략 선택**: 질문 길이에 따라 최적 전략 자동 선택
- 🔐 **간단한 라이선스**: 라이선스 키로 즉시 프리미엄 활성화
- 📊 **상세 통계**: 토큰 사용량, 비용, 절감률 실시간 확인

## 💰 비용 절감 예시
```python
# 일반 OpenAI API 사용
월 10,000개 요청 × $0.001/요청 = $10.00

# WOOSAILibrary 무료 플랜
월 10,000개 요청 × $0.00083/요청 = $8.30 (17% 절감)

# WOOSAILibrary 프리미엄 플랜
월 10,000개 요청 × $0.00057/요청 = $5.70 (43% 절감)

→ 월 $4.30 절약! 연간 $51.60 절약!
```

## 📦 설치
```bash
pip install woosailibrary
```

## 🚀 빠른 시작

### 무료 플랜
```python
from woosailibrary import WoosAI

ai = WoosAI(api_key="sk-your-openai-key")
response = ai.chat("AI란 무엇인가요?")

print(response["content"])
# 출력: AI(인공지능)는 인간의 지능을 모방하여...

print(f"절감: {response['stats']['savings']}")
# 출력: 절감: 17%
```

### 프리미엄 플랜
```python
from woosailibrary import WoosAI

ai = WoosAI(
    api_key="sk-your-openai-key",
    license_key="WOOSAI-PREMIUM-20251119-ABC123"
)

response = ai.chat("인공지능 기술의 발전 역사를 설명해주세요")

print(f"전략: {response['stats']['strategy_used']}")
# 출력: 전략: pro

print(f"절감: {response['stats']['savings']}")
# 출력: 절감: 43%
```

### 환경 변수 사용 (추천)
```bash
# .env 파일
OPENAI_API_KEY=sk-your-key
WOOSAI_LICENSE=WOOSAI-PREMIUM-20251119-ABC123
```
```python
from woosailibrary import WoosAI

ai = WoosAI()  # 자동으로 환경 변수에서 로드!
response = ai.chat("질문")
```

## 📊 플랜 비교

| 기능 | 무료 | 프리미엄 |
|------|------|----------|
| **비용 절감** | 17% | 최대 43% |
| **월 요청 수** | 1,000개 | 50,000개 |
| **최적화 방식** | 기본 (STARTER) | 완전 AUTO |
| **전략 자동 선택** | ❌ | ✅ |
| **상세 통계** | ✅ | ✅ |
| **가격** | 무료 | $20/월 |

## 🎯 프리미엄 AUTO 최적화

프리미엄 플랜은 질문 길이에 따라 자동으로 최적 전략을 선택합니다:

- **짧은 질문** (< 18토큰): STARTER 전략 → 17% 절감
- **중간 질문** (18-60토큰): PRO 전략 → 43% 절감
- **긴 질문** (> 60토큰): PREMIUM 전략 → 61% 절감
```python
ai = WoosAI(license_key="WOOSAI-PREMIUM-...")

# 짧은 질문
response = ai.chat("AI란?")
# → STARTER 전략, 17% 절감

# 긴 질문
response = ai.chat("인공지능 기술의 발전 역사와 현재 활용 사례를 자세히 설명해주세요")
# → PRO 전략, 43% 절감
```

## 🔑 라이선스 발급

프리미엄 라이선스는 [WoosAI 홈페이지](https://woosai.com/premium)에서 구매하세요.

**개발/테스트용 라이선스 생성:**
```bash
python tools/license_generator.py --plan PREMIUM --days 30
```

## 📚 API 문서

### WoosAI 클래스
```python
WoosAI(api_key=None, license_key=None)
```

**Parameters:**
- `api_key` (str): OpenAI API 키 (또는 OPENAI_API_KEY 환경 변수)
- `license_key` (str): 프리미엄 라이선스 키 (또는 WOOSAI_LICENSE 환경 변수)

### chat() 메서드
```python
ai.chat(message, compress=True)
```

**Parameters:**
- `message` (str): 질문 또는 메시지
- `compress` (bool): 입력 압축 사용 (기본값: True)

**Returns:**
```python
{
    "content": "AI 답변 내용...",
    "stats": {
        "plan": "무료 플랜",
        "strategy_used": "starter",
        "savings": "17%",
        "tokens": {
            "input": 11,
            "output": 115,
            "total": 126,
            "saved": 0
        },
        "cost": {
            "input": "$0.000002",
            "output": "$0.000069",
            "total": "$0.000071"
        },
        "usage": "1/1000"
    },
    "error": None
}
```

### 기타 메서드
```python
# 플랜 정보 확인
info = ai.get_plan_info()

# 플랜 비교
ai.compare_plans()

# 사용량 확인
usage = ai.get_usage()
```

## 🛠️ 개발 도구

### 라이선스 생성
```bash
# 프리미엄 라이선스 (30일)
python tools/license_generator.py --plan PREMIUM --days 30

# 여러 개 생성
python tools/license_generator.py --plan PREMIUM --days 30 --batch 5

# 라이선스 검증
python tools/license_generator.py --verify WOOSAI-PREMIUM-20251119-ABC123
```

## 🧪 테스트
```bash
# 라이선스 시스템 테스트
python tests/test_license.py

# 사용 예시 실행
python example_license.py
```

## 📝 라이선스

MIT License

## 👥 제작

WoosAI Team

## 🔗 링크

- 홈페이지: https://woosai.com
- 문서: https://woosai.com/docs
- 프리미엄 구매: https://woosai.com/premium
- 이슈: https://github.com/woosai/woosailibrary/issues

## 💡 기여

기여를 환영합니다! Pull Request를 보내주세요.

## 📧 문의

support@woosai.com