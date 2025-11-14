"""
Pytest fixtures and configuration for Obsidian Auto-Linker tests
"""

import pytest
import tempfile
import os
import yaml
import json
from pathlib import Path


@pytest.fixture
def temp_dir():
    """Create a temporary directory for tests"""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


@pytest.fixture
def sample_config_yaml(temp_dir):
    """Create a sample config.yaml file"""
    config_path = os.path.join(temp_dir, 'config.yaml')
    config_data = {
        'vault_path': '/path/to/vault',
        'dry_run': True,
        'fast_dry_run': False,
        'batch_size': 5,
        'file_ordering': 'recent',
        'ollama_base_url': 'http://localhost:11434',
        'ollama_model': 'qwen2.5:3b',
    }
    with open(config_path, 'w') as f:
        yaml.dump(config_data, f)
    return config_path


@pytest.fixture
def sample_json_file(temp_dir):
    """Create a sample JSON file"""
    json_path = os.path.join(temp_dir, 'test.json')
    json_data = {
        'test_key': 'test_value',
        'number': 42,
        'list': [1, 2, 3]
    }
    with open(json_path, 'w') as f:
        json.dump(json_data, f)
    return json_path


@pytest.fixture
def mock_vault(temp_dir):
    """Create a mock Obsidian vault with sample files"""
    vault_path = os.path.join(temp_dir, 'vault')
    os.makedirs(vault_path)

    # Create some sample markdown files
    notes = {
        'note1.md': '# Note 1\n\nSome content here.',
        'note2.md': '# Note 2\n\nMore content.',
        'conversation.md': '# Conversation\n\nA discussion about something.',
    }

    for filename, content in notes.items():
        with open(os.path.join(vault_path, filename), 'w') as f:
            f.write(content)

    return vault_path


@pytest.fixture
def empty_vault(temp_dir):
    """Create an empty Obsidian vault"""
    vault_path = os.path.join(temp_dir, 'empty_vault')
    os.makedirs(vault_path)
    return vault_path
