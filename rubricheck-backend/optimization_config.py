#!/usr/bin/env python3
"""
RubriCheck Performance Optimization Configuration
================================================
Configuration settings for optimizing performance and reducing API costs.
"""

import os
from typing import Dict, Any, Optional
from dataclasses import dataclass

@dataclass
class OptimizationConfig:
    """Configuration for performance optimizations."""
    
    # API Cost Optimization
    use_fast_mode_by_default: bool = True
    preferred_model: str = "gpt-4o-mini"  # Cheaper model
    max_tokens_per_request: int = 2048
    temperature: float = 0.3  # Lower temperature for more consistent results
    
    # Caching Settings
    enable_rubric_caching: bool = True
    enable_essay_caching: bool = True
    cache_ttl_seconds: int = 3600  # 1 hour
    
    # Performance Settings
    max_essay_length_chars: int = 10000  # Limit essay length for processing
    max_evidence_span_chars: int = 200  # Shorter evidence spans
    chunk_overlap_paragraphs: int = 1
    chunk_max_paragraphs: int = 4  # Smaller chunks for faster processing
    
    # Request Optimization
    timeout_seconds: int = 300  # 5 minutes max
    retry_attempts: int = 2
    retry_delay_seconds: int = 1
    
    # File Processing Limits
    max_file_size_mb: int = 10
    max_rubric_criteria: int = 10
    max_essay_paragraphs: int = 50
    
    @classmethod
    def from_env(cls) -> 'OptimizationConfig':
        """Create config from environment variables."""
        return cls(
            use_fast_mode_by_default=os.getenv('RUBRICHECK_FAST_MODE', 'true').lower() == 'true',
            preferred_model=os.getenv('RUBRICHECK_MODEL', 'gpt-4o-mini'),
            max_tokens_per_request=int(os.getenv('RUBRICHECK_MAX_TOKENS', '2048')),
            temperature=float(os.getenv('RUBRICHECK_TEMPERATURE', '0.3')),
            enable_rubric_caching=os.getenv('RUBRICHECK_CACHE_RUBRICS', 'true').lower() == 'true',
            enable_essay_caching=os.getenv('RUBRICHECK_CACHE_ESSAYS', 'true').lower() == 'true',
            cache_ttl_seconds=int(os.getenv('RUBRICHECK_CACHE_TTL', '3600')),
            max_essay_length_chars=int(os.getenv('RUBRICHECK_MAX_ESSAY_LENGTH', '10000')),
            max_evidence_span_chars=int(os.getenv('RUBRICHECK_MAX_EVIDENCE_SPAN', '200')),
            chunk_overlap_paragraphs=int(os.getenv('RUBRICHECK_CHUNK_OVERLAP', '1')),
            chunk_max_paragraphs=int(os.getenv('RUBRICHECK_CHUNK_MAX', '4')),
            timeout_seconds=int(os.getenv('RUBRICHECK_TIMEOUT', '300')),
            retry_attempts=int(os.getenv('RUBRICHECK_RETRY_ATTEMPTS', '2')),
            retry_delay_seconds=int(os.getenv('RUBRICHECK_RETRY_DELAY', '1')),
            max_file_size_mb=int(os.getenv('RUBRICHECK_MAX_FILE_SIZE', '10')),
            max_rubric_criteria=int(os.getenv('RUBRICHECK_MAX_CRITERIA', '10')),
            max_essay_paragraphs=int(os.getenv('RUBRICHECK_MAX_PARAGRAPHS', '50'))
        )

# Global optimization config
OPTIMIZATION_CONFIG = OptimizationConfig.from_env()

def get_optimization_config() -> OptimizationConfig:
    """Get the current optimization configuration."""
    return OPTIMIZATION_CONFIG

def update_optimization_config(**kwargs) -> None:
    """Update optimization configuration."""
    global OPTIMIZATION_CONFIG
    for key, value in kwargs.items():
        if hasattr(OPTIMIZATION_CONFIG, key):
            setattr(OPTIMIZATION_CONFIG, key, value)
