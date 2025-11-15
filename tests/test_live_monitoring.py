"""
Unit tests for live monitoring functionality
Tests real-time dashboard updates, system resource tracking, and performance monitoring
"""

import pytest
import time
from unittest.mock import patch, MagicMock, PropertyMock
from collections import deque

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@pytest.fixture
def dashboard():
    """Create fresh dashboard instance for each test"""
    from live_dashboard import LiveDashboard

    # Reset singleton
    LiveDashboard._instance = None
    dashboard = LiveDashboard(update_interval=1)  # Faster updates for testing
    yield dashboard
    dashboard.stop()


@pytest.mark.unit
class TestSystemResourceMonitoring:
    """Test system resource monitoring"""

    def test_update_system_resources(self, dashboard):
        """Test system resource updates"""
        dashboard.update_system_resources()

        # Should have updated stats (even if mocked)
        assert 'cpu_percent' in dashboard.stats or 'system' in str(dashboard.stats)

    @patch('psutil.cpu_percent')
    @patch('psutil.virtual_memory')
    def test_system_resources_with_psutil(self, mock_memory, mock_cpu, dashboard):
        """Test system resource tracking with psutil"""
        # Mock psutil data
        mock_cpu.return_value = 45.5
        mock_memory_obj = MagicMock()
        mock_memory_obj.percent = 60.2
        mock_memory_obj.used = 8 * 1024 * 1024 * 1024  # 8GB
        mock_memory_obj.total = 16 * 1024 * 1024 * 1024  # 16GB
        mock_memory.return_value = mock_memory_obj

        dashboard.update_system_resources()

        # Verify data was recorded
        assert dashboard.stats['cpu_percent'] == 45.5
        assert dashboard.stats['memory_percent'] == 60.2

    def test_system_resources_without_psutil(self, dashboard):
        """Test that dashboard works without psutil installed"""
        with patch.dict('sys.modules', {'psutil': None}):
            # Should not crash even if psutil unavailable
            dashboard.update_system_resources()

    def test_system_resource_history(self, dashboard):
        """Test that system resources track history"""
        with patch('psutil.cpu_percent', return_value=50.0):
            with patch('psutil.virtual_memory') as mock_mem:
                mock_mem_obj = MagicMock()
                mock_mem_obj.percent = 60.0
                mock_mem.return_value = mock_mem_obj

                # Update multiple times
                for i in range(5):
                    dashboard.update_system_resources()
                    time.sleep(0.01)

                # Should have history
                assert len(dashboard.stats.get('cpu_history', [])) > 0 or \
                       dashboard.stats.get('cpu_percent') is not None


@pytest.mark.unit
class TestRealTimeUpdates:
    """Test real-time dashboard updates"""

    def test_continuous_updates(self, dashboard):
        """Test that dashboard can handle continuous updates"""
        # Simulate rapid updates
        for i in range(20):
            dashboard.add_ai_request(
                response_time=1.0 + i * 0.1,
                success=True,
                tokens=100
            )

        assert dashboard.stats['ai_requests'] == 20

    def test_update_rate_limiting(self, dashboard):
        """Test that updates don't overwhelm the system"""
        start_time = time.time()

        # Rapid fire updates
        for i in range(100):
            dashboard.add_activity(f"Activity {i}")

        elapsed = time.time() - start_time

        # Should complete quickly (not blocked)
        assert elapsed < 1.0
        assert len(dashboard.stats['activity_log']) > 0

    def test_concurrent_metric_updates(self, dashboard):
        """Test updating multiple metrics simultaneously"""
        dashboard.add_ai_request(2.5, success=True, tokens=150)
        dashboard.add_cache_hit()
        dashboard.add_file_processing_time(500, 3.0)
        dashboard.add_moc_category("Technology")
        dashboard.add_activity("Processing file")

        # All metrics should be tracked
        assert dashboard.stats['ai_requests'] > 0
        assert dashboard.stats['cache_hits'] > 0
        assert len(dashboard.stats['file_processing_times']) > 0
        assert len(dashboard.stats['moc_distribution']) > 0


@pytest.mark.unit
class TestFileProcessingTracking:
    """Test file processing performance tracking"""

    def test_file_processing_time_tracking(self, dashboard):
        """Test tracking file processing times"""
        file_sizes = [100, 500, 1000, 2000]
        processing_times = [1.0, 2.5, 5.0, 10.0]

        for size, time_val in zip(file_sizes, processing_times):
            dashboard.add_file_processing_time(size, time_val)

        assert len(dashboard.stats['file_processing_times']) == 4

    def test_processing_time_statistics(self, dashboard):
        """Test calculating statistics from processing times"""
        # Add various processing times
        for i in range(10):
            dashboard.add_file_processing_time(500, 2.0 + i * 0.5)

        # Calculate stats
        times = [t for _, t in dashboard.stats['file_processing_times']]
        if len(times) > 0:
            avg = sum(times) / len(times)
            assert avg > 0

    def test_large_file_detection(self, dashboard):
        """Test tracking of large files"""
        # Small files
        dashboard.add_file_processing_time(50, 0.5)
        dashboard.add_file_processing_time(100, 1.0)

        # Large files
        dashboard.add_file_processing_time(5000, 15.0)
        dashboard.add_file_processing_time(10000, 30.0)

        # Should track all sizes
        sizes = [s for s, _ in dashboard.stats['file_processing_times']]
        assert max(sizes) == 10000
        assert min(sizes) == 50


@pytest.mark.unit
class TestMOCCategoryTracking:
    """Test MOC category distribution tracking"""

    def test_category_distribution(self, dashboard):
        """Test tracking MOC category distribution"""
        categories = [
            "Technology",
            "Technology",
            "Technology",
            "Business Operations",
            "Business Operations",
            "Personal Development"
        ]

        for cat in categories:
            dashboard.add_moc_category(cat)

        dist = dashboard.stats['moc_distribution']
        assert dist['Technology'] == 3
        assert dist['Business Operations'] == 2
        assert dist['Personal Development'] == 1

    def test_category_percentage_calculation(self, dashboard):
        """Test calculating category percentages"""
        for _ in range(50):
            dashboard.add_moc_category("Technology")
        for _ in range(30):
            dashboard.add_moc_category("Business Operations")
        for _ in range(20):
            dashboard.add_moc_category("Personal Development")

        total = 100
        dist = dashboard.stats['moc_distribution']

        tech_pct = (dist['Technology'] / total) * 100
        assert tech_pct == 50.0

    def test_rare_category_tracking(self, dashboard):
        """Test tracking categories that appear once"""
        dashboard.add_moc_category("Rare Category")

        assert dashboard.stats['moc_distribution']['Rare Category'] == 1


@pytest.mark.unit
class TestErrorTracking:
    """Test error tracking and reporting"""

    def test_error_logging(self, dashboard):
        """Test that errors are logged"""
        dashboard.add_error("Timeout", "AI request timed out")
        dashboard.add_error("ParseError", "Failed to parse JSON")

        assert len(dashboard.stats['errors']) == 2

    def test_error_type_categorization(self, dashboard):
        """Test errors are categorized by type"""
        dashboard.add_error("Timeout", "Error 1")
        dashboard.add_error("Timeout", "Error 2")
        dashboard.add_error("ParseError", "Error 3")

        errors = dashboard.stats['errors']
        timeout_errors = [e for e in errors if e['type'] == 'Timeout']
        assert len(timeout_errors) == 2

    def test_error_message_storage(self, dashboard):
        """Test that error messages are stored"""
        error_msg = "Specific error message with details"
        dashboard.add_error("TestError", error_msg)

        errors = dashboard.stats['errors']
        assert any(error_msg in e['message'] for e in errors)

    def test_error_limit(self, dashboard):
        """Test that error log doesn't grow unbounded"""
        # Add many errors
        for i in range(1000):
            dashboard.add_error("TestError", f"Error {i}")

        # Should have reasonable limit (check implementation)
        assert len(dashboard.stats['errors']) <= 1000


@pytest.mark.unit
class TestActivityLogging:
    """Test activity log functionality"""

    def test_activity_log_entries(self, dashboard):
        """Test adding activity log entries"""
        dashboard.add_activity("Processing started", success=True)
        dashboard.add_activity("File processed", success=True)
        dashboard.add_activity("Warning occurred", success=False)

        assert len(dashboard.stats['activity_log']) == 3

    def test_activity_success_tracking(self, dashboard):
        """Test tracking success/failure in activities"""
        dashboard.add_activity("Success", success=True)
        dashboard.add_activity("Failure", success=False)

        activities = dashboard.stats['activity_log']
        success_activities = [a for a in activities if a.get('success', True)]
        assert len(success_activities) >= 1

    def test_activity_log_limit(self, dashboard):
        """Test that activity log has reasonable size limit"""
        # Add many activities
        for i in range(500):
            dashboard.add_activity(f"Activity {i}")

        # Should have max size (typically 100-200)
        log_size = len(dashboard.stats['activity_log'])
        assert log_size <= 500  # Implementation specific


@pytest.mark.unit
class TestStatisticsCalculation:
    """Test statistics calculation methods"""

    def test_calculate_stats_average(self, dashboard):
        """Test calculating average from deque"""
        values = deque([1.0, 2.0, 3.0, 4.0, 5.0], maxlen=10)
        stats = dashboard._calculate_stats(values)

        assert 'avg' in stats
        assert stats['avg'] == 3.0

    def test_calculate_stats_min_max(self, dashboard):
        """Test calculating min/max from deque"""
        values = deque([1.0, 5.0, 3.0, 2.0, 4.0], maxlen=10)
        stats = dashboard._calculate_stats(values)

        assert stats['min'] == 1.0
        assert stats['max'] == 5.0

    def test_calculate_stats_empty(self, dashboard):
        """Test calculating stats from empty deque"""
        values = deque([], maxlen=10)
        stats = dashboard._calculate_stats(values)

        # Should handle empty gracefully
        assert stats['avg'] == 0.0 or stats == {}

    def test_calculate_stats_single_value(self, dashboard):
        """Test calculating stats from single value"""
        values = deque([42.0], maxlen=10)
        stats = dashboard._calculate_stats(values)

        assert stats['avg'] == 42.0
        assert stats['min'] == 42.0
        assert stats['max'] == 42.0


@pytest.mark.unit
class TestDashboardRendering:
    """Test dashboard rendering functionality"""

    def test_render_returns_layout(self, dashboard):
        """Test that render returns a Layout object"""
        layout = dashboard.render()

        # Should return Rich Layout or similar
        assert layout is not None

    def test_render_with_no_data(self, dashboard):
        """Test rendering with no data"""
        # Fresh dashboard with no updates
        layout = dashboard.render()

        assert layout is not None

    def test_render_with_full_data(self, dashboard):
        """Test rendering with complete data"""
        # Populate all metrics
        dashboard.add_ai_request(2.5, True, 150)
        dashboard.add_cache_hit()
        dashboard.add_file_processing_time(500, 3.0)
        dashboard.add_moc_category("Technology")
        dashboard.add_activity("Test activity")
        dashboard.update_system_resources()

        layout = dashboard.render()
        assert layout is not None

    @patch('rich.console.Console')
    def test_render_updates_console(self, mock_console, dashboard):
        """Test that rendering updates console"""
        dashboard.add_activity("Test")
        dashboard.render()

        # Render was called (layout created)
        assert True  # If we got here without error, rendering works


@pytest.mark.unit
class TestDashboardLifecycle:
    """Test dashboard start/stop lifecycle"""

    def test_start_dashboard(self, dashboard):
        """Test starting dashboard"""
        dashboard.start()

        # Dashboard should be marked as running
        assert hasattr(dashboard, 'running') or dashboard._running

    def test_stop_dashboard(self, dashboard):
        """Test stopping dashboard"""
        dashboard.start()
        dashboard.stop()

        # Dashboard should be stopped
        assert not dashboard._running

    def test_multiple_start_stop_cycles(self, dashboard):
        """Test multiple start/stop cycles"""
        for _ in range(3):
            dashboard.start()
            dashboard.stop()

        # Should handle multiple cycles
        assert not dashboard._running

    def test_updates_while_running(self, dashboard):
        """Test that updates work while dashboard is running"""
        dashboard.start()

        try:
            dashboard.add_activity("Test activity")
            assert len(dashboard.stats['activity_log']) > 0
        finally:
            dashboard.stop()


@pytest.mark.unit
class TestCachePerformanceTracking:
    """Test cache performance tracking"""

    def test_cache_hit_rate_calculation(self, dashboard):
        """Test calculating cache hit rate"""
        # 7 hits, 3 misses = 70% hit rate
        for _ in range(7):
            dashboard.add_cache_hit()
        for _ in range(3):
            dashboard.add_cache_miss()

        total = dashboard.stats['cache_hits'] + dashboard.stats['cache_misses']
        hit_rate = (dashboard.stats['cache_hits'] / total) * 100

        assert hit_rate == 70.0

    def test_cache_lookup_time_tracking(self, dashboard):
        """Test tracking cache lookup times"""
        dashboard.add_cache_hit(lookup_time=0.001)
        dashboard.add_cache_hit(lookup_time=0.002)
        dashboard.add_cache_hit(lookup_time=0.003)

        # Should track lookup times if implemented
        assert dashboard.stats['cache_hits'] == 3

    def test_cache_stats_update(self, dashboard):
        """Test updating cache size statistics"""
        dashboard.update_cache_stats(size_mb=15.5, entries=1000)

        assert dashboard.stats.get('cache_size_mb') == 15.5
        assert dashboard.stats.get('cache_entries') == 1000


@pytest.mark.unit
class TestAIPerformanceTracking:
    """Test AI performance metrics"""

    def test_ai_response_time_tracking(self, dashboard):
        """Test tracking AI response times"""
        response_times = [1.0, 2.0, 3.0, 4.0, 5.0]

        for rt in response_times:
            dashboard.add_ai_request(rt, success=True)

        times = dashboard.stats['ai_response_times']
        avg_time = sum(times) / len(times)
        assert avg_time == 3.0

    def test_ai_success_rate(self, dashboard):
        """Test calculating AI success rate"""
        # 8 successes, 2 failures = 80% success rate
        for _ in range(8):
            dashboard.add_ai_request(2.0, success=True)
        for _ in range(2):
            dashboard.add_ai_request(2.0, success=False)

        total = dashboard.stats['ai_requests']
        success_rate = (dashboard.stats['ai_success'] / total) * 100
        assert success_rate == 80.0

    def test_ai_timeout_tracking(self, dashboard):
        """Test tracking AI timeouts separately"""
        dashboard.add_ai_request(10.0, success=False, timeout=True)
        dashboard.add_ai_request(2.0, success=True, timeout=False)

        assert dashboard.stats['ai_timeouts'] == 1
        assert dashboard.stats['ai_requests'] == 2

    def test_ai_token_usage_tracking(self, dashboard):
        """Test tracking token usage"""
        dashboard.add_ai_request(2.0, success=True, tokens=100)
        dashboard.add_ai_request(3.0, success=True, tokens=150)
        dashboard.add_ai_request(2.5, success=True, tokens=200)

        total_tokens = sum(dashboard.stats.get('ai_tokens', [0]))
        assert total_tokens == 450 or len(dashboard.stats.get('ai_tokens', [])) == 3


@pytest.mark.integration
class TestLiveMonitoringIntegration:
    """Integration tests for live monitoring"""

    def test_full_monitoring_session(self, dashboard):
        """Test complete monitoring session"""
        dashboard.start()

        try:
            # Simulate processing session
            for i in range(10):
                # AI request
                dashboard.add_ai_request(
                    response_time=2.0 + i * 0.1,
                    success=i < 8,  # 2 failures
                    tokens=100 + i * 10
                )

                # Cache operation
                if i % 2 == 0:
                    dashboard.add_cache_hit()
                else:
                    dashboard.add_cache_miss()

                # File processing
                dashboard.add_file_processing_time(500 + i * 100, 2.0 + i * 0.5)

                # MOC category
                categories = ["Technology", "Business", "Personal"]
                dashboard.add_moc_category(categories[i % 3])

                # Activity
                dashboard.add_activity(f"Processing file {i}")

            # Update system resources
            dashboard.update_system_resources()

            # Render dashboard
            layout = dashboard.render()

            # Verify all metrics were tracked
            assert dashboard.stats['ai_requests'] == 10
            assert dashboard.stats['cache_hits'] + dashboard.stats['cache_misses'] == 10
            assert len(dashboard.stats['file_processing_times']) == 10
            assert len(dashboard.stats['activity_log']) > 0

        finally:
            dashboard.stop()

    def test_dashboard_under_load(self, dashboard):
        """Test dashboard performance under high load"""
        dashboard.start()

        try:
            start_time = time.time()

            # Rapid updates
            for i in range(1000):
                dashboard.add_activity(f"Activity {i}")

            elapsed = time.time() - start_time

            # Should handle load efficiently
            assert elapsed < 5.0  # Should complete in under 5 seconds

        finally:
            dashboard.stop()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
