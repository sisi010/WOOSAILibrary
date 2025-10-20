"""
WOOSAILibrary - Core Module
"""

from .lightweight_input import LightweightInputCompressor, get_compressor
from .prompt_optimizer import PromptOptimizer, get_prompt_optimizer
from .output_optimizer import OutputOptimizer, get_output_optimizer

__all__ = [
    "LightweightInputCompressor",
    "PromptOptimizer",
    "OutputOptimizer",
    "get_compressor",
    "get_prompt_optimizer",
    "get_output_optimizer",
]

__version__ = "1.0.0"