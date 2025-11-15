# 📚 API Reference

**Enhanced Obsidian Auto-Linker** - Complete API Documentation

---

## 📋 Table of Contents

1. [Core Processing Engine](#core-processing-engine)
2. [Dashboard Module](#dashboard-module)
3. [Analytics Module](#analytics-module)
4. [Model Selector Module](#model-selector-module)
5. [Logger Configuration](#logger-configuration)
6. [Configuration](#configuration)
7. [Utility Functions](#utility-functions)

---

## Core Processing Engine

**Module**: `obsidian_auto_linker_enhanced.py`

### Class: `ObsidianAutoLinker`

Main processing engine for analyzing and linking Obsidian vault files.

#### Constructor

```python
ObsidianAutoLinker()
```

**Description**: Initializes the auto-linker with default configuration.

**Attributes**:
- `config` (dict): Configuration dictionary loaded from `config.yaml`
- `vault_path` (str): Path to Obsidian vault
- `dry_run` (bool): Whether to run in dry-run mode
- `ai_cache` (dict): Cache of AI responses keyed by content hash
- `analytics` (dict): Processing analytics data

**Example**:
```python
linker = ObsidianAutoLinker()
```

---

#### Method: `load_config()`

```python
def load_config(self) -> dict
```

**Description**: Loads configuration from `config.yaml`.

**Returns**:
- `dict`: Configuration dictionary

**Raises**:
- `FileNotFoundError`: If config.yaml doesn't exist
- `yaml.YAMLError`: If config has invalid YAML syntax

**Example**:
```python
config = linker.load_config()
vault_path = config['vault_path']
```

---

#### Method: `process_vault()`

```python
def process_vault(self, dashboard=None) -> dict
```

**Description**: Main entry point for processing the entire vault.

**Parameters**:
- `dashboard` (LiveDashboard, optional): Dashboard instance for live monitoring

**Returns**:
- `dict`: Processing results containing:
  - `files_processed` (int): Number of files processed
  - `links_created` (int): Total links created
  - `cache_hits` (int): Number of cache hits
  - `errors` (list): List of errors encountered

**Example**:
```python
results = linker.process_vault()
print(f"Processed {results['files_processed']} files")
```

---

#### Method: `analyze_with_balanced_ai()`

```python
def analyze_with_balanced_ai(
    self,
    content: str,
    existing_notes: List[str],
    model_selector=None
) -> dict
```

**Description**: Analyzes content using AI to determine MOC category and related notes.

**Parameters**:
- `content` (str): Markdown content to analyze
- `existing_notes` (List[str]): List of existing note titles in vault
- `model_selector` (IntelligentModelSelector, optional): Model selector for hybrid mode

**Returns**:
- `dict`: Analysis results containing:
  - `moc_category` (str): Determined MOC category
  - `confidence_score` (float): Confidence score (0.0-1.0)
  - `reasoning` (str): Explanation for categorization
  - `suggested_links` (List[str]): Suggested related notes

**Raises**:
- `requests.exceptions.Timeout`: If AI request times out
- `JSONDecodeError`: If AI response is not valid JSON

**Example**:
```python
result = linker.analyze_with_balanced_ai(
    content="Technical analysis of Python APIs",
    existing_notes=["API Design", "Python Best Practices"]
)
print(result['moc_category'])  # e.g., "Technology"
```

---

#### Method: `create_wikilinks()`

```python
def create_wikilinks(
    self,
    content: str,
    moc_category: str,
    existing_notes: List[str]
) -> str
```

**Description**: Creates wikilinks in markdown content based on MOC category.

**Parameters**:
- `content` (str): Original markdown content
- `moc_category` (str): MOC category (e.g., "Technology", "Business Operations")
- `existing_notes` (List[str]): List of existing note titles

**Returns**:
- `str`: Updated markdown content with wikilinks

**Example**:
```python
updated = linker.create_wikilinks(
    content="This is about Python programming",
    moc_category="Technology",
    existing_notes=["Python", "Programming"]
)
# Result: "This is about [[Python]] [[Programming]]"
```

---

#### Method: `get_content_hash()`

```python
def get_content_hash(self, content: str) -> str
```

**Description**: Generates MD5 hash of content for caching.

**Parameters**:
- `content` (str): Content to hash

**Returns**:
- `str`: MD5 hash hexdigest

**Example**:
```python
hash_key = linker.get_content_hash("Some content")
# Result: "a3d5e8f7c9b1a2d4e6f8a0b2c4d6e8f0"
```

---

#### Method: `create_backup()`

```python
def create_backup(self, file_path: str) -> str
```

**Description**: Creates timestamped backup of file before modification.

**Parameters**:
- `file_path` (str): Path to file to backup

**Returns**:
- `str`: Path to backup file

**Raises**:
- `IOError`: If backup creation fails

**Example**:
```python
backup_path = linker.create_backup("/vault/note.md")
# Result: "backups/2024-11-15_10-30-45/note.md"
```

---

#### Method: `call_ollama()`

```python
def call_ollama(
    self,
    prompt: str,
    system_prompt: str = "",
    max_retries: int = 3
) -> str
```

**Description**: Calls Ollama API with retry logic.

**Parameters**:
- `prompt` (str): User prompt to send to AI
- `system_prompt` (str, optional): System prompt for context
- `max_retries` (int, optional): Maximum retry attempts (default: 3)

**Returns**:
- `str`: AI response text

**Raises**:
- `requests.exceptions.Timeout`: If all retries timeout
- `requests.exceptions.ConnectionError`: If cannot connect to Ollama

**Example**:
```python
response = linker.call_ollama(
    prompt="Categorize this content",
    system_prompt="You are a categorization expert",
    max_retries=5
)
```

---

## Dashboard Module

**Module**: `live_dashboard.py`

### Class: `LiveDashboard`

Real-time monitoring dashboard using Rich library. Implements Singleton pattern.

#### Constructor

```python
LiveDashboard()
```

**Description**: Creates or returns existing dashboard instance (Singleton).

**Example**:
```python
dashboard = LiveDashboard()
```

---

#### Method: `add_ai_request()`

```python
def add_ai_request(
    self,
    response_time: float,
    success: bool,
    tokens: int = 0,
    timeout: bool = False
) -> None
```

**Description**: Tracks an AI request for monitoring.

**Parameters**:
- `response_time` (float): Request duration in seconds
- `success` (bool): Whether request succeeded
- `tokens` (int, optional): Number of tokens in response
- `timeout` (bool, optional): Whether request timed out

**Example**:
```python
dashboard.add_ai_request(
    response_time=2.5,
    success=True,
    tokens=150
)
```

---

#### Method: `add_cache_hit()` / `add_cache_miss()`

```python
def add_cache_hit(self) -> None
def add_cache_miss(self) -> None
```

**Description**: Tracks cache performance.

**Example**:
```python
if content_hash in cache:
    dashboard.add_cache_hit()
else:
    dashboard.add_cache_miss()
```

---

#### Method: `update_file_progress()`

```python
def update_file_progress(
    self,
    current: int,
    total: int,
    filename: str = ""
) -> None
```

**Description**: Updates file processing progress.

**Parameters**:
- `current` (int): Current file number
- `total` (int): Total files to process
- `filename` (str, optional): Current filename

**Example**:
```python
dashboard.update_file_progress(
    current=15,
    total=100,
    filename="note.md"
)
```

---

#### Method: `add_activity()`

```python
def add_activity(
    self,
    message: str,
    level: str = "info"
) -> None
```

**Description**: Adds activity log entry.

**Parameters**:
- `message` (str): Log message
- `level` (str, optional): Log level ("info", "warning", "error")

**Example**:
```python
dashboard.add_activity("Processing started", level="info")
dashboard.add_activity("Timeout occurred", level="warning")
```

---

#### Method: `start()` / `stop()`

```python
def start(self) -> None
def stop(self) -> None
```

**Description**: Starts/stops dashboard rendering.

**Example**:
```python
dashboard.start()
# ... processing ...
dashboard.stop()
```

---

## Analytics Module

**Module**: `enhanced_analytics.py`

### Function: `load_analytics_data()`

```python
def load_analytics_data(analytics_file: str = "analytics.json") -> dict
```

**Description**: Loads analytics data from JSON file.

**Parameters**:
- `analytics_file` (str, optional): Path to analytics file (default: "analytics.json")

**Returns**:
- `dict`: Analytics data dictionary

**Example**:
```python
data = load_analytics_data()
print(data['files_processed'])
```

---

### Function: `generate_comprehensive_report()`

```python
def generate_comprehensive_report(
    analytics: dict,
    output_file: str = "docs/processing_report.html"
) -> str
```

**Description**: Generates HTML analytics report.

**Parameters**:
- `analytics` (dict): Analytics data
- `output_file` (str, optional): Output path for HTML file

**Returns**:
- `str`: HTML report content

**Example**:
```python
html = generate_comprehensive_report(analytics)
with open("report.html", "w") as f:
    f.write(html)
```

---

### Function: `calculate_metrics()`

```python
def calculate_metrics(analytics: dict) -> dict
```

**Description**: Calculates statistical metrics from analytics data.

**Parameters**:
- `analytics` (dict): Raw analytics data

**Returns**:
- `dict`: Calculated metrics including:
  - `avg_processing_time` (float): Average time per file
  - `cache_hit_rate` (float): Percentage of cache hits
  - `success_rate` (float): Percentage of successful processes

**Example**:
```python
metrics = calculate_metrics(analytics)
print(f"Cache hit rate: {metrics['cache_hit_rate']:.1f}%")
```

---

## Model Selector Module

**Module**: `scripts/intelligent_model_selector.py`

### Class: `IntelligentModelSelector`

Selects optimal AI model based on content complexity.

#### Constructor

```python
IntelligentModelSelector(config: dict)
```

**Description**: Initializes model selector with configuration.

**Parameters**:
- `config` (dict): Configuration dictionary

**Example**:
```python
selector = IntelligentModelSelector(config)
```

---

#### Method: `analyze_content_complexity()`

```python
def analyze_content_complexity(
    self,
    content: str,
    file_path: str
) -> dict
```

**Description**: Analyzes content to determine complexity.

**Parameters**:
- `content` (str): Content to analyze
- `file_path` (str): Path to file (for filename analysis)

**Returns**:
- `dict`: Analysis containing:
  - `word_count` (int): Number of words
  - `char_count` (int): Number of characters
  - `complexity_score` (int): Calculated complexity score
  - `recommended_model` (str): "qwen3:8b" or "qwen2.5:3b"
  - `reasoning` (str): Explanation for recommendation

**Example**:
```python
analysis = selector.analyze_content_complexity(
    content="Technical Python API documentation",
    file_path="docs/api.md"
)
print(analysis['recommended_model'])  # "qwen3:8b"
```

---

#### Method: `select_model()`

```python
def select_model(
    self,
    content: str,
    file_path: str
) -> Tuple[str, dict]
```

**Description**: Selects best model and returns configuration.

**Parameters**:
- `content` (str): Content to process
- `file_path` (str): File path

**Returns**:
- `Tuple[str, dict]`: (model_name, settings_dict)

**Example**:
```python
model, settings = selector.select_model(content, "note.md")
print(f"Using {model} with timeout {settings['timeout']}s")
```

---

#### Method: `call_selected_model()`

```python
def call_selected_model(
    self,
    content: str,
    file_path: str,
    prompt: str
) -> dict
```

**Description**: Calls appropriate model based on content analysis.

**Parameters**:
- `content` (str): Content to analyze
- `file_path` (str): File path
- `prompt` (str): Prompt to send to model

**Returns**:
- `dict`: Parsed JSON response from model

**Raises**:
- `requests.exceptions.Timeout`: If request times out
- Falls back to qwen2.5:3b on qwen3:8b failure

**Example**:
```python
result = selector.call_selected_model(
    content="Business analysis content",
    file_path="business.md",
    prompt="Categorize this content"
)
```

---

## Logger Configuration

**Module**: `logger_config.py`

### Function: `setup_logger()`

```python
def setup_logger(
    name: str = "obsidian_linker",
    log_file: str = "logs/obsidian_linker.log",
    level: int = logging.INFO
) -> logging.Logger
```

**Description**: Sets up rotating file logger.

**Parameters**:
- `name` (str, optional): Logger name
- `log_file` (str, optional): Log file path
- `level` (int, optional): Logging level (default: INFO)

**Returns**:
- `logging.Logger`: Configured logger instance

**Example**:
```python
logger = setup_logger(level=logging.DEBUG)
logger.info("Processing started")
logger.error("An error occurred")
```

---

## Configuration

### Configuration Dictionary Structure

```python
{
    # Core settings
    "vault_path": str,           # Path to Obsidian vault
    "dry_run": bool,             # Test mode (no file modifications)
    "fast_dry_run": bool,        # Skip AI, use keywords only

    # AI model settings
    "ollama_base_url": str,      # Ollama API URL
    "ollama_model": str,         # Model name (e.g., "qwen3:8b")
    "ollama_temperature": float, # Randomness (0.0-1.0)
    "ollama_timeout": int,       # Request timeout (seconds)
    "ollama_max_retries": int,   # Max retry attempts
    "ollama_max_tokens": int,    # Max response tokens

    # Processing settings
    "batch_size": int,           # Files per batch
    "parallel_workers": int,     # Parallel processing threads
    "file_ordering": str,        # "recent"|"alphabetical"|"size"

    # Analytics settings
    "analytics_enabled": bool,   # Enable analytics tracking
    "generate_report": bool,     # Generate HTML report
    "auto_open_report": bool,    # Auto-open report in browser

    # Hybrid mode settings (optional)
    "use_hybrid_models": bool,              # Enable hybrid mode
    "primary_ollama_model": str,            # Complex content model
    "secondary_ollama_model": str,          # Simple content model
    "model_switching_threshold": int,       # Word count threshold
}
```

---

## Utility Functions

### Function: `extract_existing_notes()`

```python
def extract_existing_notes(content: str) -> List[str]
```

**Description**: Extracts wikilink references from markdown content.

**Parameters**:
- `content` (str): Markdown content

**Returns**:
- `List[str]`: List of note titles referenced via [[wikilinks]]

**Example**:
```python
notes = extract_existing_notes("See [[Note 1]] and [[Note 2]]")
# Result: ["Note 1", "Note 2"]
```

---

### Function: `truncate_content()`

```python
def truncate_content(content: str, max_length: int = 4000) -> str
```

**Description**: Truncates content to maximum length for AI processing.

**Parameters**:
- `content` (str): Content to truncate
- `max_length` (int, optional): Maximum characters (default: 4000)

**Returns**:
- `str`: Truncated content

**Example**:
```python
short = truncate_content(long_text, max_length=2000)
```

---

### Function: `clean_json_response()`

```python
def clean_json_response(text: str) -> str
```

**Description**: Cleans AI response to extract valid JSON.

**Parameters**:
- `text` (str): Raw AI response text

**Returns**:
- `str`: Cleaned JSON string

**Example**:
```python
clean = clean_json_response('```json\n{"key": "value"}\n```')
# Result: '{"key": "value"}'
```

---

## MOC Categories

### Available Categories

```python
MOC_CATEGORIES = [
    "Business Operations",
    "Technology",
    "Personal Development",
    "Finance & Investing",
    "Health & Wellness",
    "Creative Projects",
    "Life & Misc"
]
```

---

## Error Handling

### Common Exceptions

#### `ConfigurationError`
```python
class ConfigurationError(Exception):
    """Raised when configuration is invalid"""
    pass
```

#### `OllamaConnectionError`
```python
class OllamaConnectionError(Exception):
    """Raised when cannot connect to Ollama service"""
    pass
```

#### `ProcessingError`
```python
class ProcessingError(Exception):
    """Raised when file processing fails"""
    pass
```

**Usage Example**:
```python
try:
    linker.process_vault()
except ConfigurationError as e:
    logger.error(f"Config error: {e}")
except OllamaConnectionError as e:
    logger.error(f"Ollama not running: {e}")
except ProcessingError as e:
    logger.error(f"Processing failed: {e}")
```

---

## Complete Usage Example

```python
#!/usr/bin/env python3
"""
Complete example of using the Enhanced Obsidian Auto-Linker API
"""

import logging
from obsidian_auto_linker_enhanced import ObsidianAutoLinker
from live_dashboard import LiveDashboard
from enhanced_analytics import generate_comprehensive_report
from scripts.intelligent_model_selector import IntelligentModelSelector
from logger_config import setup_logger

# Setup logging
logger = setup_logger(level=logging.INFO)

# Initialize components
linker = ObsidianAutoLinker()
dashboard = LiveDashboard()
config = linker.load_config()

# Optional: Initialize model selector for hybrid mode
if config.get('use_hybrid_models', False):
    model_selector = IntelligentModelSelector(config)
else:
    model_selector = None

# Start dashboard
dashboard.start()

try:
    # Process vault
    logger.info("Starting vault processing")
    results = linker.process_vault(dashboard=dashboard)

    # Log results
    logger.info(f"Processed {results['files_processed']} files")
    logger.info(f"Created {results['links_created']} links")
    logger.info(f"Cache hit rate: {results['cache_hits'] / results['files_processed'] * 100:.1f}%")

    # Generate report
    if config.get('generate_report', True):
        html = generate_comprehensive_report(linker.analytics)
        logger.info("Analytics report generated")

finally:
    # Stop dashboard
    dashboard.stop()

logger.info("Processing complete")
```

---

## Testing API

### Pytest Fixtures

Available in `tests/conftest.py`:

```python
@pytest.fixture
def temp_vault(tmp_path):
    """Creates temporary vault for testing"""
    vault = tmp_path / "test_vault"
    vault.mkdir()
    return str(vault)

@pytest.fixture
def sample_config():
    """Provides sample configuration"""
    return {
        'vault_path': '/path/to/vault',
        'dry_run': True,
        'ollama_model': 'qwen3:8b'
    }

@pytest.fixture
def mock_ollama_success():
    """Mocks successful Ollama API call"""
    with patch('requests.post') as mock:
        mock.return_value.status_code = 200
        mock.return_value.json.return_value = {
            'response': '{"moc_category": "Technology"}'
        }
        yield mock
```

**Usage**:
```python
def test_processing(temp_vault, sample_config, mock_ollama_success):
    linker = ObsidianAutoLinker()
    linker.config = sample_config
    linker.config['vault_path'] = temp_vault

    results = linker.process_vault()
    assert results['files_processed'] >= 0
```

---

## Constants

### File Patterns

```python
MARKDOWN_EXTENSION = ".md"
TEMPLATE_FOLDER = "templates"
ARCHIVE_FOLDER = "archive"
BACKUP_FOLDER = "backups"
```

### API Endpoints

```python
OLLAMA_GENERATE_URL = "{base_url}/api/generate"
OLLAMA_TAGS_URL = "{base_url}/api/tags"
```

### Cache Settings

```python
CACHE_FILE = "ai_cache.json"
CACHE_VERSION = "1.0"
MAX_CACHE_SIZE = 10000  # entries
```

---

## Performance Characteristics

### Time Complexity

| Operation | Complexity | Notes |
|-----------|-----------|-------|
| `get_content_hash()` | O(n) | n = content length |
| `cache lookup` | O(1) | Dict lookup |
| `process_vault()` | O(m * k) | m = files, k = AI call time |
| `create_wikilinks()` | O(n * p) | n = content, p = notes |

### Space Complexity

| Component | Space | Notes |
|-----------|-------|-------|
| AI Cache | ~10KB/entry | JSON storage |
| Analytics | ~5KB/run | Cumulative |
| Dashboard | ~1MB | In-memory |
| Model (qwen3:8b) | ~5GB RAM | During inference |
| Model (qwen2.5:3b) | ~2GB RAM | During inference |

---

## Version Compatibility

| Component | Minimum Version | Recommended |
|-----------|----------------|-------------|
| Python | 3.9 | 3.11+ |
| Ollama | 0.1.0 | Latest |
| pytest | 7.4.0 | 8.0+ |
| Rich | 12.0.0 | Latest |
| PyYAML | 6.0 | Latest |
| requests | 2.28.0 | Latest |

---

## Migration Guide

### From v1.0 to v1.5

**Breaking Changes:**
- Config structure updated
- New hybrid mode settings

**Migration Steps:**
```bash
# Backup old config
cp config.yaml config.yaml.v1.0.bak

# Update config with new fields
cat >> config.yaml << EOF
use_hybrid_models: false
EOF

# Clear old cache (format changed)
rm ai_cache.json
```

---

**Last Updated**: 2024-11-15
**API Version**: 1.5.0
**For More Details**: See [ARCHITECTURE.md](ARCHITECTURE.md)
