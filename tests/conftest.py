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
Pytest configuration and shared fixtures for Obsidian Auto-Linker tests
"""

import os
import json
import tempfile
import shutil
from pathlib import Path
from typing import Dict, Any
import pytest
from unittest.mock import Mock, patch, MagicMock


@pytest.fixture
def temp_vault():
    """Create a temporary vault directory for testing"""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)


@pytest.fixture
def sample_config():
    """Sample configuration for testing"""
    return {
        'vault_path': '/tmp/test_vault',
        'backup_folder': '_backups',
        'dry_run': True,
        'fast_dry_run': False,
        'max_backups': 5,
        'max_siblings': 5,
        'batch_size': 1,
        'max_retries': 3,
        'parallel_workers': 1,
        'file_ordering': 'recent',
        'resume_enabled': True,
        'cache_enabled': True,
        'interactive_mode': False,
        'analytics_enabled': True,
        'confidence_threshold': 0.8,
        'enable_review_queue': True,
        'review_queue_path': 'reviews/',
        'dry_run_limit': 10,
        'dry_run_interactive': False,
        'ollama_base_url': 'http://localhost:11434',
        'ollama_model': 'qwen3:8b',
        'ollama_timeout': 300,
        'ollama_max_retries': 5,
        'ollama_temperature': 0.1,
        'ollama_max_tokens': 1024,
    }


@pytest.fixture
def sample_markdown_content():
    """Sample markdown content for testing"""
    return """# Test Conversation

This is a test conversation about business strategy and technical implementation.

## Discussion Points

- Revenue optimization
- Market analysis
- Technical architecture
- API integration

## Action Items

1. Review current strategy
2. Implement new features
3. Analyze market trends
"""


@pytest.fixture
def sample_markdown_file(temp_vault, sample_markdown_content):
    """Create a sample markdown file in temp vault"""
    file_path = os.path.join(temp_vault, "test_conversation.md")
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(sample_markdown_content)
    return file_path


@pytest.fixture
def sample_processed_content():
    """Sample processed markdown with metadata"""
    return """# Test Conversation

This is a test conversation.

---
## 📊 METADATA

Primary Topic: Business Strategy
Topic Area: Business Operations
Confidence: 85%

---
## 🔗 WIKI STRUCTURE

Parent: [[📍 Business Operations MOC]]
Siblings: [[Related Note 1]] · [[Related Note 2]]
Children: None yet

---
## 💡 KEY CONCEPTS

- Revenue optimization
- Market analysis

---
## 🏷️ TAGS

#business #strategy #operations
"""


@pytest.fixture
def mock_ollama_response():
    """Mock Ollama API response"""
    return {
        'response': json.dumps({
            'moc_category': 'Business Operations',
            'primary_topic': 'Business Strategy Discussion',
            'hierarchical_tags': ['business', 'strategy', 'operations'],
            'key_concepts': ['revenue optimization', 'market analysis', 'technical architecture'],
            'sibling_notes': ['Related Note 1', 'Related Note 2'],
            'confidence_score': 0.85,
            'reasoning': 'Content discusses business operations and strategic planning'
        })
    }


@pytest.fixture
def mock_ollama_success(mock_ollama_response):
    """Mock successful Ollama API call"""
    with patch('requests.post') as mock_post:
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = mock_ollama_response
        mock_post.return_value.raise_for_status = Mock()
        yield mock_post


@pytest.fixture
def mock_ollama_timeout():
    """Mock Ollama API timeout"""
    with patch('requests.post') as mock_post:
        import requests
        mock_post.side_effect = requests.exceptions.Timeout("Connection timeout")
        yield mock_post


@pytest.fixture
def mock_ollama_error():
    """Mock Ollama API error"""
    with patch('requests.post') as mock_post:
        import requests
        mock_post.side_effect = requests.exceptions.RequestException("API error")
        yield mock_post


@pytest.fixture
def sample_cache():
    """Sample cache data"""
    return {
        'abc123': {
            'moc_category': 'Technical & Automation',
            'primary_topic': 'API Development',
            'hierarchical_tags': ['api', 'development', 'technical'],
            'key_concepts': ['REST API', 'Authentication', 'Integration'],
            'sibling_notes': ['API Guide', 'Auth Implementation'],
            'confidence_score': 0.9,
            'reasoning': 'Technical content about API development'
        }
    }


@pytest.fixture
def sample_progress_data():
    """Sample progress tracking data"""
    return {
        'processed_files': ['/path/to/file1.md', '/path/to/file2.md'],
        'failed_files': ['/path/to/failed.md'],
        'current_batch': 1,
        'last_update': '2024-01-01T12:00:00'
    }


@pytest.fixture
def sample_analytics():
    """Sample analytics data"""
    return {
        'start_time': '2024-01-01T10:00:00',
        'end_time': '2024-01-01T11:00:00',
        'total_files': 100,
        'processed_files': 85,
        'skipped_files': 10,
        'failed_files': 5,
        'processing_time': 3600,
        'moc_distribution': {
            'Business Operations': 20,
            'Technical & Automation': 30,
            'Learning & Skills': 15,
            'Life & Misc': 20
        },
        'error_types': {
            'timeout': 3,
            'parse_error': 2
        },
        'retry_attempts': 12,
        'cache_hits': 45,
        'cache_misses': 40
    }


@pytest.fixture
def sample_existing_notes():
    """Sample existing notes in vault"""
    return {
        'Related Note 1': 'Content preview for note 1...',
        'Related Note 2': 'Content preview for note 2...',
        'API Guide': 'Guide about API development...',
        'Business Strategy': 'Strategic planning notes...'
    }


@pytest.fixture
def mock_file_system(temp_vault):
    """Mock file system with sample files"""
    # Create some sample files
    files = [
        'conversation1.md',
        'conversation2.md',
        'technical_note.md',
        'business_plan.md'
    ]

    for filename in files:
        file_path = os.path.join(temp_vault, filename)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(f"# {filename}\n\nSample content for {filename}")

    return temp_vault


@pytest.fixture
def mock_config_file(temp_vault, sample_config):
    """Create a temporary config file"""
    config_path = os.path.join(temp_vault, 'config.yaml')
    import yaml
    with open(config_path, 'w') as f:
        yaml.dump(sample_config, f)
    return config_path


@pytest.fixture
def content_hash_fixture():
    """Fixture for testing content hashing"""
    test_content = "This is test content for hashing"
    import hashlib
    expected_hash = hashlib.md5(test_content.encode()).hexdigest()
    return test_content, expected_hash


@pytest.fixture(autouse=True)
def reset_globals():
    """Reset global variables before each test"""
    # This ensures tests don't interfere with each other
    yield
    # Cleanup after test
    pass


@pytest.fixture
def mock_datetime():
    """Mock datetime for consistent timestamps"""
    from freezegun import freeze_time
    with freeze_time("2024-01-01 12:00:00"):
        yield


# Custom assertions
def assert_file_exists(file_path: str):
    """Assert that a file exists"""
    assert os.path.exists(file_path), f"File does not exist: {file_path}"


def assert_valid_json(json_string: str):
    """Assert that a string is valid JSON"""
    try:
        json.loads(json_string)
    except json.JSONDecodeError as e:
        pytest.fail(f"Invalid JSON: {e}")


def assert_markdown_structure(content: str):
    """Assert that content has valid markdown structure"""
    assert '# ' in content, "Missing markdown headers"


# Helper functions for tests
def create_test_file(directory: str, filename: str, content: str) -> str:
    """Create a test file and return its path"""
    file_path = os.path.join(directory, filename)
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    return file_path
