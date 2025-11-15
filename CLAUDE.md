# CLAUDE.md - AI Assistant Guide for Obsidian Auto-Linker

**Last Updated**: 2025-11-14
**Version**: 1.1.0
**Purpose**: Comprehensive guide for AI assistants working with the Obsidian Auto-Linker codebase

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [Repository Structure](#2-repository-structure)
3. [Architecture & Design](#3-architecture--design)
4. [Development Workflows](#4-development-workflows)
5. [Coding Conventions](#5-coding-conventions)
6. [Configuration System](#6-configuration-system)
7. [Common Tasks](#7-common-tasks)
8. [Testing & Debugging](#8-testing--debugging)
9. [Important Gotchas](#9-important-gotchas)
10. [Extension Points](#10-extension-points)

---

## 1. Project Overview

### 1.1 What Is This?

**Obsidian Auto-Linker** is an intelligent Python tool that automatically processes Markdown files in an Obsidian vault using local AI (Ollama) to:

- Analyze note content and extract key concepts
- Categorize notes into a Map of Content (MOC) structure
- Create wiki-style links between related notes
- Generate hierarchical tags
- Build a knowledge graph with parent/sibling/child relationships

**Core Philosophy**: Safety first, privacy-focused, cost-free (local AI), resumable, and extensively monitored.

### 1.2 Key Features

| Feature | Description |
|---------|-------------|
| **Safe Processing** | Creates new `_linked.md` files, never modifies originals |
| **Smart Caching** | MD5-based cache avoids re-analyzing unchanged content |
| **Resume Capability** | Can stop/restart without losing progress |
| **Live Monitoring** | Real-time dashboard with 25+ metrics (M4-optimized) |
| **Local AI** | Uses Ollama for privacy and zero API costs |
| **Multiple Modes** | Fast Dry Run, Full Dry Run, Live Run |
| **Progress Tracking** | ETA, speed, resource usage, activity logs |
| **Comprehensive Backups** | Timestamped backups with rotation |

### 1.3 Target Environment

- **Primary OS**: macOS (optimized for MacBook Air M4 2025)
- **Python**: 3.7+
- **AI Backend**: Ollama (localhost:11434)
- **Recommended Model**: qwen2.5:3b (fast, lightweight)
- **Vault**: Obsidian vault with Markdown files

---

## 2. Repository Structure

### 2.1 File Organization

```
Obsidain-Link-Master/
├── Core Processing
│   ├── obsidian_auto_linker_enhanced.py  # Main processor (985 lines)
│   ├── run.py                            # Interactive CLI runner (432 lines)
│   └── run_with_dashboard.py             # Dashboard runner (345 lines)
│
├── Monitoring & Logging
│   ├── live_dashboard.py                 # Live terminal dashboard (640+ lines)
│   └── logger_config.py                  # Logging infrastructure (135 lines)
│
├── Utilities
│   ├── generate_detailed_report.py       # HTML report generator (260 lines)
│   ├── quick_report.py                   # Terminal report viewer (103 lines)
│   ├── config_utils.py                   # Configuration utilities (325 lines)
│   ├── config_schema.py                  # Pydantic validation schemas (240 lines)
│   └── optimize_ollama.sh                # Ollama optimization script
│
├── Configuration & Data
│   ├── config.yaml                       # User configuration (gitignored)
│   ├── requirements.txt                  # Python dependencies
│   ├── pytest.ini                        # Pytest configuration
│   ├── .ai_cache.json                    # AI response cache (gitignored)
│   ├── .processing_progress.json         # Progress tracking (gitignored)
│   └── processing_analytics.json         # Analytics data (gitignored)
│
├── Testing
│   └── tests/                            # Test suite (75 tests, 100% passing)
│       ├── __init__.py
│       ├── conftest.py                   # Pytest fixtures
│       ├── test_config_utils.py          # Config utilities tests (28)
│       ├── test_config_schema.py         # Pydantic validation tests (26)
│       ├── test_logger_config.py         # Logging tests (10)
│       ├── test_integration.py           # Integration tests (11)
│       └── README.md                     # Testing guide
│
├── Documentation
│   ├── README.md                         # Basic usage guide
│   ├── README_ENHANCED.md                # Comprehensive documentation
│   ├── IMPLEMENTATION_SUMMARY.md         # Implementation details
│   └── CLAUDE.md                         # This file
│
└── Generated Files (Ignored)
    ├── obsidian_linker.log               # Rotating log file
    ├── detailed_report.html              # HTML analytics report
    └── analytics_report.html             # Alternative report format
```

### 2.2 Component Responsibilities

| Component | Lines | Primary Responsibility | Key Dependencies |
|-----------|-------|------------------------|------------------|
| **obsidian_auto_linker_enhanced.py** | 985 | Core processing logic, AI analysis, file management | requests, yaml, json, hashlib |
| **run.py** | 500+ | Interactive CLI with dashboard support, resource monitoring | subprocess, psutil, signal |
| **run_with_dashboard.py** | 345 | Dashboard integration, config validation | rich, logger_config, live_dashboard |
| **live_dashboard.py** | 640+ | Real-time metrics (15s updates), terminal UI | rich, psutil, threading, deque |
| **logger_config.py** | 135 | Structured logging, file rotation | logging, RotatingFileHandler |
| **config_utils.py** | 325 | Config/JSON loading, Ollama checks, security validation | yaml, json, requests |
| **config_schema.py** | 240 | Pydantic models for type-safe config validation | pydantic |
| **generate_detailed_report.py** | 260 | HTML report generation | json, datetime, html |
| **quick_report.py** | 103 | Terminal report viewing | json |

---

## 3. Architecture & Design

### 3.1 System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    USER INTERFACES                           │
├──────────────────┬──────────────────┬───────────────────────┤
│   run.py         │ run_with_        │  Direct Script        │
│   (Interactive)  │ dashboard.py     │  Execution            │
│                  │ (Dashboard)      │                       │
└────────┬─────────┴─────────┬────────┴──────────┬────────────┘
         │                   │                   │
         └───────────────────┼───────────────────┘
                             │
         ┌───────────────────▼────────────────────┐
         │   CORE PROCESSING ENGINE               │
         │   obsidian_auto_linker_enhanced.py     │
         │                                         │
         │  ┌──────────────────────────────────┐ │
         │  │  1. File Discovery & Filtering   │ │
         │  │  2. AI Analysis & Categorization │ │
         │  │  3. Link Generation              │ │
         │  │  4. Wiki Structure Creation      │ │
         │  │  5. Cache Management             │ │
         │  │  6. Progress Tracking            │ │
         │  └──────────────────────────────────┘ │
         └─────────┬───────────────────┬──────────┘
                   │                   │
         ┌─────────▼────────┐  ┌──────▼──────────┐
         │  MONITORING       │  │  UTILITIES      │
         │  - Dashboard      │  │  - Logger       │
         │  - Analytics      │  │  - Reports      │
         └───────────────────┘  └─────────────────┘
                   │
         ┌─────────▼────────────────────────┐
         │   EXTERNAL SERVICES & STORAGE    │
         │  - Ollama API (localhost:11434)  │
         │  - File System (Vault)           │
         │  - Cache Files (.json)           │
         │  - Progress Files (.json)        │
         │  - Backups Folder                │
         └──────────────────────────────────┘
```

### 3.2 Core Processing Workflow

```python
# Main processing flow in obsidian_auto_linker_enhanced.py

1. Load Configuration (config.yaml)
   ├─> Validate paths and settings
   └─> Apply defaults

2. Initialize Analytics & Progress
   ├─> Load .processing_progress.json (resume support)
   ├─> Load .ai_cache.json (performance optimization)
   └─> Initialize analytics dict

3. Test Ollama Connection
   ├─> Check localhost:11434 availability
   └─> Exit if unavailable

4. Scan Vault for Notes
   ├─> Recursive directory walk
   ├─> Apply exclude/include patterns
   ├─> Apply folder whitelist/blacklist
   └─> Build existing_notes dict

5. Create MOC Notes (if missing)
   ├─> Check for 12 standard MOCs
   └─> Create from template if missing

6. Order Files
   └─> Sort by: recent/size/random/alphabetical

7. Process Each File (Sequential)
   ├─> Skip if already processed (resume)
   ├─> Read file content
   ├─> Analyze Content:
   │   ├─> Fast Dry Run: Keyword-based
   │   └─> Full Analysis: AI-powered
   │       ├─> Generate MD5 hash
   │       ├─> Check cache (return if hit)
   │       ├─> Build Ollama prompt
   │       ├─> Call API (with retries)
   │       ├─> Parse JSON response
   │       └─> Update cache
   ├─> Verify Sibling Links
   ├─> Build Footer (Metadata, Wiki, Concepts, Tags)
   ├─> Backup Original File
   ├─> Write New File (*_linked.md)
   ├─> Update Progress & Save
   └─> Update Analytics

8. Generate Analytics Report
   └─> Save processing_analytics.json
```

### 3.3 Key Design Patterns

#### **1. Cache-Aside Pattern**
```python
# Check cache first
hash_key = get_content_hash(content)
if hash_key in ai_cache:
    return ai_cache[hash_key]  # Cache hit

# Cache miss: fetch from AI
result = call_ollama(prompt)
ai_cache[hash_key] = result  # Update cache
return result
```

#### **2. Retry with Exponential Backoff**
```python
for attempt in range(max_retries):
    try:
        response = requests.post(url, timeout=timeout)
        return response.json()
    except Exception as e:
        if attempt < max_retries - 1:
            wait = 2 ** attempt  # 1s, 2s, 4s
            time.sleep(wait)
        else:
            raise
```

#### **3. Progress Tracking Pattern**
```python
# On startup
progress_data = load_progress()

# During processing
if file_path in progress_data['processed_files']:
    continue  # Skip already processed

# After success/failure
if success:
    progress_data['processed_files'].add(file_path)
else:
    progress_data['failed_files'].add(file_path)

save_progress()  # Persist to disk
```

#### **4. Graceful Degradation**
```python
# Primary: Full AI analysis
ai_result = analyze_with_balanced_ai(content, existing_notes)

# Fallback: Fast keyword-based
if ai_result is None:
    ai_result = fast_dry_run_analysis(content, file_path)

# Absolute fallback: Skip file
if ai_result is None:
    return False  # Mark as failed, continue
```

### 3.4 Data Flow Diagram

```
INPUT: Markdown File
    │
    ├─> Read Content
    │
    ├─> Generate MD5 Hash
    │
    ├─> Check Cache
    │   ├─> HIT: Return Cached Result
    │   └─> MISS: Proceed to AI
    │
    ├─> Build AI Prompt
    │   ├─> System: "You analyze conversations..."
    │   ├─> Context: First 50 existing notes
    │   ├─> Content: First 2000 chars
    │   └─> Schema: Expected JSON format
    │
    ├─> Call Ollama API
    │   ├─> POST /api/generate
    │   ├─> Timeout: 15s + (retry_count × 60s)
    │   └─> Retry: Exponential backoff
    │
    ├─> Parse JSON Response
    │   ├─> Strip markdown code blocks
    │   ├─> Extract {...} with regex if needed
    │   └─> Validate fields
    │
    ├─> Extract Results
    │   ├─> moc_category
    │   ├─> primary_topic
    │   ├─> hierarchical_tags
    │   ├─> key_concepts
    │   ├─> sibling_notes
    │   ├─> confidence_score
    │   └─> reasoning
    │
    ├─> Verify Links (notes must exist)
    │
    ├─> Build Footer
    │   ├─> ## 📊 METADATA
    │   ├─> ## 🔗 WIKI STRUCTURE
    │   ├─> ## 💡 KEY CONCEPTS
    │   └─> ## 🏷️ TAGS
    │
    ├─> Backup Original
    │   └─> _backups/filename_YYYYMMDD_HHMMSS.md
    │
    ├─> Write New File
    │   └─> filename_linked.md
    │
    └─> OUTPUT: Linked File
```

### 3.5 MOC (Map of Content) System

**12 Standard Categories**:
```python
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
```

**Custom MOCs**: Configured via `config.yaml` under `custom_mocs` key.

**MOC Template**:
```markdown
# 📍 [MOC Name] MOC

> [Auto-generated description]

## Overview
This is a Map of Content (MOC) that organizes all notes related to [topic].

## Key Concepts
(Concepts will be added as notes are processed)

## Recent Conversations
(Recent conversations will appear here automatically)

## Related MOCs
(Links to related MOCs will be added here)

---
*This MOC was auto-generated. Add your own structure and notes as needed.*
```

---

## 4. Development Workflows

### 4.1 Standard Development Cycle

```bash
# 1. Setup (First Time)
git clone <repo>
cd Obsidain-Link-Master
pip install -r requirements.txt
ollama serve  # Start in background terminal

# 2. Development
# - Make code changes
# - Test with Fast Dry Run first

python3 run.py
# Select: Fast Dry Run, batch_size=1

# 3. Full Testing
python3 run.py
# Select: Full Dry Run, batch_size=1

# 4. Review Results
python3 quick_report.py
python3 generate_detailed_report.py
open detailed_report.html

# 5. Live Run (Actual Processing)
python3 run.py
# Select: Live Run
# Check _backups/ folder exists

# 6. Monitor with Dashboard
python3 run_with_dashboard.py
# View real-time metrics
```

### 4.2 Adding a New Feature

**Process**:

1. **Understand Context**: Read relevant sections of this CLAUDE.md
2. **Identify Touch Points**: What files need changes?
3. **Update Configuration**: Add to `config.yaml` if needed
4. **Implement Core Logic**: Update `obsidian_auto_linker_enhanced.py`
5. **Update Monitoring**: Add metrics to `live_dashboard.py` if applicable
6. **Add Logging**: Use `logger_config.py` for structured logs
7. **Update Documentation**: Modify README.md and this file
8. **Test**: Use Fast Dry Run → Full Dry Run → Live Run
9. **Commit**: Follow git conventions (see section 4.4)

**Example - Adding a New MOC Category**:

```python
# In config.yaml (user's file)
custom_mocs:
  "My New Category": "📍 My New Category MOC"

# In obsidian_auto_linker_enhanced.py
# The code already supports custom_mocs from config
# No code changes needed - just document in README.md
```

**Example - Adding a New File Filter**:

```python
# 1. Update config.yaml schema
# 2. In obsidian_auto_linker_enhanced.py

def should_process_file(file_path: str) -> bool:
    # Existing filters...

    # Add new filter
    if CUSTOM_FILTER_ENABLED:
        if not custom_filter_check(file_path):
            return False

    return True

# 3. Load from config
CUSTOM_FILTER_ENABLED = config.get('custom_filter_enabled', False)
```

### 4.3 Running Tests

**Current State**: No formal test suite (Priority 2 in roadmap)

**Manual Testing Approach**:

```bash
# 1. Import Test (verify no syntax errors)
python3 -c "import obsidian_auto_linker_enhanced; print('✓ Core OK')"
python3 -c "import live_dashboard; print('✓ Dashboard OK')"
python3 -c "import logger_config; print('✓ Logger OK')"

# 2. Fast Dry Run (no AI, quick validation)
python3 run.py
# Select: Fast Dry Run, batch_size=1

# 3. Ollama Connection Test
python3 -c "
import requests
try:
    r = requests.get('http://localhost:11434/api/tags', timeout=5)
    print('✓ Ollama OK')
except:
    print('✗ Ollama unavailable')
"

# 4. Full Integration Test
python3 run.py
# Select: Full Dry Run, batch_size=1
# Verify: No exceptions, reasonable AI output

# 5. Dashboard Test
python3 run_with_dashboard.py
# Verify: Dashboard renders correctly
```

**Future**: Add pytest suite (see IMPLEMENTATION_SUMMARY.md → Priority 2)

### 4.4 Git Workflow

**Branch Strategy**:
- **Main branch**: Stable releases
- **Feature branches**: `feature/description` or `claude/session-id`
- **Hotfix branches**: `hotfix/issue-description`

**Commit Message Format**:
```
<type>: <short summary>

<optional detailed description>

<optional footer: references, breaking changes>
```

**Commit Types**:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation only
- `refactor`: Code refactoring
- `perf`: Performance improvement
- `test`: Adding tests
- `chore`: Maintenance (deps, config)

**Examples**:
```bash
git commit -m "feat: Add support for custom MOC categories"
git commit -m "fix: Handle JSON parse errors in AI responses"
git commit -m "docs: Update CLAUDE.md with workflow section"
git commit -m "refactor: Extract AI prompt building to separate function"
```

**Pre-Commit Checklist**:
- [ ] Code follows naming conventions (see section 5)
- [ ] No hardcoded paths (use config.yaml)
- [ ] Logging used instead of print() for new code
- [ ] Error handling in place
- [ ] Tested with Fast Dry Run
- [ ] Documentation updated if needed

---

## 5. Coding Conventions

### 5.1 Naming Conventions

| Type | Convention | Examples |
|------|------------|----------|
| **Functions** | `snake_case` | `process_conversation`, `get_content_hash` |
| **Classes** | `PascalCase` | `ObsidianAutoLinker`, `LiveDashboard` |
| **Constants** | `UPPER_SNAKE_CASE` | `VAULT_PATH`, `MAX_RETRIES`, `OLLAMA_MODEL` |
| **Global State** | `lowercase` | `analytics`, `progress_data`, `ai_cache` |
| **Private Methods** | `_leading_underscore` | `_create_panel`, `_calculate_stats` |
| **Module Files** | `snake_case.py` | `logger_config.py`, `live_dashboard.py` |

### 5.2 Code Organization

**File Structure**:
```python
# 1. Imports (standard library first, then third-party)
import os
import sys
import json
from typing import Optional, Dict, List

import requests
import yaml
from rich.console import Console

# 2. Constants (config-derived and hardcoded)
config = yaml.safe_load(...)
VAULT_PATH = config.get('vault_path', '')
MOCS = {...}

# 3. Global state (analytics, cache, progress)
analytics = {}
ai_cache = {}
progress_data = {}

# 4. Utility functions
def get_content_hash(content: str) -> str:
    ...

# 5. Core functions (grouped by functionality)
def call_ollama(...):
    ...

def analyze_with_balanced_ai(...):
    ...

# 6. Main processing functions
def process_conversation(...):
    ...

# 7. Entry point
def main():
    ...

if __name__ == "__main__":
    main()
```

### 5.3 Type Hints

**Usage**: Partial type hints on public functions

```python
# Good (type hints on public functions)
def process_conversation(file_path: str, existing_notes: Dict[str, str], stats: Dict) -> bool:
    ...

def analyze_with_balanced_ai(content: str, existing_notes: Dict[str, str]) -> Optional[Dict]:
    ...

def get_all_notes(vault_path: str) -> Dict[str, str]:
    ...

# Acceptable (no type hints on simple utilities)
def show_progress(current, total):
    percentage = (current / total) * 100
    print(f"Progress: {percentage:.1f}%")
```

**Import**:
```python
from typing import List, Set, Dict, Tuple, Optional, Any
```

### 5.4 String Formatting

**Preference**: Use f-strings

```python
# Good
print(f"Processing {filename}...")
print(f"Confidence: {confidence:.0%}")
footer = f"""
## 📊 METADATA

Primary Topic: {primary_topic}
Category: {moc_category}
"""

# Avoid (old style)
print("Processing %s..." % filename)
print("Processing {}...".format(filename))
```

### 5.5 Error Messages

**User-Facing Messages**: Use emoji for clarity

```python
# Success
print("✅ Configuration loaded successfully")

# Error
print("❌ Ollama connection failed. Please check...")

# Warning
print("⚠️  Cache file corrupted, starting fresh")

# Info
print("📄 Processing note.md...")
```

**Standard Emoji**:
- ✅ Success
- ❌ Error
- ⚠️ Warning
- 📄 File
- 🔗 Link
- 🏷️ Tag
- 📊 Stats
- 🤖 AI
- 💾 Cache
- ⏱️ Time
- 🔥 Dry run

### 5.6 Logging vs Print

**Rule**: New code should use logging, not print()

```python
# Bad (print statements)
print(f"Processing {file_path}...")
print(f"Error: {e}")

# Good (structured logging)
from logger_config import get_logger
logger = get_logger(__name__)

logger.info(f"Processing {file_path}...")
logger.error(f"Failed to process file: {e}")
logger.warning(f"Cache miss for {file_path}")
logger.debug(f"AI response: {response}")
```

**Log Levels**:
- `DEBUG`: Detailed diagnostic info (AI responses, cache lookups)
- `INFO`: Progress updates (file processed, batch completed)
- `WARNING`: Recoverable errors (cache miss, retry attempt)
- `ERROR`: Serious problems (file read failed, AI timeout)
- `CRITICAL`: Fatal errors (Ollama unavailable, config missing)

**Note**: Existing code in `obsidian_auto_linker_enhanced.py` still uses print() - gradual migration planned.

### 5.7 Function Length

**Guideline**: Keep functions under 50 lines

```python
# Too long (should be split)
def process_conversation(file_path, existing_notes, stats):
    # Read file (10 lines)
    # Analyze with AI (20 lines)
    # Build footer (30 lines)
    # Write file (10 lines)
    # Update stats (10 lines)
    # Total: 80 lines - too long!

# Better (split into smaller functions)
def process_conversation(file_path, existing_notes, stats):
    content = read_file_safe(file_path)
    ai_result = analyze_with_balanced_ai(content, existing_notes)
    footer = build_footer(ai_result, existing_notes)
    write_linked_file(file_path, content, footer)
    update_statistics(stats, ai_result)
```

### 5.8 Comments

**When to Comment**:
- Complex algorithms
- Non-obvious workarounds
- External API integrations
- Performance optimizations

**When NOT to Comment**:
- Obvious code (let the code speak)
- Redundant explanations

```python
# Bad (obvious)
count = 0  # Initialize counter

# Good (explains why)
# Use MD5 instead of SHA256 for performance - collisions unlikely
# given small dataset and non-cryptographic use case
hash_key = hashlib.md5(content.encode()).hexdigest()

# Good (explains complex logic)
# Exponential backoff: wait 1s, 2s, 4s between retries
# Prevents overwhelming Ollama during temporary issues
wait_time = 2 ** attempt
time.sleep(wait_time)
```

---

## 6. Configuration System

### 6.1 config.yaml Structure

**Complete Schema**:

```yaml
# === PROCESSING SETTINGS ===
vault_path: /path/to/vault          # Absolute path to Obsidian vault
dry_run: true                        # Safe mode (no file writes)
fast_dry_run: true                   # Skip AI analysis
batch_size: 5                        # Files processed per batch
file_ordering: recent                # recent|size|random|alphabetical

# === OLLAMA CONFIGURATION ===
ollama_base_url: http://localhost:11434
ollama_model: qwen2.5:3b            # Fast, lightweight model
ollama_timeout: 15                   # Base timeout (seconds)
ollama_max_retries: 1                # Retry attempts
ollama_temperature: 0.3              # Lower = more deterministic
ollama_max_tokens: 200               # Response length limit

# === FEATURES ===
cache_enabled: true                  # Use AI response cache
resume_enabled: true                 # Resume from progress file
confirm_large_batches: false         # Prompt before large batches

# === ADVANCED ===
parallel_workers: 3                  # For future parallel processing
max_retries: 1                       # General retry limit

# === FILTERING ===
exclude_patterns:                    # fnmatch patterns
  - "*.tmp"
  - ".*"
  - "_*"

include_patterns:
  - "*.md"

folder_whitelist:                    # Only process these folders
  - "Conversations"
  - "Notes"

folder_blacklist:                    # Never process these folders
  - "_backups"
  - ".git"
  - "Templates"

# === CUSTOM MOCs (Optional) ===
custom_mocs:
  "My Category": "📍 My Category MOC"
  "Another Category": "📍 Another Category MOC"
```

### 6.2 Configuration Loading Pattern

```python
# In obsidian_auto_linker_enhanced.py
try:
    with open('config.yaml', 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    if config is None:
        config = {}
except Exception as e:
    print(f"Error loading config: {e}")
    config = {}

# Extract with defaults
VAULT_PATH = config.get('vault_path', '')
DRY_RUN = config.get('dry_run', True)
FAST_DRY_RUN = config.get('fast_dry_run', False)
BATCH_SIZE = config.get('batch_size', 1)
```

### 6.3 Configuration Defaults

**Critical Defaults** (safe by default):

```python
{
    'dry_run': True,              # Never modify files by default
    'cache_enabled': True,        # Performance optimization
    'resume_enabled': True,       # User convenience
    'ollama_timeout': 15,         # Reasonable timeout
    'ollama_max_retries': 1,      # One retry attempt
    'batch_size': 1,              # Conservative batch
    'file_ordering': 'recent',    # Most relevant first
}
```

### 6.4 Accessing Configuration in Code

```python
# Module-level constants (loaded once)
VAULT_PATH = config.get('vault_path', '')
DRY_RUN = config.get('dry_run', True)

# Use constants throughout code
def process_files():
    if DRY_RUN:
        print("🔥 DRY RUN MODE - No files will be modified")
        return

    # Process files...
```

**Important**: Configuration is loaded at module import time, not runtime. To change config, restart the script.

---

## 7. Common Tasks

### 7.1 Adding a New Configuration Option

**Steps**:

1. **Add to config.yaml** (user's file):
```yaml
my_new_feature_enabled: true
```

2. **Load in code**:
```python
# In obsidian_auto_linker_enhanced.py (module level)
MY_NEW_FEATURE_ENABLED = config.get('my_new_feature_enabled', False)
```

3. **Use in logic**:
```python
def process_conversation(file_path, existing_notes, stats):
    if MY_NEW_FEATURE_ENABLED:
        # New feature logic
        pass
```

4. **Document in README.md**:
```markdown
### my_new_feature_enabled
- **Type**: boolean
- **Default**: false
- **Description**: Enables XYZ feature...
```

### 7.2 Adding a New MOC Category

**Method 1: Via config.yaml** (Recommended)

```yaml
custom_mocs:
  "My Category": "📍 My Category MOC"
```

**Method 2: Hardcoded** (if truly standard)

```python
# In obsidian_auto_linker_enhanced.py
MOCS = {
    # ... existing MOCs ...
    "My Category": "📍 My Category MOC",
}

MOC_DESCRIPTIONS = {
    # ... existing descriptions ...
    "My Category": "Notes about my category",
}
```

**Create MOC Note**:
```python
# Automatically created by create_moc_note() function
# No manual intervention needed
```

### 7.3 Modifying AI Prompt

**Location**: `obsidian_auto_linker_enhanced.py` → `analyze_with_balanced_ai()`

```python
def analyze_with_balanced_ai(content, existing_notes):
    # System prompt (AI's role)
    system_prompt = "You analyze conversations and create knowledge connections. Return valid JSON only."

    # User prompt (task + context)
    prompt = f"""Analyze this Obsidian conversation and provide structured metadata.

EXISTING NOTES (for linking):
{existing_notes_list}

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

Categories: {categories_list}

Return ONLY the JSON object, no explanations or other text.
"""
```

**Modification Tips**:
- Keep prompts concise (faster processing)
- Always request JSON output
- Provide examples in prompt for better results
- List constraints explicitly (categories, format)
- Test with multiple files after changes

### 7.4 Adding a New Dashboard Metric

**Steps**:

1. **Add tracking variable** (`live_dashboard.py`):
```python
class LiveDashboard:
    def __init__(self, update_interval=30):
        # Existing metrics...
        self.my_new_metric = 0
```

2. **Add update method**:
```python
def update_my_metric(self, value):
    self.my_new_metric = value
    self.last_update = datetime.now()
```

3. **Add to panel** (e.g., `_create_processing_panel`):
```python
def _create_processing_panel(self):
    content = f"""
    [cyan]Current File:[/cyan] {self.current_file or 'None'}
    [cyan]My Metric:[/cyan] {self.my_new_metric}
    """
    return Panel(content, title="Processing", border_style="cyan")
```

4. **Call update in processing code**:
```python
# In obsidian_auto_linker_enhanced.py or runner
if dashboard:
    dashboard.update_my_metric(new_value)
```

### 7.5 Debugging Ollama Issues

**Common Issues & Solutions**:

| Issue | Diagnosis | Solution |
|-------|-----------|----------|
| **Connection Refused** | `requests.exceptions.ConnectionError` | Start Ollama: `ollama serve` |
| **Timeout** | `requests.exceptions.Timeout` | Increase `ollama_timeout` in config |
| **Model Not Found** | `{"error":"model not found"}` | Pull model: `ollama pull qwen2.5:3b` |
| **Out of Memory** | Slow responses, system lag | Use smaller model: `qwen2.5:3b` instead of `qwen2.5:7b` |
| **Slow Processing** | Normal (2-3 min/file) | Enable cache, use fast_dry_run for testing |

**Diagnostic Commands**:
```bash
# Check Ollama is running
curl http://localhost:11434/api/tags

# List installed models
ollama list

# Pull recommended model
ollama pull qwen2.5:3b

# Test model directly
ollama run qwen2.5:3b "Hello"

# Check Ollama logs (macOS)
cat ~/Library/Logs/Ollama/server.log
```

### 7.6 Recovering from Errors

**Scenario 1: Processing Interrupted**

```bash
# Check progress file
cat .processing_progress.json

# Resume processing (if resume_enabled: true)
python3 run.py
# Processing will skip already-processed files
```

**Scenario 2: Corrupted Cache**

```bash
# Backup current cache
mv .ai_cache.json .ai_cache.json.backup

# Delete cache (will rebuild)
rm .ai_cache.json

# Restart processing
python3 run.py
```

**Scenario 3: File Write Failed**

```bash
# Check permissions
ls -la /path/to/vault

# Check disk space
df -h

# Check backup exists
ls -la _backups/

# Manually restore if needed
cp _backups/note_20251114_123456.md note.md
```

---

## 8. Testing & Debugging

### 8.1 Testing Pyramid

```
                    ┌────────────┐
                    │  Live Run  │  (Minimal - on real vault)
                    └────────────┘
                  ┌──────────────────┐
                  │   Full Dry Run   │  (Moderate - with AI)
                  └──────────────────┘
              ┌────────────────────────────┐
              │     Fast Dry Run           │  (Frequent - no AI)
              └────────────────────────────┘
          ┌──────────────────────────────────────┐
          │        Import/Syntax Tests           │  (Constant)
          └──────────────────────────────────────┘
```

### 8.2 Quick Validation

**Before Committing**:
```bash
# 1. Syntax check (all modules)
python3 -c "import obsidian_auto_linker_enhanced"
python3 -c "import live_dashboard"
python3 -c "import logger_config"
python3 -c "import run"
python3 -c "import run_with_dashboard"

# 2. Fast dry run (single file)
python3 run.py
# Select: Fast Dry Run, batch_size=1

# 3. Check logs
tail -20 obsidian_linker.log
```

### 8.3 Debugging Techniques

#### **1. Enable Debug Logging**

```python
# In logger_config.py or at runtime
logger = setup_logging(log_level="DEBUG")

# Or modify config
import logging
logging.getLogger('obsidian_linker').setLevel(logging.DEBUG)
```

#### **2. Inspect AI Responses**

```python
# In obsidian_auto_linker_enhanced.py → call_ollama()
response = requests.post(...)
print(f"DEBUG: AI Response: {response.text}")  # Add this line
```

#### **3. Cache Inspection**

```bash
# View cache contents
cat .ai_cache.json | python3 -m json.tool | less

# Count cache entries
python3 -c "
import json
with open('.ai_cache.json') as f:
    cache = json.load(f)
print(f'Cache entries: {len(cache)}')
"
```

#### **4. Progress Tracking**

```bash
# Check progress
cat .processing_progress.json | python3 -m json.tool

# Count processed files
python3 -c "
import json
with open('.processing_progress.json') as f:
    progress = json.load(f)
print(f'Processed: {len(progress[\"processed_files\"])}')
print(f'Failed: {len(progress[\"failed_files\"])}')
"
```

#### **5. Dashboard Debugging**

```python
# In live_dashboard.py
def render(self):
    print(f"DEBUG: Rendering at {datetime.now()}")  # Add this
    print(f"DEBUG: Metrics - processed: {self.processed_files}")

    layout = self._create_layout()
    return layout
```

### 8.4 Common Error Patterns

| Error Pattern | Likely Cause | Fix |
|---------------|--------------|-----|
| `FileNotFoundError: config.yaml` | Config not created | Run `run.py` first (creates config interactively) |
| `json.decoder.JSONDecodeError` | AI returned invalid JSON | Check AI prompt, increase temperature, retry |
| `requests.exceptions.ConnectionError` | Ollama not running | Start Ollama: `ollama serve` |
| `KeyError: 'moc_category'` | AI response missing field | Improve prompt, add validation |
| `UnicodeDecodeError` | Non-UTF8 file | Add encoding parameter: `open(..., encoding='utf-8', errors='ignore')` |
| `MemoryError` | Large vault, no limits | Reduce batch size, add pagination |

---

## 9. Important Gotchas

### 9.1 Configuration Issues

**Gotcha 1: Config loaded at import time**

```python
# Wrong approach
import obsidian_auto_linker_enhanced

# Modify config.yaml
# ... changes won't be reflected ...

obsidian_auto_linker_enhanced.main()

# Right approach
# Modify config.yaml FIRST, then import
python3 run.py  # Restarts process, loads new config
```

**Gotcha 2: Relative vs Absolute Paths**

```yaml
# Wrong (relative path - breaks when run from different directory)
vault_path: ../MyVault

# Right (absolute path)
vault_path: /Users/username/Documents/MyVault
```

### 9.2 Ollama Quirks

**Gotcha 1: Model must be pulled first**

```bash
# This will fail
python3 run.py  # If model not installed

# Must do this first
ollama pull qwen2.5:3b
```

**Gotcha 2: Timeout calculation includes retry**

```python
# Timeout increases with retry attempts
timeout = OLLAMA_TIMEOUT + (attempt * 60)
# Attempt 0: 15s
# Attempt 1: 75s  (not 15s!)
# Attempt 2: 135s
```

**Gotcha 3: Ollama keeps models in memory**

```bash
# After running, model stays loaded (uses RAM)
# Configure auto-unload
export OLLAMA_KEEP_ALIVE=5m  # Unload after 5 min idle
```

### 9.3 File Processing

**Gotcha 1: Files not in processed_files set**

```python
# Wrong (string comparison)
if file_path in progress_data['processed_files']:  # List check - slow

# Right (already a set in code)
if file_path in progress_data['processed_files']:  # Set check - fast
```

**Gotcha 2: Backup folder must exist**

```python
# Code creates _backups/ folder automatically
# BUT: If vault_path is wrong, creates _backups/ in wrong location
# Always verify: ls -la /path/to/vault/_backups/
```

**Gotcha 3: File naming collisions**

```markdown
# Original: note.md
# Generated: note_linked.md

# If you run twice without deleting:
# - First run: note.md → note_linked.md
# - Second run: note.md → note_linked.md (overwrites!)

# Solution: Delete *_linked.md files before re-running
find /path/to/vault -name "*_linked.md" -delete
```

### 9.4 Caching Behavior

**Gotcha 1: Content hash is partial**

```python
# Hash is of first 2000 chars only
content_sample = main_content[:2000]
hash_key = get_content_hash(content_sample)

# Implication: Changes beyond char 2000 won't invalidate cache
# Rare issue, but be aware
```

**Gotcha 2: Cache persists across runs**

```bash
# If you change AI model, cache still has old results
# Solution: Clear cache
rm .ai_cache.json
```

### 9.5 Dashboard Limitations

**Gotcha 1: Dashboard not integrated with core**

```python
# Current state: Dashboard infrastructure complete
# BUT: Integration with obsidian_auto_linker_enhanced.py pending

# run_with_dashboard.py exists but doesn't yet feed metrics
# See IMPLEMENTATION_SUMMARY.md → Priority 1
```

**Gotcha 2: M4-specific features need macOS**

```python
# Code detects 8 cores (4P + 4E)
# On non-M4 systems: Falls back to general core count
# Temperature monitoring: Requires macOS sensors
```

### 9.6 Resume Behavior

**Gotcha 1: Processed files are never reprocessed**

```python
# If file content changes AFTER processing:
# - Still skipped (based on file path, not content hash)

# Solution: Delete from progress file
python3 -c "
import json
with open('.processing_progress.json', 'r+') as f:
    data = json.load(f)
    data['processed_files'].remove('/path/to/file.md')
    f.seek(0)
    json.dump(data, f)
    f.truncate()
"
```

**Gotcha 2: Failed files are tracked separately**

```python
# Failed files are in progress_data['failed_files']
# They ARE retried on next run (not skipped)
# If want to skip failed: Move to processed_files set
```

---

## 10. Extension Points

### 10.1 Adding New File Formats

**Current**: Only `.md` files supported

**Extension Point**: `should_process_file()` and `process_conversation()`

```python
# In obsidian_auto_linker_enhanced.py

def should_process_file(file_path: str) -> bool:
    # Add new extension
    if file_path.endswith('.txt'):
        return True

    # Existing logic...

def process_conversation(file_path, existing_notes, stats):
    # Add format-specific reading
    if file_path.endswith('.txt'):
        content = read_txt_file(file_path)
    else:
        content = read_markdown_file(file_path)

    # Rest of processing...
```

### 10.2 Custom AI Models

**Current**: Ollama with configurable model

**Extension Point**: `call_ollama()` function

```python
# Option 1: Different Ollama model (easy)
# In config.yaml
ollama_model: llama2:13b

# Option 2: Different AI backend (moderate)
# In obsidian_auto_linker_enhanced.py

def call_ollama(prompt, system_prompt, max_retries):
    if AI_BACKEND == "openai":
        return call_openai(prompt, system_prompt)
    elif AI_BACKEND == "anthropic":
        return call_anthropic(prompt, system_prompt)
    else:
        # Existing Ollama code
```

### 10.3 Custom Output Formats

**Current**: Markdown footer with specific sections

**Extension Point**: `process_conversation()` → footer building

```python
def build_custom_footer(ai_result, existing_notes):
    # Custom format
    footer = f"""
---
## 🎯 SUMMARY
{ai_result['primary_topic']}

## 🔗 RELATED
{', '.join(ai_result['sibling_notes'])}

## 📌 TAGS
{' '.join(['#' + tag for tag in ai_result['hierarchical_tags']])}
"""
    return footer

# Use in process_conversation()
footer = build_custom_footer(ai_result, existing_notes)
```

### 10.4 Parallel Processing

**Current**: Sequential processing (safe, simple)

**Extension Point**: `main()` function

```python
# Future implementation (planned)
from concurrent.futures import ThreadPoolExecutor

def main():
    # ... existing setup ...

    if PARALLEL_WORKERS > 1:
        with ThreadPoolExecutor(max_workers=PARALLEL_WORKERS) as executor:
            futures = [
                executor.submit(process_conversation, file_path, existing_notes, stats)
                for file_path in files_to_process
            ]
            results = [f.result() for f in futures]
    else:
        # Sequential processing
        for file_path in files_to_process:
            process_conversation(file_path, existing_notes, stats)
```

**Note**: Requires thread-safe cache and progress updates.

### 10.5 Web Dashboard

**Current**: Terminal-based with Rich library

**Extension Point**: New module `web_dashboard.py`

```python
# Future implementation
from flask import Flask, render_template, jsonify
from live_dashboard import LiveDashboard

app = Flask(__name__)
dashboard = LiveDashboard()

@app.route('/')
def index():
    return render_template('dashboard.html')

@app.route('/api/metrics')
def metrics():
    return jsonify(dashboard.get_metrics())

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
```

### 10.6 Plugin System

**Future**: Extensible plugin architecture

**Concept**:
```python
# plugins/custom_analyzer.py
class CustomAnalyzer:
    def analyze(self, content, existing_notes):
        # Custom analysis logic
        return {
            'moc_category': 'Custom',
            'primary_topic': '...',
            # ...
        }

# In obsidian_auto_linker_enhanced.py
def load_plugins():
    plugin_dir = Path('plugins')
    for plugin_file in plugin_dir.glob('*.py'):
        module = import_module(f'plugins.{plugin_file.stem}')
        PLUGINS.append(module)

def analyze_with_plugins(content, existing_notes):
    for plugin in PLUGINS:
        if hasattr(plugin, 'CustomAnalyzer'):
            result = plugin.CustomAnalyzer().analyze(content, existing_notes)
            if result:
                return result

    # Fallback to default
    return analyze_with_balanced_ai(content, existing_notes)
```

---

## Summary for AI Assistants

### Quick Reference Card

| Task | Primary File | Key Function |
|------|-------------|--------------|
| **Process files** | `obsidian_auto_linker_enhanced.py` | `main()` |
| **AI analysis** | `obsidian_auto_linker_enhanced.py` | `analyze_with_balanced_ai()` |
| **Interactive setup** | `run.py` | `ObsidianAutoLinker.run_processing()` |
| **Dashboard** | `live_dashboard.py` | `LiveDashboard.render()` |
| **Logging** | `logger_config.py` | `setup_logging()` |
| **Configuration** | `config.yaml` | (YAML file) |
| **Reports** | `generate_detailed_report.py` | `generate_html_report()` |

### Critical Knowledge

1. **Safety First**: Always use dry run modes before live run
2. **Cache is Key**: Check `.ai_cache.json` for performance issues
3. **Resume Works**: Processing can be stopped/restarted safely
4. **Ollama Required**: Local AI server must be running
5. **Config is Static**: Loaded at import time, restart to reload
6. **Logging Over Print**: New code should use logger, not print()
7. **Type Hints Partial**: Public functions have types, utilities may not
8. **Dashboard Pending**: Infrastructure complete, integration in progress

### When to Edit Which File

| Scenario | File to Edit |
|----------|-------------|
| Change AI prompt | `obsidian_auto_linker_enhanced.py` → `analyze_with_balanced_ai()` |
| Add config option | `config.yaml` + load in `obsidian_auto_linker_enhanced.py` |
| Add MOC category | `config.yaml` (`custom_mocs`) OR `obsidian_auto_linker_enhanced.py` (`MOCS`) |
| Add dashboard metric | `live_dashboard.py` → `__init__()` + new panel method |
| Change file filtering | `obsidian_auto_linker_enhanced.py` → `should_process_file()` |
| Modify output format | `obsidian_auto_linker_enhanced.py` → `process_conversation()` (footer section) |
| Add new report | New file in root, follow `generate_detailed_report.py` pattern |
| Change Ollama settings | `config.yaml` (`ollama_*` keys) |

### Integration Status

| Component | Status | Notes |
|-----------|--------|-------|
| Core Processor | ✅ Complete | Production-ready |
| Interactive Runner | ✅ Complete | Dashboard support added |
| Dashboard Infrastructure | ✅ Complete | Fully integrated (15s updates) |
| Logging System | ✅ Complete | Structured logging in place |
| Caching | ✅ Complete | Working well |
| Progress Tracking | ✅ Complete | Resume functionality works |
| Reports | ✅ Complete | HTML and terminal |
| Config Validation | ✅ Complete | Pydantic schemas with type safety |
| Security | ✅ Enhanced | Comprehensive path validation |
| Test Suite | ✅ Complete | 75 tests, 100% passing |
| Parallel Processing | ⏳ Planned | Config exists, not implemented |
| Web Dashboard | ⏳ Future | Terminal dashboard works |

---

## Development Roadmap

### Completed in v1.1.0 ✅

#### Priority 1: Full Integration (COMPLETED)
- ✅ Integrate dashboard with `obsidian_auto_linker_enhanced.py`
- ✅ Replace print() with logger calls in core processor (91 replacements)
- ✅ Hook up metrics collection during processing (25+ metrics)
- ✅ Add dashboard support to run.py with interactive enable/disable
- ✅ Lower dashboard update interval to 15 seconds

#### Priority 2: Testing (COMPLETED)
- ✅ Create pytest test suite (75 tests, 100% passing)
- ✅ Add unit tests for config utilities (28 tests)
- ✅ Add unit tests for Pydantic validation (26 tests)
- ✅ Add unit tests for logging (10 tests)
- ✅ Add integration tests (11 tests)
- ✅ Add fixtures and test infrastructure
- ⏳ Add CI/CD pipeline (pending - see Priority 3)

#### Priority 5: Code Quality (PARTIALLY COMPLETED)
- ✅ Add type hints to core functions (10+ functions)
- ✅ Add Pydantic config validation with type safety
- ✅ Fix all bare exception handlers
- ✅ Refactor into modules (config_utils.py, config_schema.py)
- ✅ Remove code duplication (8+ patterns eliminated)
- ✅ Enhanced security for path validation
- ✅ Created comprehensive documentation
- ⏳ Setup mypy type checking (pending)
- ⏳ Add comprehensive docstrings to all functions (pending)
- ⏳ Complete modularization of monolithic processor (in progress)

### Current Priorities (v1.2.0 Planning)

#### Priority 3: Advanced Features
**Timeline**: 2-4 weeks

- [ ] Export dashboard metrics to CSV/JSON
  - Real-time metric export during processing
  - Historical run data persistence
  - Analytics report generation

- [ ] Historical run comparison
  - Compare performance across runs
  - Track improvements over time
  - Identify regressions

- [ ] Alert thresholds
  - High CPU usage alerts (>80%)
  - Error rate monitoring (>5%)
  - Slow processing detection
  - Memory leak detection

- [ ] Web dashboard option
  - Flask-based web UI
  - Real-time metrics via WebSocket
  - Mobile-responsive design
  - Authentication/security

- [ ] Mobile monitoring app (future)
  - iOS/Android companion app
  - Push notifications for alerts
  - Remote monitoring capabilities

#### Priority 4: Performance Optimization
**Timeline**: 1-2 weeks

- [ ] Implement lazy loading for large vaults
  - Stream file discovery
  - On-demand file reading
  - Memory-efficient processing
  - Batch processing improvements

- [ ] Add parallel processing
  - Use `parallel_workers` config (already exists)
  - Thread-safe cache implementation
  - Concurrent file processing
  - Performance benchmarking

- [ ] LRU cache with size limits
  - Configurable cache size (MB limit)
  - Automatic eviction policy
  - Cache warmup strategies
  - Persistent cache option

- [ ] Optimize file I/O
  - Buffered file reading
  - Async I/O for large files
  - Reduce disk seeks
  - Compression for backups

#### Priority 6: Production Readiness
**Timeline**: 1 week

- [ ] Set up CI/CD pipeline (GitHub Actions)
  - Automated testing on push
  - Code coverage reports
  - Automated releases
  - Docker containerization

- [ ] Add comprehensive docstrings
  - Google-style docstrings for all functions
  - API documentation generation
  - Usage examples in docs
  - Inline code comments

- [ ] Setup mypy type checking
  - Strict type checking enabled
  - Type stubs for dependencies
  - CI integration
  - Type coverage reports

- [ ] Security audit
  - Dependency vulnerability scanning
  - SAST (Static Application Security Testing)
  - Security best practices review
  - Regular security updates

### Future Enhancements (v2.0+)

#### Long-term Goals
- [ ] Plugin system for custom analyzers
- [ ] Support for other note-taking apps (Notion, Roam)
- [ ] Machine learning for better link suggestions
- [ ] Collaborative vault processing
- [ ] Cloud sync and backup
- [ ] Visual knowledge graph viewer
- [ ] Natural language queries
- [ ] Integration with external APIs (Wikipedia, research databases)

---

## Feature Status Matrix

| Feature | Status | Version | Notes |
|---------|--------|---------|-------|
| **Core Processing** | ✅ Complete | v1.0 | Production-ready |
| **Live Dashboard** | ✅ Complete | v1.0 | 15s updates, M4-optimized |
| **Dashboard Integration** | ✅ Complete | v1.1 | Integrated with run.py |
| **Structured Logging** | ✅ Complete | v1.0 | File rotation, multiple handlers |
| **Config Validation** | ✅ Complete | v1.1 | Pydantic type-safe validation |
| **Path Security** | ✅ Enhanced | v1.1 | Comprehensive security checks |
| **Test Suite** | ✅ Complete | v1.1 | 75 tests, 100% passing |
| **Type Hints** | 🟡 Partial | v1.1 | Core functions covered |
| **Code Deduplication** | ✅ Complete | v1.1 | Centralized utilities |
| **Documentation** | ✅ Complete | v1.1 | CLAUDE.md, testing guides |
| **Parallel Processing** | ⏳ Planned | v1.2 | Config exists, implementation pending |
| **Web Dashboard** | ⏳ Planned | v1.3 | Terminal dashboard available |
| **CI/CD** | ⏳ Planned | v1.2 | Framework ready |
| **Cache Limits** | ⏳ Planned | v1.2 | Basic cache working |
| **Lazy Loading** | ⏳ Planned | v1.2 | Performance optimization |
| **Metric Export** | ⏳ Planned | v1.2 | Dashboard infrastructure ready |
| **Alert System** | ⏳ Planned | v1.3 | Foundation in place |
| **Plugin System** | 💡 Future | v2.0 | Architecture design needed |

---

## Configuration Reference

### All Available Settings

Based on `config_schema.py` Pydantic validation:

```yaml
# === CORE PROCESSING ===
vault_path: /path/to/vault           # Required, validated for security
dry_run: true                        # Default: true (safe mode)
fast_dry_run: false                  # Default: false (requires dry_run=true)
batch_size: 5                        # Range: 1-100, default: 1
file_ordering: recent                # Options: recent|size|random|alphabetical

# === OLLAMA CONFIGURATION ===
ollama_base_url: http://localhost:11434  # Must start with http:// or https://
ollama_model: qwen2.5:3b             # Default: qwen2.5:3b
ollama_timeout: 15                   # Range: 5-300 seconds, default: 15
ollama_max_retries: 1                # Range: 0-5, default: 1
ollama_temperature: 0.3              # Range: 0.0-2.0, default: 0.3
ollama_max_tokens: 200               # Range: 50-2000, default: 200

# === FEATURES ===
cache_enabled: true                  # Default: true
resume_enabled: true                 # Default: true
confirm_large_batches: false         # Default: false

# === FILTERING ===
exclude_patterns:                    # List of fnmatch patterns
  - "*.tmp"
  - ".*"
  - "_*"

include_patterns:                    # List of fnmatch patterns
  - "*.md"

folder_whitelist:                    # Optional: only process these folders
  - "Conversations"
  - "Notes"

folder_blacklist:                    # Folders to skip
  - "_backups"
  - ".git"
  - "Templates"

# === ADVANCED ===
parallel_workers: 1                  # Range: 1-16, default: 1 (future use)
max_retries: 1                       # Range: 0-5, default: 1

# === CUSTOM MOCs ===
custom_mocs:                         # Optional: add custom categories
  "My Category": "📍 My Category MOC"
  "Research": "📍 Research MOC"
```

### Validation Rules

All settings are validated by Pydantic with:
- **Type checking**: Automatic type conversion and validation
- **Range validation**: Numeric parameters have min/max limits
- **URL validation**: ollama_base_url must be valid HTTP(S) URL
- **Enum validation**: file_ordering must be one of allowed values
- **Cross-field validation**: fast_dry_run requires dry_run=true
- **Path security**: vault_path validated for security threats
- **Helpful errors**: Clear error messages on validation failure

---

## Changelog

| Date | Version | Changes |
|------|---------|---------|
| 2025-11-14 | 1.1.0 | Major improvements: Dashboard integration in run.py, pytest framework (75 tests), Pydantic config validation, enhanced security |
| 2025-11-14 | 1.0.0 | Initial CLAUDE.md creation with comprehensive documentation |

---

## Recent Improvements (v1.1.0)

### Dashboard & Monitoring
- ✅ Added dashboard support to `run.py` - users can enable/disable interactively
- ✅ Lowered dashboard update interval from 30s to 15s across all files
- ✅ Added file count tracking (scanned/processed) to resource summary
- ✅ Dashboard now shows: Files Scanned, Files Processed, CPU/Memory usage

### Testing Infrastructure
- ✅ Set up pytest framework with comprehensive test suite
- ✅ **75 tests total, 100% passing** across 4 test modules:
  - `test_config_utils.py`: 28 tests for configuration utilities
  - `test_config_schema.py`: 26 tests for Pydantic validation
  - `test_logger_config.py`: 10 tests for logging system
  - `test_integration.py`: 11 integration tests
- ✅ Created `pytest.ini` with coverage configuration
- ✅ Added fixtures for temp directories, mock vaults, sample configs
- ✅ Complete testing documentation in `tests/README.md`

### Configuration Validation
- ✅ Created `config_schema.py` with Pydantic models for type-safe validation
- ✅ Schema includes: OllamaConfig, ProcessingConfig, FilterConfig, ObsidianConfig
- ✅ Features:
  - Automatic type validation and conversion
  - Range validation (timeout: 5-300s, batch_size: 1-100, etc.)
  - URL format validation
  - Cross-field validation (e.g., fast_dry_run requires dry_run)
  - User home directory expansion
  - YAML file loading/saving with validation
  - Helpful error messages on validation failures

### Security Enhancements
- ✅ Enhanced `validate_vault_path()` with comprehensive security checks:
  - Null byte detection (prevents path injection attacks)
  - System directory blocking (/etc, /sys, /proc, /dev, /bin, C:\Windows, etc.)
  - Root directory blocking
  - File vs directory validation
  - Read permission verification
  - Optional symlink validation
  - User home directory expansion
- ✅ 9 new security tests covering all edge cases

### Code Quality
- ✅ Created `config_utils.py` module with centralized utilities
- ✅ Eliminated code duplication across modules
- ✅ Added comprehensive type hints
- ✅ All tests passing with no regressions

### Running Tests
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov

# Run specific test file
pytest tests/test_config_utils.py

# Run with verbose output
pytest -v
```

---

**End of CLAUDE.md**

*This file is maintained for AI assistants working with the Obsidian Auto-Linker codebase. Keep it updated as the codebase evolves.*
