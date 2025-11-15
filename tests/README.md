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
# Test Suite for Obsidian Auto-Linker

Comprehensive test suite for the Obsidian Auto-Linker Enhanced system.

## Overview

This test suite provides extensive coverage of the Obsidian Auto-Linker functionality, including:
- AI integration and Ollama API calls
- Content processing and analysis
- File operations and backup management
- Caching system
- Integration workflows

## Test Coverage

Current test coverage: **~50%+** (target)

### Test Categories

#### Unit Tests (`@pytest.mark.unit`)
- **AI Integration** (`test_ollama_integration.py`): 15+ tests
  - Ollama API call success/failure scenarios
  - Retry logic and exponential backoff
  - Timeout handling
  - JSON parsing and cleanup

- **Cache Operations** (`test_cache.py`): 15+ tests
  - Cache storage and retrieval
  - Content hashing
  - Cache persistence
  - Performance benefits

- **Content Processing** (`test_content_processing.py`): 12+ tests
  - MOC categorization
  - File filtering
  - Fast dry run analysis
  - Confidence threshold validation

- **File Operations** (`test_file_operations.py`): 18+ tests
  - File processing workflows
  - Backup creation and verification
  - Progress tracking
  - File ordering strategies

#### Integration Tests (`@pytest.mark.integration`)
- **End-to-End Workflows** (`test_integration.py`): 10+ tests
  - Full processing pipeline
  - Resume from interrupted state
  - Review queue workflow
  - Analytics generation
  - Model selector integration

## Quick Start

### Installation

```bash
# Install test dependencies
pip install -r requirements-test.txt
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=. --cov-report=html --cov-report=term-missing

# Run only unit tests
pytest -m unit

# Run only integration tests
pytest -m integration

# Run specific test file
pytest tests/test_ollama_integration.py

# Run specific test
pytest tests/test_cache.py::TestCacheOperations::test_get_content_hash_consistency

# Run with verbose output
pytest -v

# Run fast tests only (exclude slow tests)
pytest -m "not slow"
```

### Test Markers

Use markers to run specific test categories:

```bash
# Unit tests only
pytest -m unit

# Integration tests only
pytest -m integration

# AI-related tests
pytest -m ai

# Cache tests
pytest -m cache

# File operation tests
pytest -m file_ops

# Exclude slow tests
pytest -m "not slow"
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
├── conftest.py              # Shared fixtures and configuration
├── test_ollama_integration.py   # AI integration tests
├── test_cache.py            # Caching system tests
├── test_content_processing.py   # Content analysis tests
├── test_file_operations.py  # File handling tests
├── test_integration.py      # End-to-end integration tests
├── fixtures/                # Test data and fixtures
└── README.md               # This file
```

## Fixtures

Common fixtures available in `conftest.py`:

- `temp_vault`: Temporary vault directory
- `sample_config`: Sample configuration dictionary
- `sample_markdown_content`: Sample markdown content
- `sample_markdown_file`: Sample markdown file in temp vault
- `mock_ollama_success`: Mock successful Ollama API call
- `mock_ollama_timeout`: Mock Ollama timeout
- `mock_ollama_error`: Mock Ollama error
- `sample_cache`: Sample cache data
- `sample_existing_notes`: Sample existing notes
- `mock_file_system`: Mock file system with sample files

## Coverage Reports

After running tests with coverage:

```bash
# Generate HTML coverage report
pytest --cov=. --cov-report=html

# Open coverage report
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
```

## Continuous Integration

Tests run automatically on:
- Every push to `main`, `develop`, or `claude/*` branches
- Every pull request
- Manual workflow dispatch

See `.github/workflows/test.yml` for CI/CD configuration.

### CI/CD Jobs

1. **test**: Main test suite across Python 3.9-3.12
2. **test-fast**: Quick unit tests only
3. **test-slow**: Long-running integration tests
4. **security-scan**: Security vulnerability scanning

## Writing New Tests

### Test Template

```python
import pytest
from unittest.mock import patch, Mock

@pytest.mark.unit
class TestYourFeature:
    """Test suite for your feature"""

    def test_your_function(self, fixture_name):
        """Test description"""
        # Arrange
        # ... setup test data

        # Act
        # ... call function

        # Assert
        # ... verify results
        assert result is not None
```

### Best Practices

1. **Use descriptive test names**: `test_function_name_scenario_expected_result`
2. **One assertion per test**: Focus on testing one thing
3. **Use fixtures**: Avoid code duplication
4. **Mock external dependencies**: Don't rely on actual Ollama API
5. **Test edge cases**: Empty inputs, errors, boundaries
6. **Add markers**: Categorize tests properly
7. **Keep tests fast**: Mock slow operations
8. **Clean up**: Use fixtures with cleanup

### Adding Fixtures

Add new fixtures to `tests/conftest.py`:

```python
@pytest.fixture
def your_fixture():
    """Description of fixture"""
    # Setup
    data = create_test_data()
    yield data
    # Cleanup (if needed)
    cleanup_test_data()
```

## Debugging Tests

```bash
# Run with pdb on failure
pytest --pdb

# Stop on first failure
pytest -x

# Show local variables on failure
pytest -l

# Increase verbosity
pytest -vv

# Show print statements
pytest -s
```

## Test Coverage Goals

Current coverage by module:

- `obsidian_auto_linker_enhanced.py`: **Target 70%+**
- `enhanced_analytics.py`: **Target 40%+**
- `live_dashboard.py`: **Target 30%+**
- `ultra_detailed_analytics.py`: **Target 40%+**
- `scripts/`: **Target 50%+**

## Known Issues

- Some integration tests require mocking of file system operations
- Slow tests can take 30+ seconds
- Cache tests depend on consistent hashing

## Contributing

When adding new features:

1. Write tests first (TDD approach)
2. Ensure all tests pass: `pytest`
3. Check coverage: `pytest --cov`
4. Update this README if needed

## Questions?

See the main [CONTRIBUTING.md](../CONTRIBUTING.md) for more details on development practices.
2. Ensure tests pass locally
3. Add appropriate markers
4. Update this README if adding new test categories
5. Maintain minimum 50% coverage

## Support

For issues with tests:
1. Check fixture availability in `conftest.py`
2. Verify mock configurations
3. Review test markers
4. Check CI/CD logs for failures

## Future Improvements

- [ ] Add property-based testing with Hypothesis
- [ ] Add mutation testing with mutmut
- [ ] Increase coverage to 80%+
- [ ] Add performance benchmarking tests
- [ ] Add snapshot testing for reports
- [ ] Add contract tests for API interactions
