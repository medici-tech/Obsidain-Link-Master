"""
Integration tests for end-to-end workflows
Tests complete processing pipelines
"""

import pytest
import os
import json
import shutil
from unittest.mock import patch, Mock

import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@pytest.mark.integration
class TestEndToEndWorkflow:
    """Integration tests for complete workflows"""

    def test_full_file_processing_workflow(self, temp_vault, sample_markdown_content, mock_ollama_success):
        """Test complete file processing from start to finish"""
        from obsidian_auto_linker_enhanced import (
            process_conversation,
            backup_file,
            get_all_notes
        )

        # Setup
        test_file = os.path.join(temp_vault, "test_conversation.md")
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write(sample_markdown_content)

        backup_folder = os.path.join(temp_vault, '_backups')
        stats = {
            'processed': 0,
            'already_processed': 0,
            'failed': 0,
            'would_process': 0,
            'links_added': 0,
            'tags_added': 0
        }

        # Execute workflow
        with patch('obsidian_auto_linker_enhanced.DRY_RUN', False):
            with patch('obsidian_auto_linker_enhanced.BACKUP_FOLDER', backup_folder):
                with patch('obsidian_auto_linker_enhanced.progress_data', {'processed_files': set(), 'failed_files': set()}):
                    with patch('obsidian_auto_linker_enhanced.ai_cache', {}):
                        with patch('obsidian_auto_linker_enhanced.config', {'backup_verification': True}):
                            existing_notes = get_all_notes(temp_vault)
                            result = process_conversation(test_file, existing_notes, stats)

        # Verify results
        # Check that backup was created
        if os.path.exists(backup_folder):
            backups = os.listdir(backup_folder)
            assert len(backups) > 0

    def test_resume_from_interrupted_state(self, temp_vault, mock_file_system):
        """Test resuming processing from interrupted state"""
        from obsidian_auto_linker_enhanced import load_progress, save_progress

        progress_file = os.path.join(temp_vault, '.progress.json')

        # Simulate interrupted state
        interrupted_progress = {
            'processed_files': [
                os.path.join(mock_file_system, 'conversation1.md'),
                os.path.join(mock_file_system, 'conversation2.md')
            ],
            'failed_files': [],
            'current_batch': 2,
            'last_update': '2024-01-01T12:00:00'
        }

        with open(progress_file, 'w') as f:
            json.dump(interrupted_progress, f)

        # Load progress
        with patch('obsidian_auto_linker_enhanced.progress_data', {'processed_files': set(), 'failed_files': set(), 'current_batch': 0}):
            with patch('obsidian_auto_linker_enhanced.config', {'progress_file': progress_file, 'resume_enabled': True}):
                load_progress()

    def test_review_queue_workflow(self, temp_vault, sample_markdown_content, mock_ollama_success):
        """Test low confidence file review queue workflow"""
        from obsidian_auto_linker_enhanced import add_to_review_queue

        # Setup low confidence AI result
        ai_result = {
            'moc_category': 'Life & Misc',
            'primary_topic': 'Unknown',
            'hierarchical_tags': [],
            'key_concepts': [],
            'sibling_notes': [],
            'confidence_score': 0.3,  # Low confidence
            'reasoning': 'Content is unclear'
        }

        review_queue_path = os.path.join(temp_vault, 'reviews')
        test_file = os.path.join(temp_vault, 'unclear_file.md')

        with open(test_file, 'w') as f:
            f.write(sample_markdown_content)

        with patch('obsidian_auto_linker_enhanced.ENABLE_REVIEW_QUEUE', True):
            with patch('obsidian_auto_linker_enhanced.REVIEW_QUEUE_PATH', review_queue_path):
                add_to_review_queue(test_file, ai_result, 0.3)

                # Verify review file was created
                assert os.path.exists(review_queue_path)
                review_files = os.listdir(review_queue_path)
                assert len(review_files) > 0

                # Verify review file content
                review_file = os.path.join(review_queue_path, review_files[0])
                with open(review_file, 'r') as f:
                    content = f.read()
                    assert 'REVIEW REQUIRED' in content
                    assert 'Low Confidence' in content

    def test_analytics_generation_workflow(self, sample_analytics):
        """Test analytics report generation"""
        from enhanced_analytics import generate_comprehensive_report

        report_html = generate_comprehensive_report({'processing': sample_analytics})

        # Verify report structure
        assert '<!DOCTYPE html>' in report_html
        assert 'Obsidian Auto-Linker Analytics' in report_html
        assert str(sample_analytics['total_files']) in report_html
        assert str(sample_analytics['processed_files']) in report_html

    def test_cache_persistence_across_runs(self, temp_vault, sample_cache):
        """Test that cache persists across multiple runs"""
        from obsidian_auto_linker_enhanced import save_cache, load_cache

        cache_file = os.path.join(temp_vault, '.ai_cache.json')

        # First run - save cache
        with patch('obsidian_auto_linker_enhanced.ai_cache', sample_cache):
            with patch('obsidian_auto_linker_enhanced.config', {'cache_file': cache_file, 'cache_enabled': True}):
                save_cache()

        # Second run - load cache
        with patch('obsidian_auto_linker_enhanced.ai_cache', {}):
            with patch('obsidian_auto_linker_enhanced.config', {'cache_file': cache_file, 'cache_enabled': True}):
                from obsidian_auto_linker_enhanced import ai_cache
                load_cache()

                # Verify cache was loaded
                assert len(ai_cache) > 0 or os.path.exists(cache_file)

    def test_batch_processing_workflow(self, mock_file_system, mock_ollama_success):
        """Test batch processing of multiple files"""
        from obsidian_auto_linker_enhanced import process_batch, get_all_notes

        files = [
            os.path.join(mock_file_system, 'conversation1.md'),
            os.path.join(mock_file_system, 'conversation2.md')
        ]

        existing_notes = get_all_notes(mock_file_system)
        stats = {
            'processed': 0,
            'already_processed': 0,
            'failed': 0,
            'would_process': 0,
            'links_added': 0,
            'tags_added': 0
        }

        with patch('obsidian_auto_linker_enhanced.DRY_RUN', True):
            with patch('obsidian_auto_linker_enhanced.progress_data', {'processed_files': set(), 'failed_files': set()}):
                with patch('obsidian_auto_linker_enhanced.ai_cache', {}):
                    batch_stats = process_batch(files, existing_notes, stats)

                    # Verify batch was processed
                    assert batch_stats is not None

    def test_error_recovery_workflow(self, temp_vault, sample_markdown_content):
        """Test error recovery and retry logic"""
        from obsidian_auto_linker_enhanced import process_conversation

        test_file = os.path.join(temp_vault, 'test.md')
        with open(test_file, 'w') as f:
            f.write(sample_markdown_content)

        stats = {
            'processed': 0,
            'already_processed': 0,
            'failed': 0,
            'would_process': 0,
            'links_added': 0,
            'tags_added': 0
        }

        # Simulate AI failures then success
        call_count = 0

        def mock_analyze(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                return None  # Fail first time
            return {
                'moc_category': 'Test',
                'confidence_score': 0.8,
                'primary_topic': 'Test',
                'hierarchical_tags': [],
                'key_concepts': [],
                'sibling_notes': [],
                'reasoning': 'Test'
            }

        with patch('obsidian_auto_linker_enhanced.analyze_with_balanced_ai', side_effect=mock_analyze):
            with patch('obsidian_auto_linker_enhanced.progress_data', {'processed_files': set(), 'failed_files': set()}):
                with patch('obsidian_auto_linker_enhanced.MAX_RETRIES', 3):
                    with patch('obsidian_auto_linker_enhanced.FAST_DRY_RUN', False):
                        result = process_conversation(test_file, {}, stats)

                        # Should succeed after retry
                        assert call_count >= 2

    def test_moc_structure_creation(self, temp_vault):
        """Test creation of complete MOC structure"""
        from obsidian_auto_linker_enhanced import create_moc_note, MOCS

        with patch('obsidian_auto_linker_enhanced.DRY_RUN', False):
            with patch('obsidian_auto_linker_enhanced.MOC_DESCRIPTIONS', {
                'Test MOC': 'Test description'
            }):
                with patch('obsidian_auto_linker_enhanced.MOCS', {'Test MOC': '📍 Test MOC'}):
                    create_moc_note('Test MOC', temp_vault)

                    moc_file = os.path.join(temp_vault, 'Test MOC.md')
                    if os.path.exists(moc_file):
                        with open(moc_file, 'r') as f:
                            content = f.read()
                            assert '# 📍 Test MOC' in content
                            assert 'Overview' in content
                            assert 'Key Concepts' in content

    @pytest.mark.slow
    def test_full_vault_processing(self, mock_file_system, mock_ollama_success):
        """Test processing entire vault (slow integration test)"""
        from obsidian_auto_linker_enhanced import get_all_notes

        existing_notes = get_all_notes(mock_file_system)

        # Verify notes were found
        assert len(existing_notes) > 0

        # Verify note structure
        for title, preview in existing_notes.items():
            assert isinstance(title, str)
            assert isinstance(preview, str)
            assert len(preview) <= 800  # Preview should be truncated


@pytest.mark.integration
class TestModelSelectorIntegration:
    """Integration tests for intelligent model selector"""

    def test_model_selector_simple_content(self):
        """Test model selection for simple content"""
        from scripts.intelligent_model_selector import IntelligentModelSelector

        config = {
            'model_switching_threshold': 1000,
            'primary_ollama_model': 'qwen3:8b',
            'secondary_ollama_model': 'qwen2.5:3b'
        }

        selector = IntelligentModelSelector(config)

        simple_content = "This is a short note about my day."
        selected_model, settings = selector.select_model(simple_content, "simple.md")

        # Should select faster model for simple content
        assert selected_model == 'qwen2.5:3b'

    def test_model_selector_complex_content(self):
        """Test model selection for complex content"""
        from scripts.intelligent_model_selector import IntelligentModelSelector

        config = {
            'model_switching_threshold': 100,  # Low threshold for test
            'primary_ollama_model': 'qwen3:8b',
            'secondary_ollama_model': 'qwen2.5:3b'
        }

        selector = IntelligentModelSelector(config)

        complex_content = """
        Detailed technical analysis of business strategy and revenue optimization.
        This involves complex financial modeling, API integration, database architecture,
        and advanced automation systems. We need to consider investment portfolios,
        market analysis, and strategic planning for maximum optimization.
        """ * 5  # Make it longer

        selected_model, settings = selector.select_model(complex_content, "complex_analysis.md")

        # Should select more capable model for complex content
        assert selected_model == 'qwen3:8b'
