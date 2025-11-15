"""
Configuration and utility functions for Obsidian Auto-Linker

This module provides reusable utility functions to eliminate code duplication
across the codebase, particularly for config loading, Ollama checks, and file I/O.
"""

import os
import json
import yaml
import requests
from typing import Dict, Any, Optional
from pathlib import Path
from logger_config import get_logger

logger = get_logger(__name__)


def load_yaml_config(config_path: str = 'config.yaml', default: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Load YAML configuration file with error handling.

    Args:
        config_path: Path to YAML config file
        default: Default dict to return if file not found or invalid

    Returns:
        Dictionary containing configuration, or default/empty dict on error
    """
    if default is None:
        default = {}

    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
            if config is None:
                logger.warning(f"Config file {config_path} is empty, using defaults")
                return default
            return config
    except FileNotFoundError:
        logger.info(f"Config file {config_path} not found, using defaults")
        return default
    except yaml.YAMLError as e:
        logger.error(f"YAML error in {config_path}: {e}")
        return default
    except (IOError, OSError) as e:
        logger.error(f"Error reading {config_path}: {e}")
        return default


def check_ollama_connection(
    base_url: str = 'http://localhost:11434',
    timeout: int = 5,
    required_models: Optional[list] = None
) -> bool:
    """Check if Ollama is running and accessible.

    Args:
        base_url: Ollama API base URL
        timeout: Request timeout in seconds
        required_models: Optional list of required model names

    Returns:
        True if Ollama is accessible (and has required models), False otherwise
    """
    try:
        response = requests.get(f'{base_url}/api/tags', timeout=timeout)
        response.raise_for_status()

        if required_models:
            data = response.json()
            available_models = [model['name'] for model in data.get('models', [])]

            for required_model in required_models:
                if not any(required_model in model for model in available_models):
                    logger.error(f"Required model '{required_model}' not found in Ollama")
                    logger.info(f"Available models: {', '.join(available_models)}")
                    return False

        return True

    except requests.exceptions.ConnectionError:
        logger.error("Ollama not running. Start it with: ollama serve")
        return False
    except requests.exceptions.Timeout:
        logger.error(f"Ollama connection timed out after {timeout}s")
        return False
    except requests.exceptions.RequestException as e:
        logger.error(f"Error connecting to Ollama: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error checking Ollama: {e}")
        return False


def load_json_file(file_path: str, default: Optional[Any] = None) -> Any:
    """Load JSON file with error handling.

    Args:
        file_path: Path to JSON file
        default: Default value to return if file not found or invalid

    Returns:
        Parsed JSON data, or default value on error
    """
    if default is None:
        default = {}

    if not os.path.exists(file_path):
        logger.debug(f"JSON file {file_path} not found, returning default")
        return default

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if data is None:
                logger.warning(f"JSON file {file_path} is empty")
                return default
            return data
    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error in {file_path}: {e}")
        return default
    except (IOError, OSError) as e:
        logger.error(f"Error reading {file_path}: {e}")
        return default


def save_json_file(file_path: str, data: Any, indent: int = 2, create_backup: bool = False) -> bool:
    """Save data to JSON file with error handling.

    Args:
        file_path: Path to JSON file
        data: Data to save (must be JSON serializable)
        indent: JSON indentation level
        create_backup: If True, create backup of existing file

    Returns:
        True if save succeeded, False otherwise
    """
    try:
        # Create backup if requested and file exists
        if create_backup and os.path.exists(file_path):
            backup_path = f"{file_path}.backup"
            try:
                import shutil
                shutil.copy2(file_path, backup_path)
                logger.debug(f"Created backup: {backup_path}")
            except Exception as e:
                logger.warning(f"Could not create backup: {e}")

        # Ensure directory exists
        directory = os.path.dirname(file_path)
        if directory:
            os.makedirs(directory, exist_ok=True)

        # Write JSON file
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=indent)

        logger.debug(f"Saved JSON to {file_path}")
        return True

    except (TypeError, ValueError) as e:
        logger.error(f"Data is not JSON serializable: {e}")
        return False
    except (IOError, OSError) as e:
        logger.error(f"Error writing {file_path}: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error saving JSON: {e}")
        return False


def ensure_directory_exists(directory: str, create: bool = True) -> bool:
    """Ensure directory exists, optionally creating it.

    Args:
        directory: Path to directory
        create: If True, create directory if it doesn't exist

    Returns:
        True if directory exists or was created, False otherwise
    """
    try:
        if os.path.exists(directory):
            if not os.path.isdir(directory):
                logger.error(f"{directory} exists but is not a directory")
                return False
            return True

        if create:
            os.makedirs(directory, exist_ok=True)
            logger.debug(f"Created directory: {directory}")
            return True
        else:
            logger.warning(f"Directory does not exist: {directory}")
            return False

    except (IOError, OSError) as e:
        logger.error(f"Error with directory {directory}: {e}")
        return False


def get_file_size_kb(file_path: str) -> float:
    """Get file size in kilobytes.

    Args:
        file_path: Path to file

    Returns:
        File size in KB, or 0.0 if file doesn't exist or error occurs
    """
    try:
        size_bytes = os.path.getsize(file_path)
        return size_bytes / 1024
    except (FileNotFoundError, OSError):
        return 0.0


def get_file_size_category(size_kb: float) -> str:
    """Categorize file size into small/medium/large.

    Args:
        size_kb: File size in kilobytes

    Returns:
        Category string: 'small', 'medium', or 'large'
    """
    if size_kb < 10:  # < 10 KB
        return 'small'
    elif size_kb < 100:  # 10-100 KB
        return 'medium'
    else:  # > 100 KB
        return 'large'


def validate_vault_path(vault_path: str, must_exist: bool = True, allow_symlinks: bool = True) -> bool:
    """Validate Obsidian vault path with security checks.

    Args:
        vault_path: Path to Obsidian vault
        must_exist: If True, path must exist
        allow_symlinks: If True, allow symlinked directories

    Returns:
        True if path is valid, False otherwise

    Security Checks:
        - Path is not empty
        - Not a system/sensitive directory
        - No null bytes in path
        - Resolves to absolute path
        - Is a directory (if must_exist=True)
        - Optionally validates symlinks
    """
    if not vault_path:
        logger.error("Vault path is empty")
        return False

    # Security: Check for null bytes (can bypass some checks)
    if '\x00' in vault_path:
        logger.error("Vault path contains null bytes - potential security issue")
        return False

    # Expand user home directory
    expanded_path = os.path.expanduser(vault_path)

    # Resolve to absolute path
    try:
        resolved_path = os.path.abspath(expanded_path)
    except (ValueError, OSError) as e:
        logger.error(f"Could not resolve vault path: {e}")
        return False

    # Security: Block system/sensitive directories
    sensitive_dirs = [
        '/etc', '/sys', '/proc', '/dev', '/boot',
        '/bin', '/sbin', '/usr/bin', '/usr/sbin',
        'C:\\Windows', 'C:\\Program Files', 'C:\\Program Files (x86)',
        '/System', '/Library',  # macOS system directories
    ]

    for sensitive_dir in sensitive_dirs:
        if resolved_path.lower().startswith(sensitive_dir.lower()):
            logger.error(f"Vault path cannot be in system directory: {resolved_path}")
            return False

    # Security: Block root directory
    if resolved_path in ['/', 'C:\\', 'C:/']:
        logger.error("Vault path cannot be root directory")
        return False

    # Check if path exists (if required)
    if must_exist:
        if not os.path.exists(resolved_path):
            logger.error(f"Vault path does not exist: {resolved_path}")
            return False

        # Verify it's a directory
        if not os.path.isdir(resolved_path):
            logger.error(f"Vault path is not a directory: {resolved_path}")
            return False

        # Security: Check for symlinks if not allowed
        if not allow_symlinks and os.path.islink(expanded_path):
            logger.error(f"Vault path is a symlink (not allowed): {expanded_path}")
            return False

        # Security: Verify we have read permissions
        if not os.access(resolved_path, os.R_OK):
            logger.error(f"Vault path is not readable: {resolved_path}")
            return False

    logger.debug(f"Vault path validated: {resolved_path}")
    return True


def get_config_value(config: Dict[str, Any], key: str, default: Any = None) -> Any:
    """Safely get configuration value with default.

    Args:
        config: Configuration dictionary
        key: Configuration key
        default: Default value if key not found

    Returns:
        Configuration value or default
    """
    value = config.get(key, default)
    if value is None and default is not None:
        logger.debug(f"Config key '{key}' not found, using default: {default}")
        return default
    return value


# Configuration path defaults
DEFAULT_CONFIG_PATH = 'config.yaml'
DEFAULT_PROGRESS_FILE = '.processing_progress.json'
DEFAULT_CACHE_FILE = '.ai_cache.json'
DEFAULT_ANALYTICS_FILE = 'processing_analytics.json'
DEFAULT_LOG_FILE = 'obsidian_linker.log'


if __name__ == "__main__":
    # Test utilities
    print("Testing config_utils.py...")

    # Test YAML loading
    test_config = load_yaml_config('config.yaml')
    print(f"✓ Config loaded: {len(test_config)} keys")

    # Test Ollama check
    ollama_ok = check_ollama_connection()
    print(f"✓ Ollama status: {'running' if ollama_ok else 'not running'}")

    # Test JSON operations
    test_data = {"test": "data", "number": 42}
    save_json_file('test.json', test_data)
    loaded_data = load_json_file('test.json')
    assert loaded_data == test_data, "JSON save/load failed"
    print("✓ JSON operations work")

    # Cleanup
    if os.path.exists('test.json'):
        os.remove('test.json')

    print("\nAll tests passed!")
