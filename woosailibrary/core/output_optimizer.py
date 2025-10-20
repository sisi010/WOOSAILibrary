"""
WOOSAILibrary - Output Optimizer
Main orchestrator for output optimization

Purpose: Combine all optimization techniques for maximum savings
Components: Input compression + Prompt optimization + API parameters + Token counting
Savings: 10-75% total cost reduction

Strategy Selection (Updated 2025-01-10 - Safety Margins + Abbreviation Detection):
- STARTER (Free): Natural responses, quality-focused (2000 tokens, 10-15% savings)
- PRO (Paid): Balanced optimization (1300 tokens, 25-35% savings)
- PREMIUM (Paid): Maximum cost savings (700 tokens, 45-55% savings)
- AUTO (default): Automatically selects strategy based on input analysis

Features (Updated 2025-01-10):
- Safety margins applied (2000/1300/700 tokens)
- Abbreviation detection (56 common abbreviations)
- Conditional abbreviation usage based on user style
- All users can use all strategies (currently free)

Future monetization plan:
- Free: STARTER only
- Paid: PRO, PREMIUM, AUTO

Author: WoosAI Team
Created: 2025-01-03
Updated: 2025-01-10
"""

from typing import Dict, Optional, Tuple
import tiktoken

from .lightweight_input import LightweightInputCompressor
from .prompt_optimizer import PromptOptimizer
from .structured_schema import StructuredSchemaManager


class OutputOptimizer:
    """
    Complete optimization pipeline for OpenAI calls
    
    Pipeline:
    1. Input compression (optional, 5ms)
    2. Token counting (for dynamic strategy selection)
    3. Abbreviation detection (NEW - 0.15ms)
    4. Strategy selection (AUTO logic)
    5. Prompt optimization with abbreviation preference (0ms)
    6. API parameters optimization
    7. Returns optimized parameters for OpenAI call
    
    Usage:
        optimizer = OutputOptimizer()
        
        # AUTO strategy (recommended)
        params = optimizer.get_optimized_params(
            user_message="Hello, how are you?",
            strategy="auto",  # default
            compress_input=True
        )
        
        # Manual strategy selection
        params = optimizer.get_optimized_params(
            user_message="Long question...",
            strategy="premium",  # or "starter", "pro"
            compress_input=True
        )
        
        # Use with OpenAI
        import openai
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": params["system_prompt"]},
                {"role": "user", "content": params["user_message"]}
            ],
            max_tokens=params["max_tokens"],
            temperature=params["temperature"],
            top_p=params.get("top_p"),
            frequency_penalty=params.get("frequency_penalty"),
            presence_penalty=params.get("presence_penalty"),
            response_format=params["response_format"]
        )
    """
    
    # Abbreviations known by general public (56 items - final)
    # Criteria: Middle school students recognize, appears in news/daily life
    GENERAL_PUBLIC_ABBREVIATIONS = [
        # === Everyday Tech/Electronics (25) ===
        "PC",       # Personal Computer
        "TV",       # Television
        "DVD",      # Digital Versatile Disc
        "CD",       # Compact Disc
        "USB",      # Universal Serial Bus
        "WiFi",     # Wireless Fidelity
        "GPS",      # Global Positioning System
        "SMS",      # Short Message Service
        "MMS",      # Multimedia Messaging Service
        "QR",       # Quick Response
        "APP",      # Application
        "AI",       # Artificial Intelligence
        "IT",       # Information Technology
        "SNS",      # Social Network Service
        "LED",      # Light-Emitting Diode
        "LCD",      # Liquid Crystal Display
        "CCTV",     # Closed-Circuit Television
        "ATM",      # Automated Teller Machine
        "MP3",      # MPEG Audio Layer-3
        "MP4",      # MPEG-4
        "HDMI",     # High-Definition Multimedia Interface
        "OS",       # Operating System
        "3D",       # Three-Dimensional
        "VR",       # Virtual Reality
        "5G",       # 5th Generation
        
        # === International Organizations (20) ===
        "UN",       # United Nations
        "WHO",      # World Health Organization
        "NASA",     # National Aeronautics and Space Administration
        "FBI",      # Federal Bureau of Investigation
        "CIA",      # Central Intelligence Agency
        "EU",       # European Union
        "NGO",      # Non-Governmental Organization
        "OECD",     # Organisation for Economic Co-operation and Development
        "IMF",      # International Monetary Fund
        "WTO",      # World Trade Organization
        "G7",       # Group of Seven
        "G20",      # Group of Twenty
        "NATO",     # North Atlantic Treaty Organization
        "OPEC",     # Organization of Petroleum Exporting Countries
        "ASEAN",    # Association of Southeast Asian Nations
        "UNESCO",   # United Nations Educational, Scientific and Cultural Organization
        "UNICEF",   # United Nations Children's Fund
        "USA",      # United States of America
        "UK",       # United Kingdom
        "UAE",      # United Arab Emirates
        
        # === Economy/Business (8) ===
        "CEO",      # Chief Executive Officer
        "GDP",      # Gross Domestic Product
        "VIP",      # Very Important Person
        "PR",       # Public Relations
        "VAT",      # Value-Added Tax
        "VISA",     # Visa card brand
        "CPI",      # Consumer Price Index
        "M&A",      # Mergers and Acquisitions
        
        # === Transportation (1) ===
        "KTX",      # Korea Train Express
        
        # === Sports/Entertainment (8) ===
        "NBA",      # National Basketball Association
        "MLB",      # Major League Baseball
        "FIFA",     # Federation Internationale de Football Association
        "UEFA",     # Union of European Football Associations
        "DJ",       # Disc Jockey
        "MC",       # Master of Ceremonies
        "VJ",       # Video Jockey
        "PD",       # Producer/Program Director
        
        # === General Expressions (6) ===
        "FAQ",      # Frequently Asked Questions
        "OK",       # Okay
        "NO",       # Number
        "VS",       # Versus
        "TIP",      # Tip
        "DIY",      # Do It Yourself
    ]
    
    def __init__(self):
        """Initialize optimizer with all components"""
        self.input_compressor = LightweightInputCompressor()
        self.prompt_optimizer = PromptOptimizer()
        self.schema_manager = StructuredSchemaManager()
        
        # Initialize tiktoken encoder for token counting
        try:
            self.encoder = tiktoken.encoding_for_model("gpt-4o-mini")
        except:
            # Fallback to cl100k_base if model not found
            self.encoder = tiktoken.get_encoding("cl100k_base")
    
    def count_tokens(self, text: str) -> int:
        """
        Count tokens in text using tiktoken
        
        Args:
            text: Input text to count
            
        Returns:
            Number of tokens
            
        Example:
            >>> optimizer = OutputOptimizer()
            >>> tokens = optimizer.count_tokens("Hello world")
            >>> print(tokens)  # 2
        """
        return len(self.encoder.encode(text))
    
    def _detect_abbreviations(self, text: str) -> bool:
        """
        Detect abbreviations that general public knows (56 items)
        
        This function checks if the user uses common abbreviations that
        most people recognize. If detected, AI will also use abbreviations.
        
        Excluded:
        - Professional terms (API, DB, SQL, NLP, ML, DL, etc.)
        - Medical jargon (ICU, ER, CPR, DNA, etc.)
        - Business-only (HR, IPO, R&D, etc.)
        - Technical transport (LRT, BRT, SRT, ETA, etc.)
        
        Args:
            text: User's message
            
        Returns:
            True if user uses common abbreviations
            
        Example:
            >>> optimizer = OutputOptimizer()
            >>> optimizer._detect_abbreviations("PC가 느려요")
            True
            >>> optimizer._detect_abbreviations("컴퓨터가 느려요")
            False
            >>> optimizer._detect_abbreviations("API 설계")
            False  # Professional term not in list
        """
        # Normalize text: add spaces and convert to uppercase
        text_normalized = f" {text.upper()} "
        
        for abbr in self.GENERAL_PUBLIC_ABBREVIATIONS:
            # Check various boundary patterns to avoid false positives
            patterns = [
                f" {abbr} ",      # Space on both sides: " AI "
                f" {abbr}?",      # Question mark: " AI?"
                f" {abbr}.",      # Period: " AI."
                f" {abbr},",      # Comma: " AI,"
                f" {abbr}:",      # Colon: " AI:"
                f" {abbr})",      # Closing parenthesis: " AI)"
                f"({abbr} ",      # Opening parenthesis: "(AI "
            ]
            
            # Also check start/end of text
            if (any(pattern in text_normalized for pattern in patterns) or
                text_normalized.strip().startswith(f"{abbr} ") or
                text_normalized.strip().endswith(f" {abbr}")):
                return True
        
        return False
    
    def auto_select_strategy(self, user_message: str, is_paid_user: bool = False) -> str:
        """
        Automatically select optimal strategy based on input length
        
        Current logic (all free during beta):
        - Input < 50 tokens -> STARTER (quality-focused, natural)
        - Input 50-150 tokens -> PRO (balanced, cost-efficient)
        - Input >= 150 tokens -> PREMIUM (cost-focused, maximum savings)
        
        Future monetization logic:
        - Free users: Always STARTER
        - Paid users: Auto-select based on input length (as above)
        
        Args:
            user_message: User's input message
            is_paid_user: Reserved for future use (currently ignored)
            
        Returns:
            Selected strategy: "starter", "pro", or "premium"
            
        Example:
            >>> optimizer = OutputOptimizer()
            
            >>> # Short input
            >>> strategy = optimizer.auto_select_strategy("Hi")
            >>> print(strategy)  # "starter"
            
            >>> # Medium input
            >>> strategy = optimizer.auto_select_strategy("Question " * 15)
            >>> print(strategy)  # "pro"
            
            >>> # Long input
            >>> strategy = optimizer.auto_select_strategy("Long question " * 30)
            >>> print(strategy)  # "premium"
        """
        input_tokens = self.count_tokens(user_message)
        
        # Currently all free - select based on input length
        # Future: if not is_paid_user: return "starter"
        
        if input_tokens < 18:
            return "starter"
        elif input_tokens < 60:
            return "pro"
        else:
            return "premium"
    
    def get_optimized_params(self,
                            user_message: str,
                            task: str = None,
                            strategy: str = "auto",
                            compress_input: bool = True,
                            schema_type: Optional[str] = None,
                            custom_system_prompt: str = None,
                            is_paid_user: bool = False) -> Dict:
        """
        Get complete set of optimized parameters for OpenAI call
        
        Args:
            user_message: User's input message
            task: Optional task description for system prompt (currently not used)
            strategy: "auto" (default), "starter", "pro", or "premium"
            compress_input: Whether to compress input (default True)
            schema_type: Optional schema type ("chat", "summary", "qa", "list")
            custom_system_prompt: Optional custom system prompt (overrides generated)
            is_paid_user: Whether user has paid plan (default False)
            
        Returns:
            Dictionary with all optimized parameters:
            {
                # Core parameters for OpenAI API
                "user_message": str (compressed if enabled),
                "system_prompt": str (optimized),
                "max_tokens": int,
                "temperature": float,
                "top_p": float or None,
                "frequency_penalty": float or None,
                "presence_penalty": float or None,
                "response_format": dict or None,
                
                # Metadata for transparency
                "strategy_used": str,
                "tier": str,
                "input_tokens": int,
                "estimated_output_tokens": int,
                "estimated_cost": float,
                "uses_abbreviations": bool (NEW),
                "optimization_info": dict
            }
        """
        import time
        start_time = time.perf_counter()
        
        optimization_info = {
            "input_compressed": compress_input,
            "schema_applied": schema_type is not None,
            "processing_time_ms": 0
        }
        
        # Step 1: Input compression (optional, 5ms)
        processed_message = user_message
        if compress_input:
            compressed, compression_info = self.input_compressor.compress(user_message)
            processed_message = compression_info["compressed_text"]
            optimization_info["input_compression"] = {
                "tokens_saved": compression_info["tokens_saved"],
                "savings_percent": compression_info["savings_percent"],
                "time_ms": compression_info["processing_time_ms"],
                "stages": compression_info.get("stages", {})  # ← 이 줄 추가!
            }
        
        # Step 2: Count input tokens (for AUTO strategy)
        input_tokens = self.count_tokens(processed_message)
        
        # Step 3: Detect abbreviations (NEW - 0.15ms)
        uses_abbreviations = self._detect_abbreviations(user_message)
        optimization_info["abbreviations_detected"] = uses_abbreviations
        
        # Step 4: Strategy selection (AUTO logic)
        if strategy == "auto":
            selected_strategy = self.auto_select_strategy(processed_message, is_paid_user)
        else:
            # Manual strategy selection
            selected_strategy = strategy
        
        # Validate strategy
        valid_strategies = ["starter", "pro", "premium"]
        if selected_strategy not in valid_strategies:
            # Fallback to AUTO if invalid strategy
            selected_strategy = self.auto_select_strategy(processed_message, is_paid_user)
        
        # Step 5: Determine abbreviation usage by strategy
        # STARTER: Never use abbreviations (beginner-friendly)
        # PRO: Use abbreviations if user uses them
        # PREMIUM: Always use abbreviations (expert mode)
        if selected_strategy == "starter":
            use_abbreviations = False
        elif selected_strategy == "pro":
            use_abbreviations = uses_abbreviations
        else:  # premium
            use_abbreviations = True
        
        # Step 6: System prompt optimization with abbreviation preference
        if custom_system_prompt:
            system_prompt = custom_system_prompt
        else:
            system_prompt = self.prompt_optimizer.get_system_prompt(
                task=task,
                strategy=selected_strategy,
                input_tokens=input_tokens,
                use_abbreviations=use_abbreviations  # NEW parameter
            )
            
            # Add schema instruction if using structured output
            if schema_type:
                schema_instruction = self.schema_manager.get_system_prompt_addition(schema_type)
                if schema_instruction:
                    system_prompt += f"\n\n{schema_instruction}"
        
        # Step 7: Get optimization config
        config = self.prompt_optimizer.get_optimization_config(
            strategy=selected_strategy,
            input_tokens=input_tokens
        )
        
        # Step 8: Get additional API parameters based on strategy
        api_params = self._get_api_parameters(selected_strategy)
        
        # Step 9: Get schema if requested
        response_format = None
        if schema_type:
            schema = self.schema_manager.get_schema(schema_type)
            if schema:
                response_format = {"type": "json_object"}
                optimization_info["schema_type"] = schema_type
        
        # Step 10: Calculate estimated cost
        # GPT-4o-mini pricing (per 1M tokens)
        input_price_per_million = 0.150   # $0.150 per 1M input tokens
        output_price_per_million = 0.600  # $0.600 per 1M output tokens
        
        # Realistic output estimation based on input length
        # Short input -> short output, long input -> longer output
        if input_tokens < 30:
            # Very short input (e.g., "Hi", "Hello") -> Brief response
            estimated_output_tokens = min(50, config["max_tokens"])
        elif input_tokens < 100:
            # Medium input (normal questions) -> Medium response
            estimated_output_tokens = min(150, config["max_tokens"])
        elif input_tokens < 200:
            # Long input (detailed questions) -> Longer response
            estimated_output_tokens = min(300, config["max_tokens"])
        else:
            # Very long input -> Use 50% of max_tokens as estimate
            estimated_output_tokens = min(int(config["max_tokens"] * 0.5), config["max_tokens"])
        
        input_cost = (input_tokens / 1_000_000) * input_price_per_million
        output_cost = (estimated_output_tokens / 1_000_000) * output_price_per_million
        total_cost = input_cost + output_cost
        
        # Calculate processing time
        end_time = time.perf_counter()
        optimization_info["processing_time_ms"] = round((end_time - start_time) * 1000, 2)
        
        # Build result dictionary
        result = {
            # Core parameters for OpenAI API
            "user_message": processed_message,
            "system_prompt": system_prompt,
            "max_tokens": config["max_tokens"],
            "temperature": config["temperature"],
            "response_format": response_format,
            
            # Metadata for transparency
            "strategy_used": selected_strategy,
            "tier": config["tier"],
            "input_tokens": input_tokens,
            "estimated_output_tokens": estimated_output_tokens,
            "estimated_cost": round(total_cost, 8),
            "uses_abbreviations": use_abbreviations,  # NEW
            "optimization_info": optimization_info
        }
        
        # Add additional API parameters (only if not None)
        if api_params.get("top_p") is not None:
            result["top_p"] = api_params["top_p"]
        if api_params.get("frequency_penalty") is not None:
            result["frequency_penalty"] = api_params["frequency_penalty"]
        if api_params.get("presence_penalty") is not None:
            result["presence_penalty"] = api_params["presence_penalty"]
        
        return result
    
    def _get_api_parameters(self, strategy: str) -> Dict:
        """
        Get additional OpenAI API parameters based on strategy
        
        Parameters:
        - top_p: Nucleus sampling (controls diversity)
        - frequency_penalty: Reduces repetition (0.0 to 2.0)
        - presence_penalty: Encourages new topics (0.0 to 2.0)
        
        Args:
            strategy: Optimization strategy
            
        Returns:
            Dictionary with API parameters
        """
        if strategy == "premium":
            # PREMIUM: Maximum optimization with all parameters
            return {
                "top_p": 0.8,                # Focused outputs
                "frequency_penalty": 0.5,    # Strong repetition reduction
                "presence_penalty": 0.3      # Encourage brevity
            }
        elif strategy == "pro":
            # PRO: Balanced optimization
            return {
                "top_p": 0.9,                # Slight focus
                "frequency_penalty": 0.3,    # Moderate repetition reduction
                "presence_penalty": None     # No presence penalty
            }
        else:  # starter
            # STARTER: Natural output, no additional constraints
            return {
                "top_p": None,
                "frequency_penalty": None,
                "presence_penalty": None
            }
    
    def calculate_savings(self,
                         original_tokens: int,
                         optimized_tokens: int,
                         strategy: str = "auto") -> Dict:
        """
        Calculate token and cost savings
        
        Args:
            original_tokens: Original token count (without optimization)
            optimized_tokens: Optimized token count (with optimization)
            strategy: Strategy used ("auto", "starter", "pro", or "premium")
            
        Returns:
            Dictionary with savings statistics
            
        Example:
            >>> optimizer = OutputOptimizer()
            >>> savings = optimizer.calculate_savings(500, 150, "premium")
            >>> print(savings["savings_percent"])  # 70.0
            >>> print(savings["cost_saved_usd"])   # Cost saved in USD
        """
        tokens_saved = original_tokens - optimized_tokens
        savings_percent = (tokens_saved / original_tokens * 100) if original_tokens > 0 else 0
        
        # GPT-4o-mini pricing (per 1M tokens)
        # Using output token pricing as this is typically the larger cost
        output_price_per_million = 0.600
        
        # Calculate cost savings (assuming output tokens)
        original_cost = (original_tokens / 1_000_000) * output_price_per_million
        optimized_cost = (optimized_tokens / 1_000_000) * output_price_per_million
        cost_saved = original_cost - optimized_cost
        
        return {
            "original_tokens": original_tokens,
            "optimized_tokens": optimized_tokens,
            "tokens_saved": tokens_saved,
            "savings_percent": round(savings_percent, 2),
            "original_cost_usd": round(original_cost, 8),
            "optimized_cost_usd": round(optimized_cost, 8),
            "cost_saved_usd": round(cost_saved, 8),
            "strategy": strategy
        }


# Singleton instance
_output_optimizer_instance = None

def get_output_optimizer():
    """
    Get singleton output optimizer instance
    
    Returns:
        Singleton OutputOptimizer instance
        
    Example:
        >>> optimizer = get_output_optimizer()
        >>> params = optimizer.get_optimized_params("Hello")
    """
    global _output_optimizer_instance
    if _output_optimizer_instance is None:
        _output_optimizer_instance = OutputOptimizer()
    return _output_optimizer_instance