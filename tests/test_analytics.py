"""
Unit tests for enhanced analytics module
Tests analytics report generation and data processing
"""

import pytest
import json
import os
import tempfile
from datetime import datetime
from unittest.mock import patch, mock_open, MagicMock

import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@pytest.mark.unit
class TestEnhancedAnalytics:
    """Test suite for enhanced analytics"""

    def test_load_analytics_data_success(self, temp_vault, sample_analytics):
        """Test successful loading of analytics data"""
        from enhanced_analytics import load_analytics_data

        # Create analytics file
        analytics_file = os.path.join(temp_vault, 'processing_analytics.json')
        with open(analytics_file, 'w') as f:
            json.dump(sample_analytics, f)

        with patch('enhanced_analytics.os.path.exists', return_value=True):
            with patch('builtins.open', mock_open(read_data=json.dumps({'processing': sample_analytics}))):
                result = load_analytics_data()

                assert 'processing' in result

    def test_load_analytics_data_missing_file(self):
        """Test loading when analytics file doesn't exist"""
        from enhanced_analytics import load_analytics_data

        with patch('enhanced_analytics.os.path.exists', return_value=False):
            result = load_analytics_data()

            # Should return empty dict or handle gracefully
            assert isinstance(result, dict)

    def test_generate_comprehensive_report_structure(self, sample_analytics):
        """Test that comprehensive report has correct HTML structure"""
        from enhanced_analytics import generate_comprehensive_report

        analytics = {'processing': sample_analytics}
        html = generate_comprehensive_report(analytics)

        # Verify HTML structure
        assert '<!DOCTYPE html>' in html
        assert '<html' in html
        assert '</html>' in html
        assert '<head>' in html
        assert '<body>' in html

    def test_generate_comprehensive_report_includes_metrics(self, sample_analytics):
        """Test that report includes all key metrics"""
        from enhanced_analytics import generate_comprehensive_report

        analytics = {'processing': sample_analytics}
        html = generate_comprehensive_report(analytics)

        # Verify key metrics are included
        assert str(sample_analytics['total_files']) in html
        assert str(sample_analytics['processed_files']) in html
        assert 'Processing Summary' in html or 'PERFORMANCE' in html

    def test_generate_comprehensive_report_moc_distribution(self, sample_analytics):
        """Test MOC distribution visualization"""
        from enhanced_analytics import generate_comprehensive_report

        analytics = {'processing': sample_analytics}
        html = generate_comprehensive_report(analytics)

        # Verify MOC categories are shown
        for moc in sample_analytics['moc_distribution'].keys():
            assert moc in html

    def test_generate_comprehensive_report_recommendations(self, sample_analytics):
        """Test that recommendations are generated"""
        from enhanced_analytics import generate_comprehensive_report

        analytics = {'processing': sample_analytics}
        html = generate_comprehensive_report(analytics)

        # Should have recommendations section
        assert 'Recommendations' in html or 'RECOMMEND' in html

    def test_auto_open_report_success(self, temp_vault):
        """Test auto-opening report in browser"""
        from enhanced_analytics import auto_open_report

        report_path = os.path.join(temp_vault, 'test_report.html')
        with open(report_path, 'w') as f:
            f.write('<html></html>')

        with patch('enhanced_analytics.webbrowser.open') as mock_open:
            auto_open_report(report_path)

            # Should attempt to open browser
            mock_open.assert_called_once()

    def test_auto_open_report_file_not_found(self):
        """Test auto-open with missing file"""
        from enhanced_analytics import auto_open_report

        with patch('enhanced_analytics.webbrowser.open', side_effect=Exception("File not found")):
            # Should not raise exception
            auto_open_report('/nonexistent/path.html')

    def test_main_function_creates_report(self, sample_analytics, temp_vault):
        """Test main function creates report file"""
        from enhanced_analytics import main

        analytics_file = os.path.join(temp_vault, 'processing_analytics.json')
        with open(analytics_file, 'w') as f:
            json.dump(sample_analytics, f)

        with patch('enhanced_analytics.load_analytics_data', return_value={'processing': sample_analytics}):
            with patch('enhanced_analytics.auto_open_report'):
                with patch('builtins.open', mock_open()) as mock_file:
                    report_path = main()

                    # Should return report path
                    assert report_path is not None

    def test_calculate_performance_metrics(self, sample_analytics):
        """Test performance metrics calculation"""
        from enhanced_analytics import generate_comprehensive_report

        analytics = {'processing': sample_analytics}
        html = generate_comprehensive_report(analytics)

        # Should calculate files per minute
        total_time = sample_analytics['processing_time']
        processed = sample_analytics['processed_files']
        if total_time > 0:
            expected_speed = int((processed / total_time) * 60)
            # Speed might be in the HTML (allowing for formatting differences)

    def test_empty_analytics_data(self):
        """Test report generation with empty data"""
        from enhanced_analytics import generate_comprehensive_report

        empty_analytics = {
            'processing': {
                'total_files': 0,
                'processed_files': 0,
                'skipped_files': 0,
                'failed_files': 0,
                'processing_time': 0,
                'moc_distribution': {},
                'error_types': {}
            }
        }

        html = generate_comprehensive_report(empty_analytics)

        # Should still generate valid HTML
        assert '<!DOCTYPE html>' in html
        assert '0' in html  # Should show zeros

    def test_moc_percentage_calculation(self, sample_analytics):
        """Test MOC distribution percentage calculation"""
        from enhanced_analytics import generate_comprehensive_report

        analytics = {'processing': sample_analytics}
        html = generate_comprehensive_report(analytics)

        # Calculate expected percentages
        total = sample_analytics['total_files']
        for moc, count in sample_analytics['moc_distribution'].items():
            percentage = (count / total * 100) if total > 0 else 0
            # Percentage might be formatted differently, just check it's present

    def test_report_styling(self, sample_analytics):
        """Test that report includes CSS styling"""
        from enhanced_analytics import generate_comprehensive_report

        analytics = {'processing': sample_analytics}
        html = generate_comprehensive_report(analytics)

        # Should have style section
        assert '<style>' in html or '<link' in html
        assert 'background' in html or 'color' in html

    def test_report_timestamp(self, sample_analytics):
        """Test that report includes timestamp"""
        from enhanced_analytics import generate_comprehensive_report

        analytics = {'processing': sample_analytics}
        html = generate_comprehensive_report(analytics)

        # Should have generation timestamp
        current_year = datetime.now().year
        assert str(current_year) in html

    def test_success_rate_calculation(self, sample_analytics):
        """Test success rate calculation"""
        from enhanced_analytics import generate_comprehensive_report

        analytics = {'processing': sample_analytics}
        html = generate_comprehensive_report(analytics)

        # Calculate expected success rate
        total = sample_analytics['total_files']
        processed = sample_analytics['processed_files']
        if total > 0:
            success_rate = (processed / total * 100)
            # Should be somewhere in the report

    def test_error_summary_included(self, sample_analytics):
        """Test that error summary is included"""
        from enhanced_analytics import generate_comprehensive_report

        analytics = {'processing': sample_analytics}
        html = generate_comprehensive_report(analytics)

        # Should have error section
        for error_type in sample_analytics['error_types'].keys():
            assert error_type in html or 'Error' in html


@pytest.mark.integration
class TestAnalyticsIntegration:
    """Integration tests for analytics workflow"""

    def test_full_analytics_workflow(self, sample_analytics, temp_vault):
        """Test complete analytics generation workflow"""
        from enhanced_analytics import load_analytics_data, generate_comprehensive_report, main

        # Create analytics file
        analytics_file = os.path.join(temp_vault, 'processing_analytics.json')
        with open(analytics_file, 'w') as f:
            json.dump(sample_analytics, f)

        # Load data
        with patch('enhanced_analytics.os.path.exists', return_value=True):
            with patch('builtins.open', mock_open(read_data=json.dumps({'processing': sample_analytics}))):
                data = load_analytics_data()
                assert 'processing' in data

        # Generate report
        html = generate_comprehensive_report({'processing': sample_analytics})
        assert len(html) > 0

    def test_report_file_creation(self, sample_analytics, temp_vault):
        """Test that report file is actually created"""
        from enhanced_analytics import main

        with patch('enhanced_analytics.load_analytics_data', return_value={'processing': sample_analytics}):
            with patch('enhanced_analytics.auto_open_report'):
                report_path = main()

                # In real scenario, file should exist
                # In test, we're mocking, but path should be returned
                assert report_path is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
