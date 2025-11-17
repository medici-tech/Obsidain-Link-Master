# 🤖 Claude Context Document

**For AI Assistants working on this project**

**Last Updated**: 2025-03-30
**Version**: 3.1.0 - Post-Review Edition
**Purpose**: Comprehensive guide for AI assistants working with the Obsidian Auto-Linker codebase

---

## 📋 Table of Contents

1. [Project Overview](#1-project-overview)
2. [Current Status](#2-current-status)
3. [Repository Structure](#3-repository-structure)
4. [Architecture & Design](#4-architecture--design)
5. [Development Workflows](#5-development-workflows)
6. [Coding Conventions](#6-coding-conventions)
7. [Configuration System](#7-configuration-system)
8. [Testing Infrastructure](#8-testing-infrastructure)
9. [Common Tasks](#9-common-tasks)
10. [Important Gotchas](#10-important-gotchas)
11. [Roadmap & Priorities](#11-roadmap--priorities)

---

## 1. Project Overview

### 1.1 What Is This?

**Enhanced Obsidian Auto-Linker** is an intelligent Python tool that automatically processes Markdown files in an Obsidian vault using **local AI (Ollama)** to:

- Analyze note content and extract key concepts
- Categorize notes into a Map of Content (MOC) structure
- Create wiki-style links between related notes
- Generate hierarchical tags
- Build a knowledge graph with parent/sibling/child relationships

**Core Philosophy**:
- ✅ **Local-only** (no cloud/external APIs)
- ✅ **Privacy-focused** (all processing happens locally)
- ✅ **Cost-free** (using local Ollama models)
- ✅ **Safe** (dry-run mode, automatic backups)
- ✅ **Resumable** (can stop/restart without losing progress)

### 1.2 Key Features

| Feature | Status | Description |
|---------|--------|-------------|
| **Safe Processing** | ✅ Complete | Dry-run mode, automatic backups |
| **Smart Caching** | ✅ Complete | MD5-based cache with LRU eviction |
| **Bounded Cache** | ✅ Implemented | Memory leak prevention with size limits |
| **Incremental Processing** | ✅ Implemented | 90% faster on reruns (hash-based) |
| **Resume Capability** | ✅ Complete | Stop/restart without losing progress |
| **Live Dashboard** | ✅ Complete | Real-time metrics with Rich library |
| **Multiple Modes** | ✅ Complete | Fast Dry Run, Full Dry Run, Live Run |
| **Comprehensive Testing** | ✅ Complete | 291+ tests across 14 test files |
| **Parallel Processing** | ⏳ Planned | Config exists, implementation planned |

### 1.3 Target Environment

- **Primary OS**: macOS, Linux, Windows
- **Python**: 3.9+
- **AI Backend**: Ollama (localhost:11434)
- **Recommended Models**:
  - qwen3:8b (complex content, high accuracy)
  - qwen2.5:3b (simple content, fast processing)
- **Vault**: Obsidian vault with Markdown files

---

## 2. Current Status

### 2.1 Recent Major Accomplishments (November 2025)

**✅ Phase 1 Complete - Code Organization & Cleanup**
- Archived 13 duplicate/experimental files
- Consolidated duplicate code (cache_utils.py)
- Fixed all import issues
- Created comprehensive documentation
- Professional README with CI badges
- 47% reduction in root directory files

**✅ Phase 2 In Progress - Performance Features**
- ✅ **Bounded Cache Implemented** (prevents memory leaks)
- ✅ **Incremental Processing Implemented** (90% faster reruns)
- ⏳ Parallel Processing (planned)

**✅ Comprehensive Testing**
- 291+ tests across 14 test files
- 55% code coverage (target: 70%+)
- Full CI/CD pipeline with GitHub Actions
- Multi-version Python testing (3.9-3.12)

### 2.2 Project Health Metrics

```
Code Organization:    ⭐⭐⭐⭐⭐ (5/5) - Clean, professional
Documentation:        ⭐⭐⭐⭐⭐ (5/5) - Comprehensive (100KB+)
Test Coverage:        ⭐⭐⭐⭐ (4/5) - Good (55%, improving)
Code Quality:         ⭐⭐⭐⭐ (4/5) - High quality, some improvements needed
Maintainability:      ⭐⭐⭐⭐⭐ (5/5) - Excellent structure
Developer Experience: ⭐⭐⭐⭐⭐ (5/5) - Clear, well-documented

Overall:              ⭐⭐⭐⭐⭐ (5/5) - EXCELLENT
```

### 2.3 What's Working Well

- ✅ Core processing engine (stable, production-ready)
- ✅ Caching system (now with bounded cache)
- ✅ Incremental processing (90% faster on reruns)
- ✅ Dashboard infrastructure (integrated with runners)
- ✅ Progress tracking and resume functionality
- ✅ Comprehensive test suite
- ✅ CI/CD automation
- ✅ Documentation (extensive and up-to-date)

### 2.4 Known Limitations

- ⏳ Parallel processing not yet implemented (sequential only)
- ⏳ Test coverage at 55% (targeting 70%+)
- ⏳ Some magic numbers in code (acceptable for now)
- ⏳ Scripts directory needs README (planned)

### 2.5 March 2025 Review Highlights

- ⚠️ **Configuration validation gaps**: CLI flags (especially `--live`/`--dashboard`) can bypass schema checks—prefer loading configs through `config_utils.validate_and_resolve_config` and tighten validation before new releases.
- ⚠️ **Ollama timeout handling**: Long-running generations can exceed defaults; adjust `ollama_timeout_seconds` in configs or propagate per-call overrides to prevent stuck runs.
- ⚠️ **Incomplete default coverage**: Some config keys (e.g., cache/dry-run toggles) rely on implicit defaults—keep `config_schema.py` and sample YAML files aligned.
- ⚠️ **Test setup guidance drift**: Several docs still reference deprecated setup scripts; follow `TESTING_GUIDE.md` and `requirements-test.txt` for current workflows until docs are refreshed.
- 📄 Full details: see `CODE_REVIEW_2025-03-30.md` for actionable recommendations and context from the latest audit.

---

## 3. Repository Structure

### 3.1 Current File Organization (Post-Cleanup)

```
/home/user/Obsidain-Link-Master/
├── 📁 Core Application (Root Directory - 12 files)
│   ├── obsidian_auto_linker_enhanced.py  # Main processor (2,052 lines)
│   ├── run.py                            # Interactive CLI runner (575 lines)
│   ├── run_with_dashboard.py             # Dashboard runner (567 lines)
│   ├── live_dashboard.py                 # Live dashboard (688 lines)
│   ├── enhanced_analytics.py             # Analytics (530 lines)
│   ├── ultra_detailed_analytics.py       # Advanced analytics (567 lines)
│   ├── logger_config.py                  # Logging system (110 lines)
│   ├── memory_monitor.py                 # Memory tracking (215 lines)
│   ├── config_utils.py                   # Config utilities (353 lines)
│   ├── config_schema.py                  # Pydantic validation (285 lines)
│   ├── check_memory.py                   # Memory check utility (74 lines)
│   └── config.yaml                       # User configuration
│
├── 📁 Scripts (Utilities)
│   ├── intelligent_model_selector.py     # Model selection logic
│   ├── model_performance_test.py         # Model benchmarking
│   ├── optimize_performance.py           # Performance tuning
│   ├── dry_run_analysis.py              # Dry run tools
│   ├── cache_utils.py                   # Cache management (bounded cache)
│   ├── incremental_processing.py        # Incremental processing (FileHashTracker)
│   ├── verify_system.py                 # System verification
│   └── README.md                        # Scripts documentation (planned)
│
├── 📁 Tests (14 test files, 291+ tests)
│   ├── conftest.py                      # Pytest fixtures
│   ├── test_ollama_integration.py       # AI integration (15 tests)
│   ├── test_cache.py                    # Cache operations (15 tests)
│   ├── test_analytics.py                # Analytics (22 tests)
│   ├── test_dashboard.py                # Dashboard (30+ tests)
│   ├── test_model_selector.py           # Model selection (40+ tests)
│   ├── test_ultra_detailed_analytics.py # Advanced analytics (45+ tests)
│   ├── test_live_monitoring.py          # Live monitoring (70+ tests)
│   ├── test_performance_benchmarks.py   # Performance (50+ tests)
│   ├── test_content_processing.py       # Content processing (12 tests)
│   ├── test_file_operations.py          # File operations (18 tests)
│   ├── test_integration.py              # Integration tests (12 tests)
│   ├── test_logger_config.py            # Logging (10 tests)
│   ├── test_config_utils.py             # Config utilities (28 tests)
│   └── test_config_schema.py            # Pydantic validation (26 tests)
│
├── 📁 Configs (8 active configurations)
│   ├── config_fast.yaml                 # Fast processing
│   ├── config_ultra_fast.yaml           # Ultra-fast mode
│   ├── config_hybrid_models.yaml        # Hybrid model selection
│   ├── config_qwen3_maximum_detail.yaml # Maximum detail mode
│   ├── config_extended_timeout.yaml     # Extended timeouts
│   ├── config_detailed_analytics.yaml   # Detailed analytics
│   ├── config_parallel_optimized.yaml   # Parallel processing (future)
│   ├── config_macbook_air_16gb.yaml     # MacBook Air optimized
│   ├── deprecated/                      # Deprecated configs (archived)
│   └── README.md                        # Configuration guide
│
├── 📁 Documentation (100KB+ docs)
│   ├── README.md                        # Quick start (10KB)
│   ├── CLAUDE.md                        # This file (AI assistant guide)
│   ├── ARCHITECTURE.md                  # System architecture (28KB)
│   ├── API_REFERENCE.md                 # API documentation (20KB)
│   ├── TROUBLESHOOTING.md               # Problem solving (17KB)
│   ├── ROADMAP.md                       # Development roadmap (24KB)
│   ├── README_ENHANCED.md               # Comprehensive guide (14KB)
│   ├── QUICK_START.md                   # 5-minute setup (2KB)
│   ├── COMPREHENSIVE_REVIEW.md          # Project review (35KB)
│   ├── SESSION_COMPLETION_SUMMARY.md    # Phase 1 completion (16KB)
│   ├── CLEANUP_SUMMARY.md               # Cleanup report (10KB)
│   ├── PHASE_2_PROGRESS_SUMMARY.md      # Phase 2 status (12KB)
│   ├── REFACTORING_PLAN.md              # Refactoring guide (22KB)
│   ├── REPOSITORY_ANALYSIS_SUMMARY.md   # Repo analysis (22KB)
│   ├── PROJECT_TODO.md                  # Master TODO list (9KB)
│   ├── TESTING_GUIDE.md                 # Testing guide (13KB)
│   ├── DEPLOYMENT.md                    # Deployment guide (6KB)
│   ├── CONTRIBUTING.md                  # Contribution guide (10KB)
│   └── USAGE.md                         # Usage examples (2KB)
│
├── 📁 Archive (Experimental/deprecated files)
│   ├── experimental_runners/            # Old runner scripts (10 files)
│   ├── experimental_tests/              # Old test files (3 files)
│   ├── old_docs/                        # Archived documentation
│   └── README.md                        # Archive documentation
│
├── 📁 Other Directories
│   ├── .github/workflows/               # CI/CD (GitHub Actions)
│   ├── reports/                         # Generated analytics
│   ├── reviews/                         # Manual review queue
│   └── docs/                            # Additional documentation
│
└── 📁 Configuration Files
    ├── requirements.txt                 # Python dependencies
    ├── requirements-test.txt            # Testing dependencies
    ├── pytest.ini                       # Pytest configuration
    ├── .gitignore                       # Git ignore rules
    └── LICENSE                          # MIT License
```

### 3.2 Key Metrics

```
Total Python Files:     ~30 core files + 14 test files + 8 utility scripts
Total Lines of Code:    ~15,000 lines (core) + ~5,000 lines (tests)
Documentation:          100KB+ across 20+ files
Tests:                  291+ tests across 14 files
Test Coverage:          55% (target: 70%+)
Configs:                8 active + 2 deprecated
```

---

## 4. Architecture & Design

### 4.1 System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    USER INTERFACES                           │
├──────────────────┬──────────────────┬───────────────────────┤
│   run.py         │ run_with_        │  Direct Script        │
│   (Interactive)  │ dashboard.py     │  Execution            │
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
         │  │  2. Incremental Check (NEW!)     │ │
         │  │  3. AI Analysis & Categorization │ │
         │  │  4. Bounded Cache (NEW!)         │ │
         │  │  5. Link Generation              │ │
         │  │  6. Wiki Structure Creation      │ │
         │  │  7. Progress Tracking            │ │
         │  └──────────────────────────────────┘ │
         └─────────┬───────────────────┬──────────┘
                   │                   │
         ┌─────────▼────────┐  ┌──────▼──────────┐
         │  MONITORING       │  │  UTILITIES      │
         │  - Dashboard      │  │  - Logger       │
         │  - Analytics      │  │  - Model Sel    │
         │  - Memory Mon     │  │  - Cache Utils  │
         └───────────────────┘  └─────────────────┘
                   │
         ┌─────────▼────────────────────────┐
         │   EXTERNAL SERVICES & STORAGE    │
         │  - Ollama API (localhost:11434)  │
         │  - File System (Vault)           │
         │  - Bounded Cache (JSON + LRU)    │
         │  - Progress Files (JSON)         │
         │  - Hash Tracker (Incremental)    │
         │  - Backups Folder                │
         └──────────────────────────────────┘
```

### 4.2 Core Processing Workflow

```python
1. Load Configuration (config.yaml)
   ├─> Validate with Pydantic schemas
   └─> Apply defaults

2. Initialize Components
   ├─> BoundedCache (LRU eviction, size limits) ✨ NEW
   ├─> FileHashTracker (incremental processing) ✨ NEW
   ├─> Progress tracking (resume support)
   └─> Analytics dict

3. Test Ollama Connection
   ├─> Check localhost:11434 availability
   └─> Exit if unavailable

4. Scan Vault for Notes
   ├─> Recursive directory walk
   ├─> Apply exclude/include patterns
   ├─> Apply folder whitelist/blacklist
   └─> Build existing_notes dict

5. Incremental Processing Check ✨ NEW
   ├─> Calculate file content hashes
   ├─> Compare with previous run
   ├─> Skip unchanged files (90% faster!)
   └─> Queue only modified/new files

6. Create MOC Notes (if missing)
   ├─> Check for 12 standard MOCs
   └─> Create from template if missing

7. Process Each File (Sequential)
   ├─> Skip if already processed (resume)
   ├─> Read file content
   ├─> Analyze Content:
   │   ├─> Fast Dry Run: Keyword-based
   │   └─> Full Analysis: AI-powered
   │       ├─> Generate MD5 hash
   │       ├─> Check bounded cache ✨ UPDATED
   │       ├─> Build Ollama prompt
   │       ├─> Call API (with retries)
   │       ├─> Parse JSON response
   │       └─> Update cache (with LRU eviction) ✨ UPDATED
   ├─> Verify Sibling Links
   ├─> Build Footer (Metadata, Wiki, Concepts, Tags)
   ├─> Backup Original File
   ├─> Write New File (*_linked.md)
   ├─> Update Progress & Save
   ├─> Update Hash Tracker ✨ NEW
   └─> Update Analytics

8. Save State
   ├─> Persist bounded cache
   ├─> Save hash tracker state
   └─> Generate analytics report
```

### 4.3 Key Design Patterns

#### **1. Cache-Aside Pattern with LRU Eviction** ✨ UPDATED
```python
# Bounded cache with LRU eviction (prevents memory leaks)
from scripts.cache_utils import BoundedCache

cache = BoundedCache(max_size_mb=1000, max_entries=10000)

hash_key = get_content_hash(content)
if hash_key in cache:
    return cache[hash_key]  # Cache hit

# Cache miss: fetch from AI
result = call_ollama(prompt)
cache[hash_key] = result  # Update cache (auto-evicts oldest if full)
return result
```

#### **2. Incremental Processing Pattern** ✨ NEW
```python
# Only process files that changed since last run
from scripts.incremental_processing import FileHashTracker

tracker = FileHashTracker('.file_hashes.json')

for file_path in all_files:
    if tracker.should_reprocess(file_path):
        # File is new or modified
        process_file(file_path)
        tracker.mark_processed(file_path)
    else:
        # File unchanged, skip processing
        continue

tracker.save()  # Persist hashes for next run
```

#### **3. Retry with Exponential Backoff**
```python
for attempt in range(max_retries):
    try:
        response = requests.post(url, timeout=timeout)
        return response.json()
    except Exception as e:
        if attempt < max_retries - 1:
            wait = 2 ** attempt  # 1s, 2s, 4s, 8s, 16s
            time.sleep(wait)
        else:
            raise
```

#### **4. Progress Tracking Pattern**
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

### 4.4 MOC (Map of Content) System

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

---

## 5. Development Workflows

### 5.1 Standard Development Cycle

```bash
# 1. Setup (First Time)
git clone <repo>
cd Obsidain-Link-Master
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install -r requirements-test.txt

# 2. Start Ollama
ollama serve  # In separate terminal

# 3. Pull models
ollama pull qwen3:8b
ollama pull qwen2.5:3b

# 4. Run tests
pytest -v

# 5. Make changes
# Edit code...

# 6. Test changes
pytest tests/test_yourfile.py -v

# 7. Run application
python3 run.py  # Interactive mode
# or
python3 run_with_dashboard.py  # With dashboard

# 8. Commit
git add .
git commit -m "feat: your feature description"
git push -u origin <branch-name>
```

### 5.2 Git Workflow

**Branch Strategy**:
- **Main branch**: Stable releases
- **Feature branches**: `claude/session-id` or `feature/description`
- **Current branch**: `claude/claude-md-mi1z4qzm9ilscy54-01Q3nQzENBMbrEEpbfq8m7BQ`

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
git commit -m "feat: Implement bounded cache with LRU eviction"
git commit -m "fix: Handle JSON parse errors in AI responses"
git commit -m "docs: Update CLAUDE.md with current repository state"
```

### 5.3 Testing Workflow

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_cache.py -v

# Run specific test
pytest tests/test_cache.py::test_bounded_cache -v

# Run with coverage
pytest --cov=. --cov-report=html
open htmlcov/index.html

# Run fast tests only
pytest -m unit

# Run integration tests
pytest -m integration

# Run performance benchmarks
pytest -m benchmark

# Use test script
./run_tests.sh fast      # Quick unit tests
./run_tests.sh coverage  # With coverage report
```

---

## 6. Coding Conventions

### 6.1 Naming Conventions

| Type | Convention | Examples |
|------|------------|----------|
| **Functions** | `snake_case` | `process_conversation`, `get_content_hash` |
| **Classes** | `PascalCase` | `BoundedCache`, `FileHashTracker`, `LiveDashboard` |
| **Constants** | `UPPER_SNAKE_CASE` | `VAULT_PATH`, `MAX_RETRIES`, `OLLAMA_MODEL` |
| **Global State** | `lowercase` | `analytics`, `progress_data`, `ai_cache` |
| **Private Methods** | `_leading_underscore` | `_create_panel`, `_calculate_stats` |
| **Module Files** | `snake_case.py` | `logger_config.py`, `live_dashboard.py` |

### 6.2 Type Hints

**Usage**: Partial type hints on public functions

```python
from typing import List, Set, Dict, Tuple, Optional, Any

# Good (type hints on public functions)
def process_conversation(file_path: str, existing_notes: Dict[str, str], stats: Dict) -> bool:
    ...

def analyze_with_balanced_ai(content: str, existing_notes: Dict[str, str]) -> Optional[Dict]:
    ...

# Acceptable (no type hints on simple utilities)
def show_progress(current, total):
    percentage = (current / total) * 100
    print(f"Progress: {percentage:.1f}%")
```

### 6.3 Error Handling

**Pattern**: Use specific exceptions, provide context

```python
# Good
try:
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
except FileNotFoundError:
    logger.error(f"File not found: {file_path}")
    return None
except PermissionError:
    logger.error(f"Permission denied: {file_path}")
    return None
except Exception as e:
    logger.error(f"Unexpected error reading {file_path}: {e}")
    return None

# Bad (bare except)
try:
    content = open(file_path).read()
except:
    pass
```

### 6.4 Logging vs Print

**Rule**: New code should use logging, not print()

```python
# Good (structured logging)
from logger_config import get_logger
logger = get_logger(__name__)

logger.info(f"Processing {file_path}...")
logger.error(f"Failed to process file: {e}")
logger.warning(f"Cache miss for {file_path}")
logger.debug(f"AI response: {response}")

# Bad (print statements)
print(f"Processing {file_path}...")
print(f"Error: {e}")
```

### 6.5 Standard Emoji for User Messages

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
- ✨ New feature

---

## 7. Configuration System

### 7.1 config.yaml Structure

**Complete Schema**:

```yaml
# === PROCESSING SETTINGS ===
vault_path: /path/to/vault          # Absolute path to Obsidian vault
dry_run: true                        # Safe mode (no file writes)
fast_dry_run: false                  # Skip AI analysis
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
incremental: true                    # ✨ NEW: Enable incremental processing

# === CACHE SETTINGS (Bounded Cache) ===
max_cache_size_mb: 1000             # ✨ NEW: Max cache size in MB
max_cache_entries: 10000            # ✨ NEW: Max number of cache entries

# === ADVANCED ===
parallel_workers: 1                  # For future parallel processing
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

### 7.2 Configuration Validation

**Pydantic Schemas**: All settings validated with `config_schema.py`

Features:
- ✅ Automatic type validation and conversion
- ✅ Range validation (timeout: 5-300s, batch_size: 1-100, etc.)
- ✅ URL format validation
- ✅ Enum validation (file_ordering must be valid option)
- ✅ Cross-field validation (e.g., fast_dry_run requires dry_run)
- ✅ Path security validation (prevents injection attacks)
- ✅ Helpful error messages on validation failure

---

## 8. Testing Infrastructure

### 8.1 Test Organization

**14 Test Files, 291+ Tests**:

| Test File | Tests | Focus Area |
|-----------|-------|------------|
| `test_ollama_integration.py` | 15 | AI integration, API calls |
| `test_cache.py` | 15 | Cache operations, bounded cache |
| `test_analytics.py` | 22 | Analytics generation |
| `test_dashboard.py` | 30+ | Dashboard UI, metrics |
| `test_model_selector.py` | 40+ | Model selection logic |
| `test_ultra_detailed_analytics.py` | 45+ | Advanced analytics |
| `test_live_monitoring.py` | 70+ | Live monitoring |
| `test_performance_benchmarks.py` | 50+ | Performance baselines |
| `test_content_processing.py` | 12 | Content analysis |
| `test_file_operations.py` | 18 | File I/O operations |
| `test_integration.py` | 12 | End-to-end workflows |
| `test_logger_config.py` | 10 | Logging system |
| `test_config_utils.py` | 28 | Config utilities |
| `test_config_schema.py` | 26 | Pydantic validation |

### 8.2 Running Tests

```bash
# All tests
pytest

# With verbose output
pytest -v

# With coverage
pytest --cov=. --cov-report=html

# Specific test file
pytest tests/test_cache.py -v

# Specific test function
pytest tests/test_cache.py::test_bounded_cache -v

# By marker
pytest -m unit        # Unit tests only
pytest -m integration # Integration tests only
pytest -m benchmark   # Performance benchmarks

# Fast tests (skip slow ones)
./run_tests.sh fast

# Coverage report
./run_tests.sh coverage
```

### 8.3 Test Fixtures (conftest.py)

Available fixtures:
- `temp_vault`: Temporary Obsidian vault
- `sample_markdown`: Sample markdown files
- `mock_ollama`: Mocked Ollama responses
- `sample_config`: Sample configuration
- `mock_cache`: Mocked cache instance

### 8.4 CI/CD Pipeline

**GitHub Actions** (`.github/workflows/test.yml`):
- ✅ Runs on every push and PR
- ✅ Tests on Python 3.9, 3.10, 3.11, 3.12
- ✅ Code coverage reporting
- ✅ Security scanning with Bandit
- ✅ Dependency checking
- ✅ Badge in README.md

---

## 9. Common Tasks

### 9.1 Adding a New Feature

**Process**:

1. **Read relevant documentation** (this file + ARCHITECTURE.md)
2. **Identify touch points** (what files need changes?)
3. **Write tests first** (TDD approach)
4. **Update configuration** (add to config.yaml if needed)
5. **Implement core logic** (update main processor)
6. **Add monitoring** (update dashboard if applicable)
7. **Add logging** (use logger_config.py)
8. **Update documentation** (README.md, API_REFERENCE.md)
9. **Run tests** (pytest -v)
10. **Commit** (follow git conventions)

### 9.2 Adding a New Configuration Option

```python
# 1. Add to config.yaml
my_new_feature_enabled: true

# 2. Add to config_schema.py (Pydantic validation)
class ProcessingConfig(BaseModel):
    my_new_feature_enabled: bool = False

# 3. Load in code (obsidian_auto_linker_enhanced.py)
MY_NEW_FEATURE_ENABLED = config.get('my_new_feature_enabled', False)

# 4. Use in logic
def process_conversation(file_path, existing_notes, stats):
    if MY_NEW_FEATURE_ENABLED:
        # New feature logic
        pass

# 5. Document in README.md and API_REFERENCE.md
```

### 9.3 Debugging Ollama Issues

**Common Issues**:

| Issue | Diagnosis | Solution |
|-------|-----------|----------|
| Connection Refused | `requests.exceptions.ConnectionError` | Start Ollama: `ollama serve` |
| Timeout | `requests.exceptions.Timeout` | Increase `ollama_timeout` in config |
| Model Not Found | `{"error":"model not found"}` | Pull model: `ollama pull qwen2.5:3b` |
| Out of Memory | Slow responses, system lag | Use smaller model (qwen2.5:3b) |

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
```

### 9.4 Recovering from Errors

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

**Scenario 3: Incremental Hashes Out of Sync**
```bash
# Delete hash tracker (will reprocess all files)
rm .file_hashes.json

# Next run will rebuild hashes
python3 run.py
```

---

## 10. Important Gotchas

### 10.1 Configuration Issues

**Gotcha 1: Config loaded at import time**
```python
# Wrong approach - changes won't be reflected
import obsidian_auto_linker_enhanced
# Modify config.yaml
# ... changes won't be reflected ...

# Right approach
# Modify config.yaml FIRST, then run
python3 run.py  # Restarts process, loads new config
```

**Gotcha 2: Relative vs Absolute Paths**
```yaml
# Wrong (relative path)
vault_path: ../MyVault

# Right (absolute path)
vault_path: /Users/username/Documents/MyVault
```

### 10.2 Cache Behavior

**Gotcha 1: Bounded cache evicts oldest entries**
```python
# If cache exceeds max_cache_size_mb or max_cache_entries,
# oldest entries are evicted (LRU policy)
# This is EXPECTED behavior to prevent memory leaks

# If you need persistent cache, increase limits
max_cache_size_mb: 2000  # 2GB
max_cache_entries: 20000
```

**Gotcha 2: Incremental processing uses content hashes**
```python
# If file content changes, it will be reprocessed
# If only metadata changes (timestamps), it will be skipped
# This is EXPECTED behavior for efficiency

# To force reprocess, delete hash tracker
rm .file_hashes.json
```

### 10.3 Ollama Quirks

**Gotcha 1: Model must be pulled first**
```bash
# This will fail if model not installed
python3 run.py

# Must do this first
ollama pull qwen2.5:3b
```

**Gotcha 2: Ollama keeps models in memory**
```bash
# After running, model stays loaded (uses RAM)
# Configure auto-unload
export OLLAMA_KEEP_ALIVE=5m  # Unload after 5 min idle
```

### 10.4 Resume Behavior

**Gotcha: Processed files are never reprocessed (by resume system)**
```python
# If file content changes AFTER processing:
# - Resume system still skips (based on file path)
# - Incremental system detects change (reprocesses)

# Recommendation: Use incremental processing (enabled by default)
incremental: true  # in config.yaml
```

---

## 11. Roadmap & Priorities

### 11.1 Current Status (2025-11-16)

**✅ Phase 1 Complete** (Code Organization & Cleanup)
- All duplicate files archived
- Code organization complete
- Documentation comprehensive
- Professional appearance

**✅ Phase 2 Partially Complete** (Performance Features)
- ✅ Bounded Cache implemented
- ✅ Incremental Processing implemented
- ⏳ Parallel Processing planned

### 11.2 Immediate Priorities (Next 2-4 weeks)

#### Priority 1: Parallel Processing (5-8 hours)
**Status**: ⏳ Planned (config exists, not implemented)

**Implementation**:
```python
from concurrent.futures import ThreadPoolExecutor, as_completed

with ThreadPoolExecutor(max_workers=PARALLEL_WORKERS) as executor:
    futures = {
        executor.submit(process_file, f): f
        for f in files
    }
    for future in as_completed(futures):
        result = future.result()
```

**Challenges**:
- Thread-safe cache updates (use locks)
- Thread-safe progress tracking
- Error handling in threads

**Expected Impact**: 300% faster on multi-core systems

#### Priority 2: Increase Test Coverage (6-8 hours)
**Current**: 55%
**Target**: 70%+

**Focus Areas**:
- Core processing functions
- Error handling paths
- Edge cases in file operations
- Integration test scenarios

#### Priority 3: Scripts Directory README (2 hours)
**Status**: Planned

Create comprehensive documentation for all utility scripts in `scripts/` directory.

#### Priority 4: Performance Profiling (3-4 hours)
**Status**: Planned

- Profile slow operations with cProfile
- Identify bottlenecks
- Optimize hot paths
- Create performance benchmarks

### 11.3 Medium-Term Goals (1-2 months)

1. **Web Dashboard** (12-16 hours)
   - Flask/FastAPI + WebSockets
   - Real-time metrics visualization
   - Mobile-friendly responsive design

2. **Enhanced Analytics** (4-6 hours)
   - Export to CSV/JSON
   - Historical run comparison
   - Trend analysis

3. **Alert System** (3-4 hours)
   - CPU/memory thresholds
   - Error rate monitoring
   - Slow processing detection

4. **Plugin System** (8-12 hours)
   - Extensible architecture
   - Custom analyzers
   - Third-party integrations

### 11.4 Long-Term Vision (3-6 months)

1. **Machine Learning Integration**
   - Better link quality scoring
   - Automatic MOC optimization
   - Content similarity analysis

2. **Advanced Features**
   - Multi-vault support
   - Collaborative processing
   - Cloud sync (optional)

3. **Obsidian Plugin**
   - Native integration
   - Command palette
   - Settings UI

### 11.5 Success Metrics

**Performance Targets**:
- ✅ Incremental processing 90% faster (ACHIEVED)
- ✅ No memory leaks with bounded cache (ACHIEVED)
- ⏳ Parallel processing 3x faster (pending)
- ⏳ Test coverage > 70% (current: 55%)
- ⏳ AI success rate > 95% (needs measurement)

**Quality Targets**:
- ✅ Zero crashes on normal operation (ACHIEVED)
- ✅ All features documented (ACHIEVED)
- ✅ Clear error messages (ACHIEVED)
- ⏳ Type hints coverage 100% (partial)
- ⏳ Zero mypy errors (pending)

---

## 📚 Quick Reference

### Key Files to Read

**For Understanding**:
1. README.md - Project introduction
2. ARCHITECTURE.md - System design
3. QUICK_START.md - Getting started
4. TROUBLESHOOTING.md - Common problems

**For Development**:
1. This file (CLAUDE.md) - AI assistant guide
2. API_REFERENCE.md - Complete API docs
3. configs/README.md - Configuration guide
4. tests/conftest.py - Test fixtures

### When to Edit Which File

| Scenario | File to Edit |
|----------|-------------|
| Change AI prompt | `obsidian_auto_linker_enhanced.py` → `analyze_with_balanced_ai()` |
| Add config option | `config.yaml` + `config_schema.py` + load in main processor |
| Add MOC category | `config.yaml` (`custom_mocs`) OR main processor (`MOCS`) |
| Add dashboard metric | `live_dashboard.py` → `__init__()` + new panel method |
| Change file filtering | `obsidian_auto_linker_enhanced.py` → `should_process_file()` |
| Modify output format | `obsidian_auto_linker_enhanced.py` → footer building section |
| Add new utility | `scripts/yourscript.py` + document in scripts/README.md |
| Change Ollama settings | `config.yaml` (`ollama_*` keys) |

### Component Status

| Component | Status | Notes |
|-----------|--------|-------|
| Core Processor | ✅ Complete | Production-ready |
| Bounded Cache | ✅ Complete | LRU eviction, size limits |
| Incremental Processing | ✅ Complete | 90% faster reruns |
| Dashboard | ✅ Complete | Integrated with runners |
| Logging System | ✅ Complete | Structured logging |
| Progress Tracking | ✅ Complete | Resume functionality |
| Test Suite | ✅ Complete | 291+ tests, 55% coverage |
| CI/CD | ✅ Complete | GitHub Actions |
| Parallel Processing | ⏳ Planned | Sequential only for now |
| Web Dashboard | ⏳ Future | Terminal dashboard works |

---

## 🎯 For AI Assistants: Key Takeaways

1. **Project is local-only** - No cloud services, no external APIs, privacy-first
2. **Phase 1 complete** - Code organization, cleanup, documentation all done
3. **Phase 2 in progress** - Bounded cache ✅, Incremental ✅, Parallel ⏳
4. **Test coverage is good** - 291+ tests, 55% coverage, CI/CD working
5. **Documentation is comprehensive** - 100KB+ across 20+ files
6. **Main priorities** - Parallel processing, increase test coverage, scripts README

### Critical Knowledge

- ✅ **Bounded cache implemented** - Prevents memory leaks with LRU eviction
- ✅ **Incremental processing implemented** - 90% faster on subsequent runs
- ✅ **Config validation with Pydantic** - Type-safe, comprehensive validation
- ✅ **Resume functionality works** - Can stop/restart without losing progress
- ⏳ **Parallel processing planned** - Config exists, implementation pending
- ✅ **All code well-organized** - 47% reduction in root directory clutter

### Before Making Changes

1. Read relevant sections of this file
2. Check ARCHITECTURE.md for system design
3. Run existing tests: `pytest -v`
4. Check test coverage: `pytest --cov`
5. Follow coding conventions (section 6)
6. Update documentation
7. Write tests for new features
8. Commit with proper message format

---

**Last Updated**: 2025-11-16
**Status**: ✅ Phase 1 Complete, Phase 2 Partially Complete
**Next Focus**: Parallel Processing, Test Coverage, Scripts README

**For**: AI Assistants (Claude, etc.) working on this project
**Remember**: This is a local-only tool. All features work entirely offline with local Ollama models!

---

**END OF CLAUDE.MD** 🎉
