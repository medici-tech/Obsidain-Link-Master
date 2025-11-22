#!/usr/bin/env python3
"""Project launcher that self-starts Ollama and loads required models.

Run this script to execute the Obsidian Auto-Linker without manually starting
Ollama. It will:
1. Load the project configuration to discover which models are required.
2. Check whether the Ollama service is reachable; if not, start it.
3. Pull any missing models before kicking off the main pipeline.
"""

import argparse
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import Iterable, List, Optional, Set

import requests

from config_utils import load_yaml_config
from logger_config import get_logger

LOGGER = get_logger("run")
DEFAULT_CONFIG = Path("config.yaml")
DEFAULT_BASE_URL = "http://localhost:11434"
POLL_INTERVAL = 2
READY_TIMEOUT = 90


def parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    """Parse launcher arguments."""
    parser = argparse.ArgumentParser(
        description="Run the Obsidian Auto-Linker with auto-started Ollama",
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=DEFAULT_CONFIG,
        help="Path to the YAML config file (default: config.yaml)",
    )
    parser.add_argument(
        "--skip-model-pulls",
        action="store_true",
        help="Skip pulling models if they are missing",
    )
    return parser.parse_args(argv)


def is_ollama_ready(base_url: str) -> bool:
    """Return True if Ollama responds to the tags endpoint."""
    try:
        response = requests.get(f"{base_url}/api/tags", timeout=5)
        response.raise_for_status()
        return True
    except Exception:
        return False


def start_ollama_service() -> subprocess.Popen:
    """Start the Ollama service in the background."""
    if not shutil.which("ollama"):
        raise RuntimeError("`ollama` binary not found in PATH; please install Ollama first")

    LOGGER.info("Starting Ollama service...")
    process = subprocess.Popen(
        ["ollama", "serve"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    return process


def wait_for_ollama(base_url: str, timeout: int = READY_TIMEOUT) -> bool:
    """Wait for Ollama to become reachable."""
    start = time.time()
    while time.time() - start < timeout:
        if is_ollama_ready(base_url):
            return True
        time.sleep(POLL_INTERVAL)
    return False


def list_models(base_url: str) -> Set[str]:
    """Return the set of models available in Ollama."""
    try:
        response = requests.get(f"{base_url}/api/tags", timeout=10)
        response.raise_for_status()
        data = response.json()
        return {model["name"] for model in data.get("models", [])}
    except Exception:
        return set()


def pull_model(model: str) -> None:
    """Pull a model via the Ollama CLI."""
    LOGGER.info("Pulling model %s", model)
    result = subprocess.run(["ollama", "pull", model], check=False)
    if result.returncode != 0:
        raise RuntimeError(f"Failed to pull Ollama model: {model}")


def discover_required_models(config: dict) -> List[str]:
    """Inspect the config for model references that should be present."""

    ai_provider = str(config.get("ai_provider", "ollama")).lower()
    candidate_keys = [
        "analysis_model",
        "ollama_model",
        "primary_ollama_model",
        "secondary_ollama_model",
        "fast_ollama_model",
        "fast_model",
        "fallback_model",
        "model",
    ]

    models: List[str] = []

    if ai_provider == "ollama":
        for key in candidate_keys:
            value = config.get(key)
            if isinstance(value, str) and value.strip():
                models.append(value.strip())

    if config.get("embedding_enabled"):
        embedding_model = config.get("embedding_model")
        if isinstance(embedding_model, str) and embedding_model.strip():
            models.append(embedding_model.strip())
    # Remove duplicates while preserving order
    seen: Set[str] = set()
    deduped: List[str] = []
    for model in models:
        if model not in seen:
            seen.add(model)
            deduped.append(model)
    return deduped


def ensure_models_available(base_url: str, required_models: Iterable[str], skip_pulls: bool) -> None:
    """Ensure all required models are present, pulling them if needed."""
    available = list_models(base_url)
    missing = [model for model in required_models if model not in available]

    if not missing:
        LOGGER.info("All required models are already available: %s", ", ".join(required_models) or "(none)")
        return

    if skip_pulls:
        LOGGER.warning("Skipping pulls; missing models: %s", ", ".join(missing))
        return

    for model in missing:
        pull_model(model)


def run_pipeline(config_path: Path) -> int:
    """Invoke the main pipeline script using the provided config."""
    env = os.environ.copy()
    env.setdefault("OBSIDIAN_LINK_MASTER_CONFIG", str(config_path))
    command = [sys.executable, "obsidian_auto_linker_enhanced.py"]
    LOGGER.info("Launching pipeline with %s", config_path)
    result = subprocess.run(command, env=env)
    return result.returncode


def run_embedding_tests(base_url: str, model: str) -> None:
    """Run embedding smoke tests and abort if they fail."""

    command = [
        sys.executable,
        "scripts/test_embeddings.py",
        "--base-url",
        base_url,
        "--model",
        model,
    ]
    LOGGER.info("Running embedding verification for model %s", model)
    result = subprocess.run(command)
    if result.returncode != 0:
        raise RuntimeError(
            "Embedding verification failed; aborting startup before running pipeline"
        )


def main(argv: Optional[List[str]] = None) -> None:
    args = parse_args(argv)
    config = load_yaml_config(str(args.config), default={})
    base_url = config.get("ollama_url") or config.get("ollama_base_url", DEFAULT_BASE_URL)
    required_models = discover_required_models(config)

    vault_path = config.get("vault_path")
    if not vault_path:
        LOGGER.error("`vault_path` must be set to a valid Obsidian vault directory")
        sys.exit(1)

    vault_dir = Path(vault_path)
    if not vault_dir.is_dir():
        LOGGER.error("Configured `vault_path` is not a directory: %s", vault_dir)
        sys.exit(1)

    LOGGER.info("Using config: %s", args.config)
    LOGGER.info("Ollama base URL: %s", base_url)

    started_process: Optional[subprocess.Popen] = None

    try:
        if not is_ollama_ready(base_url):
            started_process = start_ollama_service()
            if not wait_for_ollama(base_url):
                raise RuntimeError("Ollama did not become ready in time")
        else:
            LOGGER.info("Ollama is already running")

        ensure_models_available(base_url, required_models, args.skip_model_pulls)

        embedding_model = config.get("embedding_model")
        if not embedding_model:
            raise RuntimeError("`embedding_model` must be set in the configuration")

        run_embedding_tests(base_url, embedding_model)

        exit_code = run_pipeline(args.config)
    except Exception as exc:
        LOGGER.error("Launcher failed: %s", exc)
        exit_code = 1
    finally:
        if started_process and started_process.poll() is None:
            LOGGER.info("Stopping Ollama service started by launcher")
            started_process.terminate()
            try:
                started_process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                started_process.kill()

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
