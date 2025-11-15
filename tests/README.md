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
