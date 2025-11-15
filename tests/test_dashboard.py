"""
Unit tests for live dashboard module
Tests dashboard initialization, metrics tracking, and rendering
"""

import pytest
import time
from datetime import datetime
from collections import deque
from unittest.mock import patch, MagicMock

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@pytest.mark.unit
class TestLiveDashboard:
    """Test suite for LiveDashboard"""

    def test_dashboard_initialization(self):
        """Test dashboard initializes with correct defaults"""
        from live_dashboard import LiveDashboard

        dashboard = LiveDashboard(update_interval=30)

        assert dashboard.update_interval == 30
        assert dashboard.running == False
        assert dashboard.stats is not None
        assert 'total_files' in dashboard.stats
        assert 'processed_files' in dashboard.stats

    def test_dashboard_start(self):
        """Test dashboard start method"""
        from live_dashboard import LiveDashboard

        dashboard = LiveDashboard()
        dashboard.start()

        assert dashboard.running == True
        assert dashboard.stats['start_time'] is not None

    def test_dashboard_stop(self):
        """Test dashboard stop method"""
        from live_dashboard import LiveDashboard

        dashboard = LiveDashboard()
        dashboard.start()
        dashboard.stop()

        assert dashboard.running == False

    def test_update_processing_stats(self):
        """Test updating processing statistics"""
        from live_dashboard import LiveDashboard

        dashboard = LiveDashboard()
        dashboard.update_processing(
            total_files=100,
            processed_files=50,
            failed_files=5,
            current_file='test.md',
            current_stage='Processing'
        )

        assert dashboard.stats['total_files'] == 100
        assert dashboard.stats['processed_files'] == 50
        assert dashboard.stats['failed_files'] == 5
        assert dashboard.stats['current_file'] == 'test.md'
        assert dashboard.stats['current_stage'] == 'Processing'

    def test_add_ai_request_success(self):
        """Test tracking successful AI request"""
        from live_dashboard import LiveDashboard

        dashboard = LiveDashboard()
        dashboard.add_ai_request(response_time=2.5, success=True, tokens=100)

        assert dashboard.stats['ai_requests'] == 1
        assert dashboard.stats['ai_success'] == 1
        assert len(dashboard.stats['ai_response_times']) == 1
        assert dashboard.stats['ai_response_times'][0] == 2.5

    def test_add_ai_request_failure(self):
        """Test tracking failed AI request"""
        from live_dashboard import LiveDashboard

        dashboard = LiveDashboard()
        dashboard.add_ai_request(response_time=5.0, success=False, timeout=True)

        assert dashboard.stats['ai_requests'] == 1
        assert dashboard.stats['ai_failures'] == 1
        assert dashboard.stats['ai_timeouts'] == 1

    def test_add_cache_hit(self):
        """Test tracking cache hit"""
        from live_dashboard import LiveDashboard

        dashboard = LiveDashboard()
        dashboard.add_cache_hit(lookup_time=0.001)

        assert dashboard.stats['cache_hits'] == 1
        assert len(dashboard.stats['cache_lookup_times']) == 1

    def test_add_cache_miss(self):
        """Test tracking cache miss"""
        from live_dashboard import LiveDashboard

        dashboard = LiveDashboard()
        dashboard.add_cache_miss()

        assert dashboard.stats['cache_misses'] == 1

    def test_update_cache_stats(self):
        """Test updating cache statistics"""
        from live_dashboard import LiveDashboard

        dashboard = LiveDashboard()
        dashboard.update_cache_stats(size_mb=2.5, entries=100)

        assert dashboard.stats['cache_size_mb'] == 2.5
        assert dashboard.stats['cache_entries'] == 100

    def test_add_file_processing_time(self):
        """Test tracking file processing time"""
        from live_dashboard import LiveDashboard

        dashboard = LiveDashboard()

        # Small file
        dashboard.add_file_processing_time(file_size_kb=3, processing_time=1.5)
        assert len(dashboard.stats['file_times_small']) == 1

        # Medium file
        dashboard.add_file_processing_time(file_size_kb=25, processing_time=5.0)
        assert len(dashboard.stats['file_times_medium']) == 1

        # Large file
        dashboard.add_file_processing_time(file_size_kb=100, processing_time=10.0)
        assert len(dashboard.stats['file_times_large']) == 1

    def test_add_moc_category(self):
        """Test tracking MOC category distribution"""
        from live_dashboard import LiveDashboard

        dashboard = LiveDashboard()
        dashboard.add_moc_category('Business Operations')
        dashboard.add_moc_category('Business Operations')
        dashboard.add_moc_category('Technical & Automation')

        assert dashboard.stats['moc_distribution']['Business Operations'] == 2
        assert dashboard.stats['moc_distribution']['Technical & Automation'] == 1

    def test_add_error(self):
        """Test error tracking"""
        from live_dashboard import LiveDashboard

        dashboard = LiveDashboard()
        dashboard.add_error('timeout', 'Connection timed out')

        assert len(dashboard.stats['recent_errors']) == 1
        assert dashboard.stats['error_types']['timeout'] == 1

    def test_add_activity(self):
        """Test activity logging"""
        from live_dashboard import LiveDashboard

        dashboard = LiveDashboard()
        dashboard.add_activity('Processing file.md', success=True)
        dashboard.add_activity('Failed to process', success=False)

        assert len(dashboard.stats['recent_activity']) == 2
        assert '✓' in dashboard.stats['recent_activity'][0]
        assert '✗' in dashboard.stats['recent_activity'][1]

    def test_update_system_resources(self):
        """Test system resource monitoring"""
        from live_dashboard import LiveDashboard

        dashboard = LiveDashboard()

        with patch('live_dashboard.psutil.cpu_percent', return_value=50.0):
            with patch('live_dashboard.psutil.virtual_memory') as mock_mem:
                mock_mem.return_value = MagicMock(
                    percent=60.0,
                    used=8 * 1024**3,
                    total=16 * 1024**3
                )
                dashboard.update_system_resources()

                assert dashboard.stats['cpu_percent'] > 0
                assert dashboard.stats['memory_percent'] > 0

    def test_calculate_stats_empty(self):
        """Test stats calculation with empty data"""
        from live_dashboard import LiveDashboard

        dashboard = LiveDashboard()
        result = dashboard._calculate_stats(deque())

        assert result['min'] == 0
        assert result['max'] == 0
        assert result['avg'] == 0

    def test_calculate_stats_with_data(self):
        """Test stats calculation with data"""
        from live_dashboard import LiveDashboard

        dashboard = LiveDashboard()
        data = deque([1.0, 2.0, 3.0, 4.0, 5.0])
        result = dashboard._calculate_stats(data)

        assert result['min'] == 1.0
        assert result['max'] == 5.0
        assert result['avg'] == 3.0
        assert result['median'] == 3.0

    def test_create_processing_panel(self):
        """Test processing panel creation"""
        from live_dashboard import LiveDashboard

        dashboard = LiveDashboard()
        dashboard.update_processing(total_files=100, processed_files=50)

        panel = dashboard._create_processing_panel()

        assert panel is not None
        assert hasattr(panel, 'renderable') or isinstance(panel, object)

    def test_create_system_panel(self):
        """Test system panel creation"""
        from live_dashboard import LiveDashboard

        dashboard = LiveDashboard()

        with patch('live_dashboard.psutil.cpu_percent', return_value=50.0):
            with patch('live_dashboard.psutil.virtual_memory') as mock_mem:
                mock_mem.return_value = MagicMock(percent=60.0, used=8*1024**3, total=16*1024**3)
                panel = dashboard._create_system_panel()

                assert panel is not None

    def test_create_ai_panel(self):
        """Test AI performance panel creation"""
        from live_dashboard import LiveDashboard

        dashboard = LiveDashboard()
        dashboard.add_ai_request(2.5, True, 100)

        panel = dashboard._create_ai_panel()

        assert panel is not None

    def test_create_cache_panel(self):
        """Test cache panel creation"""
        from live_dashboard import LiveDashboard

        dashboard = LiveDashboard()
        dashboard.add_cache_hit()
        dashboard.add_cache_miss()

        panel = dashboard._create_cache_panel()

        assert panel is not None

    def test_render(self):
        """Test dashboard rendering"""
        from live_dashboard import LiveDashboard

        dashboard = LiveDashboard()

        with patch('live_dashboard.psutil.cpu_percent', return_value=50.0):
            with patch('live_dashboard.psutil.virtual_memory') as mock_mem:
                mock_mem.return_value = MagicMock(percent=60.0, used=8*1024**3, total=16*1024**3)
                with patch('live_dashboard.psutil.disk_io_counters', return_value=None):
                    with patch('live_dashboard.psutil.net_io_counters', return_value=None):
                        layout = dashboard.render()

                        assert layout is not None

    def test_get_dashboard_singleton(self):
        """Test dashboard singleton pattern"""
        from live_dashboard import get_dashboard

        dashboard1 = get_dashboard()
        dashboard2 = get_dashboard()

        # Should return same instance
        assert dashboard1 is dashboard2

    def test_deque_max_length(self):
        """Test that deques respect max length"""
        from live_dashboard import LiveDashboard

        dashboard = LiveDashboard()

        # Add more than max items
        for i in range(150):
            dashboard.add_ai_request(1.0, True, 100)

        # Should only keep last 100
        assert len(dashboard.stats['ai_response_times']) == 100

    def test_activity_log_max_length(self):
        """Test activity log max length"""
        from live_dashboard import LiveDashboard

        dashboard = LiveDashboard()

        # Add more than max activities
        for i in range(10):
            dashboard.add_activity(f'Activity {i}', success=True)

        # Should only keep last 5
        assert len(dashboard.stats['recent_activity']) <= 5

    def test_tokens_per_second_calculation(self):
        """Test tokens per second calculation"""
        from live_dashboard import LiveDashboard

        dashboard = LiveDashboard()
        dashboard.add_ai_request(response_time=2.0, success=True, tokens=200)

        # Should calculate tokens per second
        assert dashboard.stats['tokens_per_second'] == 100.0


@pytest.mark.integration
class TestDashboardIntegration:
    """Integration tests for dashboard"""

    def test_dashboard_full_workflow(self):
        """Test complete dashboard workflow"""
        from live_dashboard import LiveDashboard

        dashboard = LiveDashboard(update_interval=1)
        dashboard.start()

        # Simulate processing
        dashboard.update_processing(total_files=10, processed_files=0)

        for i in range(5):
            dashboard.update_processing(processed_files=i+1)
            dashboard.add_ai_request(2.0, True, 100)
            dashboard.add_cache_hit()
            dashboard.add_activity(f'Processed file {i}', success=True)

        dashboard.stop()

        assert dashboard.stats['processed_files'] == 5
        assert dashboard.stats['ai_requests'] == 5
        assert dashboard.stats['cache_hits'] == 5


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
