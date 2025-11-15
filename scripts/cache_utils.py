#!/usr/bin/env python3
"""
Cache Utilities - Bounded Cache with LRU Eviction
Prevents memory issues on large vaults by limiting cache size
"""

import json
import os
from collections import OrderedDict
from typing import Any, Optional
from datetime import datetime


class BoundedCache:
    """
    Bounded cache with LRU (Least Recently Used) eviction policy

    Features:
    - Maximum size limit (entries)
    - Maximum memory limit (MB)
    - LRU eviction when limits exceeded
    - Persistence to JSON file
    - Statistics tracking
    """

    def __init__(self, maxsize: int = 10000, max_memory_mb: float = 100.0):
        """
        Initialize bounded cache

        Args:
            maxsize: Maximum number of entries (default: 10000)
            max_memory_mb: Maximum cache size in MB (default: 100MB)
        """
        self.cache = OrderedDict()
        self.maxsize = maxsize
        self.max_memory_mb = max_memory_mb

        # Statistics
        self.stats = {
            'hits': 0,
            'misses': 0,
            'evictions': 0,
            'sets': 0,
            'created': datetime.now().isoformat()
        }

    def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache (LRU update)

        Args:
            key: Cache key

        Returns:
            Cached value or None if not found
        """
        if key in self.cache:
            # Move to end (most recently used)
            self.cache.move_to_end(key)
            self.stats['hits'] += 1
            return self.cache[key]

        self.stats['misses'] += 1
        return None

    def set(self, key: str, value: Any) -> None:
        """
        Set value in cache (with LRU eviction)

        Args:
            key: Cache key
            value: Value to cache
        """
        # If key exists, update and move to end
        if key in self.cache:
            self.cache.move_to_end(key)
            self.cache[key] = value
            self.stats['sets'] += 1
            return

        # Add new entry
        self.cache[key] = value
        self.stats['sets'] += 1

        # Check if we need to evict (size limit)
        if len(self.cache) > self.maxsize:
            evicted_key, evicted_value = self.cache.popitem(last=False)
            self.stats['evictions'] += 1

        # Check memory limit (approximate)
        self._check_memory_limit()

    def _check_memory_limit(self) -> None:
        """Check and enforce memory limit by evicting oldest entries"""
        # Approximate size in MB
        estimated_size_mb = self._estimate_size_mb()

        # Evict oldest entries until under limit
        while estimated_size_mb > self.max_memory_mb and len(self.cache) > 0:
            self.cache.popitem(last=False)  # Remove oldest
            self.stats['evictions'] += 1
            estimated_size_mb = self._estimate_size_mb()

    def _estimate_size_mb(self) -> float:
        """
        Estimate cache size in MB (rough approximation)

        Returns:
            Estimated size in MB
        """
        # Rough estimate: assume ~1KB per entry average
        # This is conservative for JSON data
        estimated_bytes = len(self.cache) * 1024
        return estimated_bytes / (1024 * 1024)

    def clear(self) -> None:
        """Clear all cache entries"""
        self.cache.clear()
        self.stats['evictions'] += len(self.cache)

    def size(self) -> int:
        """Get current cache size (number of entries)"""
        return len(self.cache)

    def hit_rate(self) -> float:
        """
        Calculate cache hit rate

        Returns:
            Hit rate as percentage (0-100)
        """
        total = self.stats['hits'] + self.stats['misses']
        if total == 0:
            return 0.0
        return (self.stats['hits'] / total) * 100

    def get_stats(self) -> dict:
        """
        Get cache statistics

        Returns:
            Dictionary with cache stats
        """
        return {
            **self.stats,
            'current_size': len(self.cache),
            'max_size': self.maxsize,
            'max_memory_mb': self.max_memory_mb,
            'estimated_size_mb': self._estimate_size_mb(),
            'hit_rate': f"{self.hit_rate():.1f}%"
        }

    def save_to_file(self, filepath: str) -> None:
        """
        Save cache to JSON file

        Args:
            filepath: Path to save cache
        """
        cache_data = {
            'cache': dict(self.cache),
            'stats': self.get_stats(),
            'saved_at': datetime.now().isoformat()
        }

        with open(filepath, 'w') as f:
            json.dump(cache_data, f, indent=2)

    def load_from_file(self, filepath: str) -> bool:
        """
        Load cache from JSON file

        Args:
            filepath: Path to load cache from

        Returns:
            True if loaded successfully, False otherwise
        """
        if not os.path.exists(filepath):
            return False

        try:
            with open(filepath, 'r') as f:
                cache_data = json.load(f)

            # Load cache entries (maintain order)
            if 'cache' in cache_data:
                self.cache = OrderedDict(cache_data['cache'])

                # Enforce size limits on load
                while len(self.cache) > self.maxsize:
                    self.cache.popitem(last=False)
                    self.stats['evictions'] += 1

                self._check_memory_limit()

            # Load stats if available
            if 'stats' in cache_data and isinstance(cache_data['stats'], dict):
                # Preserve cumulative stats
                for key in ['hits', 'misses', 'evictions', 'sets']:
                    if key in cache_data['stats']:
                        self.stats[key] = cache_data['stats'].get(key, 0)

            return True

        except Exception as e:
            print(f"Warning: Failed to load cache from {filepath}: {e}")
            return False

    def __contains__(self, key: str) -> bool:
        """Check if key is in cache"""
        return key in self.cache

    def __len__(self) -> int:
        """Get cache size"""
        return len(self.cache)

    def __repr__(self) -> str:
        """String representation"""
        return (f"BoundedCache(size={len(self.cache)}/{self.maxsize}, "
                f"hit_rate={self.hit_rate():.1f}%, "
                f"evictions={self.stats['evictions']})")


def create_bounded_cache(config: dict) -> BoundedCache:
    """
    Create bounded cache from configuration

    Args:
        config: Configuration dictionary with cache settings

    Returns:
        Configured BoundedCache instance
    """
    maxsize = config.get('cache_max_size', 10000)
    max_memory_mb = config.get('cache_max_memory_mb', 100.0)

    cache = BoundedCache(maxsize=maxsize, max_memory_mb=max_memory_mb)

    # Try to load existing cache
    cache_file = config.get('cache_file', 'ai_cache.json')
    cache.load_from_file(cache_file)

    return cache


if __name__ == "__main__":
    # Test bounded cache
    print("Testing BoundedCache...")

    cache = BoundedCache(maxsize=5)

    # Add entries
    for i in range(10):
        cache.set(f"key_{i}", {"data": f"value_{i}", "index": i})

    print(f"\nCache after adding 10 entries (max 5): {cache}")
    print(f"Cache size: {cache.size()}")
    print(f"Stats: {cache.get_stats()}")

    # Test retrieval
    print(f"\nGet key_5: {cache.get('key_5')}")
    print(f"Get key_0 (evicted): {cache.get('key_0')}")

    # Test persistence
    cache.save_to_file('test_cache.json')
    print("\nCache saved to test_cache.json")

    # Load in new cache
    new_cache = BoundedCache(maxsize=5)
    new_cache.load_from_file('test_cache.json')
    print(f"Loaded cache: {new_cache}")
    print(f"Stats: {new_cache.get_stats()}")

    # Cleanup
    os.remove('test_cache.json')
    print("\nTest complete!")
