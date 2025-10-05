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

def get_api_key_from_file(file_path: str = r"C:\Users\Leo\AI projects\_api.txt", keyname: str = "RubricParserPrompt") -> str:
    """
    Read API key from api.txt file for RubriCheck project.
    
    Args:
        file_path: Path to the API key file
        keyname: Key name to look for in the file
        
    Returns:
        API key string
        
    Raises:
        ValueError: If API key not found
        FileNotFoundError: If API file not found
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip().startswith(f'{keyname}:'):
                    return line.strip().split(':', 1)[1].strip()
        raise ValueError(f"{keyname} API key not found in file")
    except FileNotFoundError:
        raise FileNotFoundError(f"API file not found at {file_path}")

def get_openai_client(api_key: Optional[str] = None) -> OpenAI:
    """
    Get OpenAI client instance, creating it if needed.
    Uses global client to avoid duplication across modules.
    
    Args:
        api_key: OpenAI API key (if None, will read from file)
        
    Returns:
        OpenAI client instance
    """
    global _client
    
    if _client is None:
        try:
            if api_key is None:
                api_key = get_api_key_from_file()
            
            os.environ["OPENAI_API_KEY"] = api_key
            _client = OpenAI(api_key=api_key)
        except Exception as e:
            print(f"⚠️  Warning: Could not load API key: {e}")
            # Fallback to environment variable
            _client = OpenAI()
    
    return _client

def reset_client():
    """Reset the global client (useful for testing)."""
    global _client
    _client = None
