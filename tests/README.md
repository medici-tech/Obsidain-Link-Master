# Obsidian Auto-Linker Tests

This directory contains the test suite for the Obsidian Auto-Linker project.

## Setup

Install test dependencies:

```bash
pip install -r requirements.txt
```

This will install:
- `pytest` - Testing framework
- `pytest-cov` - Coverage plugin for pytest

## Running Tests

### Run all tests

```bash
pytest
```

### Run with verbose output

```bash
pytest -v
```

### Run specific test file

```bash
pytest tests/test_config_utils.py
pytest tests/test_logger_config.py
pytest tests/test_integration.py
```

### Run specific test class

```bash
pytest tests/test_config_utils.py::TestLoadYamlConfig
```

### Run specific test function

```bash
pytest tests/test_config_utils.py::TestLoadYamlConfig::test_load_valid_config
```

### Run with coverage

```bash
pytest --cov
```

### Run with coverage report

```bash
pytest --cov --cov-report=html
```

This will generate an HTML coverage report in `htmlcov/index.html`.

### Run with coverage for specific module

```bash
pytest --cov=config_utils tests/test_config_utils.py
```

## Test Structure

```
tests/
├── __init__.py              # Test package initialization
├── conftest.py              # Pytest fixtures and configuration
├── test_config_utils.py     # Tests for config_utils module
├── test_logger_config.py    # Tests for logger_config module
├── test_integration.py      # Integration tests
└── README.md                # This file
```

## Test Fixtures

Common fixtures are defined in `conftest.py`:

- `temp_dir` - Temporary directory for tests
- `sample_config_yaml` - Sample YAML config file
- `sample_json_file` - Sample JSON file
- `mock_vault` - Mock Obsidian vault with sample files
- `empty_vault` - Empty Obsidian vault

## Writing New Tests

### Test File Naming

- Test files must start with `test_`
- Test classes must start with `Test`
- Test functions must start with `test_`

### Example Test

```python
import pytest
from config_utils import load_yaml_config

class TestMyFeature:
    """Tests for my new feature"""

    def test_basic_functionality(self, temp_dir):
        """Test basic functionality with temp directory"""
        # Arrange
        config_path = os.path.join(temp_dir, 'config.yaml')

        # Act
        result = load_yaml_config(config_path)

        # Assert
        assert result is not None
```

### Using Fixtures

```python
def test_with_mock_vault(self, mock_vault):
    """Test using the mock vault fixture"""
    # mock_vault provides a temporary vault with sample files
    assert os.path.isdir(mock_vault)
    assert os.path.exists(os.path.join(mock_vault, 'note1.md'))
```

## Coverage Goals

Current test coverage focuses on:

- ✅ `config_utils.py` - Comprehensive coverage of all utility functions
- ✅ `logger_config.py` - Logging setup and configuration
- ✅ Integration tests - Module imports and basic workflows
- ⏳ `obsidian_auto_linker_enhanced.py` - Planned
- ⏳ `live_dashboard.py` - Planned
- ⏳ `run.py` and `run_with_dashboard.py` - Planned

## CI/CD Integration

These tests are designed to run in CI/CD pipelines. The `pytest.ini` configuration ensures consistent behavior across environments.

### GitHub Actions Example

```yaml
- name: Run tests
  run: |
    pip install -r requirements.txt
    pytest --cov --cov-report=xml

- name: Upload coverage
  uses: codecov/codecov-action@v3
  with:
    file: ./coverage.xml
```

## Troubleshooting

### Import Errors

If you get import errors, make sure you're running pytest from the project root:

```bash
cd /path/to/Obsidain-Link-Master
pytest
```

### Missing Dependencies

Install all dependencies including test dependencies:

```bash
pip install -r requirements.txt
```

### Ollama Connection Tests

Some tests check Ollama connection. These tests will pass even if Ollama is not running, as they test error handling. To test actual Ollama integration, ensure Ollama is running:

```bash
ollama serve
```

## Test Categories

Tests are organized by category:

1. **Unit Tests** - Test individual functions in isolation
   - `test_config_utils.py`
   - `test_logger_config.py`

2. **Integration Tests** - Test modules working together
   - `test_integration.py`

3. **End-to-End Tests** - Planned for future
   - Will test complete workflows

## Best Practices

1. **Isolation** - Each test should be independent
2. **Fixtures** - Use fixtures for common setup
3. **Assertions** - Make assertions clear and specific
4. **Documentation** - Add docstrings to tests
5. **Coverage** - Aim for high coverage, but focus on meaningful tests

## Contributing

When adding new features:

1. Write tests first (TDD approach)
2. Ensure all tests pass: `pytest`
3. Check coverage: `pytest --cov`
4. Update this README if needed

## Questions?

See the main [CONTRIBUTING.md](../CONTRIBUTING.md) for more details on development practices.
