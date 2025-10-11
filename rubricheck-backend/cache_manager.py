#!/usr/bin/env python3
"""
RubriCheck Cache Manager
========================
Simple in-memory cache for rubrics and essays to reduce API calls and improve performance.
"""

import hashlib
import json
import time
from typing import Dict, Any, Optional, Tuple
from dataclasses import dataclass
from optimization_config import get_optimization_config

@dataclass
class CacheEntry:
    """A cache entry with timestamp and data."""
    data: Any
    timestamp: float
    ttl: int

class CacheManager:
    """Simple in-memory cache manager for RubriCheck."""
    
    def __init__(self):
        self.cache: Dict[str, CacheEntry] = {}
        self.config = get_optimization_config()
    
    def _generate_key(self, content: str, prefix: str = "") -> str:
        """Generate a cache key from content."""
        content_hash = hashlib.md5(content.encode('utf-8')).hexdigest()
        return f"{prefix}:{content_hash}"
    
    def _is_expired(self, entry: CacheEntry) -> bool:
        """Check if a cache entry is expired."""
        return time.time() - entry.timestamp > entry.ttl
    
    def get(self, key: str) -> Optional[Any]:
        """Get data from cache."""
        if not self.config.enable_rubric_caching and not self.config.enable_essay_caching:
            return None
            
        entry = self.cache.get(key)
        if entry is None:
            return None
            
        if self._is_expired(entry):
            del self.cache[key]
            return None
            
        return entry.data
    
    def set(self, key: str, data: Any, ttl: Optional[int] = None) -> None:
        """Set data in cache."""
        if ttl is None:
            ttl = self.config.cache_ttl_seconds
            
        self.cache[key] = CacheEntry(
            data=data,
            timestamp=time.time(),
            ttl=ttl
        )
    
    def get_rubric(self, rubric_content: str) -> Optional[Dict[str, Any]]:
        """Get cached rubric."""
        if not self.config.enable_rubric_caching:
            return None
        key = self._generate_key(rubric_content, "rubric")
        return self.get(key)
    
    def set_rubric(self, rubric_content: str, rubric_data: Dict[str, Any]) -> None:
        """Cache parsed rubric."""
        if not self.config.enable_rubric_caching:
            return
        key = self._generate_key(rubric_content, "rubric")
        self.set(key, rubric_data)
    
    def get_essay_processing(self, essay_content: str) -> Optional[Any]:
        """Get cached essay processing result."""
        if not self.config.enable_essay_caching:
            return None
        key = self._generate_key(essay_content, "essay")
        return self.get(key)
    
    def set_essay_processing(self, essay_content: str, processing_result: Any) -> None:
        """Cache essay processing result."""
        if not self.config.enable_essay_caching:
            return
        key = self._generate_key(essay_content, "essay")
        self.set(key, processing_result)
    
    def clear(self) -> None:
        """Clear all cache entries."""
        self.cache.clear()
    
    def clear_expired(self) -> None:
        """Clear expired cache entries."""
        expired_keys = [
            key for key, entry in self.cache.items()
            if self._is_expired(entry)
        ]
        for key in expired_keys:
            del self.cache[key]
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        total_entries = len(self.cache)
        expired_entries = sum(1 for entry in self.cache.values() if self._is_expired(entry))
        
        return {
            "total_entries": total_entries,
            "expired_entries": expired_entries,
            "active_entries": total_entries - expired_entries,
            "cache_enabled": self.config.enable_rubric_caching or self.config.enable_essay_caching,
            "ttl_seconds": self.config.cache_ttl_seconds
        }

# Global cache manager instance
cache_manager = CacheManager()

def get_cache_manager() -> CacheManager:
    """Get the global cache manager instance."""
    return cache_manager
