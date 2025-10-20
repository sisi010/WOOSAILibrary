"""
WOOSAILibrary - Basic Usage Examples
Simple examples showing how to use the library

This file demonstrates:
1. Quick Start (simplest usage)
2. Strategy Selection (speed, maximum, auto)
3. With/Without Input Compression
4. Cost Calculation
5. Real OpenAI API Integration

Note: Set your OPENAI_API_KEY in .env file before running

Author: WoosAI Team
Created: 2025-01-08
"""

import sys
import os

# Add parent directory to path for local development
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core import get_output_optimizer
import openai
from dotenv import load_dotenv


# ============================================================
# Setup
# ============================================================

# Load environment variables from .env file
load_dotenv()

# Set your OpenAI API key
# Option 1: From .env file (recommended)
openai.api_key = os.getenv("OPENAI_API_KEY")

# Option 2: Set directly (not recommended for production)
# openai.api_key = "sk-your-api-key-here"

model = "gpt-4o-mini"  # or "gpt-4", "gpt-3.5-turbo", etc.


# ============================================================
# Example 1: Quick Start (Simplest Usage)
# ============================================================

def example_1_quick_start():
    """
    Simplest way to use the library
    Just 3 lines of code!
    """
    print("\n" + "=" * 60)
    print("Example 1: Quick Start")
    print("=" * 60)
    
    # Step 1: Create optimizer
    optimizer = get_output_optimizer()
    
    # Step 2: Get optimized parameters (AUTO strategy by default)
    params = optimizer.get_optimized_params(
        user_message="What is the capital of France?",
        strategy="auto"  # Automatically selects best strategy
    )
    
    # Step 3: Use with OpenAI
    messages = []
    if params["system_prompt"]:
        messages.append({"role": "system", "content": params["system_prompt"]})
    messages.append({"role": "user", "content": params["user_message"]})
    
    response = openai.chat.completions.create(
        model=model,
        messages=messages,
        max_tokens=params["max_tokens"],
        temperature=params["temperature"]
    )
    
    print(f"Question: What is the capital of France?")
    print(f"Answer: {response.choices[0].message.content}")
    print(f"\nStrategy used: {params['strategy_used']}")
    print(f"Input tokens: {params['input_tokens']}")
    print(f"Output tokens: {response.usage.completion_tokens}")
    print(f"Cost: ${params['estimated_cost']:.8f}")


# ============================================================
# Example 2: Strategy Comparison
# ============================================================

def example_2_strategies():
    """
    Compare different optimization strategies
    - SPEED: Quality-focused, natural responses
    - MAXIMUM: Cost-focused, controlled output
    - AUTO: Automatically selects best strategy
    """
    print("\n" + "=" * 60)
    print("Example 2: Strategy Comparison")
    print("=" * 60)
    
    optimizer = get_output_optimizer()
    user_message = "Explain machine learning in simple terms."
    
    strategies = ["speed", "maximum", "auto"]
    
    for strategy in strategies:
        print(f"\n--- {strategy.upper()} Strategy ---")
        
        params = optimizer.get_optimized_params(
            user_message=user_message,
            strategy=strategy,
            compress_input=True
        )
        
        print(f"System prompt: '{params['system_prompt']}'")
        print(f"Max tokens: {params['max_tokens']}")
        print(f"Temperature: {params['temperature']}")
        print(f"Estimated cost: ${params['estimated_cost']:.8f}")
        
        # Note: Remove this comment to make actual API calls
        # response = openai.chat.completions.create(...)


# ============================================================
# Example 3: Korean Language Support
# ============================================================

def example_3_korean():
    """
    Korean language works perfectly
    System prompts are in English, but answers will be in Korean
    """
    print("\n" + "=" * 60)
    print("Example 3: Korean Language Support")
    print("=" * 60)
    
    optimizer = get_output_optimizer()
    
    # Korean question
    korean_question = "인공지능이란 무엇인가요?"
    
    params = optimizer.get_optimized_params(
        user_message=korean_question,
        strategy="auto",
        compress_input=True
    )
    
    print(f"Korean question: {korean_question}")
    print(f"Strategy used: {params['strategy_used']}")
    print(f"System prompt (English): '{params['system_prompt']}'")
    print(f"Note: Answer will be in Korean even though system prompt is English")
    
    # Make API call
    messages = []
    if params["system_prompt"]:
        messages.append({"role": "system", "content": params["system_prompt"]})
    messages.append({"role": "user", "content": params["user_message"]})
    
    response = openai.chat.completions.create(
        model=model,
        messages=messages,
        max_tokens=params["max_tokens"],
        temperature=params["temperature"]
    )
    
    print(f"\nAnswer (Korean): {response.choices[0].message.content}")


# ============================================================
# Example 4: With and Without Input Compression
# ============================================================

def example_4_compression():
    """
    Compare results with and without input compression
    Input compression reduces input tokens by removing unnecessary words
    """
    print("\n" + "=" * 60)
    print("Example 4: Input Compression")
    print("=" * 60)
    
    optimizer = get_output_optimizer()
    
    # Message with compressible content
    message = "In the year 2024, the sales were 15000000 won. Can you analyze this?"
    
    print("Original message:")
    print(f"  '{message}'")
    
    # Without compression
    print("\n--- Without Compression ---")
    params_no_compress = optimizer.get_optimized_params(
        user_message=message,
        strategy="auto",
        compress_input=False  # Disable compression
    )
    print(f"Message: {params_no_compress['user_message']}")
    print(f"Input tokens: {params_no_compress['input_tokens']}")
    
    # With compression
    print("\n--- With Compression ---")
    params_with_compress = optimizer.get_optimized_params(
        user_message=message,
        strategy="auto",
        compress_input=True  # Enable compression
    )
    print(f"Message: {params_with_compress['user_message']}")
    print(f"Input tokens: {params_with_compress['input_tokens']}")
    
    # Show savings
    if 'input_compression' in params_with_compress['optimization_info']:
        compression_info = params_with_compress['optimization_info']['input_compression']
        print(f"\nTokens saved: {compression_info['tokens_saved']}")
        print(f"Savings: {compression_info['savings_percent']:.1f}%")


# ============================================================
# Example 5: Cost Calculation
# ============================================================

def example_5_cost_calculation():
    """
    Calculate and compare costs between baseline and optimized
    """
    print("\n" + "=" * 60)
    print("Example 5: Cost Calculation")
    print("=" * 60)
    
    optimizer = get_output_optimizer()
    
    # Simulate baseline (no optimization)
    baseline_output_tokens = 500
    
    # Get optimized parameters
    params = optimizer.get_optimized_params(
        user_message="Explain quantum computing.",
        strategy="maximum",
        compress_input=True
    )
    
    optimized_output_tokens = params['estimated_output_tokens']
    
    # Calculate savings
    savings = optimizer.calculate_savings(
        original_tokens=baseline_output_tokens,
        optimized_tokens=optimized_output_tokens,
        strategy="maximum"
    )
    
    print("\n--- Cost Comparison ---")
    print(f"Baseline output tokens: {savings['original_tokens']}")
    print(f"Optimized output tokens: {savings['optimized_tokens']}")
    print(f"Tokens saved: {savings['tokens_saved']} ({savings['savings_percent']}%)")
    print(f"\nBaseline cost: ${savings['original_cost_usd']:.8f}")
    print(f"Optimized cost: ${savings['optimized_cost_usd']:.8f}")
    print(f"Cost saved: ${savings['cost_saved_usd']:.8f}")
    
    # Monthly projection
    monthly_requests = 10000
    monthly_savings = savings['cost_saved_usd'] * monthly_requests
    
    print(f"\n--- Monthly Projection (10,000 requests) ---")
    print(f"Monthly savings: ${monthly_savings:.2f}")
    print(f"Annual savings: ${monthly_savings * 12:.2f}")


# ============================================================
# Example 6: Complete Workflow
# ============================================================

def example_6_complete_workflow():
    """
    Complete workflow showing all features together
    This is a real-world usage example
    """
    print("\n" + "=" * 60)
    print("Example 6: Complete Workflow")
    print("=" * 60)
    
    # Initialize
    optimizer = get_output_optimizer()
    
    # User input (could be from web form, API, etc.)
    user_question = "What are the benefits of using Python for data science?"
    
    # Get optimized parameters
    # AUTO strategy automatically selects best approach
    params = optimizer.get_optimized_params(
        user_message=user_question,
        strategy="auto",  # Recommended: automatic selection
        compress_input=True  # Recommended: enable compression
    )
    
    # Display optimization info
    print("\n--- Optimization Applied ---")
    print(f"Original message: {user_question}")
    print(f"Optimized message: {params['user_message']}")
    print(f"Strategy selected: {params['strategy_used']}")
    print(f"System prompt: '{params['system_prompt']}'")
    print(f"Max tokens: {params['max_tokens']}")
    print(f"Input tokens: {params['input_tokens']}")
    print(f"Estimated cost: ${params['estimated_cost']:.8f}")
    
    # Build messages for OpenAI
    messages = []
    if params["system_prompt"]:
        messages.append({"role": "system", "content": params["system_prompt"]})
    messages.append({"role": "user", "content": params["user_message"]})
    
    # Call OpenAI API
    print("\n--- Calling OpenAI API ---")
    response = openai.chat.completions.create(
        model=model,
        messages=messages,
        max_tokens=params["max_tokens"],
        temperature=params["temperature"],
        response_format=params["response_format"]
    )
    
    # Get result
    answer = response.choices[0].message.content
    actual_tokens = response.usage.completion_tokens
    
    print(f"Answer: {answer[:200]}...")
    print(f"\n--- Results ---")
    print(f"Actual output tokens: {actual_tokens}")
    print(f"Estimated tokens: {params['estimated_output_tokens']}")
    print(f"Accuracy: {(1 - abs(actual_tokens - params['estimated_output_tokens']) / params['estimated_output_tokens']) * 100:.1f}%")
    
    # Calculate actual cost
    actual_input_cost = (response.usage.prompt_tokens / 1_000_000) * 0.150
    actual_output_cost = (response.usage.completion_tokens / 1_000_000) * 0.600
    actual_total_cost = actual_input_cost + actual_output_cost
    
    print(f"\nActual cost: ${actual_total_cost:.8f}")
    print(f"Estimated cost: ${params['estimated_cost']:.8f}")


# ============================================================
# Example 7: Batch Processing
# ============================================================

def example_7_batch_processing():
    """
    Process multiple requests efficiently
    Useful for bulk operations
    """
    print("\n" + "=" * 60)
    print("Example 7: Batch Processing")
    print("=" * 60)
    
    optimizer = get_output_optimizer()
    
    # Multiple questions
    questions = [
        "What is AI?",
        "Explain neural networks briefly.",
        "What is the difference between ML and DL?",
        "Name 3 popular Python libraries for data science."
    ]
    
    total_estimated_cost = 0
    
    print("\nProcessing batch of questions:")
    print(f"Total questions: {len(questions)}")
    
    for i, question in enumerate(questions, 1):
        params = optimizer.get_optimized_params(
            user_message=question,
            strategy="auto",
            compress_input=True
        )
        
        total_estimated_cost += params['estimated_cost']
        
        print(f"\n{i}. {question}")
        print(f"   Strategy: {params['strategy_used']}")
        print(f"   Max tokens: {params['max_tokens']}")
        print(f"   Estimated cost: ${params['estimated_cost']:.8f}")
        
        # Note: In real usage, you would make API calls here
        # response = openai.chat.completions.create(...)
    
    print(f"\n--- Batch Summary ---")
    print(f"Total questions: {len(questions)}")
    print(f"Total estimated cost: ${total_estimated_cost:.8f}")
    print(f"Average cost per question: ${total_estimated_cost/len(questions):.8f}")


# ============================================================
# Main Function
# ============================================================

def main():
    """
    Run all examples
    
    Note: Some examples make real API calls and will cost money
    Comment out examples you don't want to run
    """
    print("=" * 60)
    print("WOOSAILibrary - Basic Usage Examples")
    print("=" * 60)
    print("\nThese examples demonstrate how to use the library.")
    print("Some examples make real API calls (costs money).")
    print("\nExamples that make API calls:")
    print("- Example 1: Quick Start")
    print("- Example 3: Korean Language")
    print("- Example 6: Complete Workflow")
    
    choice = input("\nRun examples with API calls? (y/n, default=n): ").strip().lower()
    
    if choice == 'y':
        # Examples with API calls (costs money)
        example_1_quick_start()
        example_3_korean()
        example_6_complete_workflow()
    
    # Examples without API calls (free)
    example_2_strategies()
    example_4_compression()
    example_5_cost_calculation()
    example_7_batch_processing()
    
    print("\n" + "=" * 60)
    print("All examples completed!")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Read the documentation in README.md")
    print("2. Try modifying these examples")
    print("3. Integrate into your own projects")
    print("\nFor more information, visit:")
    print("https://github.com/yourusername/WOOSAILibrary")


if __name__ == "__main__":
    main()