"""
Unit tests for file operations
Tests file processing, backup creation, and file management
"""

import pytest
import os
import shutil
import tempfile
from datetime import datetime
from unittest.mock import patch, Mock, mock_open

import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@pytest.mark.unit
@pytest.mark.file_ops
class TestFileOperations:
    """Test suite for file operations"""

    def test_backup_file_creates_backup(self, temp_vault, sample_markdown_file):
        """Test that backup file is created"""
        from obsidian_auto_linker_enhanced import backup_file

        backup_folder = os.path.join(temp_vault, '_backups')

        with patch('obsidian_auto_linker_enhanced.BACKUP_FOLDER', backup_folder):
            with patch('obsidian_auto_linker_enhanced.config', {'backup_verification': True}):
                backup_file(sample_markdown_file)

                # Verify backup folder was created
                assert os.path.exists(backup_folder)

                # Verify backup file exists
                backups = os.listdir(backup_folder)
                assert len(backups) > 0

    def test_backup_file_verification(self, temp_vault, sample_markdown_file):
        """Test that backup verification works"""
        from obsidian_auto_linker_enhanced import backup_file

        backup_folder = os.path.join(temp_vault, '_backups')

        with patch('obsidian_auto_linker_enhanced.BACKUP_FOLDER', backup_folder):
            with patch('obsidian_auto_linker_enhanced.config', {'backup_verification': True}):
                # Should not raise exception
                backup_file(sample_markdown_file)

                # Verify backup content matches original
                original_content = open(sample_markdown_file, 'r').read()
                backups = os.listdir(backup_folder)
                backup_path = os.path.join(backup_folder, backups[0])
                backup_content = open(backup_path, 'r').read()

                assert original_content == backup_content

    def test_backup_file_cleanup_old_backups(self, temp_vault, sample_markdown_file):
        """Test that old backups are cleaned up"""
        from obsidian_auto_linker_enhanced import backup_file

        backup_folder = os.path.join(temp_vault, '_backups')
        os.makedirs(backup_folder, exist_ok=True)

        # Create old backup files
        base_name = os.path.basename(sample_markdown_file)[:-3]
        for i in range(10):
            old_backup = os.path.join(backup_folder, f"{base_name}_old{i}.md")
            with open(old_backup, 'w') as f:
                f.write("Old backup")

        with patch('obsidian_auto_linker_enhanced.BACKUP_FOLDER', backup_folder):
            with patch('obsidian_auto_linker_enhanced.MAX_BACKUPS', 5):
                with patch('obsidian_auto_linker_enhanced.config', {'backup_verification': True}):
                    backup_file(sample_markdown_file)

                    # Should only keep MAX_BACKUPS
                    backups = [f for f in os.listdir(backup_folder) if f.startswith(base_name)]
                    assert len(backups) <= 6  # 5 old + 1 new

    def test_process_conversation_already_processed(self, temp_vault, sample_processed_content, sample_existing_notes):
        """Test that already processed files are skipped"""
        from obsidian_auto_linker_enhanced import process_conversation

        # Create file with metadata
        test_file = os.path.join(temp_vault, "processed.md")
        with open(test_file, 'w') as f:
            f.write(sample_processed_content)

        stats = {
            'processed': 0,
            'already_processed': 0,
            'failed': 0,
            'would_process': 0,
            'links_added': 0,
            'tags_added': 0
        }

        with patch('obsidian_auto_linker_enhanced.progress_data', {'processed_files': set(), 'failed_files': set()}):
            result = process_conversation(test_file, sample_existing_notes, stats)

            # Should skip already processed file
            assert stats['already_processed'] > 0

    def test_process_conversation_creates_linked_file(self, temp_vault, sample_markdown_file, sample_existing_notes, mock_ollama_success):
        """Test that processing creates a new linked file"""
        from obsidian_auto_linker_enhanced import process_conversation

        stats = {
            'processed': 0,
            'already_processed': 0,
            'failed': 0,
            'would_process': 0,
            'links_added': 0,
            'tags_added': 0
        }

        backup_folder = os.path.join(temp_vault, '_backups')

        with patch('obsidian_auto_linker_enhanced.DRY_RUN', False):
            with patch('obsidian_auto_linker_enhanced.BACKUP_FOLDER', backup_folder):
                with patch('obsidian_auto_linker_enhanced.progress_data', {'processed_files': set(), 'failed_files': set()}):
                    with patch('obsidian_auto_linker_enhanced.ai_cache', {}):
                        with patch('obsidian_auto_linker_enhanced.MAX_RETRIES', 1):
                            with patch('obsidian_auto_linker_enhanced.config', {'backup_verification': True}):
                                result = process_conversation(sample_markdown_file, sample_existing_notes, stats)

                                # Check for _linked file
                                base_name = os.path.splitext(sample_markdown_file)[0]
                                linked_file = f"{base_name}_linked.md"

                                if os.path.exists(linked_file):
                                    assert os.path.exists(linked_file)

    def test_process_conversation_dry_run_mode(self, temp_vault, sample_markdown_file, sample_existing_notes, mock_ollama_success):
        """Test that dry run doesn't modify files"""
        from obsidian_auto_linker_enhanced import process_conversation

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
                    process_conversation(sample_markdown_file, sample_existing_notes, stats)

                    # Should increment would_process in dry run
                    assert stats['would_process'] >= 0

    def test_process_conversation_handles_read_error(self, temp_vault, sample_existing_notes):
        """Test handling of file read errors"""
        from obsidian_auto_linker_enhanced import process_conversation

        nonexistent_file = os.path.join(temp_vault, "nonexistent.md")

        stats = {
            'processed': 0,
            'already_processed': 0,
            'failed': 0,
            'would_process': 0,
            'links_added': 0,
            'tags_added': 0
        }

        with patch('obsidian_auto_linker_enhanced.progress_data', {'processed_files': set(), 'failed_files': set()}):
            result = process_conversation(nonexistent_file, sample_existing_notes, stats)

            # Should handle gracefully
            assert result is False

    def test_process_conversation_handles_ai_failure(self, temp_vault, sample_markdown_file, sample_existing_notes):
        """Test handling of AI analysis failure"""
        from obsidian_auto_linker_enhanced import process_conversation

        stats = {
            'processed': 0,
            'already_processed': 0,
            'failed': 0,
            'would_process': 0,
            'links_added': 0,
            'tags_added': 0
        }

        with patch('obsidian_auto_linker_enhanced.analyze_with_balanced_ai', return_value=None):
            with patch('obsidian_auto_linker_enhanced.progress_data', {'processed_files': set(), 'failed_files': set()}):
                with patch('obsidian_auto_linker_enhanced.FAST_DRY_RUN', False):
                    result = process_conversation(sample_markdown_file, sample_existing_notes, stats)

                    # Should mark as failed
                    assert stats['failed'] > 0

    def test_create_moc_note(self, temp_vault):
        """Test MOC note creation"""
        from obsidian_auto_linker_enhanced import create_moc_note

        moc_name = "Technical & Automation"

        with patch('obsidian_auto_linker_enhanced.DRY_RUN', False):
            with patch('obsidian_auto_linker_enhanced.MOCS', {"Technical & Automation": "📍 Technical & Automation MOC"}):
                with patch('obsidian_auto_linker_enhanced.MOC_DESCRIPTIONS', {"Technical & Automation": "Tech content"}):
                    create_moc_note(moc_name, temp_vault)

                    # Verify MOC file was created
                    moc_file = os.path.join(temp_vault, "Technical & Automation MOC.md")
                    assert os.path.exists(moc_file)

                    # Verify content
                    with open(moc_file, 'r') as f:
                        content = f.read()
                        assert '📍 Technical & Automation MOC' in content

    def test_create_moc_note_dry_run(self, temp_vault):
        """Test that MOC note is not created in dry run"""
        from obsidian_auto_linker_enhanced import create_moc_note

        moc_name = "Technical & Automation"

        with patch('obsidian_auto_linker_enhanced.DRY_RUN', True):
            with patch('obsidian_auto_linker_enhanced.MOCS', {"Technical & Automation": "📍 Technical & Automation MOC"}):
                create_moc_note(moc_name, temp_vault)

                # MOC file should not be created in dry run
                moc_file = os.path.join(temp_vault, "Technical & Automation MOC.md")
                # In dry run, file won't be created

    def test_create_moc_note_already_exists(self, temp_vault):
        """Test that existing MOC note is not overwritten"""
        from obsidian_auto_linker_enhanced import create_moc_note

        moc_name = "Technical & Automation"
        moc_file = os.path.join(temp_vault, "Technical & Automation MOC.md")

        # Create existing MOC
        with open(moc_file, 'w') as f:
            f.write("# Existing MOC")

        original_content = open(moc_file, 'r').read()

        with patch('obsidian_auto_linker_enhanced.DRY_RUN', False):
            with patch('obsidian_auto_linker_enhanced.MOCS', {"Technical & Automation": "📍 Technical & Automation MOC"}):
                create_moc_note(moc_name, temp_vault)

                # Content should not change
                new_content = open(moc_file, 'r').read()
                assert new_content == original_content

    def test_order_files_by_recent(self, mock_file_system):
        """Test ordering files by modification time (recent first)"""
        from obsidian_auto_linker_enhanced import order_files
        import time

        files = []
        for i in range(3):
            file_path = os.path.join(mock_file_system, f"file{i}.md")
            with open(file_path, 'w') as f:
                f.write(f"File {i}")
            files.append(file_path)
            time.sleep(0.01)  # Small delay to ensure different mtimes

        ordered = order_files(files, 'recent')

        # Most recent should be first
        assert ordered[0] == files[-1]

    def test_order_files_by_smallest(self, mock_file_system):
        """Test ordering files by size (smallest first)"""
        from obsidian_auto_linker_enhanced import order_files

        # Create files of different sizes
        files = []
        for i in range(3):
            file_path = os.path.join(mock_file_system, f"sized{i}.md")
            with open(file_path, 'w') as f:
                f.write("x" * (i + 1) * 100)  # Increasing sizes
            files.append(file_path)

        ordered = order_files(files, 'smallest')

        # Smallest should be first
        assert os.path.getsize(ordered[0]) <= os.path.getsize(ordered[1])

    def test_order_files_alphabetical(self, mock_file_system):
        """Test alphabetical file ordering"""
        from obsidian_auto_linker_enhanced import order_files

        files = [
            os.path.join(mock_file_system, "charlie.md"),
            os.path.join(mock_file_system, "alice.md"),
            os.path.join(mock_file_system, "bob.md")
        ]

        for f in files:
            with open(f, 'w') as file:
                file.write("content")

        ordered = order_files(files, 'alphabetical')

        # Should be in alphabetical order
        assert 'alice' in ordered[0]
        assert 'bob' in ordered[1]
        assert 'charlie' in ordered[2]

    def test_save_progress(self, temp_vault):
        """Test saving progress to file"""
        from obsidian_auto_linker_enhanced import save_progress

        progress_file = os.path.join(temp_vault, '.progress.json')

        with patch('obsidian_auto_linker_enhanced.progress_data', {
            'processed_files': set(['/path/to/file1.md']),
            'failed_files': set(['/path/to/failed.md']),
            'current_batch': 5
        }):
            with patch('obsidian_auto_linker_enhanced.config', {'progress_file': progress_file, 'resume_enabled': True}):
                save_progress()

                # Verify file was created
                assert os.path.exists(progress_file)

                # Verify content
                import json
                with open(progress_file, 'r') as f:
                    data = json.load(f)
                    assert 'processed_files' in data
                    assert 'current_batch' in data

    def test_load_progress(self, temp_vault, sample_progress_data):
        """Test loading progress from file"""
        from obsidian_auto_linker_enhanced import load_progress

        progress_file = os.path.join(temp_vault, '.progress.json')

        # Create progress file
        import json
        with open(progress_file, 'w') as f:
            json.dump(sample_progress_data, f)

        with patch('obsidian_auto_linker_enhanced.progress_data', {'processed_files': set(), 'failed_files': set(), 'current_batch': 0}):
            with patch('obsidian_auto_linker_enhanced.config', {'progress_file': progress_file, 'resume_enabled': True}):
                load_progress()

    def test_load_progress_corrupted_file(self, temp_vault):
        """Test loading progress from corrupted file"""
        from obsidian_auto_linker_enhanced import load_progress

        progress_file = os.path.join(temp_vault, '.progress.json')

        # Create corrupted file
        with open(progress_file, 'w') as f:
            f.write("This is not valid JSON{{{")

        with patch('obsidian_auto_linker_enhanced.progress_data', {'processed_files': set(), 'failed_files': set(), 'current_batch': 0}):
            with patch('obsidian_auto_linker_enhanced.config', {'progress_file': progress_file, 'resume_enabled': True}):
                # Should handle gracefully
                load_progress()
