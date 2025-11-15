#!/usr/bin/env python3
"""
Enhanced Obsidian Vault Auto-Linker with Advanced Features
Processes conversations and creates MOC-based wiki structure
"""

import os
import re
import sys
import yaml  # pyright: ignore[reportMissingModuleSource]
import json
import shutil
import hashlib
import time
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
import requests
import fnmatch

# Try to import anthropic for Claude API support (optional)
try:
    from anthropic import Anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False
    Anthropic = None

# Add scripts directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'scripts'))
from cache_utils import BoundedCache, create_bounded_cache
from incremental_processing import FileHashTracker, create_hash_tracker

# Load config
try:
    with open('config.yaml', 'r') as f:
        config = yaml.safe_load(f)
    if config is None:
        config = {}
except Exception as e:
    print(f"Error loading config: {e}")
    config = {}
# Import logging and dashboard
from logger_config import get_logger, setup_logging
from live_dashboard import LiveDashboard
from config_utils import (
    load_yaml_config,
    check_ollama_connection,
    load_json_file,
    save_json_file,
    validate_vault_path,
    get_file_size_kb,
    get_file_size_category
)
from cache_utils import BoundedCache, IncrementalTracker

# Initialize logger
logger = get_logger(__name__)

# Load config using utility function
config = load_yaml_config('config.yaml')

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
INCREMENTAL_PROCESSING = config.get('incremental_processing', True)
FORCE_REPROCESS = config.get('force_reprocess', False)
INTERACTIVE_MODE = config.get('interactive_mode', True)
ANALYTICS_ENABLED = config.get('analytics_enabled', True)

# Cache configuration
MAX_CACHE_SIZE_MB = config.get('max_cache_size_mb', 1000)
MAX_CACHE_ENTRIES = config.get('max_cache_entries', 10000)

# Incremental processing configuration
INCREMENTAL_ENABLED = config.get('incremental', False)
INCREMENTAL_TRACKER_FILE = config.get('incremental_tracker_file', '.incremental_tracker.json')
# Quality control settings
CONFIDENCE_THRESHOLD = config.get('confidence_threshold', 0.8)
ENABLE_REVIEW_QUEUE = config.get('enable_review_queue', True)
REVIEW_QUEUE_PATH = config.get('review_queue_path', 'reviews/')

# Dry run settings
DRY_RUN_LIMIT = config.get('dry_run_limit', 10)
DRY_RUN_INTERACTIVE = config.get('dry_run_interactive', True)

# Ollama configuration
OLLAMA_BASE_URL = config.get('ollama_base_url', 'http://localhost:11434')
OLLAMA_MODEL = config.get('ollama_model', 'qwen3:8b')  # Default to Qwen3:8b for maximum accuracy
OLLAMA_TIMEOUT = config.get('ollama_timeout', 300)  # Default 5 minutes for Qwen3:8b
OLLAMA_MAX_RETRIES = config.get('ollama_max_retries', 5)  # More retries for complex reasoning
OLLAMA_TEMPERATURE = config.get('ollama_temperature', 0.1)
OLLAMA_MAX_TOKENS = config.get('ollama_max_tokens', 1024)  # More tokens for detailed responses

def call_ollama(prompt: str, system_prompt: str = "", max_retries: int = None) -> str:
# AI Provider selection (ollama or claude)
AI_PROVIDER = config.get('ai_provider', 'ollama')

# Claude API configuration (only used if ai_provider: claude)
CLAUDE_API_KEY = config.get('claude_api_key', os.environ.get('ANTHROPIC_API_KEY', ''))
CLAUDE_MODEL = config.get('claude_model', 'claude-sonnet-4-5-20250929')
CLAUDE_MAX_TOKENS = config.get('claude_max_tokens', 2048)
CLAUDE_TEMPERATURE = config.get('claude_temperature', 0.1)
CLAUDE_TIMEOUT = config.get('claude_timeout', 60)

# Initialize Claude client if using Claude provider
claude_client = None
if AI_PROVIDER == 'claude':
    if not ANTHROPIC_AVAILABLE:
        print("⚠️  WARNING: anthropic package not installed. Install with: pip install anthropic")
        print("⚠️  Falling back to Ollama provider")
        AI_PROVIDER = 'ollama'
    elif not CLAUDE_API_KEY:
        print("⚠️  WARNING: Claude API key not found in config or ANTHROPIC_API_KEY env var")
        print("⚠️  Falling back to Ollama provider")
        AI_PROVIDER = 'ollama'
    else:
        try:
            claude_client = Anthropic(api_key=CLAUDE_API_KEY)
            print(f"✅ Claude API initialized (model: {CLAUDE_MODEL})")
        except Exception as e:
            print(f"⚠️  WARNING: Failed to initialize Claude API: {e}")
            print("⚠️  Falling back to Ollama provider")
            AI_PROVIDER = 'ollama'

# Cost tracking disabled for local LLM (free to use)

# Global dashboard reference (optional)
dashboard = None

def call_ollama(prompt: str, system_prompt: str = "", max_retries: int = None, track_metrics: bool = True) -> str:
    """Call Ollama API with the given prompt and retry logic"""
    if max_retries is None:
        max_retries = OLLAMA_MAX_RETRIES

    for attempt in range(max_retries):
        start_time = time.time()
        try:
            url = f"{OLLAMA_BASE_URL}/api/generate"

            # Prepare the full prompt
            full_prompt = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt

            payload = {
                "model": OLLAMA_MODEL,
                "prompt": full_prompt,
                "stream": False,
                "options": {
                    "temperature": OLLAMA_TEMPERATURE,  # From config
                    "top_p": 0.8,        # Slightly lower top_p
                    "top_k": 20,          # Limit vocabulary
                    "repeat_penalty": 1.1, # Prevent repetition
                    "num_ctx": 2048,     # Smaller context window
                    "num_predict": OLLAMA_MAX_TOKENS,  # From config
                    "stop": ["```", "\n\n\n"]  # Stop tokens
                }
            }

            # Increase timeout with each retry (for slow local models)
            timeout = OLLAMA_TIMEOUT + (attempt * 60)  # Base + 1min per retry
            
            # Increase timeout with each retry (for complex reasoning)
            timeout = OLLAMA_TIMEOUT + (attempt * 180)  # Base + 3min per retry for Qwen3:8b reasoning
            response = requests.post(url, json=payload, timeout=timeout)
            response.raise_for_status()

            result = response.json()
            return result.get('response', '').strip()

            response_text = result.get('response', '').strip()

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
                logger.warning(f"⏰ Attempt {attempt + 1} timed out ({timeout}s). Local models are slow - retrying in {wait_time}s...")
                print(f"⏰ Attempt {attempt + 1} timed out ({timeout}s). Qwen3:8b needs time for complex reasoning - retrying in {wait_time}s...")
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


def call_claude(prompt: str, system_prompt: str = "", max_retries: int = 3, track_metrics: bool = True) -> str:
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
    if not claude_client:
        logger.error("❌ Claude client not initialized")
        return ""

    for attempt in range(max_retries):
        start_time = time.time()
        try:
            # Call Claude API
            message = claude_client.messages.create(
                model=CLAUDE_MODEL,
                max_tokens=CLAUDE_MAX_TOKENS,
                temperature=CLAUDE_TEMPERATURE,
                system=system_prompt if system_prompt else "You are a helpful assistant.",
                messages=[
                    {"role": "user", "content": prompt}
                ],
                timeout=CLAUDE_TIMEOUT
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


def call_ai_provider(prompt: str, system_prompt: str = "", max_retries: int = None, track_metrics: bool = True) -> str:
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
    if AI_PROVIDER == 'claude':
        if max_retries is None:
            max_retries = 3  # Claude is fast, fewer retries needed
        return call_claude(prompt, system_prompt, max_retries, track_metrics)
    else:
        # Default to Ollama
        if max_retries is None:
            max_retries = OLLAMA_MAX_RETRIES
        return call_ollama(prompt, system_prompt, max_retries, track_metrics)


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
    'cache_misses': 0
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

# Cache for AI responses (BoundedCache with LRU eviction)
ai_cache = create_bounded_cache(config)

# Threading locks for parallel processing
cache_lock = threading.Lock()
progress_lock = threading.Lock()
analytics_lock = threading.Lock()
hash_tracker_lock = threading.Lock()
# Cache for AI responses (bounded with LRU eviction)
ai_cache = BoundedCache(max_size_mb=MAX_CACHE_SIZE_MB, max_entries=MAX_CACHE_ENTRIES)

# Incremental processing tracker
incremental_tracker = IncrementalTracker()

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
                    print(f"📂 Loaded progress: {len(progress_data['processed_files'])} files already processed")
                    if progress_data['file_stages']:
                        stages_summary = {}
                        for filepath, stage_data in progress_data['file_stages'].items():
                            stage = stage_data.get('stage', 'unknown')
                            stages_summary[stage] = stages_summary.get(stage, 0) + 1
                        print(f"   📋 File stages: {dict(stages_summary)}")
                else:
                    progress_data['processed_files'] = set()
                    progress_data['failed_files'] = set()
                    progress_data['current_batch'] = 0
        except (json.JSONDecodeError, ValueError):
            progress_data['processed_files'] = set()
            progress_data['failed_files'] = set()
            progress_data['current_batch'] = 0
        except Exception as e:
            print(f"⚠️  Could not load progress file: {e}")
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
        print(f"⚠️  Could not save progress: {e}")


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


def load_cache():
    """Load AI cache from file (handled by BoundedCache init)"""
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
            print(f"⚠️  Could not load cache: {e}")

        if ai_cache:
            print(f"💾 Loaded cache: {len(ai_cache)} cached responses")
    # Cache is already loaded in create_bounded_cache()
    # Just display info
    cache_size = len(ai_cache)
    if cache_size > 0:
        stats = ai_cache.get_stats()
        print(f"💾 Loaded cache: {cache_size} entries (max: {stats['max_size']})")
        print(f"   Hit rate: {stats['hit_rate']}, Evictions: {stats['evictions']}")
    data = {
        'processed_files': list(progress_data['processed_files']),
        'failed_files': list(progress_data['failed_files']),
        'current_batch': progress_data['current_batch'],
        'last_update': datetime.now().isoformat()
    }
    save_json_file(progress_file, data)

def load_cache() -> None:
    """Load AI cache from file using config_utils"""
    if not CACHE_ENABLED:
        return

    cache_file = config.get('cache_file', '.ai_cache.json')
    cache_data = load_json_file(cache_file, default={})

    if cache_data:
        ai_cache.from_dict(cache_data)
        logger.info(f"💾 Loaded cache: {len(cache_data)} cached responses")

        # Update dashboard with cache stats
        if dashboard:
            cache_stats = ai_cache.get_stats()
            dashboard.update_cache_stats(cache_stats['size_mb'], cache_stats['entries'])

def save_cache() -> None:
    """Save AI cache to file using config_utils"""
    if not CACHE_ENABLED:
        return

    cache_file = config.get('cache_file', '.ai_cache.json')
    try:
        ai_cache.save_to_file(cache_file)
        stats = ai_cache.get_stats()
        print(f"💾 Saved cache: {len(ai_cache)} entries")
        print(f"   Stats - Hits: {stats['hits']}, Misses: {stats['misses']}, Evictions: {stats['evictions']}")
    except Exception as e:
        print(f"⚠️  Could not save cache: {e}")
    cache_data = ai_cache.to_dict()
    save_json_file(cache_file, cache_data)

def load_incremental_tracker() -> None:
    """Load incremental tracker from file"""
    if not INCREMENTAL_ENABLED:
        return

    tracker_data = load_json_file(INCREMENTAL_TRACKER_FILE, default={})
    if tracker_data:
        incremental_tracker.from_dict(tracker_data)
        logger.info(f"📊 Loaded incremental tracker: {len(tracker_data.get('file_hashes', {}))} files tracked")

def save_incremental_tracker() -> None:
    """Save incremental tracker to file"""
    if not INCREMENTAL_ENABLED:
        return

    tracker_data = incremental_tracker.to_dict()
    save_json_file(INCREMENTAL_TRACKER_FILE, tracker_data)

def get_content_hash(content: str) -> str:
    """Generate hash for content caching"""
    return hashlib.md5(content.encode()).hexdigest()

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

def analyze_with_balanced_ai(content: str, existing_notes: Dict[str, str]) -> Optional[Dict]:
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
    if ai_cache.has(content_hash):
        cached_result = ai_cache.get(content_hash)
        analytics['cache_hits'] += 1
        return ai_cache[content_hash]

    analytics['cache_misses'] += 1

        if dashboard:
            lookup_time = time.time() - cache_start
            dashboard.add_cache_hit(lookup_time)
        return cached_result

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
        result_text = call_ollama(prompt, system_prompt)
        result_text = call_ai_provider(prompt, system_prompt)

        if not result_text:
            logger.error(f"❌ Empty response from {AI_PROVIDER.upper()}")
            return None

        # Clean up potential markdown formatting
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
            print(f"  ⚠️  JSON parse error: {e}")
            print(f"  Response was: {result_text[:200]}")
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

        # Cache the result
        ai_cache[content_hash] = result
        with cache_lock:
            ai_cache.set(content_hash, result)
        
        # Cache the result (with automatic LRU eviction if needed)
        ai_cache.set(content_hash, result)

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
        print(f"  📝 Review file created: {review_filename}")
    except Exception as e:
        print(f"  ❌ Failed to create review file: {e}")

def process_conversation(file_path: str, existing_notes: Dict[str, str], stats: Dict) -> bool:
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

    print(f"  ✓ Confidence: {confidence:.0%}")
    print(f"  ✓ MOC: {ai_result.get('moc_category')}")
    print(f"  ✓ Reasoning: {ai_result.get('reasoning', 'N/A')[:80]}...")

    # Check confidence threshold
    if confidence < CONFIDENCE_THRESHOLD:
        print(f"  ⚠️  LOW CONFIDENCE: {confidence:.0%} < {CONFIDENCE_THRESHOLD:.0%} threshold")
        print(f"  📋 Flagging for manual review...")

        # Add to review queue
        if ENABLE_REVIEW_QUEUE:
            add_to_review_queue(file_path, ai_result, confidence)
            analytics['review_queue_count'] = analytics.get('review_queue_count', 0) + 1
            print(f"  📝 Added to review queue: {REVIEW_QUEUE_PATH}")

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

    # Verify sibling notes exist
    verified_siblings = []
    for note in sibling_notes[:MAX_SIBLINGS]:
        if note in existing_notes:
            verified_siblings.append(f"[[{note}]]")

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

    # Extract main content (before any existing footer)
    main_content = re.split(r'\n---\n## 📊 METADATA', content)[0].strip()

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
    print(f"  🏷️  Tags: {len(hierarchical_tags)}")
    print(f"  🔗 Siblings: {len(verified_siblings)}")
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

            print(f"  📄 Created new file: {os.path.basename(new_file_path)}")
            print("  ✅ File updated")
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
        print("  🔥 DRY RUN - No changes made")
        logger.info("  🔥 DRY RUN - No changes made")

    # Track file processing time
    if dashboard:
        processing_time = time.time() - file_start_time
        file_size_kb = len(content) / 1024
        dashboard.add_file_processing_time(file_size_kb, processing_time)

    # Update incremental tracker with file hash
    if INCREMENTAL_ENABLED:
        content_hash = get_content_hash(content)
        incremental_tracker.set_hash(file_path, content_hash)

    return True

def process_batch(files: List[str], existing_notes: Dict[str, str], stats: Dict) -> Dict:
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
        if process_conversation(file_path, existing_notes, batch_stats):
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

    # Generate HTML report
    if config.get('generate_report', True):
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
        <div class="metric"><strong>Retry Attempts:</strong> {analytics['retry_attempts']}</div>
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

        print(f"📊 Analytics report saved to: analytics_report.html")

def process_file_wrapper(file_path, existing_notes, stats, hash_tracker, file_num, total_files, start_time):
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
        Tuple of (file_path, success, skip_reason)
    """
    current_file = os.path.basename(file_path)

    try:
        # Check if file has changed (incremental processing)
        if INCREMENTAL_PROCESSING and hash_tracker and not FORCE_REPROCESS:
            with hash_tracker_lock:
                if not hash_tracker.has_changed(file_path):
                    print(f"  ⏭️  {current_file}: Skipping (unchanged)")
                    with progress_lock:
                        stats['already_processed'] += 1
                    set_file_stage(file_path, 'completed')  # Mark as completed (unchanged)
                    return (file_path, True, 'unchanged')

        # Set stage: analyzing
        set_file_stage(file_path, 'analyzing')

        # Show progress
        show_progress(current_file, "Processing", file_num, total_files, start_time)

        # Process the file (this includes linking)
        set_file_stage(file_path, 'linking')
        file_processed = process_conversation(file_path, existing_notes, stats)

        # Update hash tracker after processing
        if INCREMENTAL_PROCESSING and hash_tracker:
            with hash_tracker_lock:
                hash_tracker.update_hash(file_path, success=file_processed)
                hash_tracker.save()

        if file_processed:
            set_file_stage(file_path, 'completed')
            show_progress(current_file, "Completed", file_num, total_files, start_time)
            return (file_path, True, None)
        else:
            set_file_stage(file_path, 'completed')  # Still mark as completed even if skipped
            show_progress(current_file, "Skipped", file_num, total_files, start_time)
            return (file_path, False, 'skipped')

    except Exception as e:
        print(f"❌ Error processing {current_file}: {e}")
        set_file_stage(file_path, 'failed')
        with progress_lock:
            stats['failed'] += 1
        return (file_path, False, f'error: {e}')


def main():
        logger.info(f"📊 Analytics report saved to: analytics_report.html")

def main(enable_dashboard: bool = False, dashboard_update_interval: int = 15) -> None:
    """Enhanced main processing function"""
    global dashboard

    # Initialize dashboard if requested
    if enable_dashboard:
        dashboard = LiveDashboard(update_interval=dashboard_update_interval)
        dashboard.start()

    logger.info("=" * 60)
    logger.info("🚀 ENHANCED OBSIDIAN VAULT AUTO-LINKER")
    # Declare global variables for interactive mode
    global DRY_RUN, BATCH_SIZE, OLLAMA_MODEL, FILE_ORDERING

    print("=" * 60)
    print("🚀 ENHANCED OBSIDIAN VAULT AUTO-LINKER")
    if FAST_DRY_RUN:
        logger.info("   ⚡ FAST DRY RUN MODE - No AI Analysis")
    elif DRY_RUN:
        logger.info("   🔍 DRY RUN MODE - Full AI Analysis")
    else:
        print("   🚀 LIVE MODE - Processing Files")
    print("=" * 60)
    print()
        logger.info("   🚀 LIVE MODE - Processing Files")
    logger.info("=" * 60)
    logger.info("")

    # Initialize analytics
    analytics['start_time'] = datetime.now()

    # Load progress and cache
    load_progress()
    load_cache()

    # Load progress, cache, and incremental tracker
    load_progress()
    load_cache()

    # Initialize incremental processing tracker
    hash_tracker = None
    if INCREMENTAL_PROCESSING:
        hash_tracker = create_hash_tracker(config)
        print(f"📝 Incremental processing enabled")
        print(f"   Tracking {len(hash_tracker)} files from previous runs")
        if FORCE_REPROCESS:
            print(f"   ⚠️  Force reprocess enabled - will process all files")
    load_incremental_tracker()

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

    # Test Ollama connection first
    print("🔍 Testing Ollama connection...")
    print("   ⏳ This may take 2-3 minutes for local models (this is normal)...")
    test_response = call_ollama("Hello", "You are a helpful assistant.")
    
    # Test AI provider connection first
    logger.info(f"🔍 Testing {AI_PROVIDER.upper()} connection...")
    if AI_PROVIDER == 'ollama':
        logger.info("   ⏳ This may take 2-3 minutes for local models (this is normal)...")
    test_response = call_ai_provider("Hello", "You are a helpful assistant.")
    if not test_response:
        if AI_PROVIDER == 'claude':
            logger.error("❌ Claude API connection failed. Please check your API key and internet connection.")
            logger.info("   Set claude_api_key in config.yaml or ANTHROPIC_API_KEY env var")
        else:
            logger.error("❌ Ollama connection failed. Please check if Ollama is running and the model is loaded.")
            logger.info("   Try: ollama serve")
            logger.info(f"   Then: ollama pull {OLLAMA_MODEL}")
        return
    else:
        print("✅ Ollama connection successful")
        print("   🐌 Note: Local models are slow (2-3 minutes per file is normal)")
        print(f"   🤖 Using model: {OLLAMA_MODEL}")
        print(f"   ⏱️  Base timeout: {OLLAMA_TIMEOUT}s (extended for complex reasoning)")
        print(f"   🔄 Max retries: {OLLAMA_MAX_RETRIES} (progressive timeouts: +3min per retry)")
        print(f"   📝 Max tokens: {OLLAMA_MAX_TOKENS} (detailed responses)")
        print(f"   🧠 Extended timeouts prevent reasoning interruptions")

        if AI_PROVIDER == 'claude':
            logger.info(f"✅ Claude API connection successful")
            logger.info(f"   🤖 Using model: {CLAUDE_MODEL}")
            logger.info(f"   ⚡ Claude is fast (5-10 seconds per file)")
            print(f"✅ Claude API connection successful")
            print(f"   🤖 Using model: {CLAUDE_MODEL}")
            print(f"   ⚡ Claude is fast (5-10 seconds per file)")
            print(f"   ⏱️  Timeout: {CLAUDE_TIMEOUT}s")
            print(f"   📝 Max tokens: {CLAUDE_MAX_TOKENS}")
        else:
            logger.info("✅ Ollama connection successful")
            logger.info("   🐌 Note: Local models are slow (2-3 minutes per file is normal)")
            logger.info(f"   🤖 Using model: {OLLAMA_MODEL}")
            print("✅ Ollama connection successful")
            print("   🐌 Note: Local models are slow (2-3 minutes per file is normal)")
            print(f"   🤖 Using model: {OLLAMA_MODEL}")
            print(f"   ⏱️  Base timeout: {OLLAMA_TIMEOUT}s (extended for complex reasoning)")
            print(f"   🔄 Max retries: {OLLAMA_MAX_RETRIES} (progressive timeouts: +3min per retry)")
            print(f"   📝 Max tokens: {OLLAMA_MAX_TOKENS} (detailed responses)")
            print(f"   🧠 Extended timeouts prevent reasoning interruptions")
    
    # Scan vault
    logger.info("🔍 Scanning vault...")
    logger.info(f"   Vault path: {VAULT_PATH}")
    existing_notes = get_all_notes(VAULT_PATH)
    print(f"   Found {len(existing_notes)} existing notes")
    logger.info(f"   Found {len(existing_notes)} existing notes")

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

    # Filter out unchanged files (incremental processing)
    if INCREMENTAL_ENABLED:
        filtered_files = []
        skipped_unchanged = 0
        for file_path in all_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                current_hash = get_content_hash(content)
                if incremental_tracker.has_changed(file_path, current_hash):
                    filtered_files.append(file_path)
                else:
                    skipped_unchanged += 1
            except Exception as e:
                # If we can't read file, include it for processing
                filtered_files.append(file_path)
        all_files = filtered_files
        if skipped_unchanged > 0:
            logger.info(f"📊 Incremental: Skipped {skipped_unchanged} unchanged files")

    # Order files based on configuration
    logger.info(f"📋 Ordering files by: {FILE_ORDERING}")
    all_files = order_files(all_files, FILE_ORDERING)

    print(f"   Found {len(all_files)} markdown files to process")
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
            print(f"   ⏰ Estimated time: {total_estimated_minutes:.0f} minutes (local models are slow)")
        print("   💡 Tip: You can stop and resume processing anytime")

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
            print("=" * 60)

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
                print("✅ Selected: Dry Run Mode")
                # Keep dry_run = True
            elif choice == "2":
                print("✅ Selected: Real Processing Mode")
                print("⚠️  WARNING: This will modify your files!")
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
                        print(f"✅ Batch size set to: {BATCH_SIZE}")
                    except ValueError:
                        print("⚠️  Invalid batch size, keeping current")

                # Model selection
                print(f"\nCurrent model: {OLLAMA_MODEL}")
                print("Available models: qwen3:8b, qwen2.5:3b")
                model_input = input("Model (press Enter to keep current): ").strip()
                if model_input in ["qwen3:8b", "qwen2.5:3b"]:
                    OLLAMA_MODEL = model_input
                    print(f"✅ Model set to: {OLLAMA_MODEL}")
                elif model_input:
                    print("⚠️  Invalid model, keeping current")

                # File ordering
                print(f"\nCurrent file ordering: {FILE_ORDERING}")
                print("Available options: recent, oldest, smallest, largest, random, alphabetical")
                order_input = input("File ordering (press Enter to keep current): ").strip()
                if order_input in ["recent", "oldest", "smallest", "largest", "random", "alphabetical"]:
                    FILE_ORDERING = order_input
                    print(f"✅ File ordering set to: {FILE_ORDERING}")
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
                print("✅ Selected: Start with Smallest Files")
                print("🐣 Perfect for quick testing!")
                FILE_ORDERING = "smallest"
                print(f"✅ File ordering set to: {FILE_ORDERING}")
            elif choice == "5":
                print("❌ Processing cancelled by user")
                return
            else:
                print("⚠️  Invalid choice, using default settings")

            # Final confirmation
            print(f"\n📋 Final Configuration:")
            print(f"   🤖 Model: {OLLAMA_MODEL}")
            print(f"   📦 Batch size: {BATCH_SIZE}")
            print(f"   🧪 Mode: {'Dry Run' if DRY_RUN else 'Real Processing'}")
            print(f"   📁 Files: {len(all_files)}")

            final_confirm = input("\nProceed with these settings? (y/N): ")
            if final_confirm.lower() != 'y':
                print("❌ Processing cancelled by user")
                return

        except EOFError:
            # Running in non-interactive mode (like from web GUI)
            print(f"⚠️  Auto-continuing with default settings...")
            pass

        # Cost tracking removed for local LLM

    if DRY_RUN:
        logger.info("\n🔥 DRY RUN MODE - No files will be modified")
        logger.info("   Set dry_run: false in config.yaml to process for real\n")
        print("\n🔥 DRY RUN MODE - No files will be modified")
        print(f"   📊 Limited to first {DRY_RUN_LIMIT} files for analysis")
        print("   Set dry_run: false in config.yaml to process for real\n")
    else:
        print(f"\n⚠️  PROCESSING FOR REAL - Backups will be created")
        print(f"   Backups stored in: {BACKUP_FOLDER}\n")

    # Process files one at a time
    print("📝 Processing files one at a time...\n")

    analytics['total_files'] = len(all_files)

    for i, file_path in enumerate(all_files, 1):
        current_file = os.path.basename(file_path)
    
    # Process files (sequential or parallel based on PARALLEL_WORKERS)
    if PARALLEL_WORKERS > 1:
        print(f"📝 Processing files with {PARALLEL_WORKERS} parallel workers...\n")
    else:
        print("📝 Processing files sequentially...\n")

    analytics['total_files'] = len(all_files)

    # Choose processing mode based on workers
    if PARALLEL_WORKERS > 1:
        # PARALLEL PROCESSING MODE
        print(f"⚡ Parallel mode: Processing up to {PARALLEL_WORKERS} files simultaneously")

        with ThreadPoolExecutor(max_workers=PARALLEL_WORKERS) as executor:
            # Submit all files for processing
            future_to_file = {}
            for i, file_path in enumerate(all_files, 1):
                # Check dry run limit before submitting
                if DRY_RUN and i > DRY_RUN_LIMIT:
                    break

                future = executor.submit(
                    process_file_wrapper,
                    file_path,
                    existing_notes,
                    stats,
                    hash_tracker,
                    i,
                    len(all_files),
                    start_time
                )
                future_to_file[future] = (file_path, i)

            # Process completed futures as they finish
            processed_count = 0
            for future in as_completed(future_to_file):
                file_path, file_num = future_to_file[future]
                current_file = os.path.basename(file_path)

        logger.warning(f"\n⚠️  PROCESSING FOR REAL - Backups will be created")
        logger.info(f"   Backups stored in: {BACKUP_FOLDER}\n")

    # Process files (parallel or sequential based on config)
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
        # Parallel processing with ThreadPoolExecutor
        from concurrent.futures import ThreadPoolExecutor, as_completed

        def process_file_wrapper(args):
            """Wrapper for parallel processing"""
            file_path, file_index, total = args
            current_file = os.path.basename(file_path)

        print(f"\n📄 Processing file {i}/{len(all_files)}: {current_file}")

        # Check dry run limit
        if DRY_RUN and i > DRY_RUN_LIMIT:
            print(f"\n🛑 DRY RUN LIMIT REACHED ({DRY_RUN_LIMIT} files)")
            print("=" * 60)
            print("📊 DRY RUN SUMMARY")
            print("=" * 60)
            print(f"✅ Files analyzed: {i-1}")
            print(f"📊 Would process: {stats['would_process']}")
            print(f"⏭️  Already processed: {stats['already_processed']}")
            print(f"❌ Failed: {stats['failed']}")
            print(f"⚠️  Low confidence files: {analytics.get('low_confidence_files', 0)}")
            print(f"📋 Review queue: {analytics.get('review_queue_count', 0)} files")
            print(f"⏱️  Time elapsed: {datetime.now() - start_time}")

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
                        print("   This will modify your files!")
                        confirm = input("Are you sure? Type 'YES' to continue: ")
                        if confirm == "YES":
                            DRY_RUN = False
                            print("✅ Real processing enabled - continuing with remaining files...")
                        else:
                            print("❌ Real processing cancelled")
                    file_path_result, success, skip_reason = future.result()

                    if success:
                        processed_count += 1

                    # Save progress after each file
                    save_progress()
                    with cache_lock:
                        save_cache()

                    # Show file summary
                    print(f"\n📊 File {file_num} complete:")
                    print(f"   ✅ Processed: {stats['processed']}")
                    print(f"   ⏭️  Skipped: {stats['already_processed']}")
                    print(f"   ❌ Failed: {stats['failed']}")
                    print(f"   🔗 Links added: {stats.get('links_added', 0)}")
                    print(f"   🏷️  Tags added: {stats.get('tags_added', 0)}")

                except Exception as e:
                    print(f"❌ Error processing {current_file}: {e}")
                    stats['failed'] += 1

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
                print(f"✅ Files analyzed: {i-1}")
                print(f"📊 Would process: {stats['would_process']}")
                print(f"⏭️  Already processed: {stats['already_processed']}")
                print(f"❌ Failed: {stats['failed']}")
                print(f"⚠️  Low confidence files: {analytics.get('low_confidence_files', 0)}")
                print(f"📋 Review queue: {analytics.get('review_queue_count', 0)} files")
                print(f"⏱️  Time elapsed: {datetime.now() - start_time}")

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
                            print("   This will modify your files!")
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
                    print(f"  ⏭️  Skipping (unchanged since last run)")
                    stats['already_processed'] += 1
                    set_file_stage(file_path, 'completed')  # Mark as completed (unchanged)
                    continue

            # Set stage: analyzing
            set_file_stage(file_path, 'analyzing')

            # Show progress
            show_progress(current_file, "Processing", processed_count, total_files, start_time)

            # Process the file (this includes linking)
            set_file_stage(file_path, 'linking')
            file_processed = process_conversation(file_path, existing_notes, stats)

            # Update hash tracker after processing
            if INCREMENTAL_PROCESSING and hash_tracker:
                hash_tracker.update_hash(file_path, success=file_processed)
                hash_tracker.save()

            if file_processed:
                set_file_stage(file_path, 'completed')
                processed_count += 1
                show_progress(current_file, "Completed", processed_count, total_files, start_time)
            else:
                set_file_stage(file_path, 'completed')  # Still mark as completed even if skipped
                print("📊 Dry run limit reached - generating analytics report...")
                break

        # Show progress
        show_progress(current_file, "Processing", processed_count, total_files, start_time)

        # Process the file
        if process_conversation(file_path, existing_notes, stats):
            processed_count += 1
            show_progress(current_file, "Completed", processed_count, total_files, start_time)
        else:
            show_progress(current_file, "Skipped", processed_count, total_files, start_time)

        # Save progress after each file
        save_progress()
        save_cache()

        # Show file summary
        print(f"\n📊 File {i} complete:")
        print(f"   ✅ Processed: {stats['processed']}")
        print(f"   ⏭️  Skipped: {stats['already_processed']}")
        print(f"   ❌ Failed: {stats['failed']}")
        print(f"   🔗 Links added: {stats['links_added']}")
        print(f"   🏷️  Tags added: {stats['tags_added']}")

            # Process results as they complete
            for future in as_completed(future_to_file):
                file_path, success = future.result()
                if success:
                    processed_count += 1

    else:
        # Sequential processing (original logic)
        for i, file_path in enumerate(all_files, 1):
            current_file = os.path.basename(file_path)
            logger.info(f"\n📄 Processing file {i}/{len(all_files)}: {current_file}")

            # Update dashboard
            if dashboard:
                dashboard.update_processing(
                    total_files=len(all_files),
                    processed_files=processed_count,
                    failed_files=stats['failed'],
                    current_file=current_file,
                    current_stage="Processing"
                )

            # Show progress
            show_progress(current_file, "Processing", processed_count, total_files, start_time)

            # Process the file
            if process_conversation(file_path, existing_notes, stats):
                processed_count += 1
                show_progress(current_file, "Completed", processed_count, total_files, start_time)
            else:
                show_progress(current_file, "Skipped", processed_count, total_files, start_time)

            # Save progress after each file
            save_progress()
            save_cache()

            # Show file summary
            print(f"\n📊 File {i} complete:")
            print(f"   ✅ Processed: {stats['processed']}")
            print(f"   ⏭️  Skipped: {stats['already_processed']}")
            print(f"   ❌ Failed: {stats['failed']}")
            print(f"   🔗 Links added: {stats['links_added']}")
            print(f"   🏷️  Tags added: {stats['tags_added']}")
            save_incremental_tracker()

        # Update dashboard after processing
        if dashboard:
            dashboard.update_processing(
                total_files=len(all_files),
                processed_files=processed_count,
                failed_files=stats['failed'],
                current_file=current_file,
                current_stage="Completed"
            )

        # Show file summary
        logger.info(f"\n📊 File {i} complete:")
        logger.info(f"   ✅ Processed: {stats['processed']}")
        logger.info(f"   ⏭️  Skipped: {stats['already_processed']}")
        logger.info(f"   ❌ Failed: {stats['failed']}")
        logger.info(f"   🔗 Links added: {stats['links_added']}")
        logger.info(f"   🏷️  Tags added: {stats['tags_added']}")
    
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
        print(f"📊 Processed: {stats['processed']} files")
        print(f"📄 New files created: {stats['processed']} (with '_linked' suffix)")
        print(f"🔗 Links added: {stats['links_added']}")
        print(f"🏷️  Tags added: {stats['tags_added']}")
    print(f"⏭️  Already processed: {stats['already_processed']}")
    print(f"❌ Failed: {stats['failed']}")
    print(f"⚠️  Low confidence files: {analytics.get('low_confidence_files', 0)} (below {CONFIDENCE_THRESHOLD:.0%} threshold)")
    print(f"📋 Review queue: {analytics.get('review_queue_count', 0)} files flagged for manual review")

    # Incremental processing stats
    if INCREMENTAL_PROCESSING and hash_tracker:
        inc_stats = hash_tracker.get_stats()
        print(f"\n📝 Incremental Processing:")
        print(f"   ⏭️  Skipped (unchanged): {inc_stats['unchanged_files']} files ({inc_stats['skip_rate']}% skip rate)")
        print(f"   🔄 Changed: {inc_stats['changed_files']} files")
        print(f"   ✨ New: {inc_stats['new_files']} files")
        print(f"   💾 Tracking: {inc_stats['total_tracked_files']} files total")

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
            print("✅ Ultra detailed analytics generated!")
            print("🌐 Ultra detailed report will open automatically in your browser")
        else:
            print("⚠️ Ultra detailed analytics failed, using standard report")
            print(f"Error: {result.stderr}")
    except Exception as e:
        print(f"⚠️ Ultra detailed analytics failed: {e}")
        print("📊 Using standard analytics report")

    if DRY_RUN:
        logger.info("💡 Set dry_run: false in config.yaml to process for real")
    else:
        print(f"💾 Backups saved to: {BACKUP_FOLDER}")

    print("=" * 60)
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

