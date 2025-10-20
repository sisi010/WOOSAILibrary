"""
WOOSAILibrary - Structured Schema Manager
Manage JSON schemas for OpenAI Structured Outputs

Purpose: Generate minimal JSON schemas to reduce output tokens
Speed: 0ms (just returns schema dictionaries)
Savings: 20-30% additional reduction through structure

Author: WoosAI Team
Created: 2025-01-03
"""

from typing import Dict, Optional


class StructuredSchemaManager:
    """
    Manage JSON schemas for structured outputs
    
    Optimization techniques:
    - Minimal field names (a, b, c vs description, title, content)
    - Required fields only
    - No nested objects unless necessary
    - English keys (shorter tokens than Korean)
    
    Usage:
        manager = StructuredSchemaManager()
        schema = manager.get_schema("chat_response")
        
        # Use with OpenAI
        response = openai.chat.completions.create(
            ...
            response_format={"type": "json_object"},
            ...
        )
    """
    
    def __init__(self):
        """Initialize schema manager with predefined schemas"""
        self.schemas = self._load_schemas()
    
    def _load_schemas(self) -> Dict:
        """Load predefined optimized schemas"""
        return {
            # Simple chat response
            "chat": {
                "name": "chat_response",
                "description": "Concise chat response",
                "schema": {
                    "type": "object",
                    "properties": {
                        "msg": {
                            "type": "string",
                            "description": "Response message"
                        }
                    },
                    "required": ["msg"],
                    "additionalProperties": False
                }
            },
            
            # Summary with key points
            "summary": {
                "name": "summary_response",
                "description": "Summary with key points",
                "schema": {
                    "type": "object",
                    "properties": {
                        "sum": {
                            "type": "string",
                            "description": "Brief summary"
                        },
                        "pts": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Key points (max 3)"
                        }
                    },
                    "required": ["sum"],
                    "additionalProperties": False
                }
            },
            
            # Question answer
            "qa": {
                "name": "qa_response",
                "description": "Question answer format",
                "schema": {
                    "type": "object",
                    "properties": {
                        "ans": {
                            "type": "string",
                            "description": "Direct answer"
                        },
                        "conf": {
                            "type": "number",
                            "description": "Confidence 0-1"
                        }
                    },
                    "required": ["ans"],
                    "additionalProperties": False
                }
            },
            
            # List response
            "list": {
                "name": "list_response",
                "description": "List of items",
                "schema": {
                    "type": "object",
                    "properties": {
                        "items": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "List items"
                        },
                        "cnt": {
                            "type": "integer",
                            "description": "Total count"
                        }
                    },
                    "required": ["items"],
                    "additionalProperties": False
                }
            }
        }
    
    def get_schema(self, schema_type: str = "chat") -> Optional[Dict]:
        """
        Get predefined schema by type
        
        Args:
            schema_type: Schema type ("chat", "summary", "qa", "list")
            
        Returns:
            Schema dictionary or None if not found
            
        Example:
            >>> manager = StructuredSchemaManager()
            >>> schema = manager.get_schema("chat")
            >>> print(schema['schema']['properties'])
            {'msg': {'type': 'string', 'description': 'Response message'}}
        """
        return self.schemas.get(schema_type)
    
    def create_custom_schema(self,
                            fields: Dict[str, str],
                            required: list = None,
                            name: str = "custom") -> Dict:
        """
        Create custom optimized schema
        
        Args:
            fields: Dict of field_name: field_type
            required: List of required field names
            name: Schema name
            
        Returns:
            Custom schema dictionary
            
        Example:
            >>> manager = StructuredSchemaManager()
            >>> schema = manager.create_custom_schema(
            ...     fields={"ans": "string", "score": "number"},
            ...     required=["ans"],
            ...     name="custom_qa"
            ... )
        """
        properties = {}
        for field_name, field_type in fields.items():
            properties[field_name] = {"type": field_type}
        
        return {
            "name": name,
            "schema": {
                "type": "object",
                "properties": properties,
                "required": required or list(fields.keys()),
                "additionalProperties": False
            }
        }
    
    def get_system_prompt_addition(self, schema_type: str) -> str:
        """
        Get additional system prompt text for schema
        
        Args:
            schema_type: Schema type
            
        Returns:
            Additional prompt text to ensure JSON output
        """
        prompts = {
            "chat": "Output format: JSON with 'msg' field only.",
            "summary": "Output format: JSON with 'sum' (summary) and optional 'pts' (key points array).",
            "qa": "Output format: JSON with 'ans' (answer) and optional 'conf' (confidence 0-1).",
            "list": "Output format: JSON with 'items' array and 'cnt' count."
        }
        return prompts.get(schema_type, "Output in JSON format.")


# Singleton instance
_schema_manager_instance = None

def get_schema_manager():
    """Get singleton schema manager instance"""
    global _schema_manager_instance
    if _schema_manager_instance is None:
        _schema_manager_instance = StructuredSchemaManager()
    return _schema_manager_instance