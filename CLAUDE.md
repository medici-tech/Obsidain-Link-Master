# 🤖 Claude Context Document

**For AI Assistants working on this project**

This document provides comprehensive context for AI assistants (like Claude) to quickly understand the project, its current state, and how to contribute effectively.

---

## 📋 Project Overview

**Name**: Enhanced Obsidian Auto-Linker
**Type**: Local-only Python tool
**Purpose**: Automatically categorize and link markdown notes in Obsidian vaults using local AI models
**AI Backend**: Ollama (local LLM runtime)
**Primary Models**: Qwen3:8b (complex content), Qwen2.5:3b (simple content)

### What It Does

1. **Scans** your Obsidian vault for markdown files
2. **Analyzes** content using local Ollama AI models
3. **Categorizes** notes into MOC (Map of Content) categories
4. **Creates** wikilinks between related notes automatically
5. **Monitors** processing with a live terminal dashboard
6. **Caches** AI responses to avoid redundant processing
7. **Tracks** analytics and generates HTML reports

### Key Features

- ✅ Local-only (no cloud/external APIs)
- ✅ Intelligent model selection (hybrid mode)
- ✅ Content-based caching (MD5 hashing)
- ✅ Live terminal dashboard (Rich library)
- ✅ Comprehensive analytics and reporting
- ✅ Safe processing (automatic backups, dry-run mode)
- ✅ Retry logic with exponential backoff
- ✅ 291+ comprehensive tests (55% coverage)

---

## 📊 Current Status (2024-11-15)

### ✅ What's Complete

**Testing** (Priority 1 & 2 ✅ Complete):
- 291+ tests across 11 test files
- Unit tests, integration tests, benchmark tests
- Analytics tests, dashboard tests, model selector tests
- CI/CD pipeline with GitHub Actions
- 55% test coverage (target: 70%+)

**Documentation** (✅ Comprehensive):
- ARCHITECTURE.md (800+ lines) - System design
- API_REFERENCE.md (1000+ lines) - Complete API docs
- TROUBLESHOOTING.md (900+ lines) - Problem solving
- configs/README.md - Configuration guide
- All major workflows documented

**Code Organization** (✅ Clean):
- Root: Main launcher scripts only
- scripts/: All utility scripts
- tests/: Complete test suite (11 files)
- configs/: Configuration presets (7 active, 1 deprecated)
- Deprecated files identified and documented

**Critical Tasks** (✅ All Complete):
- All Priority 1 testing done
- All Priority 2 testing done
- Architecture documentation complete
- Code organization complete
- Configuration documentation complete

### 📝 What Remains (Important Priority)

1. **Performance optimization** - Profile and optimize slow operations
2. **Bug fixes** - Large vault handling, memory optimization
3. **End-to-end testing** - Full workflow validation
4. **Cleanup** - Remove deprecated config_default_extended.yaml
5. **Pre-commit hooks** - Auto-formatting, linting
6. **Scripts README** - Document utility scripts in scripts/

### 🟢 Nice to Have (Future)

- Dashboard themes (light/dark for terminal)
- Export analytics to CSV/JSON
- Performance benchmarking mode
- Better AI model selection
- Graph-based linking improvements

---

## 🏗️ Architecture Quick Reference

### Core Components

```
obsidian_auto_linker_enhanced.py (48.6k lines)
├── Main processing engine
├── File discovery and filtering
├── Content analysis with AI
├── Wikilink creation
├── Backup and safety systems
└── Cache management

live_dashboard.py (20.3k lines)
├── Real-time terminal UI (Rich)
├── Metrics tracking
├── System resource monitoring
└── Singleton pattern

enhanced_analytics.py (16.8k lines)
├── Performance metrics
├── HTML report generation
├── MOC distribution analysis
└── Cache performance stats

ultra_detailed_analytics.py (19k lines)
├── Advanced analytics
├── Before/after comparisons
├── Time-series tracking
└── Reasoning analysis

scripts/intelligent_model_selector.py (9.2k lines)
├── Content complexity analysis
├── Model selection (qwen3 vs qwen2.5)
├── Hybrid mode implementation
└── Automatic fallback
```

### Data Flow

```
Markdown File
    ↓
Read Content → Calculate MD5 Hash
    ↓
Check Cache → [HIT] Return Cached
    ↓ [MISS]
Analyze Complexity → Select Model
    ↓
Call Ollama API (with retries)
    ↓
Parse JSON Response → Cache Result
    ↓
Create Wikilinks → Update File → Backup
    ↓
Update Analytics → Dashboard
```

### File Structure

```
/
├── run.py, run_with_dashboard.py     # Main launchers
├── obsidian_auto_linker_enhanced.py  # Core engine
├── live_dashboard.py                 # Dashboard UI
├── enhanced_analytics.py             # Analytics
├── config.yaml                       # Active config
│
├── scripts/                          # Utilities
│   ├── intelligent_model_selector.py
│   ├── model_performance_test.py
│   ├── setup_new_computer.sh
│   └── [other utilities]
│
├── configs/                          # Presets
│   ├── config_hybrid_models.yaml    # Active
│   ├── config_qwen3_maximum_detail.yaml
│   ├── config_extended_timeout.yaml
│   └── [6 other configs]
│
├── tests/                            # Test suite
│   ├── conftest.py                  # Fixtures
│   ├── test_ollama_integration.py   # 15 tests
│   ├── test_cache.py                # 15 tests
│   ├── test_analytics.py            # 22 tests
│   ├── test_dashboard.py            # 30+ tests
│   ├── test_model_selector.py       # 40+ tests
│   ├── test_ultra_detailed_analytics.py  # 45+ tests
│   ├── test_live_monitoring.py      # 70+ tests
│   ├── test_performance_benchmarks.py    # 50+ tests
│   └── [8 more test files]
│
└── docs/                             # Documentation
    ├── ARCHITECTURE.md              # System design
    ├── API_REFERENCE.md             # API docs
    ├── TROUBLESHOOTING.md           # Problem solving
    ├── PROJECT_TODO.md              # Roadmap
    └── [other docs]
```

---

## 🔑 Key Concepts

### 1. MOC Categories

The system categorizes notes into these MOC (Map of Content) types:
- Business Operations
- Technology
- Personal Development
- Finance & Investing
- Health & Wellness
- Creative Projects
- Life & Misc

### 2. Hybrid Model Selection

**Content Complexity Analysis**:
- Word count (>1000 = complex)
- Technical keywords (api, code, python, database, etc.)
- Business keywords (revenue, investment, strategy, etc.)
- Filename patterns (technical_, business_, etc.)

**Model Selection**:
- **qwen3:8b**: Complex content, accuracy-focused (5GB RAM, 300s timeout)
- **qwen2.5:3b**: Simple content, speed-focused (2GB RAM, 60s timeout)

### 3. Caching Strategy

**Cache Key**: MD5 hash of file content
**Cache Hit**: Return cached result immediately
**Cache Miss**: Call AI, cache result, return
**Persistence**: Saved to `ai_cache.json`
**Hit Rate**: Typically 30-50% on repeated runs

### 4. Safety Features

- **Dry Run Mode**: Test without modifying files
- **Automatic Backups**: Timestamped copies before changes
- **Retry Logic**: Exponential backoff (1s, 2s, 4s, 8s, 16s)
- **Fallback**: qwen3:8b fails → qwen2.5:3b fallback
- **Validation**: JSON parsing with error handling

---

## 🛠️ Working on This Project

### Quick Start for Development

```bash
# Setup
./scripts/setup_new_computer.sh
source venv/bin/activate

# Run tests
pytest                    # All tests
./run_tests.sh fast      # Quick unit tests
./run_tests.sh coverage  # With coverage report

# Run application
python run.py                    # Interactive CLI
python run_with_dashboard.py     # With live dashboard

# Lint/Format (when pre-commit hooks added)
# pre-commit run --all-files
```

### Before Making Changes

1. **Read relevant documentation**:
   - ARCHITECTURE.md for system design
   - API_REFERENCE.md for API details
   - TROUBLESHOOTING.md for common issues

2. **Run existing tests**:
   ```bash
   pytest -v
   ```

3. **Check coverage**:
   ```bash
   pytest --cov=. --cov-report=html
   open htmlcov/index.html
   ```

### When Adding Features

1. **Write tests first** (TDD approach preferred)
2. **Update documentation** (API_REFERENCE.md, ARCHITECTURE.md)
3. **Add to PROJECT_TODO.md** if applicable
4. **Run full test suite** before committing
5. **Update this file** if architecture changes

### Common Tasks

**Add new test**:
```bash
# Find appropriate test file in tests/
# Add test following existing patterns
# Run: pytest tests/test_yourfile.py -v
```

**Add new configuration preset**:
```bash
# Create in configs/config_yourname.yaml
# Document in configs/README.md
# Add to "Configuration Status" section
```

**Add new utility script**:
```bash
# Create in scripts/yourscript.py
# Make executable if shell script
# Document in scripts/README.md (when created)
```

**Profile performance**:
```bash
python -m cProfile -o profile.stats run.py
# Or use test_performance_benchmarks.py
```

---

## 📐 Design Patterns Used

### 1. Singleton Pattern
**Where**: `LiveDashboard`
**Why**: Only one dashboard instance should exist globally

### 2. Wrapper/Decorator Pattern
**Where**: Dashboard integration with `call_ollama()`
**Why**: Add monitoring without modifying core functions

### 3. Strategy Pattern
**Where**: File ordering (recent, alphabetical, size)
**Why**: Flexible file processing strategies

### 4. Cache-Aside Pattern
**Where**: AI response caching
**Why**: Reduce expensive AI calls

### 5. Factory Pattern
**Where**: Model selection in `IntelligentModelSelector`
**Why**: Dynamic model instantiation based on criteria

### 6. Builder Pattern
**Where**: Configuration construction
**Why**: Flexible configuration assembly

---

## 🧪 Testing Philosophy

### Test Categories

**Unit Tests** (240+ tests):
- Fast, isolated, no external dependencies
- Mock Ollama API calls
- Test individual functions/methods

**Integration Tests** (30+ tests):
- Test component interactions
- May use temporary files
- End-to-end workflows

**Benchmark Tests** (50+ tests):
- Performance validation
- Regression detection
- Baseline establishment

### Performance Baselines

These are expected performance targets:

```python
# Cache operations
hash_generation:     < 100ms for 1000 hashes
cache_lookup:        < 10ms for 10000 lookups
cache_write:         < 10ms for 5000 writes

# File operations
file_read:           < 100ms for 100 files
file_write:          < 200ms for 100 files
file_glob:           < 10ms for 100 files

# Processing
json_parsing:        < 50ms for 10000 parses
wikilink_extraction: < 100ms for 1000 documents
complexity_analysis: < 100ms for 1000 documents
model_selection:     < 150ms for 1000 selections

# Dashboard
dashboard_updates:   < 50ms for 1000 updates
dashboard_render:    < 1s for 100 renders
```

If tests fail these baselines, investigate performance regression.

---

## ⚠️ Common Pitfalls

### 1. Ollama Not Running
**Symptom**: `ConnectionRefusedError`
**Solution**: Start Ollama with `ollama serve`

### 2. Memory Issues
**Symptom**: System hangs, killed processes
**Solution**: Use hybrid mode or qwen2.5:3b, batch_size=1

### 3. Test Failures
**Symptom**: Tests fail after changes
**Solution**: Check mocks, verify file paths are absolute

### 4. Cache Not Working
**Symptom**: Same files processed repeatedly
**Solution**: Check `ai_cache.json` exists and is writable

### 5. Import Errors
**Symptom**: `ModuleNotFoundError`
**Solution**: Activate venv, `pip install -r requirements.txt`

---

## 🎯 Project Scope (Important!)

### ✅ In Scope (Local-Only)

- Local Ollama AI models
- Terminal-based UI (Rich library)
- Personal vault management
- Local file processing
- Local analytics and reporting
- Local caching
- Development tooling

### ❌ Out of Scope (Not Local)

- ❌ Remote/web interfaces
- ❌ Cloud services or external APIs
- ❌ Multi-user features
- ❌ Authentication/authorization
- ❌ Database servers
- ❌ Web-based dashboards
- ❌ Public releases/distribution
- ❌ Plugin marketplace

**This is a personal tool for local use only.**

---

## 📚 Key Files to Read

### For Understanding

1. **README.md** - Project introduction
2. **ARCHITECTURE.md** - System design (read this first!)
3. **QUICK_START.md** - Getting started
4. **PROJECT_TODO.md** - Roadmap and status

### For Development

1. **API_REFERENCE.md** - Complete API documentation
2. **TROUBLESHOOTING.md** - Common problems and solutions
3. **configs/README.md** - Configuration guide
4. **tests/conftest.py** - Test fixtures

### For Features

1. **obsidian_auto_linker_enhanced.py** - Core processing
2. **live_dashboard.py** - Dashboard implementation
3. **scripts/intelligent_model_selector.py** - Model selection
4. **enhanced_analytics.py** - Analytics generation

---

## 🔄 Recent Major Changes

**2024-11-15 - Session Work**:
- ✅ Added 165 new tests (126 → 291+ total)
- ✅ Created ARCHITECTURE.md (800+ lines)
- ✅ Created API_REFERENCE.md (1000+ lines)
- ✅ Created TROUBLESHOOTING.md (900+ lines)
- ✅ Completed all code organization tasks
- ✅ Moved utility scripts to scripts/
- ✅ Documented all configs with status
- ✅ Refocused roadmap for local-only use
- ✅ All critical priority tasks complete

---

## 💡 Tips for AI Assistants

### 1. Always Check Context
- Read PROJECT_TODO.md for current status
- Check ARCHITECTURE.md for system design
- Review relevant test files before modifying code

### 2. Follow Established Patterns
- Use existing design patterns (Singleton, Factory, etc.)
- Match existing code style and structure
- Keep local-only focus (no web/cloud features)

### 3. Test Everything
- Write tests for new features
- Run existing tests before committing
- Maintain or improve coverage percentage

### 4. Document Changes
- Update API_REFERENCE.md for new APIs
- Update ARCHITECTURE.md for structural changes
- Update PROJECT_TODO.md to mark completions
- Update this file for major architectural changes

### 5. Respect Constraints
- Local-only (no external services)
- Python 3.9+ compatibility
- Ollama dependency (local AI)
- Terminal UI only (Rich library)
- Personal use (not public distribution)

### 6. Be Cautious With
- File system operations (always test with temp dirs)
- AI API calls (expensive, use mocking in tests)
- Memory usage (test with large datasets)
- Configuration changes (document thoroughly)

---

## 🎓 Learning Resources

### Understanding the Codebase

**Start here**:
1. README.md → ARCHITECTURE.md → API_REFERENCE.md
2. Run `python run.py` in dry-run mode
3. Explore tests in `tests/` directory
4. Read configuration examples in `configs/`

**Deep dive**:
1. Study `obsidian_auto_linker_enhanced.py:process_vault()`
2. Trace a file through the processing pipeline
3. Understand model selection in `intelligent_model_selector.py`
4. Review caching strategy in `get_content_hash()`

### External References

- **Ollama**: https://ollama.ai/docs
- **Rich (Terminal UI)**: https://rich.readthedocs.io/
- **Pytest**: https://docs.pytest.org/
- **Obsidian**: https://obsidian.md/

---

## 📞 Getting Help

### For Understanding

1. **Read Documentation**: Start with ARCHITECTURE.md
2. **Check Tests**: See how features are tested
3. **Run Examples**: Use existing configs and test data
4. **Review Issues**: Check PROJECT_TODO.md

### For Debugging

1. **Check Logs**: `logs/obsidian_linker.log`
2. **Read Troubleshooting**: TROUBLESHOOTING.md has 100+ solutions
3. **Run Tests**: `pytest -v` to isolate issues
4. **Use Debugger**: Python debugger or print statements

---

## 🚀 Quick Command Reference

```bash
# Setup & Environment
./scripts/setup_new_computer.sh      # Initial setup
source venv/bin/activate              # Activate venv
pip install -r requirements.txt       # Install deps
pip install -r requirements-test.txt  # Install test deps

# Running
python run.py                         # Main CLI
python run_with_dashboard.py          # With dashboard
python run_detailed_analytics.py      # With analytics
python run_ultra_detailed.py          # Maximum detail

# Testing
pytest                                # All tests
pytest -v                             # Verbose
pytest -k test_name                   # Specific test
pytest tests/test_cache.py            # Specific file
pytest -m unit                        # Unit tests only
pytest -m integration                 # Integration only
pytest -m benchmark                   # Benchmarks only
./run_tests.sh fast                   # Quick tests
./run_tests.sh coverage               # With coverage

# Coverage
pytest --cov=. --cov-report=html      # Generate report
open htmlcov/index.html               # View report

# Utilities
python scripts/verify_system.py       # System check
python scripts/model_performance_test.py  # Model benchmarks
ollama list                           # List models
ollama serve                          # Start Ollama
```

---

## ✅ Checklist for Changes

Before committing changes:

- [ ] Tests pass: `pytest -v`
- [ ] Coverage maintained/improved
- [ ] Documentation updated (if needed)
- [ ] No new external dependencies (local-only!)
- [ ] Code follows existing patterns
- [ ] Config changes documented
- [ ] TODO list updated (if applicable)
- [ ] No breaking changes (or documented)
- [ ] Local-only constraint maintained

---

**Last Updated**: 2024-11-15
**Status**: All critical tasks complete, project in excellent state
**For**: AI Assistants (Claude, etc.) working on this project

**Remember**: This is a local-only tool. All features should work entirely offline with local Ollama models. No web services, no cloud APIs, no remote dependencies!
