"""Configuration helpers for Obsidian Link Master.

This module centralizes default settings, type-safe runtime configuration,
and resilient loading so callers do not need to duplicate vault resolution or
provider selection logic.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict

from config_utils import ensure_directory_exists, load_yaml_config, validate_vault_path
from logger_config import get_logger

__all__ = ["DEFAULT_CONFIG", "RuntimeConfig", "load_runtime_config"]

logger = get_logger(__name__)

DEFAULT_CONFIG: Dict[str, Any] = {
    "vault_path": str(Path("/Users/medici/Documents/MediciVault")),
    "backup_folder": "_backups",
    "dry_run": True,
    "fast_dry_run": False,
    "force_reprocess": False,
    "max_backups": 5,
    "max_siblings": 5,
    "batch_size": 1,
    "max_retries": 3,
    "parallel_processing_enabled": False,
    "parallel_workers": 1,
    "file_ordering": "recent",
    "resume_enabled": True,
    "cache_enabled": True,
    "analytics_enabled": True,
    "generate_report": False,
    "interactive_mode": True,
    "incremental_processing": True,
    "incremental": True,
    "max_cache_size_mb": 1000,
    "max_cache_entries": 10000,
    "incremental_tracker_file": ".incremental_tracker.json",
    "confidence_threshold": 0.8,
    "enable_review_queue": True,
    "review_queue_path": "reviews/",
    "dry_run_limit": 10,
    "dry_run_interactive": True,
    "ollama_base_url": "http://localhost:11434",
    "ollama_model": "Qwen3-Embedding-8B:Q8_0",
    "ollama_timeout": 300,
    "ollama_max_retries": 5,
    "ollama_temperature": 0.1,
    "ollama_max_tokens": 1024,
    "ai_provider": "ollama",
    "claude_model": "claude-sonnet-4-5-20250929",
    "claude_max_tokens": 2048,
    "claude_temperature": 0.1,
    "claude_timeout": 60,
}


@dataclass
class RuntimeConfig:
    """Normalized runtime configuration loaded from disk and environment."""

    vault_path: str
    backup_folder: str
    dry_run: bool
    fast_dry_run: bool
    force_reprocess: bool
    max_backups: int
    max_siblings: int
    batch_size: int
    max_retries: int
    parallel_processing_enabled: bool
    parallel_workers: int
    file_ordering: str
    resume_enabled: bool
    cache_enabled: bool
    analytics_enabled: bool
    generate_report: bool
    interactive_mode: bool
    incremental_processing: bool
    incremental: bool
    max_cache_size_mb: int
    max_cache_entries: int
    incremental_tracker_file: str
    confidence_threshold: float
    enable_review_queue: bool
    review_queue_path: str
    dry_run_limit: int
    dry_run_interactive: bool
    ollama_base_url: str
    ollama_model: str
    ollama_timeout: int
    ollama_max_retries: int
    ollama_temperature: float
    ollama_max_tokens: int
    ai_provider: str
    claude_api_key: str
    claude_model: str
    claude_max_tokens: int
    claude_temperature: float
    claude_timeout: int


def load_runtime_config(config_path: str = "config.yaml") -> RuntimeConfig:
    """Load configuration from disk with sane defaults and validation."""

    raw_config: Dict[str, Any] = {**DEFAULT_CONFIG, **load_yaml_config(config_path, default={})}

    vault_path = os.environ.get("OBSIDIAN_VAULT_PATH") or raw_config.get("vault_path")
    if not vault_path:
        vault_path = DEFAULT_CONFIG["vault_path"]

    if not validate_vault_path(vault_path, must_exist=False):
        fallback = DEFAULT_CONFIG["vault_path"]
        logger.warning(
            "Invalid vault path '%s'. Falling back to %s. Set OBSIDIAN_VAULT_PATH or update %s to override.",
            vault_path,
            fallback,
            config_path,
        )
        vault_path = fallback

    ensure_directory_exists(vault_path, create=True)
    backup_folder = os.path.join(vault_path, raw_config.get("backup_folder", DEFAULT_CONFIG["backup_folder"]))

    return RuntimeConfig(
        vault_path=vault_path,
        backup_folder=backup_folder,
        dry_run=bool(raw_config["dry_run"]),
        fast_dry_run=bool(raw_config["fast_dry_run"]),
        force_reprocess=bool(raw_config["force_reprocess"]),
        max_backups=int(raw_config["max_backups"]),
        max_siblings=int(raw_config["max_siblings"]),
        batch_size=int(raw_config["batch_size"]),
        max_retries=int(raw_config["max_retries"]),
        parallel_processing_enabled=bool(raw_config["parallel_processing_enabled"]),
        parallel_workers=int(raw_config["parallel_workers"]),
        file_ordering=str(raw_config["file_ordering"]),
        resume_enabled=bool(raw_config["resume_enabled"]),
        cache_enabled=bool(raw_config["cache_enabled"]),
        analytics_enabled=bool(raw_config["analytics_enabled"]),
        generate_report=bool(raw_config.get("generate_report", DEFAULT_CONFIG["generate_report"])),
        interactive_mode=bool(raw_config["interactive_mode"]),
        incremental_processing=bool(raw_config["incremental_processing"]),
        incremental=bool(raw_config["incremental"]),
        max_cache_size_mb=int(raw_config["max_cache_size_mb"]),
        max_cache_entries=int(raw_config["max_cache_entries"]),
        incremental_tracker_file=str(raw_config["incremental_tracker_file"]),
        confidence_threshold=float(raw_config["confidence_threshold"]),
        enable_review_queue=bool(raw_config["enable_review_queue"]),
        review_queue_path=str(raw_config["review_queue_path"]),
        dry_run_limit=int(raw_config["dry_run_limit"]),
        dry_run_interactive=bool(raw_config["dry_run_interactive"]),
        ollama_base_url=str(raw_config["ollama_base_url"]),
        ollama_model=str(raw_config["ollama_model"]),
        ollama_timeout=int(raw_config["ollama_timeout"]),
        ollama_max_retries=int(raw_config["ollama_max_retries"]),
        ollama_temperature=float(raw_config["ollama_temperature"]),
        ollama_max_tokens=int(raw_config["ollama_max_tokens"]),
        ai_provider=str(raw_config["ai_provider"]).lower(),
        claude_api_key=raw_config.get("claude_api_key") or os.environ.get("ANTHROPIC_API_KEY", ""),
        claude_model=str(raw_config["claude_model"]),
        claude_max_tokens=int(raw_config["claude_max_tokens"]),
        claude_temperature=float(raw_config["claude_temperature"]),
        claude_timeout=int(raw_config["claude_timeout"]),
    )
