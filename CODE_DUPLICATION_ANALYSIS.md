# Code Duplication Analysis Report
## Obsidian Auto-Linker Codebase

**Analysis Date**: 2025-11-14
**Files Analyzed**:
- obsidian_auto_linker_enhanced.py (1,109 lines)
- run.py (436 lines)
- run_with_dashboard.py (315 lines)
- logger_config.py (116 lines)

**Total Occurrences of config.get()**: 40 occurrences
**Total JSON load/dump operations**: 10 occurrences
**Total path validation checks**: 9 occurrences

---

## Top 10 Most Significant Code Duplication Issues

### 1. **YAML Configuration Loading Pattern** ⭐⭐⭐⭐⭐
**Severity**: CRITICAL | **Frequency**: 3 duplications | **Impact**: High

#### Locations:
- **obsidian_auto_linker_enhanced.py:31-39** (Module-level)
- **run_with_dashboard.py:74-76** (load_config method)
- **run_with_dashboard.py:127-134** (interactive_setup method)

#### Duplicated Code:
```python
# Pattern 1 (obsidian_auto_linker_enhanced.py)
try:
    with open('config.yaml', 'r') as f:
        config = yaml.safe_load(f)
    if config is None:
        config = {}
        logger.warning("Config file is empty, using defaults")
except Exception as e:
    logger.error(f"Error loading config: {e}")
    config = {}

# Pattern 2 (run_with_dashboard.py:74-76)
with open(config_file, 'r') as f:
    self.config = yaml.safe_load(f) or {}

# Pattern 3 (run_with_dashboard.py:127-134)
try:
    with open('config.yaml', 'r') as f:
        existing_config = yaml.safe_load(f) or {}
except FileNotFoundError:
    existing_config = {}
except (yaml.YAMLError, IOError) as e:
    logger.warning(f"Error loading config: {e}")
    existing_config = {}
```

#### Suggestion:
**Create a shared utility function** in a new module `config_utils.py`:
```python
def load_yaml_config(filepath: str, logger=None, default: dict = None) -> dict:
    """
    Load YAML configuration file with consistent error handling

    Args:
        filepath: Path to YAML file
        logger: Optional logger instance
        default: Default config dict if file doesn't exist

    Returns:
        Loaded config or default/empty dict
    """
    if default is None:
        default = {}

    try:
        with open(filepath, 'r') as f:
            config = yaml.safe_load(f) or default
        return config
    except FileNotFoundError:
        if logger:
            logger.warning(f"Config file not found: {filepath}")
        return default
    except (yaml.YAMLError, IOError) as e:
        if logger:
            logger.error(f"Error loading config {filepath}: {e}")
        return default
    except Exception as e:
        if logger:
            logger.error(f"Unexpected error loading config: {e}")
        return default
```

---

### 2. **Ollama Connection Check** ⭐⭐⭐⭐
**Severity**: HIGH | **Frequency**: 2 duplications | **Impact**: Medium

#### Locations:
- **run.py:265-286** (ObsidianAutoLinker.check_ollama)
- **run_with_dashboard.py:98-118** (EnhancedRunner.check_ollama)

#### Duplicated Code:
```python
# run.py version
def check_ollama(self):
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

# run_with_dashboard.py version (same logic, different output)
def check_ollama(self) -> bool:
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

#### Issue:
- Same API call logic, identical structure
- Only difference is print() vs logger
- Inconsistent error handling

#### Suggestion:
**Create a shared utility function** in `config_utils.py`:
```python
def check_ollama_connection(
    base_url: str = "http://localhost:11434",
    timeout: int = 5,
    logger=None
) -> tuple[bool, int, str]:
    """
    Check if Ollama server is running and has models loaded

    Returns:
        (is_available: bool, model_count: int, message: str)
    """
    try:
        import requests
        response = requests.get(f'{base_url}/api/tags', timeout=timeout)

        if response.status_code != 200:
            return (False, 0, "Ollama not responding properly")

        models = response.json().get('models', [])

        if not models:
            return (False, 0, "Ollama running but no models loaded")

        return (True, len(models), f"Ollama ready with {len(models)} models")

    except requests.exceptions.RequestException as e:
        return (False, 0, f"Ollama not running: {e}")
    except Exception as e:
        return (False, 0, f"Unexpected error: {e}")
```

Usage:
```python
is_available, count, message = check_ollama_connection(logger=logger)
if logger:
    log_func = logger.info if is_available else logger.error
    log_func(message)
```

---

### 3. **JSON File Loading Pattern** ⭐⭐⭐⭐
**Severity**: HIGH | **Frequency**: 3 duplications | **Impact**: Medium

#### Locations:
- **obsidian_auto_linker_enhanced.py:225-240** (load_progress)
- **obsidian_auto_linker_enhanced.py:268-283** (load_cache)
- **run.py:349-366** (show_previous_results)

#### Duplicated Code:
```python
# Pattern 1: load_progress (lines 225-240)
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
                # Reset to defaults
                progress_data['processed_files'] = set()
                progress_data['failed_files'] = set()
                progress_data['current_batch'] = 0
    except (json.JSONDecodeError, ValueError):
        progress_data['processed_files'] = set()
        progress_data['failed_files'] = set()
        progress_data['current_batch'] = 0
    except Exception as e:
        logger.warning(f"⚠️  Could not load progress file: {e}")

# Pattern 2: load_cache (lines 268-283)
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

# Pattern 3: show_previous_results (run.py:349-366)
progress_file = '.processing_progress.json'
if os.path.exists(progress_file):
    try:
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
```

#### Issue:
- Repeated try/except block for JSON loading
- Duplicate error handling logic
- Hardcoded file paths with defaults

#### Suggestion:
**Create a generic JSON file loader** in `config_utils.py`:
```python
def load_json_file(
    filepath: str,
    default: Any = None,
    logger=None,
    error_message: str = None
) -> Any:
    """
    Load JSON file with consistent error handling

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
            prefix = error_message or "Invalid JSON"
            logger.warning(f"{prefix} in {filepath}: {e}")
        return default
    except Exception as e:
        if logger:
            prefix = error_message or "Error loading"
            logger.warning(f"{prefix} {filepath}: {e}")
        return default
```

---

### 4. **Config Value Extraction with Defaults** ⭐⭐⭐⭐
**Severity**: HIGH | **Frequency**: 6+ duplications | **Impact**: High

#### Locations:
- **obsidian_auto_linker_enhanced.py:41-64** (Module-level, 24 extractions)
- **obsidian_auto_linker_enhanced.py:224, 250, 267, 295, 811** (5 more file path extractions)

#### Duplicated Code:
```python
# Multiple instances of:
VAULT_PATH = config.get('vault_path', '')
DRY_RUN = config.get('dry_run', True)
FAST_DRY_RUN = config.get('fast_dry_run', False)
# ... repeated 24 times with different keys and defaults

# File paths repeated:
progress_file = config.get('progress_file', '.processing_progress.json')  # Line 224
cache_file = config.get('cache_file', '.ai_cache.json')  # Line 267
analytics_file = config.get('analytics_file', 'processing_analytics.json')  # Line 811
# ... repeated 5 times
```

#### Issue:
- Scattered extraction across module
- Magic string defaults repeated
- No single source of truth for config schema
- Makes changing defaults difficult

#### Suggestion:
**Create a configuration schema/class** in `config_utils.py`:
```python
from dataclasses import dataclass
from typing import Dict, Any

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
    """Load all configuration from YAML file with proper schema"""
    raw_config = load_yaml_config(config_file)

    processing = ProcessingConfig(**{
        k: v for k, v in raw_config.items()
        if k in ProcessingConfig.__dataclass_fields__
    })

    ollama = OllamaConfig(**{
        k.replace('ollama_', ''): v for k, v in raw_config.items()
        if k.startswith('ollama_')
    })

    file_paths = FilePathConfig(**{
        k: v for k, v in raw_config.items()
        if k in FilePathConfig.__dataclass_fields__
    })

    return processing, ollama, file_paths
```

Usage:
```python
from config_utils import load_config

processing_cfg, ollama_cfg, file_cfg = load_config()

VAULT_PATH = processing_cfg.vault_path
DRY_RUN = processing_cfg.dry_run
OLLAMA_MODEL = ollama_cfg.model
PROGRESS_FILE = file_cfg.progress_file
```

---

### 5. **Interactive User Input Pattern (File Ordering, Mode, Batch)** ⭐⭐⭐⭐
**Severity**: MEDIUM-HIGH | **Frequency**: 3 duplications | **Impact**: Medium

#### Locations:
- **run.py:156-183** (get_file_ordering)
- **run.py:185-209** (get_processing_mode)
- **run.py:211-235** (get_batch_size)
- **run_with_dashboard.py:153-166** (File ordering)
- **run_with_dashboard.py:168-184** (Processing mode)
- **run_with_dashboard.py:186-198** (Batch size)

#### Duplicated Code:
```python
# run.py: get_file_ordering (156-183)
def get_file_ordering(self):
    print("📋 File Processing Order:")
    print("   1. Recent (newest first) - Recommended")
    print("   2. Size (largest first)")
    print("   3. Random")
    print("   4. Alphabetical")

    while True:
        try:
            choice = input("   Choose (1-4, default=1): ").strip()
        except EOFError:
            choice = "1"
            print("   Using default: 1")

        if not choice:
            return "recent"
        elif choice == "1":
            return "recent"
        elif choice == "2":
            return "size"
        elif choice == "3":
            return "random"
        elif choice == "4":
            return "alphabetical"
        else:
            print("   ❌ Invalid choice. Please enter 1-4")

# run_with_dashboard.py: Same logic but different UI (153-166)
console.print("\n[bold]📋 File Processing Order:[/bold]")
console.print("   1. Recent (newest first)")
console.print("   2. Size (largest first)")
console.print("   3. Random")
console.print("   4. Alphabetical")

try:
    order_choice = input("   Choose (1-4, default=1): ").strip()
except EOFError:
    order_choice = "1"

order_map = {'1': 'recent', '2': 'size', '3': 'random', '4': 'alphabetical'}
file_ordering = order_map.get(order_choice, 'recent')
```

#### Issue:
- Same menu structure in 6 different methods
- Inconsistent implementation (run.py uses loop, run_with_dashboard uses map)
- Mixed UI (print vs console)
- Hard to maintain and update

#### Suggestion:
**Create an interactive input utility** in `ui_utils.py`:
```python
def get_choice_from_menu(
    title: str,
    options: dict[str, str],  # {key: description}
    default_key: str = "1",
    use_rich: bool = False,
    logger=None
) -> str:
    """
    Generic menu choice handler

    Args:
        title: Menu title
        options: Dict of {choice_key: description}
        default_key: Default choice if empty input
        use_rich: Use rich console for formatting
        logger: Optional logger

    Returns:
        Selected option value or default
    """
    from rich.console import Console

    console = Console() if use_rich else None

    # Print menu
    if use_rich:
        console.print(f"\n[bold]{title}[/bold]")
        for key, desc in options.items():
            console.print(f"   {key}. {desc}")
    else:
        print(f"\n{title}")
        for key, desc in options.items():
            print(f"   {key}. {desc}")

    valid_keys = list(options.keys())

    while True:
        prompt = f"   Choose ({'/'.join(valid_keys)}, default={default_key}): "

        try:
            choice = input(prompt).strip() or default_key
        except EOFError:
            if logger:
                logger.info(f"Using default: {default_key}")
            return default_key

        if choice in valid_keys:
            return choice

        msg = f"   ❌ Invalid choice. Please enter {'/'.join(valid_keys)}"
        if use_rich:
            console.print(f"[red]{msg}[/red]")
        else:
            print(msg)

# Define menu configs as constants
FILE_ORDERING_MENU = {
    "1": "Recent (newest first)",
    "2": "Size (largest first)",
    "3": "Random",
    "4": "Alphabetical"
}

PROCESSING_MODE_MENU = {
    "1": "Fast Dry Run (no AI, quick test)",
    "2": "Full Dry Run (with AI, no file changes)",
    "3": "Live Run (creates _linked.md files)"
}

BATCH_SIZE_MENU = {
    "1": "Single file (recommended)",
    "2": "Small batch (5 files)",
    "3": "Medium batch (10 files)"
}

# Mapping for results
FILE_ORDERING_MAP = {'1': 'recent', '2': 'size', '3': 'random', '4': 'alphabetical'}
BATCH_SIZE_MAP = {'1': 1, '2': 5, '3': 10}
```

Usage:
```python
# In run.py
file_ordering = get_choice_from_menu("📋 File Processing Order:", FILE_ORDERING_MENU, use_rich=False)
result = FILE_ORDERING_MAP[file_ordering]

# In run_with_dashboard.py
file_ordering = get_choice_from_menu("📋 File Processing Order:", FILE_ORDERING_MENU, use_rich=True)
result = FILE_ORDERING_MAP[file_ordering]
```

---

### 6. **JSON Save Pattern** ⭐⭐⭐
**Severity**: MEDIUM | **Frequency**: 3 duplications | **Impact**: Medium

#### Locations:
- **obsidian_auto_linker_enhanced.py:252-258** (save_progress)
- **obsidian_auto_linker_enhanced.py:297-300** (save_cache)
- **obsidian_auto_linker_enhanced.py:812-813** (generate_analytics_report)

#### Duplicated Code:
```python
# Pattern 1: save_progress
try:
    with open(progress_file, 'w') as f:
        json.dump({
            'processed_files': list(progress_data['processed_files']),
            'failed_files': list(progress_data['failed_files']),
            'current_batch': progress_data['current_batch'],
            'last_update': datetime.now().isoformat()
        }, f, indent=2)
except Exception as e:
    logger.warning(f"⚠️  Could not save progress: {e}")

# Pattern 2: save_cache
try:
    with open(cache_file, 'w') as f:
        json.dump(ai_cache, f, indent=2)
except Exception as e:
    logger.warning(f"⚠️  Could not save cache: {e}")

# Pattern 3: generate_analytics_report
with open(analytics_file, 'w') as f:
    json.dump(analytics, f, indent=2, default=str)
```

#### Suggestion:
**Create a generic JSON save utility**:
```python
def save_json_file(
    filepath: str,
    data: Any,
    logger=None,
    error_message: str = None,
    indent: int = 2,
    default=None
) -> bool:
    """
    Save data to JSON file with consistent error handling

    Args:
        filepath: Path to JSON file
        data: Data to save
        logger: Optional logger instance
        error_message: Custom error message prefix
        indent: JSON indentation (None for compact)
        default: Custom serializer function (e.g., str for datetime)

    Returns:
        True if successful, False otherwise
    """
    try:
        os.makedirs(os.path.dirname(filepath) or '.', exist_ok=True)

        kwargs = {'indent': indent}
        if default:
            kwargs['default'] = default

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, **kwargs)

        return True

    except Exception as e:
        if logger:
            prefix = error_message or "Error saving"
            logger.warning(f"{prefix} {filepath}: {e}")
        return False
```

---

### 7. **File Path Construction from Config** ⭐⭐⭐
**Severity**: MEDIUM | **Frequency**: 6 occurrences | **Impact**: Medium

#### Locations:
- **obsidian_auto_linker_enhanced.py:224** - progress_file extraction
- **obsidian_auto_linker_enhanced.py:250** - progress_file extraction (again)
- **obsidian_auto_linker_enhanced.py:267** - cache_file extraction
- **obsidian_auto_linker_enhanced.py:295** - cache_file extraction (again)
- **obsidian_auto_linker_enhanced.py:811** - analytics_file extraction

#### Duplicated Code:
```python
# Repeated 6 times in different functions:
progress_file = config.get('progress_file', '.processing_progress.json')
cache_file = config.get('cache_file', '.ai_cache.json')
analytics_file = config.get('analytics_file', 'processing_analytics.json')
```

#### Suggestion:
**Use the FilePathConfig dataclass** (from issue #4) or create module-level constants:
```python
# At module level (after config loading)
file_cfg = FilePathConfig(...)
PROGRESS_FILE = file_cfg.progress_file
CACHE_FILE = file_cfg.cache_file
ANALYTICS_FILE = file_cfg.analytics_file

# Then use throughout:
def load_progress():
    if not RESUME_ENABLED:
        return

    if os.path.exists(PROGRESS_FILE):
        # ...
```

---

### 8. **Path Validation Pattern** ⭐⭐⭐
**Severity**: MEDIUM | **Frequency**: 3 duplications | **Impact**: Low-Medium

#### Locations:
- **run.py:75-77** (get_vault_path)
- **run_with_dashboard.py:149-151** (interactive_setup)
- **obsidian_auto_linker_enhanced.py:343** (get_all_notes)

#### Duplicated Code:
```python
# run.py style (lines 75-77)
if not os.path.exists(vault_path):
    print(f"❌ Path does not exist: {vault_path}")
    return None

# run_with_dashboard.py style (lines 149-151)
if not Path(vault_path).exists():
    console.print(f"[bold red]❌ Path does not exist: {vault_path}[/bold red]")
    return False

# Implicit check in obsidian_auto_linker_enhanced.py
if config.get('backup_folder', '_backups') in root:
    continue
```

#### Issue:
- Mixed use of os.path and pathlib.Path
- Different error messages
- Different return values (None vs False)

#### Suggestion:
**Create a path validation utility**:
```python
def validate_path(
    path: str,
    must_exist: bool = True,
    path_type: str = "directory",  # "directory", "file", or "any"
    logger=None,
    use_rich: bool = False
) -> bool:
    """
    Validate file/directory path with consistent error handling

    Args:
        path: Path to validate
        must_exist: Whether path must exist
        path_type: Type of path (directory, file, any)
        logger: Optional logger
        use_rich: Use rich console for output

    Returns:
        True if valid, False otherwise
    """
    from pathlib import Path

    try:
        path_obj = Path(path)

        if not must_exist:
            return True

        if not path_obj.exists():
            msg = f"❌ Path does not exist: {path}"
            _log_message(msg, logger, use_rich, level="error")
            return False

        if path_type == "directory" and not path_obj.is_dir():
            msg = f"❌ Not a directory: {path}"
            _log_message(msg, logger, use_rich, level="error")
            return False

        if path_type == "file" and not path_obj.is_file():
            msg = f"❌ Not a file: {path}"
            _log_message(msg, logger, use_rich, level="error")
            return False

        return True

    except Exception as e:
        msg = f"❌ Error validating path: {e}"
        _log_message(msg, logger, use_rich, level="error")
        return False
```

---

### 9. **Logger/Dashboard Handler Initialization** ⭐⭐⭐
**Severity**: MEDIUM | **Frequency**: 2 duplications | **Impact**: Low-Medium

#### Locations:
- **run_with_dashboard.py:40-45** (EnhancedRunner.__init__)
- **obsidian_auto_linker_enhanced.py:24-28** (Module level)

#### Duplicated Code:
```python
# run_with_dashboard.py pattern
from logger_config import setup_logging, get_logger, DashboardLogHandler
logger = setup_logging(log_level="INFO", enable_file_logging=True)
dashboard_handler = DashboardLogHandler(dashboard)
logger.addHandler(dashboard_handler)

# obsidian_auto_linker_enhanced.py pattern
from logger_config import get_logger, setup_logging
logger = get_logger(__name__)
```

#### Suggestion:
**Create a centralized logger initialization**:
```python
def initialize_logger(
    name: str = "obsidian_linker",
    log_level: str = "INFO",
    enable_file: bool = True,
    dashboard=None
) -> logging.Logger:
    """
    Initialize logger with optional dashboard handler

    Args:
        name: Logger name
        log_level: Logging level
        enable_file: Whether to log to file
        dashboard: Optional dashboard for metrics

    Returns:
        Configured logger instance
    """
    logger = setup_logging(log_level=log_level, enable_file_logging=enable_file)

    if dashboard:
        dashboard_handler = DashboardLogHandler(dashboard)
        logger.addHandler(dashboard_handler)

    return logger
```

---

### 10. **Progress Data Dictionary Initialization** ⭐⭐⭐
**Severity**: LOW-MEDIUM | **Frequency**: Multiple scattered | **Impact**: Low

#### Locations:
- **obsidian_auto_linker_enhanced.py:173-179** (progress_data dict)
- **obsidian_auto_linker_enhanced.py:157-170** (analytics dict)
- **obsidian_auto_linker_enhanced.py:901-908** (stats dict)
- **run.py:23-33** (resource_stats dict)

#### Duplicated Code:
```python
# Multiple data structures initialized separately with similar patterns
progress_data = {
    'processed_files': set(),
    'failed_files': set(),
    'current_batch': 0,
    'total_batches': 0,
    'last_update': None
}

analytics = {
    'start_time': None,
    'end_time': None,
    'total_files': 0,
    'processed_files': 0,
    'skipped_files': 0,
    'failed_files': 0,
    # ...
}

stats = {
    'processed': 0,
    'already_processed': 0,
    'failed': 0,
    'would_process': 0,
    'links_added': 0,
    'tags_added': 0
}
```

#### Suggestion:
**Create dataclasses for state tracking**:
```python
from dataclasses import dataclass, field
from datetime import datetime
from typing import Set

@dataclass
class ProgressData:
    processed_files: Set[str] = field(default_factory=set)
    failed_files: Set[str] = field(default_factory=set)
    current_batch: int = 0
    total_batches: int = 0
    last_update: Optional[datetime] = None

@dataclass
class AnalyticsData:
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    total_files: int = 0
    processed_files: int = 0
    skipped_files: int = 0
    failed_files: int = 0
    moc_distribution: Dict[str, int] = field(default_factory=dict)
    error_types: Dict[str, int] = field(default_factory=dict)
    retry_attempts: int = 0
    cache_hits: int = 0
    cache_misses: int = 0

@dataclass
class FileStats:
    processed: int = 0
    already_processed: int = 0
    failed: int = 0
    would_process: int = 0
    links_added: int = 0
    tags_added: int = 0
```

---

## Summary Table

| Issue | Severity | Frequency | Files Affected | Refactoring Effort | Priority |
|-------|----------|-----------|---------------|--------------------|----------|
| YAML Config Loading | CRITICAL | 3 | 2 | Low | 1 |
| Ollama Connection Check | HIGH | 2 | 2 | Low | 2 |
| JSON File Loading | HIGH | 3 | 2 | Low | 3 |
| Config Value Extraction | HIGH | 6+ | 1 | Medium | 4 |
| Interactive Menu Input | MEDIUM-HIGH | 6 | 2 | Medium | 5 |
| JSON Save Pattern | MEDIUM | 3 | 1 | Low | 6 |
| File Path Construction | MEDIUM | 6 | 1 | Low | 7 |
| Path Validation | MEDIUM | 3 | 3 | Low | 8 |
| Logger Initialization | MEDIUM | 2 | 2 | Low | 9 |
| Data Structure Init | LOW-MEDIUM | 4+ | 2 | Low | 10 |

---

## Refactoring Impact Estimate

### Quick Wins (Low Effort, High Impact)
1. **Create `config_utils.py`** with:
   - `load_yaml_config()` (consolidates 3 duplications)
   - `check_ollama_connection()` (consolidates 2 duplications)
   - `load_json_file()` (consolidates 3 duplications)
   - `save_json_file()` (consolidates 3 duplications)
   - Configuration dataclasses

**Estimated effort**: 2-3 hours
**Estimated lines of code eliminated**: 150+
**Files affected**: 3 (obsidian_auto_linker_enhanced.py, run.py, run_with_dashboard.py)

### Medium Effort (Medium Impact)
2. **Create `ui_utils.py`** with:
   - `get_choice_from_menu()` (consolidates 6 duplications)
   - Menu configuration constants

**Estimated effort**: 1-2 hours
**Estimated lines of code eliminated**: 80+
**Files affected**: 2 (run.py, run_with_dashboard.py)

### Follow-up Improvements
3. **Update `logger_config.py`** to include centralized logger initialization
4. **Convert mutable state** to dataclasses for better type safety

---

## Recommendations

### Immediate Actions (High Priority)
1. Create `/home/user/Obsidain-Link-Master/config_utils.py` with utility functions
2. Create `/home/user/Obsidain-Link-Master/ui_utils.py` for menu handling
3. Update module-level config loading in `obsidian_auto_linker_enhanced.py`

### Testing After Refactor
- Run all existing tests with Fast Dry Run mode
- Verify config loading from YAML
- Test Ollama connection checks
- Validate interactive menu responses

### Long-term Improvements
- Add type hints to all utility functions
- Create unit tests for utility functions
- Document configuration schema in README
- Consider creating a configuration validator class

---

## Code Examples for Refactoring

### Step 1: Create config_utils.py
See detailed implementations in issues #1-#4 above.

### Step 2: Update obsidian_auto_linker_enhanced.py

**Before** (Lines 31-64):
```python
try:
    with open('config.yaml', 'r') as f:
        config = yaml.safe_load(f)
    if config is None:
        config = {}
        logger.warning("Config file is empty, using defaults")
except Exception as e:
    logger.error(f"Error loading config: {e}")
    config = {}

VAULT_PATH = config.get('vault_path', '')
# ... 23 more config.get() calls ...
```

**After** (With utilities):
```python
from config_utils import load_config

processing_cfg, ollama_cfg, file_cfg = load_config('config.yaml')

VAULT_PATH = processing_cfg.vault_path
BACKUP_FOLDER = os.path.join(VAULT_PATH, processing_cfg.backup_folder)
DRY_RUN = processing_cfg.dry_run
# ... etc, all from dataclass attributes
```

---

**End of Analysis Report**

Generated: 2025-11-14
