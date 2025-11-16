# 📂 Utility Scripts Directory

This directory contains utility scripts and modules used by the Enhanced Obsidian Auto-Linker.

---

## 🔧 Core Utilities

### cache_utils.py (273 lines)

**Purpose**: Bounded cache implementation with LRU eviction to prevent memory issues

**Classes**:

#### `BoundedCache`
Thread-safe bounded cache with size limits and LRU eviction.

**Features**:
- Maximum size limit (MB)
- Maximum entry limit
- LRU (Least Recently Used) eviction
- Thread-safe operations (using `threading.RLock`)
- JSON serialization
- Statistics tracking

**Usage**:
```python
from scripts.cache_utils import BoundedCache

cache = BoundedCache(max_size_mb=500, max_entries=10000)
cache.set('key', {'data': 'value'})
result = cache.get('key')  # Returns cached value or None
```

**Methods**:
- `get(key)` - Get value from cache
- `set(key, value)` - Store value in cache
- `get_size_mb()` - Get current cache size
- `save_to_file(filename)` - Persist cache to JSON
- `load_from_file(filename)` - Load cache from JSON

#### `IncrementalTracker`
Track file hashes to enable incremental processing.

**Features**:
- MD5 hash tracking
- File modification detection
- JSON persistence

**Usage**:
```python
from scripts.cache_utils import IncrementalTracker

tracker = IncrementalTracker()
if not tracker.has_changed(file_path, content):
    print("File unchanged, skipping...")
else:
    # Process file
    tracker.update(file_path, content)
```

---

### incremental_processing.py

**Purpose**: File hash tracking for incremental vault processing

**Classes**:

#### `FileHashTracker`
Track content hashes to skip unchanged files on subsequent runs.

**Features**:
- MD5-based content tracking
- Last processed timestamp
- Change detection
- JSON persistence

**Usage**:
```python
from scripts.incremental_processing import FileHashTracker

tracker = FileHashTracker('.incremental_tracker.json')
if tracker.should_reprocess(file_path):
    # Process file
    tracker.mark_processed(file_path, content_hash)
tracker.save()
```

**Methods**:
- `should_reprocess(file_path)` - Check if file needs processing
- `mark_processed(file_path, hash)` - Mark file as processed
- `get_stats()` - Get processing statistics
- `save()` - Persist tracker to file

---

### intelligent_model_selector.py (9.2KB)

**Purpose**: Select optimal Ollama model based on content complexity

**Features**:
- Content complexity analysis
- Automatic model selection (qwen3:8b vs qwen2.5:3b)
- Keyword-based heuristics
- File size considerations

**Classes**:

#### `IntelligentModelSelector`
Analyzes content and selects appropriate model.

**Complexity Factors**:
- Word count (>1000 = complex)
- Technical keywords (api, code, python, database, etc.)
- Business keywords (revenue, investment, strategy, etc.)
- File size (larger = more complex)

**Usage**:
```python
from scripts.intelligent_model_selector import IntelligentModelSelector

selector = IntelligentModelSelector()
model = selector.select_model(content, file_path)
# Returns: 'qwen3:8b' or 'qwen2.5:3b'
```

**Methods**:
- `analyze_complexity(content)` - Rate content complexity (0-100)
- `select_model(content, file_path)` - Choose optimal model
- `get_model_config(model_name)` - Get model settings

---

### dry_run_analysis.py

**Purpose**: Fast dry-run analysis using keyword-based heuristics (no AI)

**Features**:
- Keyword extraction
- MOC categorization without AI
- Fast preview mode

**Functions**:
- `fast_dry_run_analysis(content, file_path)` - Quick keyword-based analysis
- `extract_keywords(content)` - Extract key terms
- `categorize_by_keywords(keywords)` - Assign MOC category

**Usage**:
```python
from scripts.dry_run_analysis import fast_dry_run_analysis

result = fast_dry_run_analysis(content, "note.md")
# Returns dict with moc_category, primary_topic, etc.
```

---

## 🧪 Testing & Benchmarking

### model_performance_test.py

**Purpose**: Benchmark different Ollama models for speed and quality

**Features**:
- Response time measurement
- Memory usage tracking
- Quality assessment
- Comparative analysis

**Usage**:
```bash
python scripts/model_performance_test.py
```

**Output**: Comparison of qwen3:8b vs qwen2.5:3b vs llama2 etc.

---

### test_confidence_threshold.py

**Purpose**: Test quality control thresholds

**Features**:
- Confidence score analysis
- Threshold tuning
- False positive/negative rates

**Usage**:
```bash
python scripts/test_confidence_threshold.py
```

---

### test_interactive.py

**Purpose**: Interactive testing of AI analysis

**Features**:
- Single file testing
- Immediate feedback
- Debugging aid

**Usage**:
```bash
python scripts/test_interactive.py path/to/note.md
```

---

## 🛠️ Setup & Configuration

### setup_new_computer.sh

**Purpose**: One-command setup for new development machines

**Features**:
- Python environment setup
- Ollama installation verification
- Model download
- Dependency installation
- Configuration initialization

**Usage**:
```bash
chmod +x scripts/setup_new_computer.sh
./scripts/setup_new_computer.sh
```

**Steps Performed**:
1. Check Python 3.9+
2. Create virtual environment
3. Install requirements
4. Check Ollama installation
5. Pull required models
6. Create sample config

---

### verify_system.py

**Purpose**: Verify system requirements and dependencies

**Features**:
- Python version check
- Ollama connection test
- Model availability check
- Dependency verification

**Usage**:
```bash
python scripts/verify_system.py
```

**Output Example**:
```
✓ Python 3.11.5 (OK)
✓ Ollama running (http://localhost:11434)
✓ qwen3:8b installed
✓ All dependencies installed
System ready for processing!
```

---

### optimize_ollama.sh

**Purpose**: Optimize Ollama settings for M4 MacBook Air

**Features**:
- Memory allocation tuning
- GPU settings (if applicable)
- Performance optimization

**Usage**:
```bash
chmod +x scripts/optimize_ollama.sh
./scripts/optimize_ollama.sh
```

---

### optimize_performance.py

**Purpose**: Profile and optimize Python code performance

**Features**:
- cProfile integration
- Bottleneck identification
- Memory profiling
- Performance recommendations

**Usage**:
```bash
python scripts/optimize_performance.py
```

---

## 📊 Usage Statistics

| Script | Lines | Purpose | Frequency |
|--------|-------|---------|-----------|
| `cache_utils.py` | 273 | Core utility | Every run |
| `incremental_processing.py` | ~200 | Core utility | Every run |
| `intelligent_model_selector.py` | ~250 | Core utility | Every run |
| `dry_run_analysis.py` | ~300 | Testing | Dry runs |
| `model_performance_test.py` | ~150 | Benchmarking | Occasional |
| `setup_new_computer.sh` | ~150 | Setup | One-time |
| `verify_system.py` | ~100 | Verification | Setup/troubleshooting |

---

## 🔄 Import Patterns

**Always use explicit imports**:

```python
# ✅ Good - Explicit path
from scripts.cache_utils import BoundedCache, IncrementalTracker
from scripts.intelligent_model_selector import IntelligentModelSelector

# ❌ Bad - Ambiguous
from cache_utils import BoundedCache  # Which cache_utils?
```

**Why?**
- Clear dependency tracking
- No sys.path manipulation needed
- Better IDE support
- Easier debugging

---

## 🚀 Future Additions

Planned utility scripts (see ROADMAP.md):

1. **link_quality.py** - Link quality scoring
2. **graph_analyzer.py** - Knowledge graph analysis
3. **export_utils.py** - Export dashboard metrics to CSV/JSON
4. **parallel_processor.py** - Parallel processing utilities
5. **backup_manager.py** - Enhanced backup management

---

## 📝 Adding New Utilities

When adding new scripts to this directory:

1. **Use consistent naming**: `lowercase_with_underscores.py`
2. **Add docstrings**: Module, class, and function level
3. **Update this README**: Add to appropriate section
4. **Add tests**: Create corresponding test in `tests/`
5. **Import explicitly**: Use `from scripts.module import ...`

**Template**:
```python
#!/usr/bin/env python3
"""
Brief description of utility purpose

Features:
- Feature 1
- Feature 2
"""

class UtilityClass:
    """
    Brief class description

    Usage:
        >>> from scripts.my_utility import UtilityClass
        >>> util = UtilityClass()
        >>> result = util.do_something()
    """

    def __init__(self):
        """Initialize utility"""
        pass

    def do_something(self):
        """Do something useful"""
        pass
```

---

## 🐛 Troubleshooting

### Import Errors

**Problem**: `ModuleNotFoundError: No module named 'scripts'`

**Solution**: Run from project root:
```bash
cd /path/to/Obsidain-Link-Master
python obsidian_auto_linker_enhanced.py  # Not from scripts/
```

### Cache Issues

**Problem**: BoundedCache growing too large

**Solution**: Adjust config.yaml:
```yaml
max_cache_size_mb: 500  # Reduce from 1000
max_cache_entries: 5000  # Reduce from 10000
```

---

## 📚 Related Documentation

- **[ARCHITECTURE.md](../ARCHITECTURE.md)** - System design
- **[API_REFERENCE.md](../API_REFERENCE.md)** - Complete API docs
- **[TROUBLESHOOTING.md](../TROUBLESHOOTING.md)** - Problem solving
- **[tests/README.md](../tests/README.md)** - Testing guide

---

**Last Updated**: 2025-11-15
**Maintainer**: Update when adding new scripts
