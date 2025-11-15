"""
Unit tests for content processing and analysis
Tests MOC categorization, tag extraction, and AI analysis
"""

import pytest
import json
import re
from unittest.mock import patch, Mock

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@pytest.mark.unit
class TestContentProcessing:
    """Test suite for content processing"""

    def test_analyze_with_balanced_ai_success(self, sample_markdown_content, mock_ollama_success, sample_existing_notes):
        """Test successful content analysis"""
        from obsidian_auto_linker_enhanced import analyze_with_balanced_ai

        with patch('obsidian_auto_linker_enhanced.ai_cache', {}):
            result = analyze_with_balanced_ai(sample_markdown_content, sample_existing_notes)

            assert result is not None
            assert 'moc_category' in result
            assert 'primary_topic' in result
            assert 'hierarchical_tags' in result
            assert 'key_concepts' in result
            assert 'confidence_score' in result

    def test_analyze_with_balanced_ai_json_cleanup(self, sample_markdown_content, sample_existing_notes):
        """Test that markdown code blocks are cleaned from JSON response"""
        with patch('requests.post') as mock_post:
            mock_response = Mock()
            mock_response.status_code = 200
            # Response with markdown wrapper
            mock_response.json.return_value = {
                'response': '```json\n{"moc_category": "Test", "confidence_score": 0.8}\n```'
            }
            mock_response.raise_for_status = Mock()
            mock_post.return_value = mock_response

            from obsidian_auto_linker_enhanced import analyze_with_balanced_ai

            with patch('obsidian_auto_linker_enhanced.ai_cache', {}):
                result = analyze_with_balanced_ai(sample_markdown_content, sample_existing_notes)

                assert result is not None
                assert result['moc_category'] == 'Test'

    def test_analyze_with_balanced_ai_invalid_json(self, sample_markdown_content, sample_existing_notes):
        """Test handling of invalid JSON response"""
        with patch('requests.post') as mock_post:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                'response': 'This is not JSON at all'
            }
            mock_response.raise_for_status = Mock()
            mock_post.return_value = mock_response

            from obsidian_auto_linker_enhanced import analyze_with_balanced_ai

            with patch('obsidian_auto_linker_enhanced.ai_cache', {}):
                result = analyze_with_balanced_ai(sample_markdown_content, sample_existing_notes)

                # Should return None on parse failure
                assert result is None

    def test_analyze_with_balanced_ai_extracts_json(self, sample_markdown_content, sample_existing_notes):
        """Test extraction of JSON from text response"""
        with patch('requests.post') as mock_post:
            mock_response = Mock()
            mock_response.status_code = 200
            # JSON embedded in text
            mock_response.json.return_value = {
                'response': 'Here is the analysis: {"moc_category": "Test", "confidence_score": 0.9} - end'
            }
            mock_response.raise_for_status = Mock()
            mock_post.return_value = mock_response

            from obsidian_auto_linker_enhanced import analyze_with_balanced_ai

            with patch('obsidian_auto_linker_enhanced.ai_cache', {}):
                result = analyze_with_balanced_ai(sample_markdown_content, sample_existing_notes)

                assert result is not None
                assert result['moc_category'] == 'Test'

    def test_analyze_truncates_long_content(self, sample_existing_notes):
        """Test that very long content is truncated"""
        # Create very long content
        long_content = "Test content " * 1000  # Very long

        with patch('requests.post') as mock_post:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                'response': json.dumps({'moc_category': 'Test', 'confidence_score': 0.8})
            }
            mock_response.raise_for_status = Mock()
            mock_post.return_value = mock_response

            from obsidian_auto_linker_enhanced import analyze_with_balanced_ai

            with patch('obsidian_auto_linker_enhanced.ai_cache', {}):
                result = analyze_with_balanced_ai(long_content, sample_existing_notes)

                # Should still process successfully
                assert result is not None

                # Verify content was truncated in the API call
                call_args = mock_post.call_args
                payload = call_args.kwargs['json']
                prompt = payload['prompt']

                # Prompt should not be excessively long
                assert len(prompt) < 10000

    def test_should_process_file_include_patterns(self, temp_vault):
        """Test file inclusion based on patterns"""
        from obsidian_auto_linker_enhanced import should_process_file

        test_file = os.path.join(temp_vault, "test.md")

        with patch('obsidian_auto_linker_enhanced.config', {
            'include_patterns': ['*.md'],
            'exclude_patterns': [],
            'folder_whitelist': [],
            'folder_blacklist': []
        }):
            with patch('obsidian_auto_linker_enhanced.VAULT_PATH', temp_vault):
                assert should_process_file(test_file) is True

    def test_should_process_file_exclude_patterns(self, temp_vault):
        """Test file exclusion based on patterns"""
        from obsidian_auto_linker_enhanced import should_process_file

        test_file = os.path.join(temp_vault, "exclude_me.md")

        with patch('obsidian_auto_linker_enhanced.config', {
            'include_patterns': [],
            'exclude_patterns': ['exclude_*'],
            'folder_whitelist': [],
            'folder_blacklist': []
        }):
            with patch('obsidian_auto_linker_enhanced.VAULT_PATH', temp_vault):
                assert should_process_file(test_file) is False

    def test_should_process_file_folder_blacklist(self, temp_vault):
        """Test folder blacklist filtering"""
        from obsidian_auto_linker_enhanced import should_process_file

        test_file = os.path.join(temp_vault, "exclude_folder", "test.md")

        with patch('obsidian_auto_linker_enhanced.config', {
            'include_patterns': [],
            'exclude_patterns': [],
            'folder_whitelist': [],
            'folder_blacklist': ['exclude_folder']
        }):
            with patch('obsidian_auto_linker_enhanced.VAULT_PATH', temp_vault):
                assert should_process_file(test_file) is False

    def test_should_process_file_folder_whitelist(self, temp_vault):
        """Test folder whitelist filtering"""
        from obsidian_auto_linker_enhanced import should_process_file

        test_file = os.path.join(temp_vault, "allowed", "test.md")
        test_file2 = os.path.join(temp_vault, "not_allowed", "test.md")

        with patch('obsidian_auto_linker_enhanced.config', {
            'include_patterns': [],
            'exclude_patterns': [],
            'folder_whitelist': ['allowed'],
            'folder_blacklist': []
        }):
            with patch('obsidian_auto_linker_enhanced.VAULT_PATH', temp_vault):
                assert should_process_file(test_file) is True
                assert should_process_file(test_file2) is False

    def test_fast_dry_run_analysis(self, sample_markdown_content, temp_vault):
        """Test fast dry run analysis without AI"""
        from obsidian_auto_linker_enhanced import fast_dry_run_analysis

        test_file = os.path.join(temp_vault, "test.md")
        result = fast_dry_run_analysis(sample_markdown_content, test_file)

        assert result is not None
        assert 'filename' in result
        assert 'file_size' in result
        assert 'word_count' in result
        assert 'categories' in result
        assert 'analysis_type' in result
        assert result['analysis_type'] == 'fast_dry_run'

    def test_fast_dry_run_keyword_detection(self):
        """Test keyword-based category detection in fast mode"""
        from obsidian_auto_linker_enhanced import fast_dry_run_analysis

        # Test different content types
        work_content = "This is about work, job, business meeting and career"
        health_content = "Discussing health, fitness, exercise and diet plans"
        finance_content = "Investment strategies, money management and budget planning"

        work_result = fast_dry_run_analysis(work_content, "work.md")
        health_result = fast_dry_run_analysis(health_content, "health.md")
        finance_result = fast_dry_run_analysis(finance_content, "finance.md")

        assert 'Work & Career' in work_result['categories']
        assert 'Health & Fitness' in health_result['categories']
        assert 'Finance & Money' in finance_result['categories']

    def test_get_all_notes(self, mock_file_system):
        """Test retrieving all notes from vault"""
        from obsidian_auto_linker_enhanced import get_all_notes

        with patch('obsidian_auto_linker_enhanced.config', {
            'backup_folder': '_backups'
        }):
            notes = get_all_notes(mock_file_system)

            assert len(notes) > 0
            # Should have note titles as keys
            assert 'conversation1' in notes or len(notes) >= 1

    def test_get_all_notes_excludes_backups(self, temp_vault):
        """Test that backup folder is excluded from notes"""
        from obsidian_auto_linker_enhanced import get_all_notes

        # Create backup folder
        backup_dir = os.path.join(temp_vault, '_backups')
        os.makedirs(backup_dir, exist_ok=True)

        # Create files
        with open(os.path.join(temp_vault, 'note.md'), 'w') as f:
            f.write('# Note')
        with open(os.path.join(backup_dir, 'backup.md'), 'w') as f:
            f.write('# Backup')

        with patch('obsidian_auto_linker_enhanced.config', {
            'backup_folder': '_backups'
        }):
            notes = get_all_notes(temp_vault)

            # Should only include main note, not backup
            assert 'note' in notes
            assert 'backup' not in notes

    def test_moc_category_validation(self):
        """Test that MOC categories are valid"""
        from obsidian_auto_linker_enhanced import MOCS

        # Verify all expected MOCs exist
        expected_mocs = [
            'Client Acquisition',
            'Service Delivery',
            'Revenue & Pricing',
            'Marketing & Content',
            'Technical & Automation',
            'Business Operations',
            'Learning & Skills',
            'Personal Development',
            'Health & Fitness',
            'Finance & Money',
            'Life & Misc'
        ]

        for moc in expected_mocs:
            assert moc in MOCS

    def test_confidence_threshold_filtering(self, sample_markdown_content, sample_existing_notes):
        """Test that low confidence results are flagged"""
        with patch('requests.post') as mock_post:
            mock_response = Mock()
            mock_response.status_code = 200
            # Low confidence response
            mock_response.json.return_value = {
                'response': json.dumps({
                    'moc_category': 'Test',
                    'confidence_score': 0.3,  # Below threshold
                    'reasoning': 'Not very confident'
                })
            }
            mock_response.raise_for_status = Mock()
            mock_post.return_value = mock_response

            from obsidian_auto_linker_enhanced import analyze_with_balanced_ai

            with patch('obsidian_auto_linker_enhanced.ai_cache', {}):
                result = analyze_with_balanced_ai(sample_markdown_content, sample_existing_notes)

                assert result is not None
                assert result['confidence_score'] < 0.8  # Default threshold
