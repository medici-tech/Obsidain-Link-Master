#!/usr/bin/env python3
"""
Enhanced Obsidian Vault Auto-Linker with Advanced Features
Processes conversations and creates MOC-based wiki structure
"""

# Standard library imports
import fnmatch
import hashlib
import json
import os
import re
import shutil
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

# Third-party imports
import requests
import yaml  # pyright: ignore[reportMissingModuleSource]

# Try to import anthropic for Claude API support (optional)
try:
    from anthropic import Anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False
    Anthropic = None

# Local application imports
from config_utils import (
    check_ollama_connection,
    ensure_directory_exists,
    get_file_size_category,
    get_file_size_kb,
    load_yaml_config,
    load_json_file,
    save_json_file,
    validate_vault_path,
)
from live_dashboard import LiveDashboard
from logger_config import get_logger, setup_logging
from obsidian_link_master.configuration import DEFAULT_CONFIG, RuntimeConfig, load_runtime_config
from scripts.cache_utils import BoundedCache
from scripts.embedding_similarity import EmbeddingManager
from scripts.incremental_processing import FileHashTracker, create_hash_tracker

DEFAULT_CONFIG = {
    'vault_path': str(Path('/Users/medici/Documents/MediciVault')),
    'backup_folder': '_backups',
    'dry_run': True,
    'fast_dry_run': False,
    'force_reprocess': False,
    'max_backups': 5,
    'max_siblings': 5,
    'batch_size': 1,
    'max_retries': 3,
    'parallel_processing_enabled': False,
    'parallel_workers': 1,
    'file_ordering': 'recent',
    'resume_enabled': True,
    'cache_enabled': True,
    'analytics_enabled': True,
    'interactive_mode': True,
    'embedding_enabled': False,
    'embedding_base_url': 'http://localhost:11434',
    'embedding_model': 'nomic-embed-text:latest',
    'embedding_similarity_threshold': 0.7,
    'embedding_top_k': 12,
    'incremental_processing': True,
    'incremental': True,
    'max_cache_size_mb': 1000,
    'max_cache_entries': 10000,
    'incremental_tracker_file': '.incremental_tracker.json',
    'confidence_threshold': 0.8,
    'enable_review_queue': True,
    'review_queue_path': 'reviews/',
    'dry_run_limit': 10,
    'dry_run_interactive': True,
    'ollama_base_url': 'http://localhost:11434',
    'ollama_model': 'Qwen3-Embedding-8B:Q8_0',
    'ollama_timeout': 300,
    'ollama_max_retries': 5,
    'ollama_temperature': 0.1,
    'ollama_max_tokens': 1024,
    'ai_provider': 'ollama',
    'claude_model': 'claude-sonnet-4-5-20250929',
    'claude_max_tokens': 2048,
    'claude_temperature': 0.1,
    'claude_timeout': 60,
    'knowledge_graph_file': 'knowledge_graph.json',
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
    interactive_mode: bool
    embedding_enabled: bool
    embedding_base_url: str
    embedding_model: str
    embedding_similarity_threshold: float
    embedding_top_k: int
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
    knowledge_graph_file: str


def _load_runtime_config(config_path: str = 'config.yaml') -> RuntimeConfig:
    """Load configuration from disk with sane defaults and validation."""

    logger = get_logger(__name__)
    raw_config = {**DEFAULT_CONFIG, **load_yaml_config(config_path, default={})}

    vault_path = os.environ.get('OBSIDIAN_VAULT_PATH') or raw_config.get('vault_path')
    if not vault_path:
        vault_path = DEFAULT_CONFIG['vault_path']

    if not validate_vault_path(vault_path, must_exist=False):
        fallback = DEFAULT_CONFIG['vault_path']
        logger.warning(
            "Invalid vault path '%s'. Falling back to %s."
            " Set OBSIDIAN_VAULT_PATH or update config.yaml to override.",
            vault_path,
            fallback,
        )
        vault_path = fallback

    ensure_directory_exists(vault_path, create=True)
    backup_folder = os.path.join(vault_path, raw_config.get('backup_folder', DEFAULT_CONFIG['backup_folder']))

    return RuntimeConfig(
        vault_path=vault_path,
        backup_folder=backup_folder,
        dry_run=bool(raw_config['dry_run']),
        fast_dry_run=bool(raw_config['fast_dry_run']),
        force_reprocess=bool(raw_config['force_reprocess']),
        max_backups=int(raw_config['max_backups']),
        max_siblings=int(raw_config['max_siblings']),
        batch_size=int(raw_config['batch_size']),
        max_retries=int(raw_config['max_retries']),
        parallel_processing_enabled=bool(raw_config['parallel_processing_enabled']),
        parallel_workers=int(raw_config['parallel_workers']),
        file_ordering=str(raw_config['file_ordering']),
        resume_enabled=bool(raw_config['resume_enabled']),
        cache_enabled=bool(raw_config['cache_enabled']),
        analytics_enabled=bool(raw_config['analytics_enabled']),
        interactive_mode=bool(raw_config['interactive_mode']),
        embedding_enabled=bool(raw_config['embedding_enabled']),
        embedding_base_url=str(raw_config.get('embedding_base_url', raw_config['ollama_base_url'])),
        embedding_model=str(raw_config['embedding_model']),
        embedding_similarity_threshold=float(raw_config['embedding_similarity_threshold']),
        embedding_top_k=int(raw_config['embedding_top_k']),
        incremental_processing=bool(raw_config['incremental_processing']),
        incremental=bool(raw_config['incremental']),
        max_cache_size_mb=int(raw_config['max_cache_size_mb']),
        max_cache_entries=int(raw_config['max_cache_entries']),
        incremental_tracker_file=str(raw_config['incremental_tracker_file']),
        confidence_threshold=float(raw_config['confidence_threshold']),
        enable_review_queue=bool(raw_config['enable_review_queue']),
        review_queue_path=str(raw_config['review_queue_path']),
        dry_run_limit=int(raw_config['dry_run_limit']),
        dry_run_interactive=bool(raw_config['dry_run_interactive']),
        ollama_base_url=str(raw_config['ollama_base_url']),
        ollama_model=str(raw_config['ollama_model']),
        ollama_timeout=int(raw_config['ollama_timeout']),
        ollama_max_retries=int(raw_config['ollama_max_retries']),
        ollama_temperature=float(raw_config['ollama_temperature']),
        ollama_max_tokens=int(raw_config['ollama_max_tokens']),
        ai_provider=str(raw_config['ai_provider']).lower(),
        claude_api_key=raw_config.get('claude_api_key') or os.environ.get('ANTHROPIC_API_KEY', ''),
        claude_model=str(raw_config['claude_model']),
        claude_max_tokens=int(raw_config['claude_max_tokens']),
        claude_temperature=float(raw_config['claude_temperature']),
        claude_timeout=int(raw_config['claude_timeout']),
        knowledge_graph_file=str(raw_config['knowledge_graph_file']),
    )


@dataclass
class ProcessingContext:
    """Holds runtime services and resolved configuration."""

    config: RuntimeConfig
    ai_provider: str
    claude_client: Optional[Any] = None
    dashboard: Optional[LiveDashboard] = None


# Initialize logger
logger = get_logger(__name__)

# Bootstrap guard to avoid double initialization when run via multiple entrypoints
_BOOTSTRAPPED = False
_BOOTSTRAP_LOCK = threading.Lock()

# Load and normalize configuration once for the module
runtime_config = _load_runtime_config()
config: Dict[str, Any] = runtime_config.__dict__.copy()

VAULT_PATH = runtime_config.vault_path
BACKUP_FOLDER = runtime_config.backup_folder
DRY_RUN = runtime_config.dry_run
FAST_DRY_RUN = runtime_config.fast_dry_run
MAX_BACKUPS = runtime_config.max_backups
MAX_SIBLINGS = runtime_config.max_siblings
BATCH_SIZE = runtime_config.batch_size
MAX_RETRIES = runtime_config.max_retries
PARALLEL_PROCESSING_ENABLED = runtime_config.parallel_processing_enabled
PARALLEL_WORKERS = runtime_config.parallel_workers
REQUESTED_PARALLEL_WORKERS = PARALLEL_WORKERS

# Parallel processing configuration
if not PARALLEL_PROCESSING_ENABLED:
    if PARALLEL_WORKERS > 1:
        logger.info(
            "parallel_processing_enabled is False; ignoring parallel_workers=%s and running sequentially",
            PARALLEL_WORKERS,
        )
    PARALLEL_WORKERS = 1
else:
    if PARALLEL_WORKERS > 1:
        logger.info("✅ Parallel processing enabled: using %s workers", PARALLEL_WORKERS)
    else:
        logger.info("Parallel processing enabled but configured for a single worker")

FILE_ORDERING = runtime_config.file_ordering
RESUME_ENABLED = runtime_config.resume_enabled
CACHE_ENABLED = runtime_config.cache_enabled
INCREMENTAL_PROCESSING = runtime_config.incremental_processing
FORCE_REPROCESS = runtime_config.force_reprocess
INTERACTIVE_MODE = runtime_config.interactive_mode
ANALYTICS_ENABLED = runtime_config.analytics_enabled
EMBEDDING_ENABLED = runtime_config.embedding_enabled
EMBEDDING_BASE_URL = runtime_config.embedding_base_url
EMBEDDING_MODEL = runtime_config.embedding_model
EMBEDDING_THRESHOLD = runtime_config.embedding_similarity_threshold
EMBEDDING_TOP_K = runtime_config.embedding_top_k

# Cache configuration
MAX_CACHE_SIZE_MB = runtime_config.max_cache_size_mb
MAX_CACHE_ENTRIES = runtime_config.max_cache_entries

# Incremental processing configuration (enabled by default for performance)
INCREMENTAL_ENABLED = runtime_config.incremental  # Default: True for 90% faster reruns
if INCREMENTAL_ENABLED:
    logger.info("✅ Incremental processing enabled (skips unchanged files for 90% faster reruns)")
# Quality control settings
CONFIDENCE_THRESHOLD = runtime_config.confidence_threshold
ENABLE_REVIEW_QUEUE = runtime_config.enable_review_queue
REVIEW_QUEUE_PATH = runtime_config.review_queue_path
LINK_QUALITY_THRESHOLD = float(config.get('link_quality_threshold', 0.2))

# Dry run settings
DRY_RUN_LIMIT = runtime_config.dry_run_limit
DRY_RUN_INTERACTIVE = runtime_config.dry_run_interactive

# Ollama configuration
OLLAMA_BASE_URL = runtime_config.ollama_base_url
OLLAMA_MODEL = runtime_config.ollama_model
OLLAMA_TIMEOUT = runtime_config.ollama_timeout  # Default 5 minutes for Qwen3:8b
OLLAMA_MAX_RETRIES = runtime_config.ollama_max_retries  # More retries for complex reasoning
OLLAMA_TEMPERATURE = runtime_config.ollama_temperature
# Fully implemented call_ollama defined after provider configuration
OLLAMA_MAX_TOKENS = runtime_config.ollama_max_tokens  # More tokens for detailed responses

# AI Provider selection (ollama or claude)
AI_PROVIDER = runtime_config.ai_provider

# Claude API configuration (only used if ai_provider: claude)
CLAUDE_API_KEY = runtime_config.claude_api_key
CLAUDE_MODEL = runtime_config.claude_model
CLAUDE_MAX_TOKENS = runtime_config.claude_max_tokens
CLAUDE_TEMPERATURE = runtime_config.claude_temperature
CLAUDE_TIMEOUT = runtime_config.claude_timeout
KNOWLEDGE_GRAPH_FILE = runtime_config.knowledge_graph_file

# Initialize Claude client lazily
claude_client = None


def _resolve_ai_provider(config_obj: RuntimeConfig = runtime_config) -> str:
    """Determine the active AI provider with validation and fallbacks."""

    provider = config_obj.ai_provider
    if provider != 'claude':
        return provider

    if not ANTHROPIC_AVAILABLE:
        logger.warning("⚠️  anthropic package not installed; falling back to Ollama")
        return 'ollama'

    if not config_obj.claude_api_key:
        logger.warning(
            "⚠️  Claude provider selected but no API key found. Set ANTHROPIC_API_KEY"
            " or update config.yaml. Falling back to Ollama."
        )
        return 'ollama'

    return provider


def _ensure_claude_client(context: ProcessingContext) -> Optional[Any]:
    """Create a Claude client only when the provider is enabled and configured."""

    if context.claude_client:
        return context.claude_client

    if context.ai_provider != 'claude':
        return None

    try:
        context.claude_client = Anthropic(api_key=context.config.claude_api_key)
        logger.info("✅ Claude API initialized (model: %s)", context.config.claude_model)
    except Exception as exc:  # noqa: BLE001 - surface configuration failures
        logger.warning("⚠️  Failed to initialize Claude client: %s", exc)
        context.claude_client = None

    return context.claude_client


def create_processing_context(
    *, enable_dashboard: bool = False, dashboard_update_interval: int = 15,
    config_obj: RuntimeConfig = runtime_config,
) -> ProcessingContext:
    """Factory that prepares provider clients and optional dashboard."""

    dashboard = None
    if enable_dashboard:
        dashboard = LiveDashboard(update_interval=dashboard_update_interval)
        dashboard.start()

    context = ProcessingContext(
        config=config_obj,
        ai_provider=_resolve_ai_provider(config_obj),
        claude_client=None,
        dashboard=dashboard,
    )
    _ensure_claude_client(context)
    return context


AI_PROVIDER = _resolve_ai_provider()

# Default context for callers that don't manage their own lifecycle
DEFAULT_PROCESSING_CONTEXT = create_processing_context()

# Cost tracking disabled for local LLM (free to use)

# Global dashboard reference (optional)
dashboard = None

def call_ollama(
    prompt: str,
    system_prompt: str = "",
    max_retries: int = None,
    track_metrics: bool = True,
    *,
    context: ProcessingContext = DEFAULT_PROCESSING_CONTEXT,
) -> str:
    """Call Ollama API with the given prompt and retry logic"""
    cfg = context.config
    dashboard = context.dashboard
    if max_retries is None:
        max_retries = cfg.ollama_max_retries

    for attempt in range(max_retries):
        start_time = time.time()
        try:
            url = f"{cfg.ollama_base_url}/api/generate"

            # Prepare the full prompt
            full_prompt = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt

            payload = {
                "model": cfg.ollama_model,
                "prompt": full_prompt,
                "stream": False,
                "options": {
                    "temperature": cfg.ollama_temperature,  # From config
                    "top_p": 0.8,        # Slightly lower top_p
                    "top_k": 20,          # Limit vocabulary
                    "repeat_penalty": 1.1, # Prevent repetition
                    "num_ctx": 2048,     # Smaller context window
                    "num_predict": cfg.ollama_max_tokens,  # From config
                    "stop": ["```", "\n\n\n"]  # Stop tokens
                }
            }

            # Increase timeout with each retry (for slow local models)
            timeout = cfg.ollama_timeout + (attempt * 60)  # Base + 1min per retry
            
            # Increase timeout with each retry (for complex reasoning)
            timeout = cfg.ollama_timeout + (attempt * 180)  # Base + 3min per retry for Qwen3:8b reasoning
            response = requests.post(url, json=payload, timeout=timeout)
            response.raise_for_status()

            result = response.json()
            response_text = result.get('response', '').strip()

            # Clean common markdown code fences
            if response_text.startswith('```json'):
                response_text = response_text[7:]
            if response_text.startswith('```'):
                response_text = response_text[3:]
            if response_text.endswith('```'):
                response_text = response_text[:-3]
            response_text = response_text.strip()

            # Track metrics
            if track_metrics and dashboard:
                response_time = time.time() - start_time
                # Estimate tokens (rough approximation: 4 chars per token)
                tokens = len(response_text) // 4
                dashboard.add_ai_request(response_time, True, tokens, False)

            return response_text
            
        except requests.exceptions.Timeout:
            # Track timeout
            if track_metrics and dashboard:
                response_time = time.time() - start_time
                dashboard.add_ai_request(response_time, False, 0, True)

            if attempt < max_retries - 1:
                wait_time = 2 ** attempt  # Exponential backoff: 1s, 2s, 4s
                logger.warning(f"⏰ Attempt {attempt + 1} timed out ({timeout}s). Qwen3:8b needs time for complex reasoning - retrying in {wait_time}s...")
                time.sleep(wait_time)
                continue
            else:
                logger.error(f"⏰ All {max_retries} attempts timed out. Local model is very slow (this is normal).")
                if dashboard:
                    dashboard.add_error("timeout", "AI request timed out after all retries")
                return ""
        except requests.exceptions.RequestException as e:
            # Track failure
            if track_metrics and dashboard:
                response_time = time.time() - start_time
                dashboard.add_ai_request(response_time, False, 0, False)

            if attempt < max_retries - 1:
                wait_time = 2 ** attempt
                logger.warning(f"❌ Attempt {attempt + 1} failed: {e}. Retrying in {wait_time}s...")
                time.sleep(wait_time)
                continue
            else:
                logger.error(f"❌ All {max_retries} attempts failed: {e}")
                if dashboard:
                    dashboard.add_error("api_error", str(e))
                return ""
        except Exception as e:
            logger.error(f"❌ Unexpected error calling Ollama: {e}")
            if dashboard:
                dashboard.add_error("unexpected_error", str(e))
            return ""

    return ""


def call_claude(
    prompt: str,
    system_prompt: str = "",
    max_retries: int = 3,
    track_metrics: bool = True,
    *,
    context: ProcessingContext = DEFAULT_PROCESSING_CONTEXT,
) -> str:
    """
    Call Claude API with the given prompt and retry logic

    Args:
        prompt: The user prompt to send
        system_prompt: System instructions for Claude
        max_retries: Maximum number of retry attempts
        track_metrics: Whether to track metrics in dashboard

    Returns:
        Claude's response text, or empty string on failure
    """
    client = _ensure_claude_client(context)
    dashboard = context.dashboard
    if not client:
        logger.error("❌ Claude client not initialized")
        return ""

    for attempt in range(max_retries):
        start_time = time.time()
        try:
            # Call Claude API
            message = client.messages.create(
                model=context.config.claude_model,
                max_tokens=context.config.claude_max_tokens,
                temperature=context.config.claude_temperature,
                system=system_prompt if system_prompt else "You are a helpful assistant.",
                messages=[
                    {"role": "user", "content": prompt}
                ],
                timeout=context.config.claude_timeout
            )

            # Extract response text
            response_text = message.content[0].text.strip() if message.content else ""

            # Track metrics
            if track_metrics and dashboard:
                response_time = time.time() - start_time
                tokens = message.usage.output_tokens if hasattr(message, 'usage') else len(response_text) // 4
                dashboard.add_ai_request(response_time, True, tokens, False)

            return response_text

        except Exception as e:
            # Track failure
            if track_metrics and dashboard:
                response_time = time.time() - start_time
                is_timeout = 'timeout' in str(e).lower() or 'timed out' in str(e).lower()
                dashboard.add_ai_request(response_time, False, 0, is_timeout)

            if attempt < max_retries - 1:
                wait_time = 2 ** attempt  # Exponential backoff: 1s, 2s, 4s
                logger.warning(f"⚠️  Attempt {attempt + 1} failed: {e}. Retrying in {wait_time}s...")
                time.sleep(wait_time)
                continue
            else:
                logger.error(f"❌ All {max_retries} attempts failed: {e}")
                if dashboard:
                    dashboard.add_error("claude_api_error", str(e))
                return ""

    return ""


def call_ai_provider(
    prompt: str,
    system_prompt: str = "",
    max_retries: int = None,
    track_metrics: bool = True,
    *,
    context: ProcessingContext = DEFAULT_PROCESSING_CONTEXT,
) -> str:
    """
    Call the configured AI provider (Ollama or Claude)

    This is an abstraction layer that routes to the appropriate AI backend
    based on the ai_provider configuration setting.

    Args:
        prompt: The user prompt to send
        system_prompt: System instructions for the AI
        max_retries: Maximum number of retry attempts (uses provider default if None)
        track_metrics: Whether to track metrics in dashboard

    Returns:
        AI response text, or empty string on failure
    """
    if context.ai_provider == 'claude':
        if max_retries is None:
            max_retries = 3  # Claude is fast, fewer retries needed
        return call_claude(prompt, system_prompt, max_retries, track_metrics, context=context)
    else:
        # Default to Ollama
        if max_retries is None:
            max_retries = context.config.ollama_max_retries
        return call_ollama(prompt, system_prompt, max_retries, track_metrics, context=context)


# Analytics tracking
analytics = {
    'start_time': None,
    'end_time': None,
    'total_files': 0,
    'processed_files': 0,
    'skipped_files': 0,
    'failed_files': 0,
    'processing_time': 0,
    'moc_distribution': {},
    'error_types': {},
    'retry_attempts': 0,
    'cache_hits': 0,
    'cache_misses': 0,
    'embedding_candidates': 0,
    'embedding_links': 0,
    'embedding_corpus_size': 0,
    'knowledge_graph_edges': [],
    'link_quality_scores': [],
    'skipped_unchanged': 0,
    'cache_evictions': 0,
    'link_quality_summary': {
        'average': 0.0,
        'best': 0.0,
        'count': 0,
    },
    'incremental_summary': {
        'unchanged_files': 0,
        'changed_files': 0,
        'new_files': 0,
        'deleted_files': 0,
        'total_tracked_files': 0,
        'skip_rate': 0,
    },
}

# Progress tracking
progress_data = {
    'processed_files': set(),
    'failed_files': set(),
    'current_batch': 0,
    'total_batches': 0,
    'last_update': None,
    # Enhanced resume: per-file stages
    'file_stages': {}  # {filepath: {'stage': 'pending'|'analyzing'|'linking'|'completed'|'failed', 'timestamp': str}}
}
progress_lock = threading.RLock()  # Thread-safe progress updates

# Cache for AI responses (BoundedCache with LRU eviction to prevent memory leaks)
logger.info(f"Initializing bounded cache: max_size_mb={MAX_CACHE_SIZE_MB}, max_entries={MAX_CACHE_ENTRIES}")
ai_cache = BoundedCache(max_size_mb=MAX_CACHE_SIZE_MB, max_entries=MAX_CACHE_ENTRIES)

# Threading locks for parallel processing
cache_lock = threading.RLock()  # Reentrant lock for nested cache operations
progress_lock = threading.RLock()
analytics_lock = threading.RLock()
hash_tracker_lock = threading.RLock()
embedding_lock = threading.RLock()

# Incremental processing tracker (FileHashTracker is instantiated in main)
hash_tracker: Optional[FileHashTracker] = None
# Embedding manager (initialized when embedding_enabled is true)
embedding_manager: Optional[EmbeddingManager] = None
note_corpus: Dict[str, str] = {}


def verify_embedding_backend(base_url: str, model: str, timeout: int = 15) -> bool:
    """Lightweight readiness probe for the embeddings API."""

    probe_url = f"{base_url.rstrip('/')}/api/embeddings"
    payload = {"model": model, "prompt": "health check"}

    try:
        start = time.time()
        response = requests.post(probe_url, json=payload, timeout=timeout)
        response.raise_for_status()
        embedding = response.json().get('embedding')

        if not embedding:
            logger.error("❌ Embedding backend responded but returned no vector. Check model availability (%s).", model)
            return False

        logger.info("✅ Embedding backend ready (%s) in %.1fs", model, time.time() - start)
        return True
    except requests.RequestException as exc:
        logger.error("❌ Embedding backend unavailable at %s: %s", probe_url, exc)
        logger.info("   Ensure your embeddings host is running (e.g., `ollama serve`) and pull the model: ollama pull %s", model)
        return False

# 12 MOC System (enhanced with custom support)
MOCS = {
    "Client Acquisition": "📍 Client Acquisition MOC",
    "Service Delivery": "📍 Service Delivery MOC",
    "Revenue & Pricing": "📍 Revenue & Pricing MOC",
    "Marketing & Content": "📍 Marketing & Content MOC",
    "Garrison Voice Product": "📍 Garrison Voice Product MOC",
    "Technical & Automation": "📍 Technical & Automation MOC",
    "Business Operations": "📍 Business Operations MOC",
    "Learning & Skills": "📍 Learning & Skills MOC",
    "Personal Development": "📍 Personal Development MOC",
    "Health & Fitness": "📍 Health & Fitness MOC",
    "Finance & Money": "📍 Finance & Money MOC",
    "Life & Misc": "📍 Life & Misc MOC"
}

# Add custom MOCs if defined
if config.get('custom_mocs'):
    MOCS.update(config['custom_mocs'])

MOC_DESCRIPTIONS = {
    "Client Acquisition": "Getting customers for Garrison Detail & Garrison Voice",
    "Service Delivery": "Fulfilling client work and project execution",
    "Revenue & Pricing": "Making money, pricing strategies, monetization",
    "Marketing & Content": "Getting attention, content creation, brand building",
    "Garrison Voice Product": "AI voice product development and features",
    "Technical & Automation": "Tools, code, AI, n8n, automation systems",
    "Business Operations": "Running the business day-to-day",
    "Learning & Skills": "Courses, tutorials, research, skill acquisition",
    "Personal Development": "Growth, habits, mindset, self-improvement",
    "Health & Fitness": "Physical health, exercise, nutrition, wellness",
    "Finance & Money": "Personal finance, investing, budgeting",
    "Life & Misc": "Everything else that doesn't fit other categories"
}

def load_progress() -> None:
    """Load progress from file using config_utils"""
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
                    progress_data['file_stages'] = data.get('file_stages', {})
                    logger.info(f"📂 Loaded progress: {len(progress_data['processed_files'])} files already processed")
                    if progress_data['file_stages']:
                        stages_summary = {}
                        for filepath, stage_data in progress_data['file_stages'].items():
                            stage = stage_data.get('stage', 'unknown')
                            stages_summary[stage] = stages_summary.get(stage, 0) + 1
                        logger.info(f"   📋 File stages: {dict(stages_summary)}")
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
    data = load_json_file(progress_file, default={})

    if data and isinstance(data, dict):
        progress_data['processed_files'] = set(data.get('processed_files', []))
        progress_data['failed_files'] = set(data.get('failed_files', []))
        progress_data['current_batch'] = data.get('current_batch', 0)
        if progress_data['processed_files']:
            logger.info(f"📂 Loaded progress: {len(progress_data['processed_files'])} files already processed")
    else:
        progress_data['processed_files'] = set()
        progress_data['failed_files'] = set()
        progress_data['current_batch'] = 0

def save_progress() -> None:
    """Save progress to file using config_utils"""
    if not RESUME_ENABLED:
        return

    progress_file = config.get('progress_file', '.processing_progress.json')
    try:
        with open(progress_file, 'w') as f:
            json.dump({
                'processed_files': list(progress_data['processed_files']),
                'failed_files': list(progress_data['failed_files']),
                'current_batch': progress_data['current_batch'],
                'file_stages': progress_data.get('file_stages', {}),
                'last_update': datetime.now().isoformat()
            }, f, indent=2)
    except Exception as e:
        logger.warning(f"⚠️  Could not save progress: {e}")


def set_file_stage(filepath: str, stage: str):
    """
    Set the processing stage for a file

    Args:
        filepath: Path to file
        stage: Stage name ('pending', 'analyzing', 'linking', 'completed', 'failed')
    """
    if not RESUME_ENABLED:
        return

    with progress_lock:
        progress_data['file_stages'][filepath] = {
            'stage': stage,
            'timestamp': datetime.now().isoformat()
        }


def get_file_stage(filepath: str) -> str:
    """
    Get the current processing stage for a file

    Args:
        filepath: Path to file

    Returns:
        Stage name, or 'pending' if not tracked
    """
    if not RESUME_ENABLED:
        return 'pending'

    with progress_lock:
        stage_data = progress_data.get('file_stages', {}).get(filepath, {})
        return stage_data.get('stage', 'pending')


def load_cache() -> None:
    """Load AI cache from file into BoundedCache"""
    global ai_cache

    if not CACHE_ENABLED:
        logger.info("Cache disabled in config")
        return

    cache_file = config.get('cache_file', '.ai_cache.json')
    cache_data = load_json_file(cache_file, default={})

    if cache_data:
        try:
            ai_cache.from_dict(cache_data)
        except AttributeError:
            # Fallback for simple dict patches in tests
            ai_cache.clear()
            ai_cache.update(cache_data)

        logger.info(f"💾 Loaded cache: {len(cache_data)} cached responses")

        # Update dashboard with cache stats when available
        if dashboard:
            if hasattr(ai_cache, 'get_stats'):
                cache_stats = ai_cache.get_stats()
                dashboard.update_cache_stats(cache_stats['size_mb'], cache_stats['entries'])

def save_cache() -> None:
    """Save AI cache to file using BoundedCache.save_to_file()"""
    if not CACHE_ENABLED:
        return

    cache_file = config.get('cache_file', '.ai_cache.json')
    try:
        with cache_lock:
            if hasattr(ai_cache, 'save_to_file'):
                ai_cache.save_to_file(cache_file)
                stats = ai_cache.get_stats()
                logger.info(f"💾 Saved cache: {stats['entries']} entries ({stats['size_mb']:.2f}MB)")
                logger.info(f"   Cache stats - Utilization: {stats['utilization_pct']:.1f}%, Size: {stats['size_utilization_pct']:.1f}%")
            else:
                with open(cache_file, 'w', encoding='utf-8') as f:
                    json.dump(ai_cache, f, indent=2)
                logger.info(f"💾 Saved cache: {len(ai_cache)} entries")
    except Exception as e:
        logger.error(f"⚠️  Could not save cache: {e}")

def persist_hash_tracker_state() -> None:
    """Persist the incremental hash tracker to disk when available."""
    if not INCREMENTAL_PROCESSING:
        return

    if hash_tracker is None:
        return

    with hash_tracker_lock:
        try:
            hash_tracker.save()
        except Exception as exc:  # pragma: no cover - defensive logging
            logger.warning(f"⚠️  Could not persist hash tracker: {exc}")

def get_content_hash(content: str) -> str:
    """Generate hash for content caching"""
    return hashlib.md5(content.encode()).hexdigest()


def _tokenize_for_similarity(text: str) -> set[str]:
    """Lightweight tokenizer for link-quality scoring."""

    tokens = re.findall(r"[a-zA-Z]{4,}", text.lower())
    return set(tokens)


def _score_similarity(source: str, target: str) -> float:
    """Compute an overlap-based similarity score for two note snippets."""

    source_tokens = _tokenize_for_similarity(source)
    target_tokens = _tokenize_for_similarity(target)

    if not source_tokens or not target_tokens:
        return 0.0

    overlap = len(source_tokens & target_tokens)
    return overlap / max(len(source_tokens), len(target_tokens))


def rank_sibling_candidates(
    main_content: str,
    sibling_notes: list[str],
    existing_notes: Dict[str, str],
    *,
    limit: int = MAX_SIBLINGS,
    threshold: float = LINK_QUALITY_THRESHOLD,
    embedding_scores: Optional[Dict[str, float]] = None,
) -> list[tuple[str, float]]:
    """Rank sibling candidates by a transparent similarity score."""

    embedding_scores = embedding_scores or {}
    scored = []
    for note in sibling_notes:
        preview = existing_notes.get(note)
        if not preview:
            continue
        text_score = _score_similarity(main_content, preview)
        hybrid_score = max(text_score, embedding_scores.get(note, 0.0))
        score = hybrid_score
        scored.append((note, score))

    scored.sort(key=lambda item: item[1], reverse=True)

    if threshold > 0:
        scored = [item for item in scored if item[1] >= threshold]

    return scored[:limit]

def should_process_file(file_path: str) -> bool:
    """Check if file should be processed based on filters"""
    filename = os.path.basename(file_path)
    relative_path = os.path.relpath(file_path, VAULT_PATH)

    # Check exclude patterns
    exclude_patterns = config.get('exclude_patterns', [])
    for pattern in exclude_patterns:
        if fnmatch.fnmatch(filename, pattern):
            return False

    # Check include patterns
    include_patterns = config.get('include_patterns', [])
    if include_patterns:
        if not any(fnmatch.fnmatch(filename, pattern) for pattern in include_patterns):
            return False

    # Check folder whitelist
    folder_whitelist = config.get('folder_whitelist', [])
    if folder_whitelist:
        folder = os.path.dirname(relative_path)
        if not any(folder.startswith(f) for f in folder_whitelist):
            return False

    # Check folder blacklist
    folder_blacklist = config.get('folder_blacklist', [])
    if folder_blacklist:
        folder = os.path.dirname(relative_path)
        if any(folder.startswith(f) for f in folder_blacklist):
            return False

    return True

def get_all_notes(vault_path: str) -> Dict[str, str]:
    """Get all note titles with preview content"""
    notes = {}
    for root, dirs, files in os.walk(vault_path):
        if config.get('backup_folder', '_backups') in root:
            continue
        for file in files:
            if file.endswith('.md') and should_process_file(os.path.join(root, file)):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        note_title = file[:-3]
                        notes[note_title] = content[:800]
                except (UnicodeDecodeError, IOError, OSError) as e:
                    logger.debug(f"Could not read {file}: {e}")
                    continue
    return notes


def load_note_corpus(vault_path: str, *, include_content: bool = True) -> Dict[str, str]:
    """Load full note corpus for embedding-based similarity."""

    if not EMBEDDING_ENABLED:
        return {}

    corpus: Dict[str, str] = {}
    for root, _, files in os.walk(vault_path):
        if config.get('backup_folder', '_backups') in root:
            continue

        for file in files:
            if not file.endswith('.md'):
                continue

            file_path = os.path.join(root, file)
            if not should_process_file(file_path):
                continue

            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    corpus[file_path] = content if include_content else content[:800]
            except (UnicodeDecodeError, IOError, OSError) as exc:
                logger.debug(f"Could not read {file_path} for embedding corpus: {exc}")
                continue

    return corpus


class ObsidianAutoLinker:
    """Lightweight adapter exposing helper methods for benchmark tests."""

    def get_content_hash(self, content: str) -> str:
        return get_content_hash(content)

def create_moc_note(moc_name: str, vault_path: str) -> None:
    """Create MOC note if it doesn't exist"""
    moc_filename = MOCS[moc_name].replace('📍 ', '') + '.md'
    moc_path = os.path.join(vault_path, moc_filename)

    if os.path.exists(moc_path):
        return

    description = MOC_DESCRIPTIONS.get(moc_name, f"Content related to {moc_name}")

    content = f"""# {MOCS[moc_name]}

> {description}

## Overview

This is a Map of Content (MOC) that organizes all notes related to {moc_name.lower()}.

## Key Concepts

(Concepts will be added as notes are processed)

## Recent Conversations

(Recent conversations will appear here automatically)

## Related MOCs

(Links to related MOCs will be added here)

---

*This MOC was auto-generated. Add your own structure and notes as needed.*
"""

    if not DRY_RUN:
        with open(moc_path, 'w', encoding='utf-8') as f:
            f.write(content)
        logger.info(f"  ✅ Created MOC: {moc_filename}")

def fast_dry_run_analysis(content: str, file_path: str) -> Dict[str, Any]:
    """Fast dry run analysis without AI - just basic structure analysis"""
    # Extract basic file info
    filename = os.path.basename(file_path)
    file_size = len(content)
    word_count = len(content.split())

    # Simple keyword extraction (no AI)
    words = content.lower().split()
    word_freq = {}
    for word in words:
        if len(word) > 3:  # Only words longer than 3 chars
            word_freq[word] = word_freq.get(word, 0) + 1

    # Get top keywords
    top_keywords = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:10]

    # Simple category detection based on keywords
    categories = []
    if any(word in content.lower() for word in ['work', 'job', 'career', 'business', 'meeting']):
        categories.append('Work & Career')
    if any(word in content.lower() for word in ['learn', 'study', 'education', 'course', 'book']):
        categories.append('Learning & Education')
    if any(word in content.lower() for word in ['health', 'fitness', 'exercise', 'diet', 'medical']):
        categories.append('Health & Fitness')
    if any(word in content.lower() for word in ['money', 'finance', 'budget', 'invest', 'expense']):
        categories.append('Finance & Money')
    if any(word in content.lower() for word in ['project', 'idea', 'plan', 'goal', 'task']):
        categories.append('Projects & Ideas')
    if any(word in content.lower() for word in ['personal', 'life', 'family', 'friend', 'relationship']):
        categories.append('Personal & Life')

    if not categories:
        categories = ['Life & Misc']

    return {
        'filename': filename,
        'file_size': file_size,
        'word_count': word_count,
        'top_keywords': [word for word, freq in top_keywords],
        'categories': categories,
        'analysis_type': 'fast_dry_run',
        'timestamp': datetime.now().isoformat()
    }

def analyze_with_balanced_ai(
    content: str,
    existing_notes: Dict[str, str],
    context: ProcessingContext = DEFAULT_PROCESSING_CONTEXT,
) -> Optional[Dict]:
    """Balanced AI analysis with caching"""

    # Check cache first
    cache_start = time.time()
    content_hash = get_content_hash(content)
    with cache_lock:
        cached_result = ai_cache.get(content_hash)
        if cached_result is not None:
            with analytics_lock:
                analytics['cache_hits'] += 1
            return cached_result

    with analytics_lock:
        analytics['cache_misses'] += 1

    if dashboard:
        lookup_time = time.time() - cache_start
        dashboard.add_cache_miss(lookup_time)
    
    # Sample of existing notes for context (reduced for efficiency)
    note_list = "\n".join([f"- {title}" for title in list(existing_notes.keys())[:50]])

    # Extract main content (before footer if exists)
    main_content = re.split(r'\n---\n## 📊 METADATA', content)[0]

    # Truncate content for faster processing
    content_sample = main_content[:2000]  # Reduced from 4000

    prompt = f"""Analyze this Obsidian conversation and provide structured metadata.

EXISTING NOTES (for linking):
{note_list}

CONTENT:
{content_sample}

Return ONLY valid JSON in this exact format:
{{
  "moc_category": "Life & Misc",
  "primary_topic": "Brief topic description",
  "hierarchical_tags": ["tag1", "tag2"],
  "key_concepts": ["concept1", "concept2", "concept3"],
  "sibling_notes": ["note1", "note2"],
  "confidence_score": 0.8,
  "reasoning": "Brief explanation"
}}

Categories: Client Acquisition, Service Delivery, Revenue & Pricing, Marketing & Content, Garrison Voice Product, Technical & Automation, Business Operations, Learning & Skills, Personal Development, Health & Fitness, Finance & Money, Life & Misc

Return ONLY the JSON object, no explanations or other text."""

    try:
        # Call configured AI provider (Ollama or Claude)
        system_prompt = "You analyze conversations and create knowledge connections. Return valid JSON only."
        result_text = call_ai_provider(prompt, system_prompt, context=context)

        if not result_text:
            logger.error(f"❌ Empty response from {AI_PROVIDER.upper()}")
            return None

        # Clean up potential markdown formatting
        if not isinstance(result_text, str):
            result_text = json.dumps(result_text)

        result_text = result_text.strip()
        if result_text.startswith('```json'):
            result_text = result_text[7:]
        if result_text.startswith('```'):
            result_text = result_text[3:]
        if result_text.endswith('```'):
            result_text = result_text[:-3]
        result_text = result_text.strip()

        # Try to parse JSON with better error handling
        try:
            result = json.loads(result_text)
        except json.JSONDecodeError as e:
            logger.info(f"  ⚠️  JSON parse error: {e}")
            logger.info(f"  Response was: {result_text[:200]}")
            logger.warning(f"  ⚠️  JSON parse error: {e}")
            logger.debug(f"  Response was: {result_text[:200]}")

            # Try to extract JSON from the response if it's wrapped in text
            json_match = re.search(r'\{.*\}', result_text, re.DOTALL)
            if json_match:
                try:
                    result = json.loads(json_match.group())
                    logger.info(f"  ✅ Extracted JSON from response")
                except json.JSONDecodeError:
                    logger.error(f"  ❌ Could not extract valid JSON")
                    return None
            else:
                logger.error(f"  ❌ No JSON found in response")
                return None

        # Cache the result (with automatic LRU eviction if needed)
        def _set_cache(key: str, value: Dict[str, Any]):
            if hasattr(ai_cache, 'set'):
                ai_cache.set(key, value)
            else:
                ai_cache[key] = value

        with cache_lock:
            _set_cache(content_hash, result)
            if hasattr(ai_cache, 'get_stats'):
                stats = ai_cache.get_stats()
                logger.debug(
                    f"💾 Cached result (cache: {stats['entries']}/{stats['max_entries']} entries, {stats['size_mb']:.1f}/{stats['max_size_mb']}MB)"
                )

        return result
    except Exception as e:
        logger.warning(f"  ⚠️  AI analysis failed: {e}")
        return None

def backup_file(file_path: str) -> None:
    """Create timestamped backup with verification"""
    os.makedirs(BACKUP_FOLDER, exist_ok=True)

    filename = os.path.basename(file_path)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_name = f"{filename[:-3]}_{timestamp}.md"
    backup_path = os.path.join(BACKUP_FOLDER, backup_name)

    try:
        shutil.copy2(file_path, backup_path)

        # Verify backup
        if config.get('backup_verification', True):
            with open(file_path, 'r') as original:
                with open(backup_path, 'r') as backup:
                    if original.read() != backup.read():
                        raise Exception("Backup verification failed")

        # Clean old backups
        backups = sorted([f for f in os.listdir(BACKUP_FOLDER) if f.startswith(filename[:-3])])
        if len(backups) > MAX_BACKUPS:
            for old_backup in backups[:-MAX_BACKUPS]:
                os.remove(os.path.join(BACKUP_FOLDER, old_backup))

    except Exception as e:
        logger.error(f"  ❌ Backup failed: {e}")
        raise

def add_to_review_queue(file_path: str, ai_result: Dict[str, Any], confidence: float):
    """Add low confidence file to review queue"""
    if not ENABLE_REVIEW_QUEUE:
        return

    # Create review queue directory
    if not os.path.exists(REVIEW_QUEUE_PATH):
        os.makedirs(REVIEW_QUEUE_PATH)

    filename = os.path.basename(file_path)
    review_filename = f"REVIEW_{filename}"
    review_path = os.path.join(REVIEW_QUEUE_PATH, review_filename)

    # Create review file with analysis details
    review_content = f"""# 🔍 REVIEW REQUIRED: {filename}

## ⚠️ Low Confidence Analysis
**Confidence Score:** {confidence:.1%} (below {CONFIDENCE_THRESHOLD:.1%} threshold)
**Original File:** {file_path}
**Review Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 🤖 AI Analysis Results
**MOC Category:** {ai_result.get('moc_category', 'Unknown')}
**Primary Topic:** {ai_result.get('primary_topic', 'Unknown')}
**Confidence:** {confidence:.1%}
**Reasoning:** {ai_result.get('reasoning', 'No reasoning provided')}

## 🏷️ Suggested Tags
{chr(10).join([f'- {tag}' for tag in ai_result.get('hierarchical_tags', [])])}

## 🔗 Suggested Siblings
{chr(10).join([f'- {note}' for note in ai_result.get('sibling_notes', [])])}

## 💡 Key Concepts
{chr(10).join([f'- {concept}' for concept in ai_result.get('key_concepts', [])])}

## 📝 Manual Review Required
Please review the AI analysis above and determine if the categorization is correct.
You may need to:
1. Adjust the MOC category
2. Modify the tags
3. Update the sibling links
4. Correct the key concepts

## ✅ After Review
Once you've reviewed and corrected the analysis, you can:
1. Move this file back to the main processing queue
2. Update the confidence score manually
3. Process the file with the corrected metadata
"""

    try:
        with open(review_path, 'w', encoding='utf-8') as f:
            f.write(review_content)
        logger.info(f"  📝 Review file created: {review_filename}")
    except Exception as e:
        logger.info(f"  ❌ Failed to create review file: {e}")

def process_conversation(
    file_path: str,
    existing_notes: Dict[str, str],
    stats: Dict,
    note_corpus: Optional[Dict[str, str]] = None,
) -> bool:
    """Process single conversation file with enhanced error handling"""

    filename = os.path.basename(file_path)

    # Check if already processed
    if file_path in progress_data['processed_files']:
        stats['already_processed'] += 1
        return False
    file_start_time = time.time()
    filename = os.path.basename(file_path)

    # Check if already processed (thread-safe)
    with progress_lock:
        if file_path in progress_data['processed_files']:
            stats['already_processed'] += 1
            return False

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        logger.error(f"  ❌ Could not read {filename}: {e}")
        analytics['error_types']['file_read_error'] = analytics['error_types'].get('file_read_error', 0) + 1
        if dashboard:
            dashboard.add_error("file_read_error", f"Could not read {filename}")
        return False

    # Check if already processed (has proper structure)
    if '## 📊 METADATA' in content and '## 🔗 WIKI STRUCTURE' in content:
        has_parent = re.search(r'Parent: \[\[📍.*MOC\]\]', content)
        if has_parent:
            logger.info(f"  ⏭️  Already processed - skipping")
            stats['already_processed'] += 1
            with progress_lock:
                progress_data['processed_files'].add(file_path)
            return False

    # Analyze with AI or Fast Dry Run
    print(f"\n📄 {filename}")
    logger.info(f"\n📄 {filename}")

    if FAST_DRY_RUN:
        logger.info("  ⚡ Fast analysis (no AI)...")
        ai_result = fast_dry_run_analysis(content, file_path)
    else:
        logger.info("  🤖 Analyzing with balanced AI...")
        ai_result = None
        for attempt in range(MAX_RETRIES):
            try:
                ai_result = analyze_with_balanced_ai(content, existing_notes)
                if ai_result:
                    break
            except Exception as e:
                logger.warning(f"  ⚠️  Attempt {attempt + 1} failed: {e}")
                analytics['retry_attempts'] += 1
                if attempt < MAX_RETRIES - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff

    if not ai_result:
        stats['failed'] += 1
        analytics['error_types']['ai_analysis_failed'] = analytics['error_types'].get('ai_analysis_failed', 0) + 1
        with progress_lock:
            progress_data['failed_files'].add(file_path)
        if dashboard:
            dashboard.add_error("ai_analysis_failed", f"Failed to analyze {filename}")
            dashboard.add_activity(f"Failed: {filename}", success=False)
        return False

    confidence = ai_result.get('confidence_score', 0)
    logger.info(f"  ✓ Confidence: {confidence:.0%}")
    logger.info(f"  ✓ MOC: {ai_result.get('moc_category')}")
    logger.info(f"  ✓ Reasoning: {ai_result.get('reasoning', 'N/A')[:80]}...")

    logger.info(f"  ✓ Confidence: {confidence:.0%}")
    logger.info(f"  ✓ MOC: {ai_result.get('moc_category')}")
    logger.info(f"  ✓ Reasoning: {ai_result.get('reasoning', 'N/A')[:80]}...")

    # Check confidence threshold
    if confidence < CONFIDENCE_THRESHOLD:
        logger.info(f"  ⚠️  LOW CONFIDENCE: {confidence:.0%} < {CONFIDENCE_THRESHOLD:.0%} threshold")
        logger.info(f"  📋 Flagging for manual review...")

        # Add to review queue
        if ENABLE_REVIEW_QUEUE:
            add_to_review_queue(file_path, ai_result, confidence)
            analytics['review_queue_count'] = analytics.get('review_queue_count', 0) + 1
            logger.info(f"  📝 Added to review queue: {REVIEW_QUEUE_PATH}")

        # Track low confidence files
        analytics['low_confidence_files'] = analytics.get('low_confidence_files', 0) + 1

    # Track MOC distribution
    moc_category = ai_result.get('moc_category', 'Life & Misc')
    analytics['moc_distribution'][moc_category] = analytics['moc_distribution'].get(moc_category, 0) + 1

    if dashboard:
        dashboard.add_moc_category(moc_category)
    
    # Extract components
    primary_topic = ai_result.get('primary_topic', 'Unknown')
    hierarchical_tags = ai_result.get('hierarchical_tags', [])
    key_concepts = ai_result.get('key_concepts', [])
    sibling_notes = ai_result.get('sibling_notes', [])

    embedding_scores: Dict[str, float] = ai_result.get('embedding_similarity_scores', {})
    if EMBEDDING_ENABLED and embedding_manager and note_corpus is not None:
        similar_notes = embedding_manager.find_similar_notes(
            file_path,
            content,
            note_corpus,
        )
        embedding_scores.update({note: score for note, score in similar_notes})

        for candidate, _ in similar_notes:
            if candidate not in sibling_notes:
                sibling_notes.append(candidate)

        with analytics_lock:
            analytics['embedding_candidates'] += len(similar_notes)

    # Extract main content (before any existing footer)
    main_content = re.split(r'\n---\n## 📊 METADATA', content)[0].strip()

    ranked_siblings = rank_sibling_candidates(
        main_content,
        sibling_notes,
        existing_notes,
        limit=MAX_SIBLINGS,
        embedding_scores=embedding_scores,
    )
    verified_siblings = [f"[[{note}]] ({score:.0%})" for note, score in ranked_siblings]

    if ranked_siblings:
        with analytics_lock:
            analytics['link_quality_scores'].extend(score for _, score in ranked_siblings)
            source_node = Path(file_path).stem
            for note, score in ranked_siblings:
                edge = {
                    'source': source_node,
                    'target': note,
                    'score': score,
                    'via_embedding': note in embedding_scores and embedding_scores[note] >= score,
                }
                if edge['via_embedding']:
                    analytics['embedding_links'] += 1
                analytics['knowledge_graph_edges'].append(edge)

    # Build footer sections
    parent_moc = MOCS.get(moc_category, MOCS['Life & Misc'])

    metadata_section = f"""## 📊 METADATA

Primary Topic: {primary_topic}
Topic Area: {moc_category}
Confidence: {confidence:.0%}"""

    wiki_section = f"""## 🔗 WIKI STRUCTURE

Parent: [[{parent_moc}]]
Siblings: {' · '.join(verified_siblings) if verified_siblings else 'None yet'}
Children: None yet"""

    concepts_section = f"""## 💡 KEY CONCEPTS

{chr(10).join([f'- {concept}' for concept in key_concepts[:8]])}"""

    tags_section = f"""## 🏷️ TAGS

{' '.join([f'#{tag}' for tag in hierarchical_tags[:5]])}"""

    # Build new complete content
    new_content = f"""{main_content}

---
{metadata_section}

---
{wiki_section}

---
{concepts_section}

---
{tags_section}
"""

    # Show results
    logger.info(f"  🏷️  Tags: {len(hierarchical_tags)}")
    logger.info(f"  🔗 Siblings: {len(verified_siblings)}")
    logger.info(f"  🏷️  Tags: {len(hierarchical_tags)}")
    logger.info(f"  🔗 Siblings: {len(verified_siblings)}")

    # Backup and write
    if not DRY_RUN:
        try:
            # Create new file instead of overwriting
            base_name = os.path.splitext(file_path)[0]
            new_file_path = f"{base_name}_linked.md"

            # Create backup of original
            backup_file(file_path)

            # Write new file
            with open(new_file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)

            stats['processed'] += 1
            stats['links_added'] += len(verified_siblings)
            stats['tags_added'] += len(hierarchical_tags)
            progress_data['processed_files'].add(file_path)

            logger.info(f"  📄 Created new file: {os.path.basename(new_file_path)}")
            logger.info("  ✅ File updated")
            with progress_lock:
                progress_data['processed_files'].add(file_path)

            logger.info(f"  📄 Created new file: {os.path.basename(new_file_path)}")
            logger.info("  ✅ File updated")

            # Track success
            if dashboard:
                dashboard.add_activity(f"Processed: {filename}", success=True)
        except Exception as e:
            logger.error(f"  ❌ Failed to update file: {e}")
            analytics['error_types']['file_write_error'] = analytics['error_types'].get('file_write_error', 0) + 1
            if dashboard:
                dashboard.add_error("file_write_error", f"Failed to write {filename}")
                dashboard.add_activity(f"Write failed: {filename}", success=False)
            return False
    else:
        stats['would_process'] += 1
        logger.info("  🔥 DRY RUN - No changes made")
        logger.info("  🔥 DRY RUN - No changes made")

    # Track file processing time
    if dashboard:
        processing_time = time.time() - file_start_time
        file_size_kb = len(content) / 1024
        dashboard.add_file_processing_time(file_size_kb, processing_time)

    # Update incremental tracker with file hash
    if INCREMENTAL_PROCESSING and hash_tracker:
        with hash_tracker_lock:
            hash_tracker.update_hash(file_path, success=True)
        persist_hash_tracker_state()

    return True

def process_batch(
    files: List[str],
    existing_notes: Dict[str, str],
    stats: Dict,
    note_corpus: Optional[Dict[str, str]] = None,
) -> Dict:
    """Process a batch of files"""
    batch_stats = {
        'processed': 0,
        'already_processed': 0,
        'failed': 0,
        'would_process': 0,
        'links_added': 0,
        'tags_added': 0
    }

    for file_path in files:
        if process_conversation(file_path, existing_notes, batch_stats, note_corpus):
            batch_stats['processed'] += 1

    return batch_stats

def order_files(files: List[str], ordering: str) -> List[str]:
    """Order files based on the specified ordering method"""
    if ordering == 'recent':
        # Sort by modification time (newest first)
        return sorted(files, key=lambda f: os.path.getmtime(f), reverse=True)
    elif ordering == 'oldest':
        # Sort by modification time (oldest first)
        return sorted(files, key=lambda f: os.path.getmtime(f), reverse=False)
    elif ordering == 'smallest':
        # Sort by file size (smallest first) - perfect for testing!
        return sorted(files, key=lambda f: os.path.getsize(f), reverse=False)
    elif ordering == 'largest':
        # Sort by file size (largest first)
        return sorted(files, key=lambda f: os.path.getsize(f), reverse=True)
    elif ordering == 'random':
        # Random order
        import random
        random.shuffle(files)
        return files
    elif ordering == 'alphabetical':
        # Alphabetical order
        return sorted(files)
    else:
        # Default to original order
        return files

def show_progress(current_file: str, stage: str, processed: int, total: int, start_time: datetime) -> None:
    """Show progress information"""
    elapsed = datetime.now() - start_time
    elapsed_str = str(elapsed).split('.')[0]  # Remove microseconds

    if processed > 0:
        speed = processed / (elapsed.total_seconds() / 60)  # files per minute
        remaining = total - processed
        if speed > 0:
            eta_minutes = remaining / speed
            eta_str = f"{eta_minutes:.0f}min" if eta_minutes < 60 else f"{eta_minutes/60:.1f}h"
        else:
            eta_str = "∞"
    else:
        speed = 0
        eta_str = "∞"

    progress_pct = (processed / total * 100) if total > 0 else 0

    print(f"\r📊 Progress: {processed}/{total} ({progress_pct:.1f}%) | "
          f"⏱️ {elapsed_str} | 🏃 {speed:.1f}/min | ⏳ {eta_str} | "
          f"📁 {current_file[:30]}... | 🔄 {stage}", end="", flush=True)

def generate_analytics_report() -> None:
    """Generate comprehensive analytics report"""
    if not ANALYTICS_ENABLED:
        return

    analytics['end_time'] = datetime.now()
    analytics['processing_time'] = (analytics['end_time'] - analytics['start_time']).total_seconds()

    # Save analytics
    analytics_file = config.get('analytics_file', 'processing_analytics.json')
    with open(analytics_file, 'w') as f:
        json.dump(analytics, f, indent=2, default=str)

    # Persist knowledge graph edges for downstream visualization
    if analytics.get('knowledge_graph_edges'):
        nodes = sorted({edge['source'] for edge in analytics['knowledge_graph_edges']} |
                       {edge['target'] for edge in analytics['knowledge_graph_edges']})
        graph_payload = {
            'nodes': nodes,
            'edges': analytics['knowledge_graph_edges'],
        }
        graph_file = config.get('knowledge_graph_file', KNOWLEDGE_GRAPH_FILE)
        with open(graph_file, 'w', encoding='utf-8') as graph_f:
            json.dump(graph_payload, graph_f, indent=2)
        logger.info(
            "🌐 Knowledge graph exported to %s (%s nodes, %s edges)",
            graph_file,
            len(nodes),
            len(graph_payload['edges']),
        )

    # Generate HTML report if explicitly requested
    if not config.get('generate_report', True):
        logger.info("Skipping HTML analytics report; CLI dashboard already provides live metrics."
                    " Set generate_report: true to enable HTML output.")
        return

    html_report = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Obsidian Auto-Linker Analytics Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; }}
        .header {{ background: #f0f0f0; padding: 20px; border-radius: 5px; }}
        .metric {{ margin: 10px 0; }}
        .chart {{ background: #f9f9f9; padding: 20px; margin: 20px 0; border-radius: 5px; }}
        .moc-dist {{ display: flex; flex-wrap: wrap; gap: 10px; }}
        .moc-item {{ background: #e3f2fd; padding: 10px; border-radius: 3px; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>📊 Obsidian Auto-Linker Analytics Report</h1>
        <p>Generated: {analytics['end_time']}</p>
    </div>

    <div class="chart">
        <h2>📈 Processing Summary</h2>
        <div class="metric"><strong>Total Files:</strong> {analytics['total_files']}</div>
        <div class="metric"><strong>Processed:</strong> {analytics['processed_files']}</div>
        <div class="metric"><strong>Skipped:</strong> {analytics['skipped_files']}</div>
        <div class="metric"><strong>Failed:</strong> {analytics['failed_files']}</div>
        <div class="metric"><strong>Processing Time:</strong> {analytics['processing_time']:.1f} seconds</div>
        <div class="metric"><strong>Low Confidence Files:</strong> {analytics.get('low_confidence_files', 0)}</div>
        <div class="metric"><strong>Review Queue:</strong> {analytics.get('review_queue_count', 0)} files flagged for manual review</div>
        <div class="metric"><strong>Link Quality:</strong> avg {analytics['link_quality_summary']['average']*100:.0f}% • best {analytics['link_quality_summary']['best']*100:.0f}% • {analytics['link_quality_summary']['count']} ranked links</div>
        <div class="metric"><strong>Embedding Links:</strong> {analytics.get('embedding_links', 0)} (corpus {analytics.get('embedding_corpus_size', 0)} notes)</div>
        <div class="metric"><strong>Knowledge Graph Edges:</strong> {len(analytics.get('knowledge_graph_edges', []))}</div>
    </div>

    <div class="chart">
        <h2>🏷️ MOC Distribution</h2>
        <div class="moc-dist">
            {''.join([f'<div class="moc-item">{moc}: {count}</div>' for moc, count in analytics['moc_distribution'].items()])}
        </div>
    </div>

    <div class="chart">
        <h2>⚡ Performance Metrics</h2>
        <div class="metric"><strong>Cache Hits:</strong> {analytics['cache_hits']}</div>
        <div class="metric"><strong>Cache Misses:</strong> {analytics['cache_misses']}</div>
        <div class="metric"><strong>Cache Evictions:</strong> {analytics.get('cache_evictions', 0)}</div>
        <div class="metric"><strong>Retry Attempts:</strong> {analytics['retry_attempts']}</div>
    </div>

    <div class="chart">
        <h2>📝 Incremental Processing</h2>
        <div class="metric"><strong>Skipped (unchanged):</strong> {analytics['incremental_summary']['unchanged_files']} files ({analytics['incremental_summary']['skip_rate']}% skip rate)</div>
        <div class="metric"><strong>Changed:</strong> {analytics['incremental_summary']['changed_files']} files</div>
        <div class="metric"><strong>New:</strong> {analytics['incremental_summary']['new_files']} files</div>
        <div class="metric"><strong>Deleted (cleanup):</strong> {analytics['incremental_summary']['deleted_files']} files</div>
        <div class="metric"><strong>Total Tracked:</strong> {analytics['incremental_summary']['total_tracked_files']} files</div>
    </div>

    <div class="chart">
        <h2>❌ Error Summary</h2>
        {''.join([f'<div class="metric"><strong>{error}:</strong> {count}</div>' for error, count in analytics['error_types'].items()])}
    </div>
</body>
</html>
"""

    with open('analytics_report.html', 'w') as f:
        f.write(html_report)

    logger.info(f"📊 Analytics report saved to: analytics_report.html")

def process_file_wrapper(
    file_path,
    existing_notes,
    stats,
    hash_tracker,
    note_corpus,
    file_num,
    total_files,
    start_time,
):
    """
    Thread-safe wrapper for processing a single file
    Used by ThreadPoolExecutor for parallel processing

    Args:
        file_path: Path to file to process
        existing_notes: Dictionary of existing notes
        stats: Statistics dictionary (will be updated with lock)
        hash_tracker: FileHashTracker instance
        file_num: Current file number (for progress display)
        total_files: Total number of files
        start_time: Processing start time

    Returns:
        Tuple of (file_path, success, skip_reason, thread_name)
    """
    current_file = os.path.basename(file_path)

    try:
        # Check if file has changed (incremental processing)
        if INCREMENTAL_PROCESSING and hash_tracker and not FORCE_REPROCESS:
            with hash_tracker_lock:
                if not hash_tracker.has_changed(file_path):
                    logger.info(f"  ⏭️  {current_file}: Skipping (unchanged)")
                    with progress_lock:
                        stats['already_processed'] += 1
                    with analytics_lock:
                        analytics['skipped_unchanged'] += 1
                    set_file_stage(file_path, 'completed')  # Mark as completed (unchanged)
                    return (file_path, True, 'unchanged', threading.current_thread().name)

        # Set stage: analyzing
        set_file_stage(file_path, 'analyzing')

        # Show progress
        show_progress(current_file, "Processing", file_num, total_files, start_time)

        # Process the file (this includes linking)
        set_file_stage(file_path, 'linking')
        file_processed = process_conversation(
            file_path,
            existing_notes,
            stats,
            note_corpus,
        )

        # Update hash tracker after processing
        if INCREMENTAL_PROCESSING and hash_tracker:
            with hash_tracker_lock:
                hash_tracker.update_hash(file_path, success=file_processed)
            persist_hash_tracker_state()

        if file_processed:
            set_file_stage(file_path, 'completed')
            show_progress(current_file, "Completed", file_num, total_files, start_time)
            return (file_path, True, None, threading.current_thread().name)
        else:
            set_file_stage(file_path, 'completed')  # Still mark as completed even if skipped
            show_progress(current_file, "Skipped", file_num, total_files, start_time)
            return (file_path, False, 'skipped', threading.current_thread().name)

    except Exception as e:
        logger.error(f"❌ Error processing {current_file}: {e}")
        set_file_stage(file_path, 'failed')
        with progress_lock:
            stats['failed'] += 1
        return (file_path, False, f'error: {e}', threading.current_thread().name)


def bootstrap_runtime(log_level: str = "INFO") -> RuntimeConfig:
    """Initialize logging and one-time runtime settings.

    This keeps the legacy runner compatible with the packaged CLI by
    ensuring logging is configured and configuration is loaded exactly
    once, even if multiple entrypoints call into this module.
    """

    global _BOOTSTRAPPED

    if _BOOTSTRAPPED:
        return runtime_config

    with _BOOTSTRAP_LOCK:
        if not _BOOTSTRAPPED:
            setup_logging(log_level=log_level)
            logger.info(
                "Runtime bootstrap complete (vault=%s, parallel=%s, dashboard=%s)",
                VAULT_PATH,
                PARALLEL_PROCESSING_ENABLED,
                False,
            )
            _BOOTSTRAPPED = True

    return runtime_config


def main(enable_dashboard: bool = False, dashboard_update_interval: int = 15) -> None:
    """Enhanced main processing function"""
    global dashboard, claude_client, hash_tracker, embedding_manager, note_corpus

    runtime_cfg = bootstrap_runtime()
    context = create_processing_context(
        enable_dashboard=enable_dashboard,
        dashboard_update_interval=dashboard_update_interval,
        config_obj=runtime_cfg,
    )
    dashboard = context.dashboard

    logger.info("=" * 60)
    logger.info("🚀 ENHANCED OBSIDIAN VAULT AUTO-LINKER")
    # Declare global variables for interactive mode
    global DRY_RUN, BATCH_SIZE, OLLAMA_MODEL, FILE_ORDERING

    logger.info("=" * 60)
    logger.info("🚀 ENHANCED OBSIDIAN VAULT AUTO-LINKER")
    if FAST_DRY_RUN:
        logger.info("   ⚡ FAST DRY RUN MODE - No AI Analysis")
    elif DRY_RUN:
        logger.info("   🔍 DRY RUN MODE - Full AI Analysis")
    else:
        logger.info("   🚀 LIVE MODE - Processing Files")
    logger.info("=" * 60)
    logger.info("")

    # Initialize analytics
    analytics['start_time'] = datetime.now()

    # Load progress and cache
    load_progress()
    load_cache()

    # Initialize incremental processing tracker
    hash_tracker = None
    if INCREMENTAL_PROCESSING:
        hash_tracker = create_hash_tracker(config)
        logger.info(f"📝 Incremental processing enabled")
        cleaned = hash_tracker.clean_deleted_files()
        if cleaned:
            logger.info(f"   🧹 Removed {cleaned} deleted files from tracker")
        logger.info(f"   Tracking {len(hash_tracker)} files from previous runs")
        if FORCE_REPROCESS:
            logger.info(f"   ⚠️  Force reprocess enabled - will process all files")

    # Initialize stats
    stats = {
        'processed': 0,
        'already_processed': 0,
        'failed': 0,
        'would_process': 0,
        'links_added': 0,
        'tags_added': 0
    }

    # Progress tracking
    start_time = datetime.now()
    processed_count = 0

    # Test AI provider connection first
    logger.info(f"🔍 Testing {AI_PROVIDER.upper()} connection...")
    if AI_PROVIDER == 'ollama':
        logger.info("   ⏳ This may take 2-3 minutes for local models (this is normal)...")

    test_response = call_ai_provider("Hello", "You are a helpful assistant.", context=context)
    if not test_response:
        if AI_PROVIDER == 'claude':
            logger.error("❌ Claude API connection failed. Please check your API key and internet connection.")
            logger.info("   Set claude_api_key in config.yaml or ANTHROPIC_API_KEY env var")
        else:
            logger.error("❌ Ollama connection failed. Please check if Ollama is running and the model is loaded.")
            logger.info("   Try: ollama serve")
            logger.info(f"   Then: ollama pull {OLLAMA_MODEL}")
        return

    if AI_PROVIDER == 'claude':
        logger.info(f"✅ Claude API connection successful")
        logger.info(f"   🤖 Using model: {CLAUDE_MODEL}")
        logger.info(f"   ⚡ Claude is fast (5-10 seconds per file)")
        logger.info(f"   ⏱️  Timeout: {CLAUDE_TIMEOUT}s")
        logger.info(f"   📝 Max tokens: {CLAUDE_MAX_TOKENS}")
    else:
        logger.info("✅ Ollama connection successful")
        logger.info("   🐌 Note: Local models are slow (2-3 minutes per file is normal)")
        logger.info(f"   🤖 Using model: {OLLAMA_MODEL}")
        logger.info(f"   ⏱️  Base timeout: {OLLAMA_TIMEOUT}s (extended for complex reasoning)")
        logger.info(f"   🔄 Max retries: {OLLAMA_MAX_RETRIES} (progressive timeouts: +3min per retry)")
        logger.info(f"   📝 Max tokens: {OLLAMA_MAX_TOKENS} (detailed responses)")
        logger.info(f"   🧠 Extended timeouts prevent reasoning interruptions")

    if testing_mode:
        logger.info("Testing mode enabled – exiting after provider connectivity checks")
        return

    if EMBEDDING_ENABLED:
        logger.info("🔍 Probing embedding backend at %s...", EMBEDDING_BASE_URL)
        if not verify_embedding_backend(EMBEDDING_BASE_URL, EMBEDDING_MODEL):
            logger.error("Embedding check failed; start the embeddings host or set embedding_enabled: false in config.yaml")
            return

    # Scan vault
    logger.info("🔍 Scanning vault...")
    logger.info(f"   Vault path: {VAULT_PATH}")
    existing_notes = get_all_notes(VAULT_PATH)
    logger.info(f"   Found {len(existing_notes)} existing notes")

    # Prepare embedding manager and corpus for hybrid similarity
    if EMBEDDING_ENABLED:
        with embedding_lock:
            embedding_manager = EmbeddingManager({
                'embedding_base_url': EMBEDDING_BASE_URL,
                'embedding_model': EMBEDDING_MODEL,
                'embedding_enabled': EMBEDDING_ENABLED,
                'embedding_similarity_threshold': EMBEDDING_THRESHOLD,
                'embedding_top_k': EMBEDDING_TOP_K,
                'vault_path': VAULT_PATH,
            })
            note_corpus = load_note_corpus(VAULT_PATH)
            analytics['embedding_corpus_size'] = len(note_corpus)
            logger.info(
                "🧠 Embedding similarity enabled (%s, %.0f%% threshold, top %s). Corpus: %s notes",
                EMBEDDING_MODEL,
                EMBEDDING_THRESHOLD * 100,
                EMBEDDING_TOP_K,
                len(note_corpus),
            )

    # Create MOC notes if needed
    logger.info("\n📚 Checking MOC notes...")
    for moc_name in MOCS.keys():
        create_moc_note(moc_name, VAULT_PATH)

    # Find conversation files
    logger.info("\n🔎 Finding conversation files...")
    all_files = []
    for root, dirs, files in os.walk(VAULT_PATH):
        if config.get('backup_folder', '_backups') in root:
            continue
        for file in files:
            if file.endswith('.md') and not file.startswith(('📍', 'MOC')):
                file_path = os.path.join(root, file)
                if should_process_file(file_path):
                    all_files.append(file_path)

    # Filter out already processed files
    if RESUME_ENABLED:
        all_files = [f for f in all_files if f not in progress_data['processed_files']]

    # Filter out unchanged files (incremental processing for 90% faster reruns)
    if INCREMENTAL_PROCESSING and hash_tracker and not FORCE_REPROCESS:
        logger.info("🔍 Checking for unchanged files (incremental processing)...")
        filtered_files = []
        skipped_unchanged = 0
        total_before = len(all_files)

        for file_path in all_files:
            try:
                if hash_tracker.has_changed(file_path):
                    filtered_files.append(file_path)
                else:
                    skipped_unchanged += 1
                    logger.debug(f"  ⏭️  Unchanged: {os.path.basename(file_path)}")
            except Exception as e:
                # If we can't read file, include it for processing
                logger.warning(f"  ⚠️  Could not read {file_path} for hash check: {e}")
                filtered_files.append(file_path)

        all_files = filtered_files

        if skipped_unchanged > 0:
            percentage_skipped = (skipped_unchanged / total_before * 100) if total_before > 0 else 0
            logger.info(f"✅ Incremental: Skipped {skipped_unchanged}/{total_before} unchanged files ({percentage_skipped:.1f}%)")
            logger.info(f"   ⚡ Incremental processing: {skipped_unchanged} files unchanged, processing {len(all_files)} files")
            logger.info(f"   💡 This saves ~{skipped_unchanged * 2.5:.1f} minutes of processing time!")

            # Update analytics
            analytics['skipped_unchanged'] = skipped_unchanged
        else:
            logger.info("📊 Incremental: All files changed or first run")
    elif FORCE_REPROCESS:
        logger.info("🔄 Force reprocess enabled - processing all files")

    # Order files based on configuration
    logger.info(f"📋 Ordering files by: {FILE_ORDERING}")
    all_files = order_files(all_files, FILE_ORDERING)

    logger.info(f"   Found {len(all_files)} markdown files to process")

    # Set total files for progress tracking
    total_files = len(all_files)

    # Estimate processing time for slow local models
    if len(all_files) > 0:
        estimated_time_per_file = 2.5  # minutes per file for local models
        total_estimated_minutes = len(all_files) * estimated_time_per_file
        total_estimated_hours = total_estimated_minutes / 60

        if total_estimated_hours >= 1:
            logger.info(f"   ⏰ Estimated time: {total_estimated_hours:.1f} hours (local models are slow)")
        else:
            logger.info(f"   ⏰ Estimated time: {total_estimated_minutes:.0f} minutes (local models are slow)")
        logger.info("   💡 Tip: You can stop and resume processing anytime")
    
    # Interactive mode checks
    if INTERACTIVE_MODE and not DRY_RUN:
        if len(all_files) > 100 and config.get('confirm_large_batches', True):
            try:
                response = input(f"\n⚠️  Found {len(all_files)} files to process. Continue? (y/N): ")
                if response.lower() != 'y':
                    logger.info("❌ Processing cancelled by user")
                    return
            except EOFError:
                # Running in non-interactive mode (like from web GUI)
                logger.warning(f"⚠️  Found {len(all_files)} files to process. Auto-continuing...")
                pass

    if INTERACTIVE_MODE:
        try:
            print("\n" + "=" * 60)
            print("🎛️  INTERACTIVE CONFIGURATION")
            logger.info("=" * 60)

            # Ask for run type
            print(f"\n📊 Found {len(all_files)} files to process")
            print("\n🔧 Configuration Options:")
            print("1. 🧪 Dry Run (safe - no changes)")
            print("2. 🚀 Real Processing (modifies files)")
            print("3. 📝 Custom Settings")
            print("4. 🐣 Start with Smallest Files (quick test)")
            print("5. ❌ Cancel")

            choice = input("\nChoose option (1-5): ").strip()

            if choice == "1":
                logger.info("✅ Selected: Dry Run Mode")
                # Keep dry_run = True
            elif choice == "2":
                logger.info("✅ Selected: Real Processing Mode")
                logger.warning("⚠️  WARNING: This will modify your files!")
                confirm = input("Are you sure? Type 'YES' to continue: ")
                if confirm != "YES":
                    print("❌ Real processing cancelled")
                    return
                # Set dry_run = False
                DRY_RUN = False
            elif choice == "3":
                print("\n🔧 Custom Settings:")

                # Batch size
                batch_input = input(f"Batch size (current: {BATCH_SIZE}): ").strip()
                if batch_input:
                    try:
                        BATCH_SIZE = int(batch_input)
                        logger.info(f"✅ Batch size set to: {BATCH_SIZE}")
                    except ValueError:
                        print("⚠️  Invalid batch size, keeping current")

                # Model selection
                print(f"\nCurrent model: {OLLAMA_MODEL}")
                print("Available models: qwen3:8b, qwen2.5:3b")
                model_input = input("Model (press Enter to keep current): ").strip()
                if model_input in ["qwen3:8b", "qwen2.5:3b"]:
                    OLLAMA_MODEL = model_input
                    logger.info(f"✅ Model set to: {OLLAMA_MODEL}")
                elif model_input:
                    print("⚠️  Invalid model, keeping current")

                # File ordering
                print(f"\nCurrent file ordering: {FILE_ORDERING}")
                print("Available options: recent, oldest, smallest, largest, random, alphabetical")
                order_input = input("File ordering (press Enter to keep current): ").strip()
                if order_input in ["recent", "oldest", "smallest", "largest", "random", "alphabetical"]:
                    FILE_ORDERING = order_input
                    logger.info(f"✅ File ordering set to: {FILE_ORDERING}")
                elif order_input:
                    print("⚠️  Invalid ordering, keeping current")

                # Run type
                run_type = input("\nRun type (dry/real): ").strip().lower()
                if run_type == "real":
                    print("⚠️  WARNING: Real processing will modify files!")
                    confirm = input("Are you sure? Type 'YES' to continue: ")
                    if confirm == "YES":
                        DRY_RUN = False
                        print("✅ Real processing enabled")
                    else:
                        print("✅ Keeping dry run mode")
                else:
                    print("✅ Dry run mode confirmed")

            elif choice == "4":
                logger.info("✅ Selected: Start with Smallest Files")
                print("🐣 Perfect for quick testing!")
                FILE_ORDERING = "smallest"
                logger.info(f"✅ File ordering set to: {FILE_ORDERING}")
            elif choice == "5":
                logger.error("❌ Processing cancelled by user")
                return
            else:
                print("⚠️  Invalid choice, using default settings")

            # Final confirmation
            print(f"\n📋 Final Configuration:")
            logger.info(f"   🤖 Model: {OLLAMA_MODEL}")
            logger.info(f"   📦 Batch size: {BATCH_SIZE}")
            logger.info(f"   🧪 Mode: {'Dry Run' if DRY_RUN else 'Real Processing'}")
            logger.info(f"   📁 Files: {len(all_files)}")

            final_confirm = input("\nProceed with these settings? (y/N): ")
            if final_confirm.lower() != 'y':
                logger.error("❌ Processing cancelled by user")
                return

        except EOFError:
            # Running in non-interactive mode (like from web GUI)
            logger.warning(f"⚠️  Auto-continuing with default settings...")
            pass

        # Cost tracking removed for local LLM

    if DRY_RUN:
        logger.info("\n🔥 DRY RUN MODE - No files will be modified")
        logger.info("   Set dry_run: false in config.yaml to process for real\n")
        print("\n🔥 DRY RUN MODE - No files will be modified")
        logger.info(f"   📊 Limited to first {DRY_RUN_LIMIT} files for analysis")
        logger.info("   Set dry_run: false in config.yaml to process for real\n")
    else:
        print(f"\n⚠️  PROCESSING FOR REAL - Backups will be created")
        logger.info(f"   Backups stored in: {BACKUP_FOLDER}\n")

    # Decide processing mode
    if PARALLEL_WORKERS > 1:
        logger.info(f"🚀 Processing files in parallel ({PARALLEL_WORKERS} workers)...\n")
    else:
        logger.info("📝 Processing files sequentially...\n")

    analytics['total_files'] = len(all_files)

    # Initialize dashboard with total files
    if dashboard:
        dashboard.update_processing(
            total_files=len(all_files),
            processed_files=0,
            failed_files=0,
            current_file="Starting...",
            current_stage="Initializing"
        )

    if PARALLEL_WORKERS > 1:
        processed_count = 0
        last_file_name = ""

        with ThreadPoolExecutor(max_workers=PARALLEL_WORKERS) as executor:
            future_to_meta = {}
            for i, file_path in enumerate(all_files, 1):
                if DRY_RUN and i > DRY_RUN_LIMIT:
                    logger.info(f"🛑 DRY RUN LIMIT REACHED ({DRY_RUN_LIMIT} files) - stopping submission")
                    break

                future = executor.submit(
                    process_file_wrapper,
                    file_path,
                    existing_notes,
                    stats,
                    hash_tracker,
                    note_corpus,
                    i,
                    len(all_files),
                    start_time
                )
                future_to_meta[future] = (file_path, i)

            for future in as_completed(future_to_meta):
                file_path, file_num = future_to_meta[future]
                current_file = os.path.basename(file_path)
                last_file_name = current_file

                try:
                    _, success, skip_reason = future.result()
                    if success and skip_reason != 'unchanged':
                        processed_count += 1
                except Exception as e:
                    logger.error(f"❌ Error processing {current_file}: {e}")
                    with progress_lock:
                        stats['failed'] += 1
                    continue

                save_progress()
                with cache_lock:
                    save_cache()
                persist_hash_tracker_state()

                logger.info(f"\n📊 File {file_num} complete:")
                logger.info(f"   ✅ Processed: {stats['processed']}")
                logger.info(f"   ⏭️  Skipped: {stats['already_processed']}")
                logger.info(f"   ❌ Failed: {stats['failed']}")
                logger.info(f"   🔗 Links added: {stats['links_added']}")
                logger.info(f"   🏷️  Tags added: {stats['tags_added']}")

        if dashboard:
            dashboard.update_processing(
                total_files=len(all_files),
                processed_files=processed_count,
                failed_files=stats['failed'],
                current_file=last_file_name or "Complete",
                current_stage="Completed",
            )

    else:
        # SEQUENTIAL PROCESSING MODE
        processed_count = 0

        for i, file_path in enumerate(all_files, 1):
            current_file = os.path.basename(file_path)
            print(f"\n📄 Processing file {i}/{len(all_files)}: {current_file}")

            # Check dry run limit
            if DRY_RUN and i > DRY_RUN_LIMIT:
                print(f"\n🛑 DRY RUN LIMIT REACHED ({DRY_RUN_LIMIT} files)")
                print("=" * 60)
                print("📊 DRY RUN SUMMARY")
                print("=" * 60)
                logger.info(f"✅ Files analyzed: {i-1}")
                logger.info(f"📊 Would process: {stats['would_process']}")
                print(f"⏭️  Already processed: {stats['already_processed']}")
                logger.error(f"❌ Failed: {stats['failed']}")
                logger.warning(f"⚠️  Low confidence files: {analytics.get('low_confidence_files', 0)}")
                logger.info(f"📋 Review queue: {analytics.get('review_queue_count', 0)} files")
                logger.info(f"⏱️  Time elapsed: {datetime.now() - start_time}")

                if DRY_RUN_INTERACTIVE:
                    print(f"\n🎛️  What would you like to do next?")
                    print("1. 🚀 Start REAL processing (modify files)")
                    print("2. 🔍 Continue dry run (analyze more files)")
                    print("3. 📊 Generate analytics report and exit")
                    print("4. ❌ Stop processing")

                    try:
                        choice = input("\nChoose option (1-4): ").strip()

                        if choice == "1":
                            print("⚠️  SWITCHING TO REAL PROCESSING")
                            logger.info("   This will modify your files!")
                            confirm = input("Are you sure? Type 'YES' to continue: ")
                            if confirm == "YES":
                                DRY_RUN = False
                                print("✅ Real processing enabled - continuing with remaining files...")
                            else:
                                print("❌ Real processing cancelled")
                                break
                        elif choice == "2":
                            print("✅ Continuing dry run...")
                            # Continue with dry run (no change needed)
                        elif choice == "3":
                            print("📊 Generating analytics report...")
                            break
                        elif choice == "4":
                            print("❌ Processing stopped by user")
                            break
                        else:
                            print("⚠️  Invalid choice, continuing dry run...")
                    except EOFError:
                        print("⚠️  Non-interactive mode, continuing dry run...")
                else:
                    print("📊 Dry run limit reached - generating analytics report...")
                    break

            # Check if file has changed (incremental processing)
            if INCREMENTAL_PROCESSING and hash_tracker and not FORCE_REPROCESS:
                if not hash_tracker.has_changed(file_path):
                    logger.info(f"  ⏭️  Skipping (unchanged since last run)")
                    stats['already_processed'] += 1
                    with analytics_lock:
                        analytics['skipped_unchanged'] += 1
                    set_file_stage(file_path, 'completed')  # Mark as completed (unchanged)
                    continue

            # Set stage: analyzing
            set_file_stage(file_path, 'analyzing')

            # Show progress
            show_progress(current_file, "Processing", processed_count, total_files, start_time)

            # Process the file (this includes linking)
            set_file_stage(file_path, 'linking')
            file_processed = process_conversation(
                file_path,
                existing_notes,
                stats,
                note_corpus,
            )

            # Update hash tracker after processing
            if INCREMENTAL_PROCESSING and hash_tracker:
                with hash_tracker_lock:
                    hash_tracker.update_hash(file_path, success=file_processed)
                persist_hash_tracker_state()

            if file_processed:
                set_file_stage(file_path, 'completed')
                processed_count += 1
                show_progress(current_file, "Completed", processed_count, total_files, start_time)
            else:
                set_file_stage(file_path, 'completed')  # Still mark as completed even if skipped
                show_progress(current_file, "Skipped", processed_count, total_files, start_time)

            # Save progress after each file
            save_progress()
            save_cache()

            # Show file summary
            print(f"\n📊 File {i} complete:")
            logger.info(f"   ✅ Processed: {stats['processed']}")
            logger.info(f"   ⏭️  Skipped: {stats['already_processed']}")
            logger.info(f"   ❌ Failed: {stats['failed']}")
            logger.info(f"   🔗 Links added: {stats['links_added']}")
            logger.info(f"   🏷️  Tags added: {stats['tags_added']}")
            persist_hash_tracker_state()

        # Update dashboard after processing
        if dashboard:
            dashboard.update_processing(
                total_files=len(all_files),
                processed_files=processed_count,
                failed_files=stats['failed'],
                current_file=current_file,
                current_stage="Completed"
            )
    
    # Update analytics
    analytics['processed_files'] = stats['processed']
    analytics['skipped_files'] = stats['already_processed']
    analytics['failed_files'] = stats['failed']

    # Final report
    logger.info("\n" + "=" * 60)
    logger.info("✅ PROCESSING COMPLETE")
    logger.info("=" * 60)
    if DRY_RUN:
        logger.info(f"📊 Would process: {stats['would_process']} files")
    else:
        logger.info(f"📊 Processed: {stats['processed']} files")
        logger.info(f"📄 New files created: {stats['processed']} (with '_linked' suffix)")
        logger.info(f"🔗 Links added: {stats['links_added']}")
        logger.info(f"🏷️  Tags added: {stats['tags_added']}")
    logger.info(f"⏭️  Already processed: {stats['already_processed']}")
    logger.info(f"❌ Failed: {stats['failed']}")
    logger.info(f"⚠️  Low confidence files: {analytics.get('low_confidence_files', 0)} (below {CONFIDENCE_THRESHOLD:.0%} threshold)")
    logger.info(f"📋 Review queue: {analytics.get('review_queue_count', 0)} files flagged for manual review")
    if analytics['link_quality_scores']:
        avg_quality = sum(analytics['link_quality_scores']) / len(analytics['link_quality_scores'])
        best_quality = max(analytics['link_quality_scores'])
        analytics['link_quality_summary'] = {
            'average': avg_quality,
            'best': best_quality,
            'count': len(analytics['link_quality_scores']),
        }
        logger.info(
            "🔗 Link quality (>= %.0f%% threshold): avg %.0f%% • best %.0f%% • %s ranked links",
            LINK_QUALITY_THRESHOLD * 100,
            avg_quality * 100,
            best_quality * 100,
            len(analytics['link_quality_scores']),
        )
    if EMBEDDING_ENABLED:
        logger.info(
            "🧠 Embedding links: %s (corpus: %s notes, threshold %.0f%%)",
            analytics.get('embedding_links', 0),
            analytics.get('embedding_corpus_size', 0),
            EMBEDDING_THRESHOLD * 100,
        )
        logger.info(
            "🌐 Knowledge graph edges persisted: %s", len(analytics.get('knowledge_graph_edges', []))
        )
    logger.info(
        "🧵 Parallel mode summary: %s (requested=%s, effective=%s)",
        "ON" if PARALLEL_MODE_ACTIVE else "OFF",
        REQUESTED_PARALLEL_WORKERS,
        PARALLEL_EFFECTIVE_WORKERS,
    )
    if hasattr(ai_cache, 'get_stats'):
        cache_stats = ai_cache.get_stats()
        analytics['cache_evictions'] = cache_stats.get('evictions', 0)
        logger.info(
            "💾 Cache usage: %s/%s entries • %.2f/%.2f MB • evictions: %s",
            cache_stats['entries'],
            cache_stats['max_entries'],
            cache_stats['size_mb'],
            cache_stats['max_size_mb'],
            cache_stats.get('evictions', 0),
        )

    # Incremental processing stats
    if INCREMENTAL_PROCESSING and hash_tracker:
        inc_stats = hash_tracker.get_stats()
        analytics['incremental_summary'] = {
            'unchanged_files': inc_stats['unchanged_files'],
            'changed_files': inc_stats['changed_files'],
            'new_files': inc_stats['new_files'],
            'deleted_files': inc_stats['deleted_files'],
            'total_tracked_files': inc_stats['total_tracked_files'],
            'skip_rate': inc_stats['skip_rate'],
        }
        print(f"\n📝 Incremental Processing:")
        logger.info(f"   ⏭️  Skipped (unchanged): {inc_stats['unchanged_files']} files ({inc_stats['skip_rate']}% skip rate)")
        logger.info(f"   🔄 Changed: {inc_stats['changed_files']} files")
        logger.info(f"   ✨ New: {inc_stats['new_files']} files")
        logger.info(f"   💾 Tracking: {inc_stats['total_tracked_files']} files total")

    # Cost tracking removed for local LLM
    print()
    logger.info("")

    # Generate analytics report
    generate_analytics_report()

    
    # Generate ultra detailed analytics with before/after files and reasoning
    try:
        print("\n🚀 Generating ultra detailed analytics...")
        print("📊 Including before/after files and AI reasoning analysis...")
        import subprocess
        result = subprocess.run(['python3', 'ultra_detailed_analytics.py'],
                              capture_output=True, text=True, timeout=120)
        if result.returncode == 0:
            logger.info("✅ Ultra detailed analytics generated!")
            print("🌐 Ultra detailed report will open automatically in your browser")
        else:
            print("⚠️ Ultra detailed analytics failed, using standard report")
            print(f"Error: {result.stderr}")
    except Exception as e:
        logger.warning(f"⚠️ Ultra detailed analytics failed: {e}")
        print("📊 Using standard analytics report")

    if DRY_RUN:
        logger.info("💡 Set dry_run: false in config.yaml to process for real")
    else:
        logger.info(f"💾 Backups saved to: {BACKUP_FOLDER}")

    logger.info("=" * 60)

    # Stop dashboard if running
    if dashboard:
        dashboard.update_processing(
            total_files=len(all_files),
            processed_files=processed_count,
            failed_files=stats['failed'],
            current_file="Complete",
            current_stage="Finished"
        )
        logger.info("\n📊 Dashboard Summary:")
        logger.info(f"   Total Files: {len(all_files)}")
        logger.info(f"   Processed: {processed_count}")
        logger.info(f"   Failed: {stats['failed']}")
        logger.info(f"   Cache Hits: {analytics['cache_hits']}")
        logger.info(f"   Cache Misses: {analytics['cache_misses']}")
        dashboard.stop()

if __name__ == "__main__":
    main()

