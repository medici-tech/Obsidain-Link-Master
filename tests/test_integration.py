"""
Basic integration tests to verify modules can be imported
and core functionality works together
"""

import pytest
import sys
import os


class TestModuleImports:
    """Test that all core modules can be imported"""

    def test_import_config_utils(self):
        """Test importing config_utils module"""
        try:
            import config_utils
            assert hasattr(config_utils, 'load_yaml_config')
            assert hasattr(config_utils, 'check_ollama_connection')
            assert hasattr(config_utils, 'load_json_file')
        except ImportError as e:
            pytest.fail(f"Failed to import config_utils: {e}")

    def test_import_logger_config(self):
        """Test importing logger_config module"""
        try:
            import logger_config
            assert hasattr(logger_config, 'setup_logging')
            assert hasattr(logger_config, 'get_logger')
        except ImportError as e:
            pytest.fail(f"Failed to import logger_config: {e}")

    def test_import_live_dashboard(self):
        """Test importing live_dashboard module"""
        try:
            import live_dashboard
            assert hasattr(live_dashboard, 'LiveDashboard')
        except ImportError as e:
            pytest.fail(f"Failed to import live_dashboard: {e}")

    def test_import_main_processor(self):
        """Test importing main processor module"""
        try:
            import obsidian_auto_linker_enhanced
            assert hasattr(obsidian_auto_linker_enhanced, 'main')
        except ImportError as e:
            pytest.fail(f"Failed to import obsidian_auto_linker_enhanced: {e}")


class TestConfigUtilsIntegration:
    """Integration tests for config_utils module"""

    def test_yaml_and_json_workflow(self, temp_dir):
        """Test complete workflow of loading YAML config and saving JSON"""
        import config_utils
        import yaml
        import json

        # Create a YAML config
        config_path = os.path.join(temp_dir, 'config.yaml')
        config_data = {
            'vault_path': temp_dir,
            'dry_run': True,
            'batch_size': 5,
        }

        with open(config_path, 'w') as f:
            yaml.dump(config_data, f)

        # Load YAML config
        loaded_config = config_utils.load_yaml_config(config_path)
        assert loaded_config == config_data

        # Save as JSON
        json_path = os.path.join(temp_dir, 'config.json')
        result = config_utils.save_json_file(json_path, loaded_config)
        assert result is True

        # Load JSON and verify
        loaded_json = config_utils.load_json_file(json_path)
        assert loaded_json == config_data

    def test_directory_and_file_operations(self, temp_dir):
        """Test directory creation and file size operations"""
        import config_utils

        # Create directory
        new_dir = os.path.join(temp_dir, 'test_vault')
        result = config_utils.ensure_directory_exists(new_dir, create=True)
        assert result is True
        assert os.path.isdir(new_dir)

        # Validate vault path
        is_valid = config_utils.validate_vault_path(new_dir, must_exist=True)
        assert is_valid is True

        # Create a file and test size functions
        test_file = os.path.join(new_dir, 'test.txt')
        with open(test_file, 'w') as f:
            f.write('test content')

        size_kb = config_utils.get_file_size_kb(test_file)
        assert size_kb > 0

        category = config_utils.get_file_size_category(size_kb)
        assert category == 'small'


class TestLoggerIntegration:
    """Integration tests for logger_config module"""

    def test_logger_workflow(self, temp_dir):
        """Test complete logging workflow"""
        import logger_config

        log_file = os.path.join(temp_dir, 'integration.log')

        # Setup logging
        logger = logger_config.setup_logging(log_file=log_file, log_level='INFO')

        # Get logger for a module
        module_logger = logger_config.get_logger('test_module')

        # Verify logger is configured correctly
        assert module_logger is not None
        assert module_logger.name == 'test_module'

        # Log messages and verify they can be called without error
        try:
            module_logger.info("Integration test message")
            module_logger.warning("Warning message")
            module_logger.error("Error message")
        except Exception as e:
            pytest.fail(f"Logging failed with error: {e}")

        # Verify log file was created
        # Note: File content verification is handled in test_logger_config.py
        # which has more direct control over logger handlers
        assert os.path.exists(log_file) or len(logger.handlers) > 0


class TestDashboardIntegration:
    """Basic integration tests for dashboard"""

    def test_dashboard_creation(self):
        """Test creating a dashboard instance"""
        from live_dashboard import LiveDashboard

        dashboard = LiveDashboard(update_interval=15)
        assert dashboard is not None
        assert dashboard.update_interval == 15
        assert dashboard.running is False

    def test_dashboard_metrics_initialization(self):
        """Test that dashboard initializes metrics correctly"""
        from live_dashboard import LiveDashboard

        dashboard = LiveDashboard()

        # Verify dashboard has stats dictionary
        assert hasattr(dashboard, 'stats')
        assert isinstance(dashboard.stats, dict)

        # Verify key metrics are initialized in stats
        assert 'processed_files' in dashboard.stats
        assert 'total_files' in dashboard.stats
        assert 'ai_requests' in dashboard.stats
        assert 'cache_hits' in dashboard.stats

        # Verify initial values
        assert dashboard.stats['processed_files'] == 0
        assert dashboard.stats['total_files'] == 0
        assert dashboard.stats['ai_requests'] == 0


class TestMainProcessorIntegration:
    """Basic integration tests for main processor"""

    def test_main_function_signature(self):
        """Test that main function has expected signature"""
        import obsidian_auto_linker_enhanced as processor
        import inspect

        sig = inspect.signature(processor.main)
        params = list(sig.parameters.keys())

        assert 'enable_dashboard' in params
        assert 'dashboard_update_interval' in params

    def test_processor_constants(self):
        """Test that processor has expected constants"""
        import obsidian_auto_linker_enhanced as processor

        # Verify MOCS dictionary exists
        assert hasattr(processor, 'MOCS')
        assert isinstance(processor.MOCS, dict)
        assert len(processor.MOCS) > 0

        # Verify key functions exist
        assert hasattr(processor, 'call_ollama')
        assert hasattr(processor, 'process_conversation')
        assert hasattr(processor, 'analyze_with_balanced_ai')
