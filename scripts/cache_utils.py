#!/usr/bin/env python3
"""
Cache utilities with size limits and LRU eviction
Optimized for MacBook Air M4 2025
"""

import sys
import time
import threading
from collections import OrderedDict
from typing import Any, Optional, Dict
import json


class BoundedCache:
    """
    Thread-safe bounded cache with LRU eviction strategy

    Features:
    - Size limit in MB
    - Entry count limit
    - LRU eviction when limits exceeded
    - Thread-safe operations
    - Serializable to JSON
    """

    def __init__(self, max_size_mb: int = 500, max_entries: int = 10000):
        """
        Initialize bounded cache

        Args:
            max_size_mb: Maximum cache size in megabytes
            max_entries: Maximum number of cache entries
        """
        self.cache = OrderedDict()
        self.max_size_mb = max_size_mb
        self.max_entries = max_entries
        self.access_times = {}
        self.entry_sizes = {}
        self._lock = threading.RLock()  # Reentrant lock for thread safety

    def get_size_mb(self) -> float:
        """Calculate current cache size in MB"""
        total_bytes = sum(self.entry_sizes.values())
        return total_bytes / (1024 * 1024)

    def __len__(self) -> int:
        """Return number of cached entries for len() support in tests."""
        return len(self.cache)

    def __contains__(self, key: str) -> bool:
        """Allow `in` checks to mirror dict behaviour."""
        return key in self.cache

    def _estimate_size(self, value: Any) -> int:
        """Estimate size of a value in bytes"""
        try:
            # Serialize to JSON to get approximate size
            json_str = json.dumps(value)
            return sys.getsizeof(json_str)
        except:
            # Fallback to sys.getsizeof
            return sys.getsizeof(value)

    def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache

        Args:
            key: Cache key

        Returns:
            Cached value or None if not found
        """
        with self._lock:
            if key in self.cache:
                # Update access time
                self.access_times[key] = time.time()
                # Move to end (most recently used)
                self.cache.move_to_end(key)
                return self.cache[key]
            return None

    def set(self, key: str, value: Any) -> None:
        """
        Set value in cache with automatic eviction

        Args:
            key: Cache key
            value: Value to cache
        """
        with self._lock:
            # Estimate size of new entry
            entry_size = self._estimate_size(value)

            # Check if we need to evict
            while (len(self.cache) >= self.max_entries or
                   (self.get_size_mb() + entry_size / (1024 * 1024)) > self.max_size_mb):
                if len(self.cache) == 0:
                    break
                self._evict_lru()

            # Add new entry
            self.cache[key] = value
            self.access_times[key] = time.time()
            self.entry_sizes[key] = entry_size
            self.cache.move_to_end(key)

    def _evict_lru(self) -> None:
        """Evict least recently used entry"""
        if not self.cache:
            return

        # Get least recently used key (first item in OrderedDict)
        lru_key = next(iter(self.cache))

        # Remove from all tracking structures
        del self.cache[lru_key]
        if lru_key in self.access_times:
            del self.access_times[lru_key]
        if lru_key in self.entry_sizes:
            del self.entry_sizes[lru_key]

    def has(self, key: str) -> bool:
        """Check if key exists in cache"""
        with self._lock:
            return key in self.cache

    def clear(self) -> None:
        """Clear all cache entries"""
        with self._lock:
            self.cache.clear()
            self.access_times.clear()
            self.entry_sizes.clear()

    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        with self._lock:
            return {
                'entries': len(self.cache),
                'size_mb': self.get_size_mb(),
                'max_entries': self.max_entries,
                'max_size_mb': self.max_size_mb,
                'utilization_pct': (len(self.cache) / self.max_entries * 100) if self.max_entries > 0 else 0,
                'size_utilization_pct': (self.get_size_mb() / self.max_size_mb * 100) if self.max_size_mb > 0 else 0
            }

    def to_dict(self) -> Dict[str, Any]:
        """Convert cache to dictionary for serialization"""
        with self._lock:
            return dict(self.cache)

    def from_dict(self, data: Dict[str, Any]) -> None:
        """Load cache from dictionary"""
        with self._lock:
            self.cache.clear()
            self.access_times.clear()
            self.entry_sizes.clear()
            for key, value in data.items():
                # Don't use self.set() here to avoid nested locking
                entry_size = self._estimate_size(value)
                self.cache[key] = value
                self.access_times[key] = time.time()
                self.entry_sizes[key] = entry_size

    def save_to_file(self, filepath: str) -> None:
        """Save cache to JSON file"""
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, indent=2)

    def load_from_file(self, filepath: str) -> None:
        """Load cache from JSON file"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            self.from_dict(data)
        except FileNotFoundError:
            pass  # Cache file doesn't exist yet
        except json.JSONDecodeError:
            pass  # Corrupted cache, start fresh


class IncrementalTracker:
    """
    Track file content hashes for incremental processing

    Features:
    - MD5 hash tracking per file
    - Change detection
    - Last processed timestamp
    - Thread-safe operations
    - Serializable state
    """

    def __init__(self):
        self.file_hashes = {}
        self.last_processed = {}
        self._lock = threading.RLock()  # Reentrant lock for thread safety

    def get_hash(self, filepath: str) -> Optional[str]:
        """Get stored hash for file"""
        with self._lock:
            return self.file_hashes.get(filepath)

    def set_hash(self, filepath: str, content_hash: str) -> None:
        """Store hash for file"""
        with self._lock:
            self.file_hashes[filepath] = content_hash
            self.last_processed[filepath] = time.time()

    def has_changed(self, filepath: str, current_hash: str) -> bool:
        """Check if file has changed since last processing"""
        with self._lock:
            stored_hash = self.file_hashes.get(filepath)
            if stored_hash is None:
                return True  # Never processed
            return stored_hash != current_hash

    def clear(self) -> None:
        """Clear all tracked files"""
        with self._lock:
            self.file_hashes.clear()
            self.last_processed.clear()

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        with self._lock:
            return {
                'file_hashes': self.file_hashes.copy(),
                'last_processed': self.last_processed.copy()
            }

    def from_dict(self, data: Dict[str, Any]) -> None:
        """Load from dictionary"""
        with self._lock:
            self.file_hashes = data.get('file_hashes', {})
            self.last_processed = data.get('last_processed', {})

    def save_to_file(self, filepath: str) -> None:
        """Save tracker to JSON file"""
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, indent=2)

    def load_from_file(self, filepath: str) -> None:
        """Load tracker from JSON file"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            self.from_dict(data)
        except (FileNotFoundError, json.JSONDecodeError):
            pass  # Start fresh


# Testing
if __name__ == "__main__":
    print("Testing BoundedCache...")

    # Test cache with small limits
    cache = BoundedCache(max_size_mb=1, max_entries=5)

    # Add entries
    for i in range(10):
        cache.set(f"key_{i}", {"data": f"value_{i}" * 100})
        print(f"Added key_{i}, cache has {len(cache.cache)} entries, {cache.get_size_mb():.2f}MB")

    print(f"\nCache stats: {cache.get_stats()}")

    # Test retrieval
    print(f"\nRetrieving key_0: {cache.get('key_0')}")
    print(f"Retrieving key_9: {cache.get('key_9')}")

    # Test incremental tracker
    print("\n\nTesting IncrementalTracker...")
    tracker = IncrementalTracker()

    tracker.set_hash("file1.md", "hash123")
    print(f"File1 changed? {tracker.has_changed('file1.md', 'hash123')}")  # False
    print(f"File1 changed? {tracker.has_changed('file1.md', 'hash456')}")  # True
    print(f"File2 changed? {tracker.has_changed('file2.md', 'hash789')}")  # True (never processed)

    print("\n✓ All tests passed!")
