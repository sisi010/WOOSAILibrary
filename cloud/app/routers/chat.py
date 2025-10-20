# app/routers/chat.py

"""
WOOSAILibrary - Chat Optimization Router
API endpoints for AI chat with token optimization

Features:
- Multiple optimization strategies (STARTER/PRO/PREMIUM/AUTO)
- Input compression
- Output optimization
- Cost tracking
- OpenAI integration

Author: WoosAI Team
Created: 2025-01-10
Updated: 2025-10-12 - Fixed compression info missing in response
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
import os

# Import core optimization modules
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../.."))
from core.output_optimizer import get_output_optimizer

# Import OpenAI (requires: pip install openai)
try:
    import openai
except ImportError:
    openai = None

# Import auth (if you want to use API key authentication)
try:
    from app.auth import verify_api_key
except ImportError:
    verify_api_key = None


router = APIRouter(prefix="/v1/chat", tags=["chat"])


# Request/Response Models
class ChatRequest(BaseModel):
    """Chat request model"""
    message: str = Field(..., description="User message", min_length=1, max_length=10000)
    strategy: str = Field(default="auto", description="Optimization strategy: auto, starter, pro, premium")
    compress_input: bool = Field(default=True, description="Enable input compression")
    schema_type: Optional[str] = Field(default=None, description="Response schema: chat, summary, qa, list")
    model: str = Field(default="gpt-4o-mini", description="OpenAI model name")
    custom_system_prompt: Optional[str] = Field(default=None, description="Custom system prompt")
    
    class Config:
        json_schema_extra = {
            "example": {
                "message": "What is artificial intelligence?",
                "strategy": "auto",
                "compress_input": True,
                "model": "gpt-4o-mini"
            }
        }


class ChatResponse(BaseModel):
    """Chat response model"""
    success: bool
    message: str
    response: Optional[str] = None
    optimization: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


# Initialize optimizer
optimizer = get_output_optimizer()


@router.post("/completions", response_model=ChatResponse)
async def chat_completion(request: ChatRequest):
    """
    Generate optimized chat completion
    
    This endpoint:
    1. Optimizes user input (compression)
    2. Selects best strategy (AUTO/STARTER/PRO/PREMIUM)
    3. Calls OpenAI API with optimized parameters
    4. Returns response with optimization stats
    
    Args:
        request: Chat request with message and options
    
    Returns:
        Chat response with AI answer and optimization details
    
    Example:
        POST /v1/chat/completions
        {
            "message": "Explain quantum computing",
            "strategy": "auto",
            "compress_input": true
        }
    """
    try:
        # Check if OpenAI is available
        if openai is None:
            raise HTTPException(
                500,
                "OpenAI library not installed. Run: pip install openai"
            )
        
        # Check if OpenAI API key is set
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise HTTPException(
                500,
                "OPENAI_API_KEY not set in environment variables"
            )
        
        # Validate strategy
        valid_strategies = ["auto", "starter", "pro", "premium"]
        if request.strategy not in valid_strategies:
            raise HTTPException(
                400,
                f"Invalid strategy. Must be one of: {', '.join(valid_strategies)}"
            )
        
        # Get optimized parameters
        params = optimizer.get_optimized_params(
            user_message=request.message,
            strategy=request.strategy,
            compress_input=request.compress_input,
            schema_type=request.schema_type,
            custom_system_prompt=request.custom_system_prompt,
            is_paid_user=False  # TODO: Check user's plan from database
        )
        
        # Prepare messages for OpenAI
        messages = []
        if params["system_prompt"]:
            messages.append({
                "role": "system",
                "content": params["system_prompt"]
            })
        messages.append({
            "role": "user",
            "content": params["user_message"]
        })
        
        # Prepare OpenAI API call parameters
        openai_params = {
            "model": request.model,
            "messages": messages,
            "max_tokens": params["max_tokens"],
            "temperature": params["temperature"]
        }
        
        # Add optional parameters (only if not None)
        if params.get("top_p") is not None:
            openai_params["top_p"] = params["top_p"]
        if params.get("frequency_penalty") is not None:
            openai_params["frequency_penalty"] = params["frequency_penalty"]
        if params.get("presence_penalty") is not None:
            openai_params["presence_penalty"] = params["presence_penalty"]
        if params.get("response_format"):
            openai_params["response_format"] = params["response_format"]
        
        # Call OpenAI API
        client = openai.OpenAI(api_key=api_key)
        response = client.chat.completions.create(**openai_params)
        
        # Extract response text FIRST
        ai_response = response.choices[0].message.content
        
        # THEN parse JSON if schema was used
        if params.get("response_format") and params["response_format"].get("type") == "json_object":
            try:
                import json
                json_data = json.loads(ai_response)
                
                # Extract main answer field
                if "ans" in json_data:
                    ai_response = json_data["ans"]
                elif "msg" in json_data:
                    ai_response = json_data["msg"]
                elif "sum" in json_data:
                    ai_response = json_data["sum"]
                    
            except json.JSONDecodeError:
                # If JSON parsing fails, use original response
                pass
        
        # Calculate actual tokens used
        actual_input_tokens = response.usage.prompt_tokens
        actual_output_tokens = response.usage.completion_tokens
        total_tokens = response.usage.total_tokens
        
        # Calculate actual cost
        input_price_per_million = 0.150
        output_price_per_million = 0.600
        actual_cost = (
            (actual_input_tokens / 1_000_000) * input_price_per_million +
            (actual_output_tokens / 1_000_000) * output_price_per_million
        )
        
        # ============================================================
        # FIX: Extract compression details properly
        # ============================================================
        compression_info = params.get("optimization_info", {}).get("input_compression", {})
        
        # Build compression details with ALL information
        compression_details = {
            "enabled": request.compress_input,
            "original_length": compression_info.get("original_length", len(request.message)),
            "compressed_length": compression_info.get("compressed_length", len(request.message)),
            "tokens_saved": compression_info.get("tokens_saved", 0),
            "savings_percent": compression_info.get("savings_percent", 0.0),
            "time_ms": compression_info.get("time_ms", 0.0)
        }
        
        # Add stages information (CRITICAL FIX!)
        if "input_compression" in params.get("optimization_info", {}):
            # Get original compression info from optimizer
            comp_info = params["optimization_info"]["input_compression"]
            
            # Extract stages if available
            stages = {}
            if "stages" in compression_info:
                stages = compression_info["stages"]
            
            # Add detailed stage information
            compression_details["stages"] = {
                "stage1_learning_dict": {
                    "replacements": stages.get("stage1_learning_dict", {}).get("replacements", 0),
                    "tokens_saved": stages.get("stage1_learning_dict", {}).get("tokens_saved", 0),
                    "time_ms": stages.get("stage1_learning_dict", {}).get("time_ms", 0.0)
                },
                "stage2_numbers": {
                    "replacements": stages.get("stage2_numbers", {}).get("replacements", 0),
                    "tokens_saved": stages.get("stage2_numbers", {}).get("tokens_saved", 0),
                    "time_ms": stages.get("stage2_numbers", {}).get("time_ms", 0.0)
                },
                "stage3_patterns": {
                    "replacements": stages.get("stage3_patterns", {}).get("replacements", 0),
                    "time_ms": stages.get("stage3_patterns", {}).get("time_ms", 0.0)
                }
            }
        else:
            # No compression applied - set empty stages
            compression_details["stages"] = {
                "stage1_learning_dict": {"replacements": 0, "tokens_saved": 0, "time_ms": 0.0},
                "stage2_numbers": {"replacements": 0, "tokens_saved": 0, "time_ms": 0.0},
                "stage3_patterns": {"replacements": 0, "time_ms": 0.0}
            }
        
        # Prepare optimization details
        optimization_details = {
            "strategy_used": params["strategy_used"],
            "tier": params["tier"],
            "compression_enabled": request.compress_input,
            "schema_applied": request.schema_type is not None,
            
            # Token statistics
            "tokens": {
                "input": actual_input_tokens,
                "output": actual_output_tokens,
                "total": total_tokens,
                "estimated_input": params["input_tokens"],
                "estimated_output": params["estimated_output_tokens"]
            },
            
            # Cost statistics
            "cost": {
                "actual_usd": round(actual_cost, 8),
                "estimated_usd": params["estimated_cost"],
                "model": request.model
            },
            
            # Parameters used
            "parameters": {
                "max_tokens": params["max_tokens"],
                "temperature": params["temperature"],
                "top_p": params.get("top_p"),
                "frequency_penalty": params.get("frequency_penalty"),
                "presence_penalty": params.get("presence_penalty")
            },
            
            # Compression details (ALWAYS included now!)
            "compression": compression_details,
            
            # Processing info
            "processing_time_ms": params["optimization_info"]["processing_time_ms"],
            "timestamp": datetime.utcnow().isoformat()
        }
        
        return ChatResponse(
            success=True,
            message="Chat completion successful",
            response=ai_response,
            optimization=optimization_details
        )
        
    except openai.APIError as e:
        # OpenAI API error
        raise HTTPException(500, f"OpenAI API error: {str(e)}")
    except Exception as e:
        # Other errors
        raise HTTPException(500, f"Internal error: {str(e)}")


@router.post("/optimize", response_model=Dict)
async def optimize_only(request: ChatRequest):
    """
    Get optimization parameters without calling OpenAI
    
    Useful for:
    - Testing optimization logic
    - Previewing parameters before API call
    - Calculating estimated costs
    
    Args:
        request: Chat request
    
    Returns:
        Optimized parameters and cost estimates
    
    Example:
        POST /v1/chat/optimize
        {
            "message": "Long question here...",
            "strategy": "auto"
        }
    """
    try:
        # Get optimized parameters
        params = optimizer.get_optimized_params(
            user_message=request.message,
            strategy=request.strategy,
            compress_input=request.compress_input,
            schema_type=request.schema_type,
            custom_system_prompt=request.custom_system_prompt,
            is_paid_user=False  # TODO: Check user's plan
        )
        
        return {
            "success": True,
            "message": "Optimization successful",
            "parameters": params
        }
        
    except Exception as e:
        raise HTTPException(500, f"Optimization error: {str(e)}")


@router.get("/strategies")
async def list_strategies():
    """
    List available optimization strategies
    
    Returns:
        Dictionary of strategies with details
    """
    return {
        "strategies": {
            "auto": {
                "name": "AUTO",
                "description": "Automatically select best strategy",
                "tier": "free (beta)",
                "logic": "Selects STARTER/PRO/PREMIUM based on input length"
            },
            "starter": {
                "name": "STARTER",
                "description": "Natural responses, quality-focused",
                "tier": "free",
                "max_tokens": 2000,
                "savings": "10-15%",
                "best_for": "General conversations, quality priority"
            },
            "pro": {
                "name": "PRO",
                "description": "Balanced optimization",
                "tier": "paid",
                "max_tokens": 1300,
                "savings": "25-35%",
                "best_for": "Cost-conscious users, good quality"
            },
            "premium": {
                "name": "PREMIUM",
                "description": "Maximum cost savings",
                "tier": "paid",
                "max_tokens": 700,
                "savings": "45-55%",
                "best_for": "Maximum cost reduction, brief answers"
            }
        },
        "note": "All strategies currently free during beta. PRO/PREMIUM will require paid plan in future."
    }


@router.get("/health")
async def health_check():
    """
    Health check for chat service
    
    Returns:
        Service status
    """
    openai_available = openai is not None
    api_key_set = bool(os.getenv("OPENAI_API_KEY"))
    
    return {
        "status": "healthy" if (openai_available and api_key_set) else "degraded",
        "openai_library": "installed" if openai_available else "missing",
        "api_key": "configured" if api_key_set else "missing",
        "optimizer": "ready",
        "timestamp": datetime.utcnow().isoformat()
    }