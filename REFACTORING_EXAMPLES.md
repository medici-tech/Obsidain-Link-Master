# Refactoring Examples - Before & After
## Obsidian Auto-Linker Code Duplication Fixes

---

## Example 1: YAML Config Loading Utility

### BEFORE (3 locations with duplicated logic)

**obsidian_auto_linker_enhanced.py:31-39**
```python
# Load config
try:
    with open('config.yaml', 'r') as f:
        config = yaml.safe_load(f)
    if config is None:
        config = {}
        logger.warning("Config file is empty, using defaults")
except Exception as e:
    logger.error(f"Error loading config: {e}")
    config = {}
```

**run_with_dashboard.py:74-76**
```python
with open(config_file, 'r') as f:
    self.config = yaml.safe_load(f) or {}
```

**run_with_dashboard.py:127-134**
```python
try:
    with open('config.yaml', 'r') as f:
        existing_config = yaml.safe_load(f) or {}
except FileNotFoundError:
    existing_config = {}
except (yaml.YAMLError, IOError) as e:
    logger.warning(f"Error loading config: {e}")
    existing_config = {}
```

### AFTER (Single utility function)

**config_utils.py**
```python
import yaml
import os
from typing import Dict, Any, Optional

def load_yaml_config(
    filepath: str,
    logger=None,
    default: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Load YAML configuration file with consistent error handling.

    Args:
        filepath: Path to YAML file
        logger: Optional logger instance for warnings/errors
        default: Default config dict if file doesn't exist or is invalid

    Returns:
        Loaded config dict or default/empty dict
    """
    if default is None:
        default = {}

    # Check if file exists
    if not os.path.exists(filepath):
        if logger:
            logger.warning(f"Config file not found: {filepath}, using defaults")
        return default

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f) or default

        if config and logger:
            logger.debug(f"Configuration loaded from {filepath}")

        return config

    except yaml.YAMLError as e:
        if logger:
            logger.error(f"YAML parse error in {filepath}: {e}")
        return default
    except IOError as e:
        if logger:
            logger.error(f"Error reading {filepath}: {e}")
        return default
    except Exception as e:
        if logger:
            logger.error(f"Unexpected error loading {filepath}: {e}")
        return default
```

**obsidian_auto_linker_enhanced.py**
```python
from config_utils import load_yaml_config

# Load config (single line!)
config = load_yaml_config('config.yaml', logger=logger)
```

**run_with_dashboard.py (load_config method)**
```python
def load_config(self) -> bool:
    from config_utils import load_yaml_config

    config_file = Path('config.yaml')
    self.config = load_yaml_config(str(config_file), logger=logger)

    if not self.config:
        logger.error("Config file is empty")
        return False

    # Validate...
```

**run_with_dashboard.py (interactive_setup method)**
```python
def interactive_setup(self) -> bool:
    from config_utils import load_yaml_config

    # Load existing config if available
    existing_config = load_yaml_config('config.yaml', logger=logger)

    # ... rest of setup code
```

**Benefits:**
- ✅ Eliminates 3 duplicate code blocks
- ✅ Consistent error handling across all locations
- ✅ Single place to update logging behavior
- ✅ Handles all edge cases uniformly
- ✅ Saves ~20 lines of code

---

## Example 2: Ollama Connection Check Utility

### BEFORE (2 locations with duplicate logic)

**run.py:265-286**
```python
def check_ollama(self):
    """Check if Ollama is running"""
    try:
        import requests
        response = requests.get('http://localhost:11434/api/tags', timeout=5)
        if response.status_code == 200:
            models = response.json().get('models', [])
            if models:
                print(f"✅ Ollama running with {len(models)} models")
                return True
            else:
                print("❌ Ollama running but no models loaded")
                return False
        else:
            print("❌ Ollama not responding")
            return False
    except (requests.exceptions.RequestException, ConnectionError) as e:
        print(f"❌ Ollama not running: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error checking Ollama: {e}")
        return False
```

**run_with_dashboard.py:98-118**
```python
def check_ollama(self) -> bool:
    """Check if Ollama is running"""
    try:
        import requests
        response = requests.get('http://localhost:11434/api/tags', timeout=5)
        if response.status_code == 200:
            models = response.json().get('models', [])
            if models:
                logger.info(f"Ollama is running with {len(models)} models")
                return True
            else:
                logger.error("Ollama is running but no models are loaded")
                return False
        else:
            logger.error("Ollama is not responding properly")
            return False
    except Exception as e:
        logger.error(f"Ollama connection failed: {e}")
        logger.info("Please start Ollama: ollama serve")
        return False
```

### AFTER (Single utility function)

**config_utils.py**
```python
import requests
from typing import Tuple

def check_ollama_connection(
    base_url: str = "http://localhost:11434",
    timeout: int = 5,
    logger=None
) -> Tuple[bool, int, str]:
    """
    Check if Ollama server is running and has models loaded.

    Args:
        base_url: Ollama server URL
        timeout: Request timeout in seconds
        logger: Optional logger instance

    Returns:
        Tuple of (is_available: bool, model_count: int, message: str)
        Examples:
            (True, 3, "Ollama ready with 3 models")
            (False, 0, "Ollama not running: ConnectionError")
    """
    try:
        response = requests.get(f'{base_url}/api/tags', timeout=timeout)

        if response.status_code != 200:
            return (False, 0, "Ollama not responding properly")

        models = response.json().get('models', [])

        if not models:
            return (False, 0, "Ollama running but no models loaded")

        return (True, len(models), f"Ollama ready with {len(models)} models")

    except requests.exceptions.Timeout:
        msg = f"Ollama connection timeout ({timeout}s)"
        return (False, 0, msg)
    except requests.exceptions.ConnectionError as e:
        return (False, 0, f"Ollama not running: {e}")
    except requests.exceptions.RequestException as e:
        return (False, 0, f"Ollama connection failed: {e}")
    except Exception as e:
        return (False, 0, f"Unexpected error checking Ollama: {e}")
```

**run.py**
```python
from config_utils import check_ollama_connection

def check_ollama(self):
    """Check if Ollama is running"""
    is_available, model_count, message = check_ollama_connection(
        logger=None  # Using print fallback
    )

    # Log with emoji based on status
    if is_available:
        print(f"✅ {message}")
    else:
        print(f"❌ {message}")

    return is_available
```

**run_with_dashboard.py**
```python
from config_utils import check_ollama_connection

def check_ollama(self) -> bool:
    """Check if Ollama is running"""
    is_available, model_count, message = check_ollama_connection(logger=logger)

    if is_available:
        logger.info(message)
    else:
        logger.error(message)
        if not is_available and "not running" in message:
            logger.info("Please start Ollama: ollama serve")

    return is_available
```

**Benefits:**
- ✅ Single source of truth for Ollama checks
- ✅ Consistent return values (tuple unpacking)
- ✅ Flexible logging (logger or print)
- ✅ Better error classification
- ✅ Saves ~30 lines of duplicated code

---

## Example 3: JSON File Loading Utility

### BEFORE (3 locations with similar patterns)

**obsidian_auto_linker_enhanced.py:225-240 (load_progress)**
```python
def load_progress() -> None:
    if not RESUME_ENABLED:
        return

    progress_file = config.get('progress_file', '.processing_progress.json')
    if os.path.exists(progress_file):
        try:
            with open(progress_file, 'r') as f:
                data = json.load(f)
                if data and isinstance(data, dict):
                    progress_data['processed_files'] = set(data.get('processed_files', []))
                    progress_data['failed_files'] = set(data.get('failed_files', []))
                    progress_data['current_batch'] = data.get('current_batch', 0)
                    logger.info(f"📂 Loaded progress: {len(progress_data['processed_files'])} files")
                else:
                    progress_data['processed_files'] = set()
                    progress_data['failed_files'] = set()
                    progress_data['current_batch'] = 0
        except (json.JSONDecodeError, ValueError):
            progress_data['processed_files'] = set()
            progress_data['failed_files'] = set()
            progress_data['current_batch'] = 0
        except Exception as e:
            logger.warning(f"⚠️  Could not load progress file: {e}")
```

**obsidian_auto_linker_enhanced.py:268-283 (load_cache)**
```python
def load_cache() -> None:
    if not CACHE_ENABLED:
        return

    cache_file = config.get('cache_file', '.ai_cache.json')
    if os.path.exists(cache_file):
        try:
            with open(cache_file, 'r') as f:
                global ai_cache
                data = json.load(f)
                if data and isinstance(data, dict):
                    ai_cache = data
                else:
                    ai_cache = {}
        except (json.JSONDecodeError, ValueError):
            ai_cache = {}
        except Exception as e:
            logger.warning(f"⚠️  Could not load cache: {e}")
```

**run.py:349-366 (show_previous_results)**
```python
def show_previous_results(self):
    try:
        progress_file = '.processing_progress.json'
        if os.path.exists(progress_file):
            with open(progress_file, 'r') as f:
                data = json.load(f)
                if data and isinstance(data, dict):
                    processed = len(data.get('processed_files', []))
                    failed = len(data.get('failed_files', []))
                    last_update = data.get('last_update', 'Unknown')

                    print("\n📊 PREVIOUS RUN RESULTS")
                    print("="*40)
                    print(f"✅ Files Processed: {processed}")
                    print(f"❌ Files Failed: {failed}")
                    print(f"📅 Last Update: {last_update}")
                    if processed > 0:
                        print(f"📈 Success Rate: {(processed/(processed+failed)*100):.1f}%")
                    print("="*40)
                    return True
    except Exception as e:
        print(f"⚠️  Could not load previous results: {e}")
    return False
```

### AFTER (Single utility function)

**config_utils.py**
```python
import json
import os
from typing import Any, Optional

def load_json_file(
    filepath: str,
    default: Optional[Any] = None,
    logger=None,
    error_message: str = None
) -> Any:
    """
    Load JSON file with consistent error handling.

    Args:
        filepath: Path to JSON file
        default: Default value if file doesn't exist or is invalid
        logger: Optional logger instance
        error_message: Custom error message prefix

    Returns:
        Loaded data or default value
    """
    if default is None:
        default = {}

    if not os.path.exists(filepath):
        if logger:
            logger.debug(f"File not found: {filepath}")
        return default

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)

            if data and isinstance(data, dict):
                return data

            return default

    except (json.JSONDecodeError, ValueError) as e:
        if logger:
            prefix = error_message or "Invalid JSON in"
            logger.warning(f"{prefix} {filepath}: {e}")
        return default
    except IOError as e:
        if logger:
            prefix = error_message or "Error reading"
            logger.warning(f"{prefix} {filepath}: {e}")
        return default
    except Exception as e:
        if logger:
            prefix = error_message or "Error loading"
            logger.warning(f"{prefix} {filepath}: {e}")
        return default


def save_json_file(
    filepath: str,
    data: Any,
    logger=None,
    error_message: str = None,
    indent: int = 2
) -> bool:
    """
    Save data to JSON file with consistent error handling.

    Args:
        filepath: Path to JSON file
        data: Data to save
        logger: Optional logger instance
        error_message: Custom error message prefix
        indent: JSON indentation level

    Returns:
        True if successful, False otherwise
    """
    try:
        # Create parent directories if needed
        os.makedirs(os.path.dirname(filepath) or '.', exist_ok=True)

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=indent, default=str)

        if logger:
            logger.debug(f"Saved to {filepath}")

        return True

    except IOError as e:
        if logger:
            prefix = error_message or "Error writing"
            logger.warning(f"{prefix} {filepath}: {e}")
        return False
    except Exception as e:
        if logger:
            prefix = error_message or "Error saving"
            logger.warning(f"{prefix} {filepath}: {e}")
        return False
```

**obsidian_auto_linker_enhanced.py (refactored)**
```python
from config_utils import load_json_file, save_json_file

def load_progress() -> None:
    if not RESUME_ENABLED:
        return

    progress_file = PROGRESS_FILE  # Should be loaded from FilePathConfig
    data = load_json_file(progress_file, logger=logger, error_message="Could not load progress")

    if data:
        progress_data['processed_files'] = set(data.get('processed_files', []))
        progress_data['failed_files'] = set(data.get('failed_files', []))
        progress_data['current_batch'] = data.get('current_batch', 0)
        logger.info(f"📂 Loaded progress: {len(progress_data['processed_files'])} files")
    else:
        # Use defaults
        progress_data['processed_files'] = set()
        progress_data['failed_files'] = set()
        progress_data['current_batch'] = 0


def load_cache() -> None:
    if not CACHE_ENABLED:
        return

    global ai_cache
    cache_file = CACHE_FILE  # Should be loaded from FilePathConfig
    ai_cache = load_json_file(cache_file, default={}, logger=logger, error_message="Could not load cache")

    if ai_cache:
        logger.info(f"💾 Loaded cache: {len(ai_cache)} cached responses")


def save_progress() -> None:
    if not RESUME_ENABLED:
        return

    progress_file = PROGRESS_FILE
    data = {
        'processed_files': list(progress_data['processed_files']),
        'failed_files': list(progress_data['failed_files']),
        'current_batch': progress_data['current_batch'],
        'last_update': datetime.now().isoformat()
    }
    save_json_file(progress_file, data, logger=logger, error_message="Could not save progress")


def save_cache() -> None:
    if not CACHE_ENABLED:
        return

    save_json_file(CACHE_FILE, ai_cache, logger=logger, error_message="Could not save cache")
```

**run.py (refactored)**
```python
from config_utils import load_json_file

def show_previous_results(self):
    progress_file = '.processing_progress.json'
    data = load_json_file(progress_file)

    if data:
        processed = len(data.get('processed_files', []))
        failed = len(data.get('failed_files', []))
        last_update = data.get('last_update', 'Unknown')

        print("\n📊 PREVIOUS RUN RESULTS")
        print("="*40)
        print(f"✅ Files Processed: {processed}")
        print(f"❌ Files Failed: {failed}")
        print(f"📅 Last Update: {last_update}")
        if processed > 0:
            print(f"📈 Success Rate: {(processed/(processed+failed)*100):.1f}%")
        print("="*40)
        return True

    return False
```

**Benefits:**
- ✅ Eliminates ~60 lines of duplicated code
- ✅ Consistent error handling across all JSON operations
- ✅ Centralized file I/O logic
- ✅ Default value handling built-in
- ✅ Saves time when adding new JSON file operations

---

## Example 4: Configuration Loading Pattern

### BEFORE (Scattered config.get() calls)

**obsidian_auto_linker_enhanced.py:41-64**
```python
VAULT_PATH = config.get('vault_path', '')
BACKUP_FOLDER = os.path.join(VAULT_PATH, config.get('backup_folder', '_backups'))
DRY_RUN = config.get('dry_run', True)
FAST_DRY_RUN = config.get('fast_dry_run', False)
MAX_BACKUPS = config.get('max_backups', 5)
MAX_SIBLINGS = config.get('max_siblings', 5)
BATCH_SIZE = config.get('batch_size', 1)
MAX_RETRIES = config.get('max_retries', 3)
PARALLEL_WORKERS = config.get('parallel_workers', 1)
FILE_ORDERING = config.get('file_ordering', 'recent')
RESUME_ENABLED = config.get('resume_enabled', True)
CACHE_ENABLED = config.get('cache_enabled', True)
INTERACTIVE_MODE = config.get('interactive_mode', True)
ANALYTICS_ENABLED = config.get('analytics_enabled', True)
OLLAMA_BASE_URL = config.get('ollama_base_url', 'http://localhost:11434')
OLLAMA_MODEL = config.get('ollama_model', 'qwen3:8b')
OLLAMA_TIMEOUT = config.get('ollama_timeout', 30)
OLLAMA_MAX_RETRIES = config.get('ollama_max_retries', 3)
OLLAMA_TEMPERATURE = config.get('ollama_temperature', 0.1)
OLLAMA_MAX_TOKENS = config.get('ollama_max_tokens', 400)
```

Plus scattered references like:
```python
progress_file = config.get('progress_file', '.processing_progress.json')
cache_file = config.get('cache_file', '.ai_cache.json')
analytics_file = config.get('analytics_file', 'processing_analytics.json')
```

### AFTER (Type-safe dataclasses)

**config_utils.py**
```python
from dataclasses import dataclass
from pathlib import Path

@dataclass
class OllamaConfig:
    base_url: str = "http://localhost:11434"
    model: str = "qwen3:8b"
    timeout: int = 30
    max_retries: int = 3
    temperature: float = 0.1
    max_tokens: int = 400

@dataclass
class ProcessingConfig:
    vault_path: str = ""
    dry_run: bool = True
    fast_dry_run: bool = False
    batch_size: int = 1
    max_retries: int = 3
    file_ordering: str = "recent"
    resume_enabled: bool = True
    cache_enabled: bool = True
    interactive_mode: bool = True
    analytics_enabled: bool = True
    backup_folder: str = "_backups"
    max_backups: int = 5
    max_siblings: int = 5
    parallel_workers: int = 1

@dataclass
class FilePathConfig:
    progress_file: str = ".processing_progress.json"
    cache_file: str = ".ai_cache.json"
    analytics_file: str = "processing_analytics.json"
    log_file: str = "obsidian_linker.log"

def load_config(config_file: str = "config.yaml") -> tuple[ProcessingConfig, OllamaConfig, FilePathConfig]:
    """Load all configuration from YAML file"""
    raw_config = load_yaml_config(config_file)

    # Extract config sections
    processing_dict = {
        k: v for k, v in raw_config.items()
        if k in ProcessingConfig.__dataclass_fields__
    }

    ollama_dict = {
        k.replace('ollama_', ''): v for k, v in raw_config.items()
        if k.startswith('ollama_')
    }

    file_path_dict = {
        k: v for k, v in raw_config.items()
        if k in FilePathConfig.__dataclass_fields__
    }

    return (
        ProcessingConfig(**processing_dict),
        OllamaConfig(**ollama_dict),
        FilePathConfig(**file_path_dict)
    )
```

**obsidian_auto_linker_enhanced.py (refactored)**
```python
from config_utils import load_config

# Load configuration once at module level
processing_cfg, ollama_cfg, file_cfg = load_config('config.yaml')

# Use typed attributes instead of config.get()
VAULT_PATH = processing_cfg.vault_path
BACKUP_FOLDER = os.path.join(VAULT_PATH, processing_cfg.backup_folder)
DRY_RUN = processing_cfg.dry_run
FAST_DRY_RUN = processing_cfg.fast_dry_run
MAX_BACKUPS = processing_cfg.max_backups
MAX_SIBLINGS = processing_cfg.max_siblings
BATCH_SIZE = processing_cfg.batch_size
MAX_RETRIES = processing_cfg.max_retries
PARALLEL_WORKERS = processing_cfg.parallel_workers
FILE_ORDERING = processing_cfg.file_ordering
RESUME_ENABLED = processing_cfg.resume_enabled
CACHE_ENABLED = processing_cfg.cache_enabled
INTERACTIVE_MODE = processing_cfg.interactive_mode
ANALYTICS_ENABLED = processing_cfg.analytics_enabled

OLLAMA_BASE_URL = ollama_cfg.base_url
OLLAMA_MODEL = ollama_cfg.model
OLLAMA_TIMEOUT = ollama_cfg.timeout
OLLAMA_MAX_RETRIES = ollama_cfg.max_retries
OLLAMA_TEMPERATURE = ollama_cfg.temperature
OLLAMA_MAX_TOKENS = ollama_cfg.max_tokens

PROGRESS_FILE = file_cfg.progress_file
CACHE_FILE = file_cfg.cache_file
ANALYTICS_FILE = file_cfg.analytics_file
LOG_FILE = file_cfg.log_file
```

**Benefits:**
- ✅ Type hints for IDE autocomplete
- ✅ Single source of truth for defaults
- ✅ No more config.get() scattered everywhere
- ✅ Easy to add validation in dataclasses
- ✅ Better IDE support and refactoring

---

## Implementation Checklist

### Step 1: Create config_utils.py
- [ ] Add `load_yaml_config()` function
- [ ] Add `check_ollama_connection()` function
- [ ] Add `load_json_file()` function
- [ ] Add `save_json_file()` function
- [ ] Add configuration dataclasses
- [ ] Add `load_config()` function
- [ ] Test with all existing code paths

### Step 2: Update obsidian_auto_linker_enhanced.py
- [ ] Import configuration dataclasses
- [ ] Load config using new load_config()
- [ ] Replace config.get() calls with cfg attributes
- [ ] Update load_progress() to use load_json_file()
- [ ] Update load_cache() to use load_json_file()
- [ ] Update save_progress() to use save_json_file()
- [ ] Update save_cache() to use save_json_file()
- [ ] Update generate_analytics_report() to use save_json_file()
- [ ] Replace all config.get() calls with constants

### Step 3: Update run.py
- [ ] Import check_ollama_connection()
- [ ] Replace check_ollama() method with utility
- [ ] Update show_previous_results() to use load_json_file()
- [ ] Keep print-based UI for compatibility

### Step 4: Update run_with_dashboard.py
- [ ] Import config utilities
- [ ] Replace load_config() with load_yaml_config()
- [ ] Replace check_ollama() with utility
- [ ] Update interactive_setup() to use utilities

### Step 5: Testing
- [ ] Run Fast Dry Run mode
- [ ] Run Full Dry Run mode
- [ ] Verify all interactive menus work
- [ ] Check Ollama detection
- [ ] Verify config loading from YAML
- [ ] Test with missing config file
- [ ] Test with corrupted JSON files

---

## Expected Results

### Code Reduction
- **Before**: ~2,076 total lines
- **After**: ~1,850-1,900 total lines
- **Reduction**: 150-200+ lines (7-10%)

### Quality Improvements
- **Duplication**: 80-90% eliminated
- **Maintainability**: Significantly improved
- **Type Safety**: Dataclasses provide IDE support
- **Error Handling**: Consistent across codebase

### Development Speed
- **Adding new features**: 20-30% faster
- **Debugging**: Centralized logic = easier fixes
- **Changes**: Single place to update instead of multiple

---

**End of Refactoring Examples**
