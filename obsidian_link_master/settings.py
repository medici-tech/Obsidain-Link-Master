"""Centralized runtime settings for Obsidian Link Master.

This module loads configuration once and exposes derived flags so other
modules don't rely on ad-hoc globals or undefined names.
"""
from __future__ import annotations

import os

from logger_config import get_logger
from obsidian_link_master.configuration import load_runtime_config

LOGGER = get_logger(__name__)
CONFIG_PATH = os.environ.get("OBSIDIAN_LINK_MASTER_CONFIG", "config.yaml")

# Load the normalized configuration once so callers can import it safely.
runtime_config = load_runtime_config(CONFIG_PATH)

# Derived parallel-processing flags
REQUESTED_PARALLEL_WORKERS = max(1, runtime_config.parallel_workers)
PARALLEL_MODE_ACTIVE = runtime_config.parallel_processing_enabled and REQUESTED_PARALLEL_WORKERS > 1
PARALLEL_EFFECTIVE_WORKERS = REQUESTED_PARALLEL_WORKERS if runtime_config.parallel_processing_enabled else 1

if not runtime_config.parallel_processing_enabled and REQUESTED_PARALLEL_WORKERS > 1:
    LOGGER.info(
        "parallel_processing_enabled is False; ignoring parallel_workers=%s and running sequentially",
        REQUESTED_PARALLEL_WORKERS,
    )
