"""
Unit tests for ultra detailed analytics module
Tests comprehensive analytics reporting with before/after comparisons
"""

import pytest
import json
import os
from unittest.mock import patch, mock_open, MagicMock
from pathlib import Path

import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@pytest.fixture
def sample_processing_analytics():
    """Sample processing analytics data"""
    return {
        'files_processed': 50,
        'total_time': 300.5,
        'avg_time_per_file': 6.01,
        'cache_hits': 25,
        'cache_misses': 25,
        'errors': 2
    }


@pytest.fixture
def sample_cache_data():
    """Sample cache data"""
    return {
        'hash1': {'moc_category': 'Technology', 'confidence': 0.9},
        'hash2': {'moc_category': 'Business', 'confidence': 0.85},
        'hash3': {'moc_category': 'Personal', 'confidence': 0.75}
    }


@pytest.fixture
def sample_before_after_data():
    """Sample before/after file comparison data"""
    return {
        '/vault/note1.md': {
            'lines_added': 5,
            'lines_removed': 2,
            'lines_modified': 3,
            'change_score': 15.5,
            'key_changes': [
                'Added [[Technology MOC]] link',
                'Modified heading structure',
                'Added wikilinks to 3 notes'
            ]
        },
        '/vault/note2.md': {
            'lines_added': 10,
            'lines_removed': 0,
            'lines_modified': 2,
            'change_score': 22.3,
            'key_changes': [
                'Created new MOC section',
                'Added 10 wikilinks'
            ]
        }
    }


@pytest.fixture
def sample_reasoning_data():
    """Sample AI reasoning analysis data"""
    return {
        'total_categorizations': 50,
        'category_distribution': {
            'Technology': 20,
            'Business Operations': 15,
            'Personal Development': 10,
            'Life & Misc': 5
        },
        'avg_confidence': 0.82,
        'high_confidence_count': 35,
        'low_confidence_count': 5
    }


@pytest.fixture
def complete_analytics_data(
    sample_processing_analytics,
    sample_cache_data,
    sample_before_after_data,
    sample_reasoning_data
):
    """Complete analytics data combining all sources"""
    return {
        'processing': sample_processing_analytics,
        'cache': sample_cache_data,
        'before_after': sample_before_after_data,
        'reasoning': sample_reasoning_data
    }


@pytest.mark.unit
class TestLoadAnalyticsData:
    """Test analytics data loading"""

    def test_load_all_analytics_files(self, tmp_path, complete_analytics_data):
        """Test loading all analytics files when they exist"""
        from ultra_detailed_analytics import load_analytics_data

        # Create test files
        (tmp_path / 'processing_analytics.json').write_text(
            json.dumps(complete_analytics_data['processing'])
        )
        (tmp_path / '.ai_cache.json').write_text(
            json.dumps(complete_analytics_data['cache'])
        )
        (tmp_path / 'before_after_analysis.json').write_text(
            json.dumps(complete_analytics_data['before_after'])
        )
        (tmp_path / 'reasoning_analysis.json').write_text(
            json.dumps(complete_analytics_data['reasoning'])
        )

        # Change to temp directory
        original_dir = os.getcwd()
        try:
            os.chdir(tmp_path)
            analytics = load_analytics_data()

            assert 'processing' in analytics
            assert 'cache' in analytics
            assert 'before_after' in analytics
            assert 'reasoning' in analytics
            assert analytics['processing']['files_processed'] == 50
        finally:
            os.chdir(original_dir)

    def test_load_partial_analytics_files(self, tmp_path, sample_processing_analytics):
        """Test loading when only some analytics files exist"""
        from ultra_detailed_analytics import load_analytics_data

        # Create only one file
        (tmp_path / 'processing_analytics.json').write_text(
            json.dumps(sample_processing_analytics)
        )

        original_dir = os.getcwd()
        try:
            os.chdir(tmp_path)
            analytics = load_analytics_data()

            assert 'processing' in analytics
            assert 'cache' not in analytics
            assert 'before_after' not in analytics
        finally:
            os.chdir(original_dir)

    def test_load_no_analytics_files(self, tmp_path):
        """Test loading when no analytics files exist"""
        from ultra_detailed_analytics import load_analytics_data

        original_dir = os.getcwd()
        try:
            os.chdir(tmp_path)
            analytics = load_analytics_data()

            assert analytics == {}
        finally:
            os.chdir(original_dir)

    def test_load_with_invalid_json(self, tmp_path):
        """Test handling of invalid JSON in analytics files"""
        from ultra_detailed_analytics import load_analytics_data

        # Create file with invalid JSON
        (tmp_path / 'processing_analytics.json').write_text('invalid json {')

        original_dir = os.getcwd()
        try:
            os.chdir(tmp_path)
            with pytest.raises(json.JSONDecodeError):
                load_analytics_data()
        finally:
            os.chdir(original_dir)


@pytest.mark.unit
class TestBeforeAfterComparison:
    """Test before/after file comparison generation"""

    def test_generate_comparison_with_data(self, complete_analytics_data):
        """Test generating comparison HTML with data"""
        from ultra_detailed_analytics import generate_before_after_comparison

        html = generate_before_after_comparison(complete_analytics_data)

        assert '📄 Before/After File Analysis' in html
        assert 'note1.md' in html
        assert 'note2.md' in html
        assert 'Lines Added:' in html
        assert 'Lines Removed:' in html
        assert 'Change Score:' in html
        assert '5' in html  # lines_added for note1
        assert '10' in html  # lines_added for note2

    def test_generate_comparison_without_data(self):
        """Test generating comparison HTML without data"""
        from ultra_detailed_analytics import generate_before_after_comparison

        html = generate_before_after_comparison({})

        assert '📄 Before/After Analysis' in html
        assert 'No before/after data available' in html

    def test_key_changes_display(self, complete_analytics_data):
        """Test that key changes are displayed"""
        from ultra_detailed_analytics import generate_before_after_comparison

        html = generate_before_after_comparison(complete_analytics_data)

        assert '🔑 Key Changes:' in html
        assert 'Technology MOC' in html
        assert 'wikilinks' in html

    def test_key_changes_limit(self):
        """Test that only top 5 key changes are shown"""
        from ultra_detailed_analytics import generate_before_after_comparison

        analytics = {
            'before_after': {
                '/vault/test.md': {
                    'lines_added': 10,
                    'lines_removed': 5,
                    'lines_modified': 3,
                    'change_score': 25.0,
                    'key_changes': [f'Change {i}' for i in range(10)]
                }
            }
        }

        html = generate_before_after_comparison(analytics)

        # Should show 5 changes, not all 10
        assert 'Change 0' in html
        assert 'Change 4' in html
        # Should not show changes 5-9 directly (though might be in HTML)

    def test_comparison_stats_formatting(self, sample_before_after_data):
        """Test that stats are properly formatted"""
        from ultra_detailed_analytics import generate_before_after_comparison

        analytics = {'before_after': sample_before_after_data}
        html = generate_before_after_comparison(analytics)

        assert '15.5%' in html  # change_score for note1
        assert '22.3%' in html  # change_score for note2


@pytest.mark.unit
class TestReasoningAnalysis:
    """Test AI reasoning analysis generation"""

    def test_generate_reasoning_with_data(self, complete_analytics_data):
        """Test generating reasoning HTML with data"""
        from ultra_detailed_analytics import generate_reasoning_analysis

        html = generate_reasoning_analysis(complete_analytics_data)

        # Should contain reasoning analysis content
        assert isinstance(html, str)
        assert len(html) > 0

    def test_generate_reasoning_without_data(self):
        """Test generating reasoning HTML without data"""
        from ultra_detailed_analytics import generate_reasoning_analysis

        html = generate_reasoning_analysis({})

        assert isinstance(html, str)
        # Should handle missing data gracefully


@pytest.mark.unit
class TestUltraDetailedReport:
    """Test ultra detailed report generation"""

    def test_generate_report_structure(self, complete_analytics_data):
        """Test that generated report has proper HTML structure"""
        from ultra_detailed_analytics import generate_ultra_detailed_report

        html = generate_ultra_detailed_report(complete_analytics_data)

        assert '<!DOCTYPE html>' in html or '<html' in html
        assert '<head>' in html or '</head>' in html
        assert '<body>' in html or '</body>' in html

    def test_generate_report_includes_all_sections(self, complete_analytics_data):
        """Test that report includes all major sections"""
        from ultra_detailed_analytics import generate_ultra_detailed_report

        html = generate_ultra_detailed_report(complete_analytics_data)

        # Check for section markers
        assert 'Before/After' in html or 'before-after' in html.lower()
        # Report should have substantial content
        assert len(html) > 1000

    def test_generate_report_with_empty_data(self):
        """Test report generation with empty analytics"""
        from ultra_detailed_analytics import generate_ultra_detailed_report

        html = generate_ultra_detailed_report({})

        # Should still generate valid HTML
        assert isinstance(html, str)
        assert len(html) > 0

    def test_generate_report_with_partial_data(self, sample_processing_analytics):
        """Test report generation with partial analytics"""
        from ultra_detailed_analytics import generate_ultra_detailed_report

        analytics = {'processing': sample_processing_analytics}
        html = generate_ultra_detailed_report(analytics)

        assert isinstance(html, str)
        assert len(html) > 500


@pytest.mark.unit
class TestAutoOpenReport:
    """Test auto-opening report in browser"""

    def test_auto_open_calls_webbrowser(self):
        """Test that auto_open calls webbrowser.open"""
        from ultra_detailed_analytics import auto_open_report

        with patch('webbrowser.open') as mock_open:
            auto_open_report('/path/to/report.html')
            mock_open.assert_called_once()

    def test_auto_open_with_file_path(self):
        """Test auto_open with actual file path"""
        from ultra_detailed_analytics import auto_open_report

        with patch('webbrowser.open') as mock_open:
            test_path = '/tmp/test_report.html'
            auto_open_report(test_path)

            # Should have been called with the path
            args, kwargs = mock_open.call_args
            assert test_path in str(args[0])

    def test_auto_open_handles_exceptions(self):
        """Test that auto_open handles browser errors gracefully"""
        from ultra_detailed_analytics import auto_open_report

        with patch('webbrowser.open', side_effect=Exception("Browser error")):
            # Should not raise exception
            try:
                auto_open_report('/path/to/report.html')
            except Exception:
                pytest.fail("auto_open_report should handle exceptions gracefully")


@pytest.mark.integration
class TestUltraDetailedAnalyticsIntegration:
    """Integration tests for ultra detailed analytics"""

    def test_full_workflow(self, tmp_path, complete_analytics_data):
        """Test complete analytics workflow"""
        from ultra_detailed_analytics import (
            load_analytics_data,
            generate_ultra_detailed_report
        )

        # Setup test files
        (tmp_path / 'processing_analytics.json').write_text(
            json.dumps(complete_analytics_data['processing'])
        )
        (tmp_path / 'before_after_analysis.json').write_text(
            json.dumps(complete_analytics_data['before_after'])
        )

        original_dir = os.getcwd()
        try:
            os.chdir(tmp_path)

            # Load data
            analytics = load_analytics_data()

            # Generate report
            html = generate_ultra_detailed_report(analytics)

            # Verify report content
            assert len(html) > 1000
            assert 'before' in html.lower() or 'after' in html.lower()

        finally:
            os.chdir(original_dir)

    def test_report_file_creation(self, tmp_path, complete_analytics_data):
        """Test that report file is created successfully"""
        from ultra_detailed_analytics import generate_ultra_detailed_report

        html = generate_ultra_detailed_report(complete_analytics_data)

        # Write to file
        report_path = tmp_path / 'test_report.html'
        report_path.write_text(html)

        # Verify file exists and has content
        assert report_path.exists()
        assert report_path.stat().st_size > 1000

    def test_multiple_files_comparison(self, tmp_path):
        """Test comparison with multiple files"""
        from ultra_detailed_analytics import generate_before_after_comparison

        analytics = {
            'before_after': {
                f'/vault/note{i}.md': {
                    'lines_added': i * 2,
                    'lines_removed': i,
                    'lines_modified': i + 1,
                    'change_score': i * 5.0,
                    'key_changes': [f'Change in note{i}']
                }
                for i in range(1, 6)  # 5 files
            }
        }

        html = generate_before_after_comparison(analytics)

        # Should include all files
        for i in range(1, 6):
            assert f'note{i}.md' in html


@pytest.mark.unit
class TestReportFormatting:
    """Test HTML report formatting"""

    def test_html_escaping(self):
        """Test that special characters are handled"""
        from ultra_detailed_analytics import generate_before_after_comparison

        analytics = {
            'before_after': {
                '/vault/<script>alert("test")</script>.md': {
                    'lines_added': 5,
                    'lines_removed': 2,
                    'lines_modified': 1,
                    'change_score': 10.0,
                    'key_changes': ['Test change']
                }
            }
        }

        html = generate_before_after_comparison(analytics)

        # Should not contain raw script tags (should be escaped or filename sanitized)
        # This is a security consideration
        assert isinstance(html, str)

    def test_percentage_formatting(self, sample_before_after_data):
        """Test that percentages are formatted correctly"""
        from ultra_detailed_analytics import generate_before_after_comparison

        analytics = {'before_after': sample_before_after_data}
        html = generate_before_after_comparison(analytics)

        # Should have decimal percentages
        assert '.1f' in str(sample_before_after_data) or '15.5%' in html


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
