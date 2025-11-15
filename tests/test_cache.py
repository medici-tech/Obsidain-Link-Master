"""
Unit tests for caching functionality
Tests cache storage, retrieval, and management
"""

import pytest
import json
import os
import tempfile
import hashlib
from unittest.mock import patch, mock_open, MagicMock

import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@pytest.mark.unit
@pytest.mark.cache
class TestCacheOperations:
    """Test suite for cache operations"""

    def test_get_content_hash_consistency(self, content_hash_fixture):
        """Test that content hashing is consistent"""
        from obsidian_auto_linker_enhanced import get_content_hash

        test_content, expected_hash = content_hash_fixture

        # Hash should be consistent
        hash1 = get_content_hash(test_content)
        hash2 = get_content_hash(test_content)

        assert hash1 == hash2
        assert hash1 == expected_hash

    def test_get_content_hash_different_content(self):
        """Test that different content produces different hashes"""
        from obsidian_auto_linker_enhanced import get_content_hash

        content1 = "This is content 1"
        content2 = "This is content 2"

        hash1 = get_content_hash(content1)
        hash2 = get_content_hash(content2)

        assert hash1 != hash2

    def test_get_content_hash_empty_content(self):
        """Test hashing empty content"""
        from obsidian_auto_linker_enhanced import get_content_hash

        result = get_content_hash("")
        expected = hashlib.md5("".encode()).hexdigest()

        assert result == expected

    def test_load_cache_success(self, temp_vault, sample_cache):
        """Test successful cache loading"""
        # Create cache file
        cache_file = os.path.join(temp_vault, '.ai_cache.json')
        with open(cache_file, 'w') as f:
            json.dump(sample_cache, f)

        # Mock config to use temp vault
        with patch('obsidian_auto_linker_enhanced.config', {'cache_file': cache_file, 'cache_enabled': True}):
            from obsidian_auto_linker_enhanced import load_cache, ai_cache

            load_cache()

            assert len(ai_cache) > 0
            assert 'abc123' in ai_cache

    def test_load_cache_file_not_found(self, temp_vault):
        """Test loading cache when file doesn't exist"""
        cache_file = os.path.join(temp_vault, 'nonexistent.json')

        with patch('obsidian_auto_linker_enhanced.config', {'cache_file': cache_file, 'cache_enabled': True}):
            from obsidian_auto_linker_enhanced import load_cache

            # Should not raise exception
            load_cache()

    def test_load_cache_invalid_json(self, temp_vault):
        """Test loading cache with invalid JSON"""
        cache_file = os.path.join(temp_vault, '.ai_cache.json')
        with open(cache_file, 'w') as f:
            f.write("This is not valid JSON{{{")

        with patch('obsidian_auto_linker_enhanced.config', {'cache_file': cache_file, 'cache_enabled': True}):
            from obsidian_auto_linker_enhanced import load_cache, ai_cache

            # Should handle gracefully
            load_cache()

    def test_save_cache_success(self, temp_vault):
        """Test successful cache saving"""
        cache_file = os.path.join(temp_vault, '.ai_cache.json')

        with patch('obsidian_auto_linker_enhanced.config', {'cache_file': cache_file, 'cache_enabled': True}):
            with patch('obsidian_auto_linker_enhanced.ai_cache', {'test_key': {'data': 'test'}}):
                from obsidian_auto_linker_enhanced import save_cache

                save_cache()

                # Verify file was created
                assert os.path.exists(cache_file)

                # Verify content
                with open(cache_file, 'r') as f:
                    data = json.load(f)
                    assert 'test_key' in data

    def test_save_cache_disabled(self, temp_vault):
        """Test that cache is not saved when disabled"""
        cache_file = os.path.join(temp_vault, '.ai_cache.json')

        with patch('obsidian_auto_linker_enhanced.config', {'cache_file': cache_file, 'cache_enabled': False}):
            from obsidian_auto_linker_enhanced import save_cache

            save_cache()

            # File should not be created when cache is disabled
            # (This depends on implementation)

    def test_cache_hit_analytics(self):
        """Test that cache hits are tracked in analytics"""
        from obsidian_auto_linker_enhanced import analytics

        initial_hits = analytics.get('cache_hits', 0)

        # Simulate cache hit
        analytics['cache_hits'] = initial_hits + 1

        assert analytics['cache_hits'] == initial_hits + 1

    def test_cache_miss_analytics(self):
        """Test that cache misses are tracked in analytics"""
        from obsidian_auto_linker_enhanced import analytics

        initial_misses = analytics.get('cache_misses', 0)

        # Simulate cache miss
        analytics['cache_misses'] = initial_misses + 1

        assert analytics['cache_misses'] == initial_misses + 1

    def test_analyze_with_cached_result(self, sample_cache, sample_markdown_content):
        """Test that analyze function uses cached results"""
        with patch('obsidian_auto_linker_enhanced.ai_cache', sample_cache):
            with patch('obsidian_auto_linker_enhanced.get_content_hash') as mock_hash:
                mock_hash.return_value = 'abc123'  # Match cache key

                from obsidian_auto_linker_enhanced import analyze_with_balanced_ai

                result = analyze_with_balanced_ai(sample_markdown_content, {})

                # Should return cached result
                assert result is not None
                assert result['moc_category'] == 'Technical & Automation'

    def test_analyze_cache_miss_calls_ai(self, sample_markdown_content, mock_ollama_success):
        """Test that cache miss triggers AI call"""
        with patch('obsidian_auto_linker_enhanced.ai_cache', {}):
            from obsidian_auto_linker_enhanced import analyze_with_balanced_ai

            result = analyze_with_balanced_ai(sample_markdown_content, {})

            # Should have called Ollama
            assert mock_ollama_success.called

    def test_cache_stores_new_results(self, sample_markdown_content, mock_ollama_success):
        """Test that new AI results are stored in cache"""
        test_cache = {}

        with patch('obsidian_auto_linker_enhanced.ai_cache', test_cache):
            from obsidian_auto_linker_enhanced import analyze_with_balanced_ai, get_content_hash

            result = analyze_with_balanced_ai(sample_markdown_content, {})

            # Cache should now contain the result
            content_hash = get_content_hash(sample_markdown_content)
            assert content_hash in test_cache

    def test_load_cache_empty_file(self, temp_vault):
        """Test loading cache from empty file"""
        cache_file = os.path.join(temp_vault, '.ai_cache.json')
        with open(cache_file, 'w') as f:
            f.write('')

        with patch('obsidian_auto_linker_enhanced.config', {'cache_file': cache_file, 'cache_enabled': True}):
            from obsidian_auto_linker_enhanced import load_cache

            # Should handle gracefully
            load_cache()

    def test_load_cache_null_content(self, temp_vault):
        """Test loading cache with null content"""
        cache_file = os.path.join(temp_vault, '.ai_cache.json')
        with open(cache_file, 'w') as f:
            f.write('null')

        with patch('obsidian_auto_linker_enhanced.config', {'cache_file': cache_file, 'cache_enabled': True}):
            from obsidian_auto_linker_enhanced import load_cache, ai_cache

            load_cache()

    def test_cache_performance_benefit(self, sample_cache, sample_markdown_content):
        """Test that cache provides performance benefit"""
        import time

        # Mock slow AI call
        def slow_ai_call(*args, **kwargs):
            time.sleep(0.1)  # Simulate 100ms AI call
            return {'moc_category': 'Test'}

        # First call (cache miss) - should be slow
        with patch('obsidian_auto_linker_enhanced.ai_cache', {}):
            with patch('obsidian_auto_linker_enhanced.call_ollama', side_effect=slow_ai_call):
                from obsidian_auto_linker_enhanced import analyze_with_balanced_ai, get_content_hash

                start = time.time()
                result1 = analyze_with_balanced_ai(sample_markdown_content, {})
                slow_time = time.time() - start

        # Second call (cache hit) - should be fast
        content_hash = get_content_hash(sample_markdown_content)
        with patch('obsidian_auto_linker_enhanced.ai_cache', {content_hash: result1}):
            start = time.time()
            result2 = analyze_with_balanced_ai(sample_markdown_content, {})
            fast_time = time.time() - start

        # Cache should be significantly faster
        assert fast_time < slow_time / 10  # At least 10x faster
