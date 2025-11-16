"""Performance benchmark tests using deterministic measurements.

The suite now relies on ``pytest-benchmark`` to record timings while each test
asserts functional expectations (e.g., counts, serialization results) so
failures reflect logic regressions rather than raw wall-clock speed.
"""

import json
import hashlib
import os
from pathlib import Path

import pytest

import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@pytest.fixture
def benchmark_vault(tmp_path):
    """Create a benchmark vault with test files."""
    vault = tmp_path / "benchmark_vault"
    vault.mkdir()

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
    """Benchmark cache operations without asserting host-specific timing."""

    def test_hash_generation_performance(self, benchmark):
        """Benchmark hash generation and assert that hashes are produced."""
        from obsidian_auto_linker_enhanced import ObsidianAutoLinker

        linker = ObsidianAutoLinker()
        test_content = "Test content " * 1000

        def generate():
            last_hash = None
            for _ in range(1000):
                last_hash = linker.get_content_hash(test_content)
            return last_hash

        last_hash = benchmark(generate)
        assert last_hash

    def test_cache_lookup_performance(self, benchmark):
        """Benchmark cache lookups and assert every key is returned."""
        cache = {f"hash_{i}": {"moc_category": "Technology", "confidence": 0.9} for i in range(10000)}

        def lookup():
            hits = 0
            for i in range(10000):
                if cache.get(f"hash_{i}"):
                    hits += 1
            return hits

        hits = benchmark(lookup)
        assert hits == 10000

    def test_cache_write_performance(self, benchmark):
        """Benchmark cache writes and assert the expected number of entries exist."""
        cache = {}
        test_data = {"moc_category": "Technology", "confidence": 0.85, "reasoning": "Test"}

        def write_entries():
            for i in range(5000):
                cache[f"hash_{i}"] = test_data
            return len(cache)

        entries = benchmark(write_entries)
        assert entries == 5000

    def test_cache_serialization_performance(self, tmp_path, benchmark):
        """Benchmark cache serialization/deserialization and validate round-trips."""
        cache = {}
        for i in range(1000):
            cache[f"hash_{i}"] = {
                "moc_category": "Technology",
                "confidence": 0.85,
                "reasoning": "Technical content detected"
            }

        cache_file = tmp_path / "cache_test.json"

        def serialize_cycle():
            with open(cache_file, "w", encoding="utf-8") as f:
                json.dump(cache, f)
            with open(cache_file, "r", encoding="utf-8") as f:
                return json.load(f)

        loaded_cache = benchmark(serialize_cycle)
        assert len(loaded_cache) == 1000


@pytest.mark.benchmark
class TestFileOperationsPerformance:
    """Benchmark file I/O operations while checking data integrity."""

    def test_file_read_performance(self, benchmark_vault, benchmark):
        """Benchmark reading files and assert every file is processed."""
        files = list(Path(benchmark_vault).glob("*.md"))

        def read_files():
            total_chars = 0
            for file_path in files:
                total_chars += len(file_path.read_text())
            return len(files), total_chars

        file_count, total_chars = benchmark(read_files)
        assert file_count == len(files)
        assert total_chars > 0

    def test_file_write_performance(self, tmp_path, benchmark):
        """Benchmark writing files and assert the expected file count exists."""
        test_content = "# Test\n\nContent " * 100

        def write_files():
            for file_path in tmp_path.glob("*.md"):
                file_path.unlink()
            for i in range(100):
                file_path = tmp_path / f"test_{i}.md"
                file_path.write_text(test_content)
            return len(list(tmp_path.glob("*.md")))

        files_written = benchmark(write_files)
        assert files_written == 100

    def test_file_glob_performance(self, benchmark_vault, benchmark):
        """Benchmark globbing files and assert the discovered count."""
        def glob_files():
            files = list(Path(benchmark_vault).glob("**/*.md"))
            return len(files)

        file_count = benchmark(glob_files)
        assert file_count == 100


@pytest.mark.benchmark
class TestContentProcessingPerformance:
    """Benchmark content processing helpers with deterministic assertions."""

    def test_wikilink_extraction_performance(self, benchmark):
        """Benchmark wikilink extraction and ensure the links are parsed."""
        content = "See [[Note 1]] and [[Note 2]] and [[Note 3]]. " * 100

        def extract_links():
            links = []
            import re
            for _ in range(1000):
                matches = re.findall(r"\[\[([^\]]+)\]\]", content)
                links.extend(matches)
            return len(links)

        link_count = benchmark(extract_links)
        assert link_count == 3000

    def test_content_truncation_performance(self, benchmark):
        """Benchmark repeated truncation and assert the truncated length."""
        long_content = "Word " * 10000

        def truncate():
            result = None
            for _ in range(1000):
                result = long_content[:4000]
            return len(result)

        length = benchmark(truncate)
        assert length == 4000

    def test_json_parsing_performance(self, benchmark):
        """Benchmark JSON parsing and assert parsed values."""
        json_str = json.dumps({
            "moc_category": "Technology",
            "confidence_score": 0.85,
            "reasoning": "Technical content with API references and code examples"
        })

        def parse_json():
            data = None
            for _ in range(10000):
                data = json.loads(json_str)
            return data

        data = benchmark(parse_json)
        assert data["moc_category"] == "Technology"


@pytest.mark.benchmark
class TestModelSelectorPerformance:
    """Benchmark model selector logic using pytest-benchmark."""

    def test_complexity_analysis_performance(self, benchmark):
        """Benchmark complexity analysis and assert a recommendation is produced."""
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

        def analyze():
            analysis = None
            for _ in range(1000):
                analysis = selector.analyze_content_complexity(test_content, "test.md")
            return analysis

        analysis = benchmark(analyze)
        assert analysis["recommended_model"] in {"qwen3:8b", "qwen2.5:3b"}

    def test_model_selection_performance(self, benchmark):
        """Benchmark model selection and assert valid model choices."""
        from scripts.intelligent_model_selector import IntelligentModelSelector

        config = {
            'primary_ollama_model': 'qwen3:8b',
            'secondary_ollama_model': 'qwen2.5:3b',
            'model_switching_threshold': 1000
        }
        selector = IntelligentModelSelector(config)

        def select_models():
            last_model = None
            for i in range(1000):
                content = f"Test content {i}" * 50
                last_model, _ = selector.select_model(content, "test.md")
            return last_model

        model = benchmark(select_models)
        assert model in {"qwen3:8b", "qwen2.5:3b"}


@pytest.mark.benchmark
class TestDashboardPerformance:
    """Benchmark dashboard operations using deterministic checks."""

    def test_dashboard_update_performance(self, benchmark):
        """Benchmark activity updates and assert bounded activity log size."""
        from live_dashboard import LiveDashboard

        def run_updates():
            LiveDashboard._instance = None
            dashboard = LiveDashboard()
            for i in range(1000):
                dashboard.add_activity(f"Activity {i}")
            log_len = len(dashboard.stats.get('recent_activity', []))
            dashboard.stop()
            return log_len

        log_len = benchmark(run_updates)
        assert log_len <= 5

    def test_dashboard_render_performance(self, benchmark):
        """Benchmark dashboard rendering and assert a layout is produced."""
        from live_dashboard import LiveDashboard

        def render_dashboard():
            LiveDashboard._instance = None
            dashboard = LiveDashboard()
            for i in range(100):
                dashboard.add_ai_request(2.0, success=True, tokens=100)
                dashboard.add_cache_hit()
                dashboard.add_file_processing_time(500, 3.0)
            layout = None
            for _ in range(10):
                layout = dashboard.render()
            dashboard.stop()
            return layout

        layout = benchmark(render_dashboard)
        assert layout is not None


@pytest.mark.benchmark
class TestMemoryEfficiency:
    """Test memory usage patterns with logic-focused assertions."""

    def test_large_cache_memory(self):
        """Ensure cache growth remains within reasonable memory bounds."""
        import sys

        cache = {}
        entry = {
            "moc_category": "Technology",
            "confidence": 0.85,
            "reasoning": "Technical content detected with API references"
        }

        for i in range(10000):
            cache[f"hash_{i}"] = entry.copy()

        cache_size = sys.getsizeof(cache)
        assert cache_size < 10 * 1024 * 1024

    def test_rapid_cache_access(self, benchmark):
        """Benchmark mixed cache access patterns and assert read counts."""
        cache = {f"hash_{i}": {"data": i} for i in range(5000)}

        def workload():
            reads = 0
            for i in range(10000):
                if i % 2 == 0:
                    if cache.get(f"hash_{i % 5000}"):
                        reads += 1
                else:
                    cache[f"hash_{i}"] = {"data": i}
            return reads

        reads = benchmark(workload)
        assert reads == 5000

    def test_simultaneous_metrics_update(self, benchmark):
        """Benchmark simultaneous dashboard updates and assert metric growth."""
        from live_dashboard import LiveDashboard

        def update_metrics():
            LiveDashboard._instance = None
            dashboard = LiveDashboard()
            for i in range(1000):
                dashboard.add_ai_request(2.0, True, 100)
                dashboard.add_cache_hit()
                dashboard.add_file_processing_time(500, 3.0)
                dashboard.add_moc_category("Technology")
                dashboard.add_activity(f"File {i}")
            stats = {
                'ai_requests': dashboard.stats['ai_requests'],
                'cache_hits': dashboard.stats['cache_hits'],
                'file_time_counts': len(dashboard.stats['file_times_small']) +
                                   len(dashboard.stats['file_times_medium']) +
                                   len(dashboard.stats['file_times_large']),
                'moc_categories': len(dashboard.stats['moc_distribution'])
            }
            dashboard.stop()
            return stats

        stats = benchmark(update_metrics)
        assert stats['ai_requests'] == 1000
        assert stats['cache_hits'] == 1000
        assert stats['file_time_counts'] == 1000
        assert stats['moc_categories'] == 1


@pytest.mark.benchmark
class TestScalability:
    """Test scalability characteristics using deterministic checks."""

    def test_cache_scalability(self):
        """Ensure cache lookups succeed at multiple scales without timing asserts."""
        processed_sizes = []
        for size in [100, 1000, 10000]:
            cache = {f"hash_{i}": {"data": i} for i in range(size)}
            hits = sum(1 for i in range(size) if cache.get(f"hash_{i}") is not None)
            processed_sizes.append(hits)
        assert processed_sizes == [100, 1000, 10000]

    def test_file_processing_scalability(self, tmp_path):
        """Ensure file processing loops touch every file regardless of scale."""
        results = []
        for num_files in [10, 50, 100]:
            for i in range(num_files):
                (tmp_path / f"file_{num_files}_{i}.md").write_text(f"# File {i}\n\nContent")
            files = list(Path(tmp_path).glob("file_*_*.md"))
            processed = 0
            for file_path in files:
                file_path.read_text()
                processed += 1
            results.append(processed)
            for file_path in files:
                file_path.unlink()
        assert results == [10, 50, 100]


@pytest.mark.benchmark
class TestRegressionBenchmarks:
    """Regression benchmarks focused on logical correctness rather than timing."""

    def test_hash_generation_regression(self, benchmark):
        """Benchmark hash generation and assert deterministic output."""
        content = "Test content " * 1000

        def run():
            last_hash = None
            for _ in range(1000):
                last_hash = hashlib.md5(content.encode()).hexdigest()
            return last_hash

        last_hash = benchmark(run)
        assert isinstance(last_hash, str)
        assert len(last_hash) == 32

    def test_json_operations_regression(self, benchmark):
        """Benchmark JSON round-trips and assert keys remain intact."""
        test_data = {
            "moc_category": "Technology",
            "confidence": 0.85,
            "reasoning": "Test reasoning " * 10
        }

        def run():
            data = None
            for _ in range(1000):
                json_str = json.dumps(test_data)
                data = json.loads(json_str)
            return data

        data = benchmark(run)
        assert data["moc_category"] == "Technology"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
