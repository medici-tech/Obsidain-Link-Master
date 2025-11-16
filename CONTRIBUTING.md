# Contributing to Obsidian Auto-Linker

Thank you for your interest in contributing to Obsidian Auto-Linker! This document provides guidelines and instructions for contributing.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [How to Contribute](#how-to-contribute)
- [Coding Standards](#coding-standards)
- [Testing](#testing)
- [Pull Request Process](#pull-request-process)
- [Reporting Bugs](#reporting-bugs)
- [Suggesting Features](#suggesting-features)

---

## Code of Conduct

This project adheres to a simple principle: **Be respectful and constructive**. We're here to build great software together.

## Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/YOUR_USERNAME/Obsidain-Link-Master.git
   cd Obsidain-Link-Master
   ```
3. **Add upstream remote**:
   ```bash
   git remote add upstream https://github.com/medici-tech/Obsidain-Link-Master.git
   ```

## Development Setup

### Prerequisites

- Python 3.9+
- Ollama (for local AI processing)
- An Obsidian vault for testing

### Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Install Ollama (macOS)
brew install ollama

# Pull recommended model
ollama pull qwen2.5:3b

# Start Ollama server
ollama serve
```

### Configuration

```bash
# Run interactive setup
python3 run.py

# Or manually create config.yaml
cp config.yaml.example config.yaml
# Edit config.yaml with your settings
```

## How to Contribute

### Ways to Contribute

- 🐛 **Bug fixes**: Fix issues reported in GitHub Issues
- ✨ **Features**: Implement new features from the roadmap
- 📝 **Documentation**: Improve docs, add examples, fix typos
- 🧪 **Tests**: Add test coverage, improve existing tests
- 🎨 **UI/UX**: Enhance the dashboard, improve output formatting
- ⚡ **Performance**: Optimize processing speed, reduce memory usage

### Development Workflow

1. **Create a branch** for your work:
   ```bash
   git checkout -b feature/your-feature-name
   # or
   git checkout -b fix/issue-description
   ```

2. **Make your changes** following our coding standards

3. **Test your changes** locally:
   ```bash
   # Fast dry run (no AI)
   python3 run.py  # Select: Fast Dry Run

   # Full dry run (with AI, no file changes)
   python3 run.py  # Select: Full Dry Run

   # Run with dashboard
   python3 run_with_dashboard.py
   ```

4. **Commit your changes**:
   ```bash
   git add .
   git commit -m "type: brief description"
   ```

5. **Push to your fork**:
   ```bash
   git push origin feature/your-feature-name
   ```

6. **Create a Pull Request** on GitHub

## Coding Standards

### Python Style Guide

We follow [PEP 8](https://pep8.org/) with some project-specific conventions:

#### Naming Conventions

```python
# Functions: snake_case
def process_conversation():
    pass

# Classes: PascalCase
class LiveDashboard:
    pass

# Constants: UPPER_SNAKE_CASE
VAULT_PATH = "/path/to/vault"

# Private methods: _leading_underscore
def _internal_helper():
    pass
```

#### Type Hints

Use type hints for all public functions:

```python
from typing import List, Dict, Optional

def get_notes(vault_path: str) -> Dict[str, str]:
    """Get all notes from vault"""
    pass

def analyze_content(content: str, notes: Dict[str, str]) -> Optional[Dict]:
    """Analyze content with AI"""
    pass
```

#### Logging vs Print

**New code should use logging, not print():**

```python
from logger_config import get_logger
logger = get_logger(__name__)

# Good
logger.info("Processing file...")
logger.error(f"Failed to process: {e}")

# Bad
print("Processing file...")
```

#### Exception Handling

**Always use specific exception types:**

```python
# Good
try:
    with open(file_path, 'r') as f:
        content = f.read()
except FileNotFoundError:
    logger.error(f"File not found: {file_path}")
except (IOError, OSError) as e:
    logger.error(f"Could not read file: {e}")

# Bad
try:
    with open(file_path, 'r') as f:
        content = f.read()
except:  # Bare except is NOT allowed
    pass
```

### Code Documentation

#### Docstrings

Use Google-style docstrings for functions and classes:

```python
def process_file(file_path: str, existing_notes: Dict[str, str]) -> bool:
    """Process a single markdown file with AI analysis.

    Args:
        file_path: Absolute path to the markdown file
        existing_notes: Dictionary of existing note titles and content

    Returns:
        True if processing succeeded, False otherwise

    Raises:
        FileNotFoundError: If file_path doesn't exist
        ValueError: If file_path is not a markdown file
    """
    pass
```

#### Comments

- Use comments to explain **why**, not **what**
- Document complex algorithms and non-obvious workarounds
- Avoid obvious comments

```python
# Good (explains why)
# Use MD5 instead of SHA256 for performance - collisions unlikely
# given small dataset and non-cryptographic use case
hash_key = hashlib.md5(content.encode()).hexdigest()

# Bad (obvious)
count = 0  # Initialize counter
```

### Dashboard Integration

When adding features that benefit from monitoring:

```python
# Track metrics in dashboard if available
if dashboard:
    dashboard.add_activity(f"Processed: {filename}", success=True)
    dashboard.add_error("error_type", error_message)
    dashboard.update_processing(...)
```

## Testing

### Test Structure

```bash
tests/
├── test_core.py          # Core processing tests
├── test_dashboard.py     # Dashboard tests
├── test_ollama.py        # Ollama integration tests
└── test_config.py        # Configuration tests
```

### Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_core.py

# Run with coverage
pytest --cov=. --cov-report=html
```

### Writing Tests

```python
import pytest
from obsidian_auto_linker_enhanced import process_conversation

def test_process_conversation_success():
    """Test successful file processing"""
    # Arrange
    file_path = "test_files/sample.md"
    existing_notes = {"Note 1": "content"}
    stats = {'processed': 0, 'failed': 0}

    # Act
    result = process_conversation(file_path, existing_notes, stats)

    # Assert
    assert result is True
    assert stats['processed'] == 1
```

## Pull Request Process

### Before Submitting

- [ ] Code follows project style guidelines
- [ ] All tests pass
- [ ] New code has test coverage
- [ ] Documentation updated if needed
- [ ] Commit messages follow conventions
- [ ] No merge conflicts with main branch

### PR Title Format

```
<type>: <short description>

Types:
- feat: New feature
- fix: Bug fix
- docs: Documentation changes
- refactor: Code refactoring
- perf: Performance improvements
- test: Adding tests
- chore: Maintenance (deps, config)
```

Examples:
```
feat: Add parallel processing support
fix: Handle JSON parse errors in AI responses
docs: Update README with dashboard usage
refactor: Extract AI prompt building to separate function
```

### PR Description Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
Describe testing performed

## Checklist
- [ ] Tests pass
- [ ] Code follows style guide
- [ ] Documentation updated
- [ ] No breaking changes (or documented)
```

### Review Process

1. **Automated checks** run (linting, tests)
2. **Code review** by maintainers
3. **Changes requested** or **approved**
4. **Merge** to main branch

## Reporting Bugs

### Before Reporting

- Check if the bug is already reported in [Issues](https://github.com/medici-tech/Obsidain-Link-Master/issues)
- Try the latest version
- Test with Fast Dry Run to isolate the issue

### Bug Report Template

```markdown
**Describe the bug**
Clear description of what went wrong

**To Reproduce**
Steps to reproduce:
1. Configure with...
2. Run command...
3. See error...

**Expected behavior**
What you expected to happen

**Environment**
- OS: [e.g., macOS 14.0]
- Python version: [e.g., 3.11]
- Ollama model: [e.g., qwen2.5:3b]
- Config: [relevant config settings]

**Logs**
```
Paste relevant log output from obsidian_linker.log
```

**Additional context**
Any other relevant information
```

## Suggesting Features

### Feature Request Template

```markdown
**Is your feature request related to a problem?**
Clear description of the problem

**Describe the solution you'd like**
Clear description of what you want to happen

**Describe alternatives you've considered**
Other solutions you've thought about

**Additional context**
Mockups, examples, or other context
```

## Development Tips

### Using the Dashboard

```python
# Run with live dashboard for visual feedback
python3 run_with_dashboard.py
```

### Debugging

```python
# Enable debug logging
from logger_config import setup_logging
setup_logging(log_level="DEBUG")

# Check logs
tail -f obsidian_linker.log
```

### Ollama Troubleshooting

```bash
# Check Ollama is running
curl http://localhost:11434/api/tags

# List installed models
ollama list

# Pull model if needed
ollama pull qwen2.5:3b

# Test model
ollama run qwen2.5:3b "Hello"
```

## Project Structure

See [CLAUDE.md](./CLAUDE.md) for comprehensive architecture documentation.

## Questions?

- **Documentation**: Check [README.md](./README.md) and [CLAUDE.md](./CLAUDE.md)
- **Issues**: Browse [GitHub Issues](https://github.com/medici-tech/Obsidain-Link-Master/issues)
- **Discussions**: Start a [GitHub Discussion](https://github.com/medici-tech/Obsidain-Link-Master/discussions)

## License

By contributing, you agree that your contributions will be licensed under the [MIT License](./LICENSE).

---

**Thank you for contributing to Obsidian Auto-Linker!** 🎉
