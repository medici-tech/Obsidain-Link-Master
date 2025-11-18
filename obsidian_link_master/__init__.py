"""Obsidian Link Master package."""

__version__ = "0.1.0"

from .configuration import DEFAULT_CONFIG, RuntimeConfig, load_runtime_config

__all__ = ["DEFAULT_CONFIG", "RuntimeConfig", "load_runtime_config", "__version__"]
