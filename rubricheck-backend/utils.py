#!/usr/bin/env python3
"""
RubriCheck Shared Utilities
==========================
Common utilities shared across all RubriCheck modules.

Author: RubriCheck
"""

import os
from typing import Optional
from openai import OpenAI

# Global client instance to avoid duplication
_client = None

def get_api_key_from_env() -> str:
    """
    Get OpenAI API key from environment variable.
    
    Returns:
        API key string
        
    Raises:
        ValueError: If API key not found in environment
    """
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable not found")
    return api_key

def get_openai_client(api_key: Optional[str] = None) -> OpenAI:
    """
    Get OpenAI client instance, creating it if needed.
    Uses global client to avoid duplication across modules.
    
    Args:
        api_key: OpenAI API key (if None, will read from environment)
        
    Returns:
        OpenAI client instance
    """
    global _client
    
    if _client is None:
        try:
            if api_key is None:
                api_key = get_api_key_from_env()
            
            _client = OpenAI(api_key=api_key)
        except Exception as e:
            print(f"Warning: Could not load API key: {e}")
            # Fallback to environment variable
            _client = OpenAI()
    
    return _client

def reset_client():
    """Reset the global client (useful for testing)."""
    global _client
    _client = None
