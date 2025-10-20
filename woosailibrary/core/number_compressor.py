"""
WOOSAILibrary - Number Compressor V2
Enhanced number compression with better pattern matching

Updates (2025-10-13):
- Improved Korean unit handling
- Better currency compression
- Enhanced date/time patterns
- Multiple number format support
- Increased compression rate: 3.9% → 30%+ target

Author: WoosAI Team
Created: 2025-01-03
Updated: 2025-10-13
"""

import re
from typing import Dict, Tuple


class NumberCompressor:
    """
    Enhanced number compression for Korean text
    
    Compression improvements:
    - 1,500,000원 → 150w
    - 10억원 → 10e
    - 2024년 1월 → '24.1
    - 3개월 → 3mo
    - 150만원 → 150w
    
    Target: 30-45% compression on number-heavy text
    """
    
    def __init__(self):
        """Initialize enhanced number compressor"""
        pass
    
    def compress(self, text: str) -> Tuple[str, Dict]:
        """
        Compress numbers in text with enhanced patterns
        
        Args:
            text: Input text
            
        Returns:
            Tuple of (compressed_text, compression_info)
        """
        if not text or not text.strip():
            return text, self._empty_info()
        
        original_length = len(text)
        compressed = text
        replacements = 0
        
        # Stage 1: Korean number units (만/억/조)
        compressed, count1 = self._compress_korean_units(compressed)
        replacements += count1
        
        # Stage 2: Large plain numbers
        compressed, count2 = self._compress_large_numbers(compressed)
        replacements += count2
        
        # Stage 3: Currency (원)
        compressed, count3 = self._compress_currency(compressed)
        replacements += count3
        
        # Stage 4: Years
        compressed, count4 = self._compress_years(compressed)
        replacements += count4
        
        # Stage 5: Months/Days
        compressed, count5 = self._compress_time_units(compressed)
        replacements += count5
        
        # Stage 6: Percentages
        compressed, count6 = self._compress_percentages(compressed)
        replacements += count6
        
        final_length = len(compressed)
        chars_saved = original_length - final_length
        
        return compressed, {
            "original_length": original_length,
            "compressed_length": final_length,
            "chars_saved": chars_saved,
            "replacements": replacements,
            "compression_ratio": round(chars_saved / original_length, 4) if original_length > 0 else 0
        }
    
    def _compress_korean_units(self, text: str) -> Tuple[str, int]:
        """
        Compress Korean number units (만/억/조)
        
        Examples:
        - 150만원 → 150w
        - 10억원 → 10e
        - 5조원 → 5t
        """
        count = 0
        
        # 조 (trillion) - 1,000,000,000,000
        def replace_jo(match):
            nonlocal count
            num = match.group(1)
            count += 1
            return f"{num}t"
        
        text = re.sub(r'(\d+(?:\.\d+)?)조', replace_jo, text)
        
        # 억 (hundred million) - 100,000,000
        def replace_eok(match):
            nonlocal count
            num = match.group(1)
            count += 1
            return f"{num}e"
        
        text = re.sub(r'(\d+(?:\.\d+)?)억', replace_eok, text)
        
        # 만 (ten thousand) - 10,000
        def replace_man(match):
            nonlocal count
            num = match.group(1)
            count += 1
            return f"{num}w"
        
        text = re.sub(r'(\d+(?:\.\d+)?)만', replace_man, text)
        
        return text, count
    
    def _compress_large_numbers(self, text: str) -> Tuple[str, int]:
        """
        Compress large plain numbers
        
        Examples:
        - 1500000 → 150w
        - 10000000 → 1000w
        - 50000 → 5w
        """
        count = 0
        
        def replace_large(match):
            nonlocal count
            num_str = match.group(0)
            num = int(num_str)
            
            # 조 단위 (trillion, 12 zeros)
            if num >= 1_000_000_000_000:
                count += 1
                jo = num / 1_000_000_000_000
                if jo == int(jo):
                    return f"{int(jo)}t"
                else:
                    return f"{jo:.1f}t"
            
            # 억 단위 (hundred million, 8 zeros)
            elif num >= 100_000_000:
                count += 1
                eok = num / 100_000_000
                if eok == int(eok):
                    return f"{int(eok)}e"
                else:
                    return f"{eok:.1f}e"
            
            # 만 단위 (ten thousand, 4 zeros)
            elif num >= 10_000:
                count += 1
                man = num / 10_000
                if man == int(man):
                    return f"{int(man)}w"
                else:
                    return f"{man:.1f}w"
            
            # 천 단위 (thousand)
            elif num >= 1_000:
                count += 1
                return f"{num // 1000}k"
            
            return num_str
        
        # Match 4+ digit numbers
        text = re.sub(r'\b\d{4,}\b', replace_large, text)
        
        return text, count
    
    def _compress_currency(self, text: str) -> Tuple[str, int]:
        """
        Enhanced currency compression
        
        Examples:
        - 1500000원 → 150w원
        - 150만원 → 150w (already compressed)
        - 10억원 → 10e (already compressed)
        """
        count = 0
        
        # Already compressed with units (w/e/t)
        # Just remove redundant 원
        def remove_redundant_won(match):
            nonlocal count
            base = match.group(1)
            unit = match.group(2)
            count += 1
            return f"{base}{unit}"  # Remove 원
        
        text = re.sub(r'(\d+(?:\.\d+)?)(w|e|t)원', remove_redundant_won, text)
        
        # Compress remaining numbers with 원
        def compress_won(match):
            nonlocal count
            num_str = match.group(1)
            
            # Already compressed (w/e/t)
            if re.search(r'[wet]$', num_str):
                return match.group(0)
            
            try:
                num = int(num_str)
                
                if num >= 1_000_000_000_000:
                    count += 1
                    return f"{num / 1_000_000_000_000:.0f}t"
                elif num >= 100_000_000:
                    count += 1
                    return f"{num / 100_000_000:.0f}e"
                elif num >= 10_000:
                    count += 1
                    return f"{num / 10_000:.0f}w"
                elif num >= 1_000:
                    count += 1
                    return f"{num / 1_000:.0f}k"
            except:
                pass
            
            return match.group(0)
        
        text = re.sub(r'(\d+)원', compress_won, text)
        
        return text, count
    
    def _compress_years(self, text: str) -> Tuple[str, int]:
        """
        Enhanced year compression
        
        Examples:
        - 2024년 → '24
        - 2024년도 → '24
        - 2023년 1월 → '23.1
        """
        count = 0
        
        # Year with month (2024년 1월 → '24.1)
        def replace_year_month(match):
            nonlocal count
            year = match.group(1)
            month = match.group(2)
            count += 1
            return f"'{year[-2:]}.{month}"
        
        text = re.sub(r'(20\d{2}|19\d{2})년\s*(\d{1,2})월', replace_year_month, text)
        
        # Year only (2024년 or 2024년도 → '24)
        def replace_year(match):
            nonlocal count
            year = match.group(1)
            count += 1
            return f"'{year[-2:]}"
        
        text = re.sub(r'(20\d{2}|19\d{2})년(?:도)?', replace_year, text)
        
        return text, count
    
    def _compress_time_units(self, text: str) -> Tuple[str, int]:
        """
        Compress time units
        
        Examples:
        - 12개월 → 12mo
        - 30일 → 30d
        - 5년 → 5y
        """
        count = 0
        
        # 개월 (months)
        def replace_months(match):
            nonlocal count
            num = match.group(1)
            count += 1
            return f"{num}mo"
        
        text = re.sub(r'(\d+)개월', replace_months, text)
        
        # 일 (days) - but not 일요일, 월요일 etc
        def replace_days(match):
            nonlocal count
            num = match.group(1)
            # Check if not followed by 요일
            count += 1
            return f"{num}d"
        
        text = re.sub(r'(\d+)일(?!요)', replace_days, text)
        
        # 년 (years) - not already compressed
        def replace_years(match):
            nonlocal count
            num = match.group(1)
            count += 1
            return f"{num}y"
        
        text = re.sub(r'(\d+)년(?!도)', replace_years, text)
        
        return text, count
    
    def _compress_percentages(self, text: str) -> Tuple[str, int]:
        """
        Compress percentages
        
        Examples:
        - 35퍼센트 → 35%
        - 50프로 → 50%
        """
        count = 0
        
        # 퍼센트
        def replace_percent1(match):
            nonlocal count
            num = match.group(1)
            count += 1
            return f"{num}%"
        
        text = re.sub(r'(\d+(?:\.\d+)?)퍼센트', replace_percent1, text)
        
        # 프로
        def replace_percent2(match):
            nonlocal count
            num = match.group(1)
            count += 1
            return f"{num}%"
        
        text = re.sub(r'(\d+(?:\.\d+)?)프로', replace_percent2, text)
        
        return text, count
    
    def _empty_info(self) -> Dict:
        """Return empty info for empty input"""
        return {
            "original_length": 0,
            "compressed_length": 0,
            "chars_saved": 0,
            "replacements": 0,
            "compression_ratio": 0
        }


# Singleton
_number_compressor = None

def get_number_compressor():
    """Get singleton number compressor"""
    global _number_compressor
    if _number_compressor is None:
        _number_compressor = NumberCompressor()
    return _number_compressor