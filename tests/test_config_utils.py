"""
Tests for config_utils.py module
"""

import pytest
import os
import yaml
import json
from config_utils import (
    load_yaml_config,
    check_ollama_connection,
    load_json_file,
    save_json_file,
    ensure_directory_exists,
    get_file_size_kb,
    get_file_size_category,
    validate_vault_path,
    get_config_value,
)


class TestLoadYamlConfig:
    """Tests for load_yaml_config function"""

    def test_load_valid_config(self, sample_config_yaml):
        """Test loading a valid YAML config"""
        config = load_yaml_config(sample_config_yaml)
        assert isinstance(config, dict)
        assert 'vault_path' in config
        assert config['vault_path'] == '/path/to/vault'

    def test_load_nonexistent_file(self, temp_dir):
        """Test loading nonexistent file returns default"""
        config_path = os.path.join(temp_dir, 'nonexistent.yaml')
        config = load_yaml_config(config_path, default={'key': 'value'})
        assert config == {'key': 'value'}

    def test_load_empty_file(self, temp_dir):
        """Test loading empty YAML file"""
        config_path = os.path.join(temp_dir, 'empty.yaml')
        with open(config_path, 'w') as f:
            f.write('')
        config = load_yaml_config(config_path, default={'default': True})
        assert config == {'default': True}


class TestLoadJsonFile:
    """Tests for load_json_file function"""

    def test_load_valid_json(self, sample_json_file):
        """Test loading a valid JSON file"""
        data = load_json_file(sample_json_file)
        assert isinstance(data, dict)
        assert data['test_key'] == 'test_value'
        assert data['number'] == 42

    def test_load_nonexistent_json(self, temp_dir):
        """Test loading nonexistent JSON file"""
        json_path = os.path.join(temp_dir, 'nonexistent.json')
        data = load_json_file(json_path, default=[])
        assert data == []

    def test_load_invalid_json(self, temp_dir):
        """Test loading invalid JSON file"""
        json_path = os.path.join(temp_dir, 'invalid.json')
        with open(json_path, 'w') as f:
            f.write('{invalid json}')
        data = load_json_file(json_path, default={'error': True})
        assert data == {'error': True}


class TestSaveJsonFile:
    """Tests for save_json_file function"""

    def test_save_valid_json(self, temp_dir):
        """Test saving valid JSON data"""
        json_path = os.path.join(temp_dir, 'output.json')
        data = {'key': 'value', 'number': 123}
        result = save_json_file(json_path, data)
        assert result is True

        # Verify file was created and contains correct data
        with open(json_path, 'r') as f:
            loaded_data = json.load(f)
        assert loaded_data == data

    def test_save_with_backup(self, temp_dir):
        """Test saving with backup creation"""
        json_path = os.path.join(temp_dir, 'backup_test.json')

        # Create initial file
        initial_data = {'initial': True}
        save_json_file(json_path, initial_data)

        # Update with backup
        new_data = {'updated': True}
        result = save_json_file(json_path, new_data, create_backup=True)
        assert result is True

        # Verify backup was created
        backup_path = f"{json_path}.backup"
        assert os.path.exists(backup_path)


class TestEnsureDirectoryExists:
    """Tests for ensure_directory_exists function"""

    def test_create_directory(self, temp_dir):
        """Test creating a new directory"""
        new_dir = os.path.join(temp_dir, 'new_directory')
        result = ensure_directory_exists(new_dir, create=True)
        assert result is True
        assert os.path.isdir(new_dir)

    def test_existing_directory(self, temp_dir):
        """Test with existing directory"""
        result = ensure_directory_exists(temp_dir, create=False)
        assert result is True

    def test_no_create_nonexistent(self, temp_dir):
        """Test not creating nonexistent directory"""
        new_dir = os.path.join(temp_dir, 'nonexistent')
        result = ensure_directory_exists(new_dir, create=False)
        assert result is False


class TestGetFileSize:
    """Tests for file size functions"""

    def test_get_file_size_kb(self, sample_json_file):
        """Test getting file size in KB"""
        size_kb = get_file_size_kb(sample_json_file)
        assert size_kb > 0
        assert isinstance(size_kb, float)

    def test_get_file_size_nonexistent(self, temp_dir):
        """Test getting size of nonexistent file"""
        size_kb = get_file_size_kb(os.path.join(temp_dir, 'nonexistent.txt'))
        assert size_kb == 0.0

    def test_get_file_size_category_small(self):
        """Test file size category for small files"""
        assert get_file_size_category(5) == 'small'

    def test_get_file_size_category_medium(self):
        """Test file size category for medium files"""
        assert get_file_size_category(50) == 'medium'

    def test_get_file_size_category_large(self):
        """Test file size category for large files"""
        assert get_file_size_category(150) == 'large'


class TestValidateVaultPath:
    """Tests for validate_vault_path function"""

    def test_valid_existing_vault(self, mock_vault):
        """Test validating existing vault path"""
        result = validate_vault_path(mock_vault, must_exist=True)
        assert result is True

    def test_nonexistent_vault_must_exist(self, temp_dir):
        """Test nonexistent vault when must_exist=True"""
        vault_path = os.path.join(temp_dir, 'nonexistent_vault')
        result = validate_vault_path(vault_path, must_exist=True)
        assert result is False

    def test_nonexistent_vault_optional(self, temp_dir):
        """Test nonexistent vault when must_exist=False"""
        vault_path = os.path.join(temp_dir, 'future_vault')
        result = validate_vault_path(vault_path, must_exist=False)
        assert result is True

    def test_empty_vault_path(self):
        """Test empty vault path"""
        result = validate_vault_path('', must_exist=False)
        assert result is False

    def test_null_byte_in_path(self):
        """Test that null bytes in path are rejected (security)"""
        result = validate_vault_path('/tmp/vault\x00malicious', must_exist=False)
        assert result is False

    def test_system_directory_rejected(self):
        """Test that system directories are rejected (security)"""
        sensitive_paths = ['/etc', '/sys', '/proc', '/dev', '/bin']

        for path in sensitive_paths:
            result = validate_vault_path(path, must_exist=False)
            assert result is False, f"Should have rejected system path: {path}"

    def test_root_directory_rejected(self):
        """Test that root directory is rejected (security)"""
        result = validate_vault_path('/', must_exist=False)
        assert result is False

    def test_user_home_expansion(self, mock_vault):
        """Test that ~/path is expanded correctly"""
        # This test validates the expansion works
        result = validate_vault_path(mock_vault, must_exist=True)
        assert result is True

    def test_file_not_directory(self, temp_dir):
        """Test that a file (not directory) is rejected"""
        file_path = os.path.join(temp_dir, 'file.txt')
        with open(file_path, 'w') as f:
            f.write('test')

        result = validate_vault_path(file_path, must_exist=True)
        assert result is False


class TestGetConfigValue:
    """Tests for get_config_value function"""

    def test_get_existing_key(self):
        """Test getting existing config key"""
        config = {'key1': 'value1', 'key2': 'value2'}
        value = get_config_value(config, 'key1')
        assert value == 'value1'

    def test_get_missing_key_with_default(self):
        """Test getting missing key with default"""
        config = {'key1': 'value1'}
        value = get_config_value(config, 'missing_key', default='default_value')
        assert value == 'default_value'

    def test_get_none_value_with_default(self):
        """Test getting None value with default"""
        config = {'key1': None}
        value = get_config_value(config, 'key1', default='default_value')
        assert value == 'default_value'
