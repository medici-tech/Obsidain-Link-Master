#!/usr/bin/env python3
"""
Incremental Processing Utility
Tracks file hashes to skip unchanged files during processing
"""

import hashlib
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, Set


class FileHashTracker:
    """
    Tracks MD5 hashes of processed files to enable incremental processing
    Skips files that haven't changed since last run
    """

    def __init__(self, hash_file: str = ".file_hashes.json"):
        """
        Initialize file hash tracker

        Args:
            hash_file: Path to file hash storage (default: .file_hashes.json)
        """
        self.hash_file = hash_file
        self.hashes: Dict[str, Dict[str, any]] = {}
        self.stats = {
            "unchanged_files": 0,
            "changed_files": 0,
            "new_files": 0,
            "deleted_files": 0,
        }
        self.load()

    def _calculate_hash(self, filepath: str) -> Optional[str]:
        """
        Calculate MD5 hash of file content

        Args:
            filepath: Path to file

        Returns:
            MD5 hash string, or None if file can't be read
        """
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
                return hashlib.md5(content.encode("utf-8")).hexdigest()
        except Exception as e:
            print(f"⚠️  Could not hash file {filepath}: {e}")
            return None

    def load(self) -> bool:
        """
        Load file hashes from disk

        Returns:
            True if loaded successfully, False otherwise
        """
        if not os.path.exists(self.hash_file):
            self.hashes = {}
            return True

        try:
            with open(self.hash_file, "r") as f:
                data = json.load(f)
                self.hashes = data.get("hashes", {})
                return True
        except Exception as e:
            print(f"⚠️  Could not load file hashes: {e}")
            self.hashes = {}
            return False

    def save(self) -> bool:
        """
        Save file hashes to disk

        Returns:
            True if saved successfully, False otherwise
        """
        try:
            data = {
                "hashes": self.hashes,
                "last_updated": datetime.now().isoformat(),
                "stats": self.stats,
            }

            with open(self.hash_file, "w") as f:
                json.dump(data, f, indent=2)

            return True
        except Exception as e:
            print(f"⚠️  Could not save file hashes: {e}")
            return False

    def has_changed(self, filepath: str) -> bool:
        """
        Check if file has changed since last processing

        Args:
            filepath: Path to file to check

        Returns:
            True if file is new or has changed, False if unchanged
        """
        current_hash = self._calculate_hash(filepath)
        if current_hash is None:
            # Can't read file, treat as changed
            return True

        # Convert to absolute path for consistency
        abs_path = os.path.abspath(filepath)

        if abs_path not in self.hashes:
            # New file
            self.stats["new_files"] += 1
            return True

        stored_hash = self.hashes[abs_path].get("hash")
        if current_hash != stored_hash:
            # File has changed
            self.stats["changed_files"] += 1
            return True

        # File unchanged
        self.stats["unchanged_files"] += 1
        return False

    def update_hash(self, filepath: str, success: bool = True) -> None:
        """
        Update stored hash for a file after processing

        Args:
            filepath: Path to file
            success: Whether processing was successful
        """
        current_hash = self._calculate_hash(filepath)
        if current_hash is None:
            return

        # Convert to absolute path for consistency
        abs_path = os.path.abspath(filepath)

        self.hashes[abs_path] = {
            "hash": current_hash,
            "last_processed": datetime.now().isoformat(),
            "success": success,
            "size": os.path.getsize(filepath) if os.path.exists(filepath) else 0,
        }

    def remove_hash(self, filepath: str) -> None:
        """
        Remove hash entry for a deleted file

        Args:
            filepath: Path to file
        """
        abs_path = os.path.abspath(filepath)
        if abs_path in self.hashes:
            del self.hashes[abs_path]
            self.stats["deleted_files"] += 1

    def clean_deleted_files(self) -> int:
        """
        Remove hash entries for files that no longer exist

        Returns:
            Number of entries removed
        """
        deleted_count = 0
        to_remove = []

        for filepath in self.hashes.keys():
            if not os.path.exists(filepath):
                to_remove.append(filepath)

        for filepath in to_remove:
            del self.hashes[filepath]
            deleted_count += 1

        self.stats["deleted_files"] += deleted_count
        return deleted_count

    def get_stats(self) -> Dict[str, any]:
        """
        Get statistics about file changes

        Returns:
            Dictionary with stats
        """
        total_tracked = len(self.hashes)
        total_checked = sum(
            [
                self.stats["unchanged_files"],
                self.stats["changed_files"],
                self.stats["new_files"],
            ]
        )

        return {
            "total_tracked_files": total_tracked,
            "total_checked_files": total_checked,
            "unchanged_files": self.stats["unchanged_files"],
            "changed_files": self.stats["changed_files"],
            "new_files": self.stats["new_files"],
            "deleted_files": self.stats["deleted_files"],
            "skip_rate": round(
                (self.stats["unchanged_files"] / total_checked * 100)
                if total_checked > 0
                else 0,
                1,
            ),
        }

    def reset_stats(self) -> None:
        """Reset statistics counters"""
        self.stats = {
            "unchanged_files": 0,
            "changed_files": 0,
            "new_files": 0,
            "deleted_files": 0,
        }

    def __len__(self) -> int:
        """Return number of tracked files"""
        return len(self.hashes)

    def __contains__(self, filepath: str) -> bool:
        """Check if file is being tracked"""
        abs_path = os.path.abspath(filepath)
        return abs_path in self.hashes


def create_hash_tracker(config: Dict = None) -> FileHashTracker:
    """
    Factory function to create a FileHashTracker from configuration

    Args:
        config: Configuration dictionary (optional)

    Returns:
        FileHashTracker instance
    """
    if config is None:
        config = {}

    hash_file = config.get(
        "incremental_tracker_file",
        config.get("incremental_hash_file", ".file_hashes.json"),
    )

    return FileHashTracker(hash_file=hash_file)


if __name__ == "__main__":
    # Test the hash tracker
    import os
    import tempfile

    print("Testing FileHashTracker...\n")

    # Create temporary directory
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create tracker
        hash_file = os.path.join(tmpdir, "test_hashes.json")
        tracker = FileHashTracker(hash_file=hash_file)

        # Create test file
        test_file = os.path.join(tmpdir, "test.md")
        with open(test_file, "w") as f:
            f.write("# Test Content\n\nOriginal content")

        # First check - should be new
        print(f"1. First check (new file): {tracker.has_changed(test_file)}")
        assert tracker.has_changed(test_file) == True
        tracker.update_hash(test_file, success=True)
        tracker.save()

        # Second check - should be unchanged
        print(f"2. Second check (unchanged): {tracker.has_changed(test_file)}")
        assert tracker.has_changed(test_file) == False

        # Modify file
        with open(test_file, "w") as f:
            f.write("# Test Content\n\nModified content")

        # Third check - should be changed
        print(f"3. Third check (changed): {tracker.has_changed(test_file)}")
        assert tracker.has_changed(test_file) == True
        tracker.update_hash(test_file, success=True)

        # Stats
        stats = tracker.get_stats()
        print(f"\n📊 Stats:")
        print(f"   New files: {stats['new_files']}")
        print(f"   Changed files: {stats['changed_files']}")
        print(f"   Unchanged files: {stats['unchanged_files']}")
        print(f"   Skip rate: {stats['skip_rate']}%")

        print("\n✅ All tests passed!")
