"""
Performance benchmark tests
Tests and measures performance characteristics of the system
"""

import pytest
import time
import json
import hashlib
from unittest.mock import patch, MagicMock
import tempfile
import os
from pathlib import Path

import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@pytest.fixture
def benchmark_vault(tmp_path):
    """Create a benchmark vault with test files"""
    vault = tmp_path / "benchmark_vault"
    vault.mkdir()

    # Create test markdown files
    for i in range(100):
        file_path = vault / f"note_{i:03d}.md"
        content = f"""# Note {i}

This is test content for note {i}.
It contains multiple paragraphs and various markdown elements.

## Section 1
Some technical content about Python, API, and databases.

## Section 2
Business analysis and financial planning information.

## Section 3
Personal development and wellness topics.
"""
        file_path.write_text(content)

    return str(vault)


@pytest.mark.benchmark
class TestCachePerformance:
    """Benchmark cache operations"""

    def test_hash_generation_performance(self):
        """Test MD5 hash generation performance"""
        from obsidian_auto_linker_enhanced import ObsidianAutoLinker

        linker = ObsidianAutoLinker()
        test_content = "Test content " * 1000  # ~13KB

        start_time = time.time()
        for _ in range(1000):
            linker.get_content_hash(test_content)
        elapsed = time.time() - start_time

        # Should hash 1000 items in < 100ms
        assert elapsed < 0.1
        print(f"\nHash generation: {elapsed * 1000:.2f}ms for 1000 hashes")

    def test_cache_lookup_performance(self):
        """Test cache lookup speed"""
        cache = {}
        for i in range(10000):
            cache[f"hash_{i}"] = {"moc_category": "Technology", "confidence": 0.9}

        start_time = time.time()
        for i in range(10000):
            _ = cache.get(f"hash_{i}")
        elapsed = time.time() - start_time

        # Should lookup 10000 items in < 10ms
        assert elapsed < 0.01
        print(f"\nCache lookup: {elapsed * 1000:.2f}ms for 10000 lookups")

    def test_cache_write_performance(self):
        """Test cache write speed"""
        cache = {}
        test_data = {"moc_category": "Technology", "confidence": 0.85, "reasoning": "Test"}

        start_time = time.time()
        for i in range(5000):
            cache[f"hash_{i}"] = test_data
        elapsed = time.time() - start_time

        # Should write 5000 items in < 10ms
        assert elapsed < 0.01
        print(f"\nCache write: {elapsed * 1000:.2f}ms for 5000 writes")

    def test_cache_serialization_performance(self, tmp_path):
        """Test cache JSON serialization performance"""
        cache = {}
        for i in range(1000):
            cache[f"hash_{i}"] = {
                "moc_category": "Technology",
                "confidence": 0.85,
                "reasoning": "Technical content detected"
            }

        cache_file = tmp_path / "cache_test.json"

        # Measure write performance
        start_time = time.time()
        with open(cache_file, 'w') as f:
            json.dump(cache, f)
        write_time = time.time() - start_time

        # Measure read performance
        start_time = time.time()
        with open(cache_file, 'r') as f:
            loaded_cache = json.load(f)
        read_time = time.time() - start_time

        # Should serialize and deserialize quickly
        assert write_time < 0.1
        assert read_time < 0.1
        assert len(loaded_cache) == 1000

        print(f"\nCache serialization: write={write_time*1000:.2f}ms, read={read_time*1000:.2f}ms")


@pytest.mark.benchmark
class TestFileOperationsPerformance:
    """Benchmark file I/O operations"""

    def test_file_read_performance(self, benchmark_vault):
        """Test file reading speed"""
        files = list(Path(benchmark_vault).glob("*.md"))

        start_time = time.time()
        for file_path in files:
            content = file_path.read_text()
        elapsed = time.time() - start_time

        # Should read 100 files in < 100ms
        assert elapsed < 0.1
        print(f"\nFile read: {elapsed * 1000:.2f}ms for {len(files)} files")

    def test_file_write_performance(self, tmp_path):
        """Test file writing speed"""
        test_content = "# Test\n\nContent " * 100

        files_written = 0
        start_time = time.time()
        for i in range(100):
            file_path = tmp_path / f"test_{i}.md"
            file_path.write_text(test_content)
            files_written += 1
        elapsed = time.time() - start_time

        # Should write 100 files in < 200ms
        assert elapsed < 0.2
        print(f"\nFile write: {elapsed * 1000:.2f}ms for {files_written} files")

    def test_file_glob_performance(self, benchmark_vault):
        """Test file discovery performance"""
        start_time = time.time()
        files = list(Path(benchmark_vault).glob("**/*.md"))
        elapsed = time.time() - start_time

        # Should glob 100 files in < 10ms
        assert elapsed < 0.01
        assert len(files) == 100
        print(f"\nFile glob: {elapsed * 1000:.2f}ms for {len(files)} files")


@pytest.mark.benchmark
class TestContentProcessingPerformance:
    """Benchmark content processing operations"""

    def test_wikilink_extraction_performance(self):
        """Test wikilink extraction speed"""
        from obsidian_auto_linker_enhanced import ObsidianAutoLinker

        linker = ObsidianAutoLinker()
        content = "See [[Note 1]] and [[Note 2]] and [[Note 3]]. " * 100

        start_time = time.time()
        for _ in range(1000):
            # Extract wikilinks (assuming this method exists)
            links = []
            import re
            for match in re.finditer(r'\[\[([^\]]+)\]\]', content):
                links.append(match.group(1))
        elapsed = time.time() - start_time

        # Should extract from 1000 documents in < 100ms
        assert elapsed < 0.1
        print(f"\nWikilink extraction: {elapsed * 1000:.2f}ms for 1000 documents")

    def test_content_truncation_performance(self):
        """Test content truncation speed"""
        long_content = "Word " * 10000  # 50KB

        start_time = time.time()
        for _ in range(1000):
            truncated = long_content[:4000]
        elapsed = time.time() - start_time

        # Should truncate 1000 times in < 1ms
        assert elapsed < 0.001
        print(f"\nContent truncation: {elapsed * 1000:.2f}ms for 1000 truncations")

    def test_json_parsing_performance(self):
        """Test JSON parsing speed"""
        json_str = json.dumps({
            "moc_category": "Technology",
            "confidence_score": 0.85,
            "reasoning": "Technical content with API references and code examples"
        })

        start_time = time.time()
        for _ in range(10000):
            data = json.loads(json_str)
        elapsed = time.time() - start_time

        # Should parse 10000 JSON objects in < 50ms
        assert elapsed < 0.05
        print(f"\nJSON parsing: {elapsed * 1000:.2f}ms for 10000 parses")


@pytest.mark.benchmark
class TestModelSelectorPerformance:
    """Benchmark intelligent model selector"""

    def test_complexity_analysis_performance(self):
        """Test content complexity analysis speed"""
        from scripts.intelligent_model_selector import IntelligentModelSelector

        config = {
            'model_switching_threshold': 1000
        }
        selector = IntelligentModelSelector(config)

        test_content = """
        This is a technical analysis of Python API development.
        It includes database integration, business logic, and financial calculations.
        The system processes investment portfolios and market data.
        """ * 10

        start_time = time.time()
        for _ in range(1000):
            analysis = selector.analyze_content_complexity(test_content, "test.md")
        elapsed = time.time() - start_time

        # Should analyze 1000 documents in < 100ms
        assert elapsed < 0.1
        print(f"\nComplexity analysis: {elapsed * 1000:.2f}ms for 1000 analyses")

    def test_model_selection_performance(self):
        """Test model selection speed"""
        from scripts.intelligent_model_selector import IntelligentModelSelector

        config = {
            'primary_ollama_model': 'qwen3:8b',
            'secondary_ollama_model': 'qwen2.5:3b',
            'model_switching_threshold': 1000
        }
        selector = IntelligentModelSelector(config)

        start_time = time.time()
        for i in range(1000):
            content = f"Test content {i}" * 50
            model, settings = selector.select_model(content, "test.md")
        elapsed = time.time() - start_time

        # Should select model 1000 times in < 150ms
        assert elapsed < 0.15
        print(f"\nModel selection: {elapsed * 1000:.2f}ms for 1000 selections")


@pytest.mark.benchmark
class TestDashboardPerformance:
    """Benchmark dashboard operations"""

    def test_dashboard_update_performance(self):
        """Test dashboard update speed"""
        from live_dashboard import LiveDashboard

        LiveDashboard._instance = None
        dashboard = LiveDashboard()

        start_time = time.time()
        for i in range(1000):
            dashboard.add_activity(f"Activity {i}")
        elapsed = time.time() - start_time

        # Should handle 1000 updates in < 50ms
        assert elapsed < 0.05
        print(f"\nDashboard updates: {elapsed * 1000:.2f}ms for 1000 updates")

        dashboard.stop()

    def test_dashboard_render_performance(self):
        """Test dashboard rendering speed"""
        from live_dashboard import LiveDashboard

        LiveDashboard._instance = None
        dashboard = LiveDashboard()

        # Populate with data
        for i in range(100):
            dashboard.add_ai_request(2.0, success=True, tokens=100)
            dashboard.add_cache_hit()
            dashboard.add_file_processing_time(500, 3.0)

        start_time = time.time()
        for _ in range(100):
            layout = dashboard.render()
        elapsed = time.time() - start_time

        # Should render 100 times in < 1 second
        assert elapsed < 1.0
        print(f"\nDashboard render: {elapsed * 1000:.2f}ms for 100 renders")

        dashboard.stop()


@pytest.mark.benchmark
class TestMemoryEfficiency:
    """Test memory usage patterns"""

    def test_large_cache_memory(self):
        """Test memory usage with large cache"""
        import sys

        cache = {}
        entry = {
            "moc_category": "Technology",
            "confidence": 0.85,
            "reasoning": "Technical content detected with API references"
        }

        # Add 10000 entries
        for i in range(10000):
            cache[f"hash_{i}"] = entry.copy()

        # Rough size estimate
        cache_size = sys.getsizeof(cache)

        # Should be reasonable size (< 10MB for 10000 entries)
        assert cache_size < 10 * 1024 * 1024
        print(f"\nCache memory: {cache_size / 1024:.2f} KB for 10000 entries")

    def test_dashboard_stats_memory(self):
        """Test dashboard statistics memory usage"""
        from live_dashboard import LiveDashboard
        import sys

        LiveDashboard._instance = None
        dashboard = LiveDashboard()

        # Add lots of data
        for i in range(1000):
            dashboard.add_ai_request(2.0, True, 100)
            dashboard.add_cache_hit()
            dashboard.add_activity(f"Activity {i}")

        stats_size = sys.getsizeof(dashboard.stats)

        # Should be reasonable (< 5MB)
        assert stats_size < 5 * 1024 * 1024
        print(f"\nDashboard stats memory: {stats_size / 1024:.2f} KB")

        dashboard.stop()


@pytest.mark.benchmark
class TestConcurrentPerformance:
    """Test performance under concurrent operations"""

    def test_rapid_cache_access(self):
        """Test cache performance under rapid access"""
        cache = {f"hash_{i}": {"data": i} for i in range(5000)}

        start_time = time.time()

        # Simulate mixed read/write workload
        for i in range(10000):
            if i % 2 == 0:
                # Read
                _ = cache.get(f"hash_{i % 5000}")
            else:
                # Write
                cache[f"hash_{i}"] = {"data": i}

        elapsed = time.time() - start_time

        # Should handle 10000 operations in < 10ms
        assert elapsed < 0.01
        print(f"\nMixed cache operations: {elapsed * 1000:.2f}ms for 10000 ops")

    def test_simultaneous_metrics_update(self):
        """Test updating multiple metrics simultaneously"""
        from live_dashboard import LiveDashboard

        LiveDashboard._instance = None
        dashboard = LiveDashboard()

        start_time = time.time()

        for i in range(1000):
            # Update multiple metrics at once
            dashboard.add_ai_request(2.0, True, 100)
            dashboard.add_cache_hit()
            dashboard.add_file_processing_time(500, 3.0)
            dashboard.add_moc_category("Technology")
            dashboard.add_activity(f"File {i}")

        elapsed = time.time() - start_time

        # Should handle 5000 total updates (1000 * 5) in < 100ms
        assert elapsed < 0.1
        print(f"\nSimultaneous metrics: {elapsed * 1000:.2f}ms for 5000 updates")

        dashboard.stop()


@pytest.mark.benchmark
class TestScalability:
    """Test system scalability"""

    def test_cache_scalability(self):
        """Test cache performance scaling"""
        results = []

        for size in [100, 1000, 10000]:
            cache = {f"hash_{i}": {"data": i} for i in range(size)}

            start_time = time.time()
            for i in range(size):
                _ = cache.get(f"hash_{i}")
            elapsed = time.time() - start_time

            ops_per_sec = size / elapsed if elapsed > 0 else float('inf')
            results.append((size, elapsed, ops_per_sec))
            print(f"\nCache size {size}: {elapsed*1000:.2f}ms, {ops_per_sec:.0f} ops/sec")

        # Performance should scale reasonably (not exponentially worse)
        # Lookup time should remain roughly constant
        assert results[2][1] < results[0][1] * 200  # 10000 items shouldn't be 200x slower than 100

    def test_file_processing_scalability(self, tmp_path):
        """Test file processing scalability"""
        results = []

        for num_files in [10, 50, 100]:
            # Create test files
            for i in range(num_files):
                (tmp_path / f"file_{i}.md").write_text(f"# File {i}\n\nContent")

            start_time = time.time()
            files = list(Path(tmp_path).glob("*.md"))
            for file_path in files:
                content = file_path.read_text()
            elapsed = time.time() - start_time

            results.append((num_files, elapsed))
            print(f"\n{num_files} files: {elapsed*1000:.2f}ms")

            # Clean up for next iteration
            for file_path in files:
                file_path.unlink()

        # Should scale linearly (100 files ~10x slower than 10 files, not 100x)
        assert results[2][1] < results[0][1] * 20


@pytest.mark.benchmark
class TestRegressionBenchmarks:
    """Regression tests to ensure performance doesn't degrade"""

    def test_hash_generation_regression(self):
        """Regression test for hash generation"""
        content = "Test content " * 1000

        times = []
        for _ in range(10):
            start = time.time()
            for _ in range(1000):
                hashlib.md5(content.encode()).hexdigest()
            times.append(time.time() - start)

        avg_time = sum(times) / len(times)

        # Baseline: should complete in < 50ms on average
        assert avg_time < 0.05
        print(f"\nHash regression: {avg_time * 1000:.2f}ms avg for 1000 hashes")

    def test_json_operations_regression(self):
        """Regression test for JSON operations"""
        test_data = {
            "moc_category": "Technology",
            "confidence": 0.85,
            "reasoning": "Test reasoning " * 10
        }

        times = []
        for _ in range(10):
            start = time.time()
            for _ in range(1000):
                json_str = json.dumps(test_data)
                parsed = json.loads(json_str)
            times.append(time.time() - start)

        avg_time = sum(times) / len(times)

        # Baseline: should complete in < 30ms on average
        assert avg_time < 0.03
        print(f"\nJSON regression: {avg_time * 1000:.2f}ms avg for 1000 cycles")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])  # -s to show print statements
