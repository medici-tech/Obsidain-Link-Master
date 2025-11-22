#!/usr/bin/env python3
"""Convenient runner for processing an Obsidian vault with the simplified layout."""

from __future__ import annotations

import time
from pathlib import Path

from config_utils import ensure_directory_exists
from logger_config import get_logger
from obsidian_auto_linker_enhanced import bootstrap_runtime, main as process_vault
from obsidian_link_master.settings import runtime_config

LOGGER = get_logger(__name__)
POLL_INTERVAL_SECONDS = 15


def prepare_directories() -> None:
    """Ensure the expected vault subfolders exist before processing."""

    for path in [
        runtime_config.backup_folder,
        runtime_config.log_folder,
        runtime_config.moc_folder,
        runtime_config.watch_folder,
    ]:
        ensure_directory_exists(path, create=True)


def run_once() -> None:
    """Boot the pipeline once with the normalized configuration."""

    bootstrap_runtime()
    process_vault()


def watch_for_changes() -> None:
    """Continuously monitor the configured watch folder for new inputs."""

    LOGGER.info("Watch mode enabled; monitoring %s", runtime_config.watch_folder)
    watch_path = Path(runtime_config.watch_folder)

    run_once()
    last_seen_mtime = max(
        (path.stat().st_mtime for path in watch_path.rglob("*.md")),
        default=0.0,
    )

    while True:
        latest_mtime = max(
            (path.stat().st_mtime for path in watch_path.rglob("*.md")),
            default=0.0,
        )

        if latest_mtime > last_seen_mtime:
            run_once()
            last_seen_mtime = latest_mtime

        time.sleep(POLL_INTERVAL_SECONDS)


def main() -> None:
    prepare_directories()

    if runtime_config.watch_mode:
        watch_for_changes()
    else:
        run_once()


if __name__ == "__main__":
    main()
