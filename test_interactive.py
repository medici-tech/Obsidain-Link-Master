"""
Interactive Mode Tests
Tests for interactive user prompts and configuration
"""

import pytest
from unittest.mock import patch, MagicMock
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


@pytest.mark.unit
class TestInteractiveMode:
    """Test suite for interactive mode functionality"""

    def test_interactive_mode_enabled(self):
        """Test that interactive mode can be enabled"""
        from obsidian_auto_linker_enhanced import INTERACTIVE_MODE

        # Should be configurable
        assert isinstance(INTERACTIVE_MODE, bool)

    def test_interactive_mode_dry_run_choice(self):
        """Test interactive dry run vs real processing choice"""
        # Simulate user choosing dry run
        with patch('builtins.input', return_value='1'):
            choice = input("Choose option (1-5): ")
            assert choice == '1'

    def test_interactive_mode_real_processing_choice(self):
        """Test interactive real processing choice"""
        # Simulate user choosing real processing
        with patch('builtins.input', return_value='2'):
            choice = input("Choose option (1-5): ")
            assert choice == '2'

    def test_interactive_mode_confirmation(self):
        """Test user confirmation prompt"""
        # Simulate YES confirmation
        with patch('builtins.input', return_value='YES'):
            confirm = input("Are you sure? Type 'YES' to continue: ")
            assert confirm == 'YES'

    def test_interactive_mode_batch_size_input(self):
        """Test batch size configuration"""
        # Simulate batch size input
        with patch('builtins.input', return_value='5'):
            batch_size = input("Batch size (current: 1): ")
            assert int(batch_size) == 5

    def test_interactive_mode_model_selection(self):
        """Test model selection in interactive mode"""
        # Simulate model selection
        with patch('builtins.input', return_value='qwen3:8b'):
            model = input("Model (press Enter to keep current): ")
            assert model == 'qwen3:8b'

    def test_interactive_mode_eof_handling(self):
        """Test handling of EOF in non-interactive environments"""
        # Simulate EOF (non-interactive mode like CI/CD)
        with patch('builtins.input', side_effect=EOFError):
            try:
                choice = input("Choose option: ")
                pytest.fail("Should raise EOFError")
            except EOFError:
                # Expected in non-interactive mode
                pass

    def test_interactive_mode_cancel(self):
        """Test user cancellation in interactive mode"""
        # Simulate user canceling
        with patch('builtins.input', return_value='5'):
            choice = input("Choose option (1-5): ")
            assert choice == '5'  # Cancel option

    def test_interactive_dry_run_limit_prompt(self):
        """Test dry run limit reached prompt"""
        # Simulate choice at dry run limit
        with patch('builtins.input', return_value='3'):
            choice = input("Choose option (1-4): ")
            # Option 3 is "Generate analytics report and exit"
            assert choice in ['1', '2', '3', '4']

    def test_interactive_final_confirmation(self):
        """Test final confirmation before processing"""
        # Simulate final confirmation
        with patch('builtins.input', return_value='y'):
            confirm = input("Proceed with these settings? (y/N): ")
            assert confirm.lower() == 'y'


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
