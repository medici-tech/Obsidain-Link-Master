"""
Tests for config_schema.py module with Pydantic validation
"""

import pytest
import os
import yaml
from pydantic import ValidationError
from config_schema import (
    OllamaConfig,
    ProcessingConfig,
    FilterConfig,
    ObsidianConfig,
    load_and_validate_config,
)


class TestOllamaConfig:
    """Tests for OllamaConfig schema"""

    def test_default_ollama_config(self):
        """Test creating OllamaConfig with defaults"""
        config = OllamaConfig()
        assert config.base_url == "http://localhost:11434"
        assert config.model == "Qwen3-Embedding-8B:Q8_0"
        assert config.timeout == 15
        assert config.max_retries == 1

    def test_custom_ollama_config(self):
        """Test creating OllamaConfig with custom values"""
        config = OllamaConfig(
            base_url="https://custom:11434",
            model="custom-model",
            timeout=30,
            max_retries=3
        )
        assert config.base_url == "https://custom:11434"
        assert config.model == "custom-model"
        assert config.timeout == 30
        assert config.max_retries == 3

    def test_invalid_ollama_url(self):
        """Test that invalid URLs are rejected"""
        with pytest.raises(ValidationError) as exc_info:
            OllamaConfig(base_url="invalid-url")

        assert "must start with http:// or https://" in str(exc_info.value)

    def test_ollama_timeout_validation(self):
        """Test timeout range validation"""
        # Too low
        with pytest.raises(ValidationError):
            OllamaConfig(timeout=2)

        # Too high
        with pytest.raises(ValidationError):
            OllamaConfig(timeout=500)

        # Valid range
        config = OllamaConfig(timeout=30)
        assert config.timeout == 30


class TestProcessingConfig:
    """Tests for ProcessingConfig schema"""

    def test_default_processing_config(self):
        """Test creating ProcessingConfig with minimal required fields"""
        config = ProcessingConfig(vault_path="/tmp/vault")
        assert config.vault_path == "/tmp/vault"
        assert config.dry_run is True  # Safe default
        assert config.batch_size == 1

    def test_empty_vault_path_rejected(self):
        """Test that empty vault path is rejected"""
        with pytest.raises(ValidationError) as exc_info:
            ProcessingConfig(vault_path="")

        assert "cannot be empty" in str(exc_info.value)

    def test_invalid_file_ordering_rejected(self):
        """Test that invalid file_ordering is rejected"""
        with pytest.raises(ValidationError) as exc_info:
            ProcessingConfig(vault_path="/tmp", file_ordering="invalid")

        assert "file_ordering must be one of" in str(exc_info.value)

    def test_valid_file_orderings(self):
        """Test all valid file ordering options"""
        valid_orderings = ['recent', 'size', 'random', 'alphabetical']

        for ordering in valid_orderings:
            config = ProcessingConfig(vault_path="/tmp", file_ordering=ordering)
            assert config.file_ordering == ordering

    def test_batch_size_validation(self):
        """Test batch size validation"""
        # Too low
        with pytest.raises(ValidationError):
            ProcessingConfig(vault_path="/tmp", batch_size=0)

        # Too high
        with pytest.raises(ValidationError):
            ProcessingConfig(vault_path="/tmp", batch_size=200)

        # Valid
        config = ProcessingConfig(vault_path="/tmp", batch_size=50)
        assert config.batch_size == 50


class TestFilterConfig:
    """Tests for FilterConfig schema"""

    def test_default_filter_config(self):
        """Test FilterConfig with defaults"""
        config = FilterConfig()
        assert "*.md" in config.include_patterns
        assert "*.tmp" in config.exclude_patterns
        assert "_backups" in config.folder_blacklist

    def test_custom_filter_config(self):
        """Test FilterConfig with custom values"""
        config = FilterConfig(
            include_patterns=["*.txt", "*.md"],
            exclude_patterns=["*.bak"],
            folder_whitelist=["Notes", "Documents"]
        )
        assert config.include_patterns == ["*.txt", "*.md"]
        assert config.exclude_patterns == ["*.bak"]
        assert config.folder_whitelist == ["Notes", "Documents"]


class TestObsidianConfig:
    """Tests for complete ObsidianConfig schema"""

    def test_minimal_valid_config(self):
        """Test creating config with minimal required fields"""
        config = ObsidianConfig(vault_path="/tmp/vault")
        assert config.vault_path == "/tmp/vault"
        assert config.dry_run is True
        assert config.ollama_base_url == "http://localhost:11434"

    def test_complete_config(self):
        """Test creating config with all fields"""
        config = ObsidianConfig(
            vault_path="/tmp/vault",
            dry_run=False,
            fast_dry_run=False,
            batch_size=10,
            file_ordering="size",
            ollama_base_url="http://localhost:11434",
            ollama_model="custom:7b",
            cache_enabled=True,
            resume_enabled=True,
        )
        assert config.vault_path == "/tmp/vault"
        assert config.dry_run is False
        assert config.batch_size == 10
        assert config.file_ordering == "size"

    def test_empty_vault_path_rejected(self):
        """Test that empty vault_path is rejected"""
        with pytest.raises(ValidationError):
            ObsidianConfig(vault_path="")

    def test_fast_dry_run_requires_dry_run(self):
        """Test that fast_dry_run requires dry_run to be True"""
        with pytest.raises(ValidationError) as exc_info:
            ObsidianConfig(
                vault_path="/tmp",
                fast_dry_run=True,
                dry_run=False
            )

        assert "fast_dry_run requires dry_run" in str(exc_info.value)

    def test_fast_dry_run_with_dry_run_valid(self):
        """Test that fast_dry_run works when dry_run is True"""
        config = ObsidianConfig(
            vault_path="/tmp",
            fast_dry_run=True,
            dry_run=True
        )
        assert config.fast_dry_run is True
        assert config.dry_run is True

    def test_custom_mocs(self):
        """Test custom MOCs configuration"""
        config = ObsidianConfig(
            vault_path="/tmp",
            custom_mocs={"My Category": "📍 My Category MOC"}
        )
        assert "My Category" in config.custom_mocs

    def test_to_dict(self):
        """Test converting config to dictionary"""
        config = ObsidianConfig(vault_path="/tmp/vault", batch_size=5)
        data = config.to_dict()

        assert isinstance(data, dict)
        assert data['vault_path'] == "/tmp/vault"
        assert data['batch_size'] == 5

    def test_from_dict(self):
        """Test creating config from dictionary"""
        data = {
            'vault_path': '/tmp/vault',
            'batch_size': 10,
            'dry_run': False
        }
        config = ObsidianConfig.from_dict(data)

        assert config.vault_path == '/tmp/vault'
        assert config.batch_size == 10
        assert config.dry_run is False


class TestConfigFileOperations:
    """Tests for loading/saving config from/to YAML files"""

    def test_from_yaml_file(self, temp_dir):
        """Test loading config from YAML file"""
        config_path = os.path.join(temp_dir, 'config.yaml')
        config_data = {
            'vault_path': '/tmp/vault',
            'dry_run': True,
            'batch_size': 5,
        }

        with open(config_path, 'w') as f:
            yaml.dump(config_data, f)

        config = ObsidianConfig.from_yaml_file(config_path)

        assert config.vault_path == '/tmp/vault'
        assert config.dry_run is True
        assert config.batch_size == 5

    def test_from_yaml_file_nonexistent(self, temp_dir):
        """Test loading from nonexistent file raises validation error for empty vault_path"""
        config_path = os.path.join(temp_dir, 'nonexistent.yaml')

        # Should raise ValidationError because vault_path is required
        with pytest.raises(ValidationError) as exc_info:
            ObsidianConfig.from_yaml_file(config_path)

        assert "vault_path" in str(exc_info.value)

    def test_save_to_yaml_file(self, temp_dir):
        """Test saving config to YAML file"""
        config_path = os.path.join(temp_dir, 'output.yaml')
        config = ObsidianConfig(
            vault_path='/tmp/vault',
            batch_size=10,
            dry_run=False
        )

        config.save_to_yaml_file(config_path)

        # Verify file was created
        assert os.path.exists(config_path)

        # Load and verify
        with open(config_path, 'r') as f:
            loaded_data = yaml.safe_load(f)

        assert loaded_data['vault_path'] == '/tmp/vault'
        assert loaded_data['batch_size'] == 10
        assert loaded_data['dry_run'] is False

    def test_load_and_validate_config(self, temp_dir):
        """Test convenience function for loading config"""
        config_path = os.path.join(temp_dir, 'test_config.yaml')
        config_data = {
            'vault_path': '/tmp/test_vault',
            'batch_size': 3,
        }

        with open(config_path, 'w') as f:
            yaml.dump(config_data, f)

        config = load_and_validate_config(config_path)

        assert isinstance(config, ObsidianConfig)
        assert config.vault_path == '/tmp/test_vault'
        assert config.batch_size == 3


class TestConfigValidation:
    """Tests for advanced validation scenarios"""

    def test_invalid_yaml_raises_error(self, temp_dir):
        """Test that invalid YAML raises appropriate error"""
        config_path = os.path.join(temp_dir, 'invalid.yaml')
        with open(config_path, 'w') as f:
            f.write("{invalid yaml content:")

        with pytest.raises(ValueError) as exc_info:
            ObsidianConfig.from_yaml_file(config_path)

        assert "Invalid YAML" in str(exc_info.value)

    def test_user_home_expansion(self):
        """Test that ~ is expanded in vault_path"""
        config = ObsidianConfig(vault_path="~/Documents/vault")

        # Should expand ~ to actual home directory
        assert config.vault_path.startswith(os.path.expanduser("~"))
        assert "~" not in config.vault_path

    def test_parallel_workers_validation(self):
        """Test parallel workers range validation"""
        # Too low
        with pytest.raises(ValidationError):
            ObsidianConfig(vault_path="/tmp", parallel_workers=0)

        # Too high
        with pytest.raises(ValidationError):
            ObsidianConfig(vault_path="/tmp", parallel_workers=20)

        # Valid
        config = ObsidianConfig(vault_path="/tmp", parallel_workers=4)
        assert config.parallel_workers == 4
