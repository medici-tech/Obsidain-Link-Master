# 🏗️ Architecture Documentation

**Enhanced Obsidian Auto-Linker** - System Architecture and Design

---

## 📋 Table of Contents

1. [System Overview](#system-overview)
2. [Architecture Diagram](#architecture-diagram)
3. [Core Components](#core-components)
4. [Data Flow](#data-flow)
5. [Processing Pipeline](#processing-pipeline)
6. [Module Interactions](#module-interactions)
7. [File Structure](#file-structure)
8. [Technology Stack](#technology-stack)
9. [Design Patterns](#design-patterns)
10. [Performance Considerations](#performance-considerations)

---

## System Overview

### Purpose
The Enhanced Obsidian Auto-Linker is an intelligent system that:
- Analyzes markdown notes in an Obsidian vault
- Uses local AI models (Ollama) to categorize content
- Automatically creates wikilinks between related notes
- Generates Maps of Content (MOC) for organization
- Provides comprehensive analytics and reporting

### Key Features
- **AI-Powered Categorization**: Uses Qwen3:8b or Qwen2.5:3b models locally
- **Intelligent Link Creation**: Analyzes content semantically for relevant links
- **Hybrid Model Selection**: Automatically chooses best model based on complexity
- **Caching System**: Reduces redundant AI calls with content-based hashing
- **Live Dashboard**: Real-time monitoring with Rich library
- **Comprehensive Analytics**: Detailed performance and processing metrics
- **Safe Processing**: Automatic backups, dry-run mode, rollback support

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER INTERFACE                           │
│  ┌──────────────┐  ┌──────────────┐  ┌────────────────────┐   │
│  │   CLI Menu   │  │  Dashboard   │  │  Interactive Mode  │   │
│  │  (run.py)    │  │  (Live UI)   │  │   (Prompts)        │   │
│  └──────────────┘  └──────────────┘  └────────────────────┘   │
└───────────────────────────┬─────────────────────────────────────┘
                            │
┌───────────────────────────▼─────────────────────────────────────┐
│                    LAUNCHER SCRIPTS                              │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ run.py, run_with_dashboard.py, run_detailed_analytics.py│  │
│  │ run_extended_timeout.py, run_ultra_detailed.py          │  │
│  └──────────────────────────────────────────────────────────┘  │
└───────────────────────────┬─────────────────────────────────────┘
                            │
┌───────────────────────────▼─────────────────────────────────────┐
│                    CORE PROCESSING ENGINE                        │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │         obsidian_auto_linker_enhanced.py                 │  │
│  │  • Configuration Management                               │  │
│  │  • File Discovery & Filtering                            │  │
│  │  • Content Processing Pipeline                           │  │
│  │  • Backup & Safety Systems                               │  │
│  │  • Link Creation & MOC Management                        │  │
│  └──────────────────────────────────────────────────────────┘  │
└──────┬─────────────┬───────────────┬───────────────┬───────────┘
       │             │               │               │
   ┌───▼───┐   ┌────▼────┐    ┌─────▼──────┐   ┌───▼────────┐
   │  AI   │   │ Cache   │    │ Analytics  │   │ Dashboard  │
   │Module │   │ System  │    │  Engine    │   │  Monitor   │
   └───┬───┘   └────┬────┘    └─────┬──────┘   └───┬────────┘
       │            │               │               │
┌──────▼────────────▼───────────────▼───────────────▼──────────┐
│                   SUPPORT MODULES                             │
│  ┌──────────────┐  ┌──────────────┐  ┌────────────────────┐ │
│  │ AI Interface │  │  Cache Mgmt  │  │   Live Dashboard   │ │
│  │ call_ollama()│  │ get_content  │  │   (Rich library)   │ │
│  │              │  │  _hash()     │  │                    │ │
│  ├──────────────┤  ├──────────────┤  ├────────────────────┤ │
│  │  Analytics   │  │   Logger     │  │   Intelligent      │ │
│  │   enhanced   │  │   Config     │  │  Model Selector    │ │
│  │  _analytics  │  │logger_config │  │                    │ │
│  └──────────────┘  └──────────────┘  └────────────────────┘ │
└───────────────────────────┬─────────────────────────────────┘
                            │
┌───────────────────────────▼──────────────────────────────────┐
│                   EXTERNAL SERVICES                           │
│  ┌──────────────┐  ┌──────────────┐  ┌────────────────────┐ │
│  │    Ollama    │  │ File System  │  │  Obsidian Vault    │ │
│  │   (Local AI) │  │  (Backups)   │  │  (Markdown Files)  │ │
│  │qwen3:8b      │  │              │  │                    │ │
│  │qwen2.5:3b    │  │              │  │                    │ │
│  └──────────────┘  └──────────────┘  └────────────────────┘ │
└───────────────────────────────────────────────────────────────┘
```

---

## Core Components

### 1. Processing Engine (`obsidian_auto_linker_enhanced.py`)
**Responsibility**: Main orchestration of file processing
- **Class**: `ObsidianAutoLinker`
- **Key Methods**:
  - `process_vault()` - Main entry point for vault processing
  - `analyze_with_balanced_ai()` - Content analysis with AI
  - `create_wikilinks()` - Link generation logic
  - `get_content_hash()` - Cache key generation
  - `create_backup()` - Safety system

**Location**: `/obsidian_auto_linker_enhanced.py` (48,603 lines)

### 2. Dashboard System (`live_dashboard.py`)
**Responsibility**: Real-time monitoring and visualization
- **Class**: `LiveDashboard` (Singleton pattern)
- **Features**:
  - File processing progress
  - AI request tracking (success/failure/timeout)
  - Cache performance metrics (hit/miss ratio)
  - System resource monitoring (CPU/Memory)
  - Activity logging

**Location**: `/live_dashboard.py` (20,337 lines)

### 3. Analytics Engine (`enhanced_analytics.py`)
**Responsibility**: Performance metrics and reporting
- **Functions**:
  - `load_analytics_data()` - Load processing history
  - `generate_comprehensive_report()` - HTML report generation
  - `calculate_metrics()` - Statistical analysis
  - `moc_distribution()` - Category distribution

**Location**: `/enhanced_analytics.py` (16,756 lines)

### 4. Ultra Detailed Analytics (`ultra_detailed_analytics.py`)
**Responsibility**: Advanced analytics and insights
- **Features**:
  - Time-series performance tracking
  - Comparative analysis across runs
  - Trend identification
  - Performance optimization recommendations

**Location**: `/ultra_detailed_analytics.py` (19,031 lines)

### 5. Intelligent Model Selector (`scripts/intelligent_model_selector.py`)
**Responsibility**: AI model selection based on complexity
- **Class**: `IntelligentModelSelector`
- **Selection Logic**:
  - Word count analysis
  - Complexity keyword detection
  - Technical content indicators
  - Business/finance content detection
- **Models**:
  - **qwen3:8b**: Complex content, technical analysis
  - **qwen2.5:3b**: Simple content, fast processing

**Location**: `/scripts/intelligent_model_selector.py` (9,210 lines)

### 6. Logger Configuration (`logger_config.py`)
**Responsibility**: Centralized logging setup
- **Features**:
  - Rotating file handlers
  - Console output formatting
  - Log level management
  - Performance logging

**Location**: `/logger_config.py` (3,673 lines)

---

## Data Flow

### 1. Configuration Loading
```
config.yaml → load_config() → Configuration Dict → ProcessingEngine
```

### 2. File Discovery
```
Vault Path → scan_vault_files() → Filter Logic → Ordered File List
```

### 3. Content Processing
```
Markdown File
    ↓
Read Content
    ↓
Calculate MD5 Hash
    ↓
Check Cache → [HIT] → Return Cached Result
    ↓ [MISS]
Extract Existing Notes
    ↓
Call AI Model (Ollama)
    ↓
Parse JSON Response
    ↓
Cache Result
    ↓
Create Wikilinks
    ↓
Update File
    ↓
Create Backup
```

### 4. AI Request Flow
```
Content → Model Selector → [Complexity Analysis]
                               ↓
                    ┌──────────┴──────────┐
                    ↓                     ↓
            Complex Content        Simple Content
                    ↓                     ↓
             qwen3:8b (8B)          qwen2.5:3b (3B)
                    ↓                     ↓
            Temperature: 0.1       Temperature: 0.1
            Timeout: 300s          Timeout: 60s
            Tokens: 2048           Tokens: 1024
                    ↓                     ↓
                    └──────────┬──────────┘
                               ↓
                         JSON Response
                               ↓
                      Parse & Validate
                               ↓
                        Cache & Return
```

### 5. Analytics Flow
```
Processing Metrics → analytics.json → Load Data → Generate Report → HTML
                                          ↓
                                   Calculate Stats
                                          ↓
                                   MOC Distribution
                                          ↓
                                   Performance Trends
```

---

## Processing Pipeline

### Phase 1: Initialization
1. Load configuration from `config.yaml`
2. Initialize logging system
3. Set up dashboard (if enabled)
4. Validate Ollama service
5. Load AI cache from disk

### Phase 2: Discovery
1. Scan vault directory for `.md` files
2. Apply file filters:
   - Exclude templates
   - Exclude archives
   - Exclude system files
3. Order files by strategy:
   - `recent`: Most recently modified first
   - `alphabetical`: A-Z ordering
   - `size`: Largest files first

### Phase 3: Processing Loop
For each file:
1. **Read**: Load markdown content
2. **Hash**: Calculate MD5 for cache lookup
3. **Cache Check**: Look up in `ai_cache`
4. **AI Analysis** (if cache miss):
   - Select model (hybrid mode)
   - Call Ollama API
   - Retry on timeout (exponential backoff)
   - Parse JSON response
5. **Link Creation**:
   - Extract existing notes
   - Match MOC category
   - Generate wikilinks
   - Add to content
6. **File Update**:
   - Create backup
   - Write updated content
   - Update analytics
7. **Dashboard Update**: Refresh UI

### Phase 4: Finalization
1. Save analytics to `analytics.json`
2. Save cache to `ai_cache.json`
3. Generate HTML report (if enabled)
4. Display summary statistics
5. Create review queue (if needed)

---

## Module Interactions

### Primary Dependencies

```
obsidian_auto_linker_enhanced.py
    ├── logger_config.py (logging)
    ├── live_dashboard.py (monitoring)
    ├── enhanced_analytics.py (metrics)
    └── requests (Ollama API)

run_with_dashboard.py
    ├── obsidian_auto_linker_enhanced.py
    ├── live_dashboard.py
    └── yaml (config parsing)

scripts/intelligent_model_selector.py
    ├── requests (Ollama API)
    ├── json (response parsing)
    └── re (regex for JSON extraction)

enhanced_analytics.py
    ├── json (data storage)
    ├── datetime (timestamps)
    └── html (report generation)
```

### Data Storage

```
File System Structure:
.
├── config.yaml                    # Active configuration
├── analytics.json                 # Processing metrics
├── ai_cache.json                  # AI response cache
├── backups/                       # File backups
│   └── YYYY-MM-DD_HH-MM-SS/      # Timestamped backup sets
├── docs/                          # Generated reports
│   ├── processing_report.html    # Latest report
│   └── vault_review_report.md    # Review queue
└── logs/                          # Application logs
    └── obsidian_linker.log       # Rotating log file
```

---

## File Structure

### Root Directory (Launchers Only)
```
/
├── run.py                          # Main CLI launcher
├── run_with_dashboard.py           # Dashboard launcher
├── run_detailed_analytics.py       # Analytics launcher
├── run_extended_timeout.py         # Timeout launcher
├── run_ultra_detailed.py           # Ultra detailed launcher
├── activate.sh                     # Environment activation
├── run_tests.sh                    # Test runner
└── config.yaml                     # Main configuration
```

### Core Modules
```
/
├── obsidian_auto_linker_enhanced.py  # Main processing engine
├── enhanced_analytics.py              # Analytics engine
├── ultra_detailed_analytics.py        # Advanced analytics
├── live_dashboard.py                  # Dashboard UI
└── logger_config.py                   # Logging configuration
```

### Scripts Directory (Utilities)
```
/scripts/
├── intelligent_model_selector.py   # Model selection logic
├── model_performance_test.py       # Performance testing
├── dry_run_analysis.py             # Dry run utilities
├── optimize_performance.py         # Config optimization
├── verify_system.py                # System verification
├── setup_new_computer.sh           # Setup automation
├── optimize_ollama.sh              # Ollama optimization
├── test_confidence_threshold.py    # Threshold testing
├── test_interactive.py             # Interactive testing
└── setup_ide.py                    # IDE setup
```

### Configuration Directory
```
/configs/
├── README.md                        # Config documentation
├── config_fast.yaml                 # Fast preset
├── config_ultra_fast.yaml           # Ultra fast preset
├── config_detailed_analytics.yaml   # Analytics preset
├── config_qwen3_maximum_detail.yaml # Maximum quality preset
├── config_extended_timeout.yaml     # Extended timeout preset
├── config_hybrid_models.yaml        # Hybrid mode preset
└── config_default_extended.yaml     # [DEPRECATED]
```

### Test Directory
```
/tests/
├── conftest.py                      # Pytest fixtures
├── test_ollama_integration.py       # AI integration tests (15)
├── test_cache.py                    # Cache tests (15)
├── test_content_processing.py       # Content tests (12)
├── test_file_operations.py          # File ops tests (18)
├── test_integration.py              # Integration tests (12)
├── test_analytics.py                # Analytics tests (22)
├── test_dashboard.py                # Dashboard tests (30+)
└── test_model_selector.py           # Model selector tests (40+)
```

### Documentation
```
/docs/
├── processing_report.html           # Latest analytics report
├── vault_review_report.md           # Manual review queue
├── cleanup_analysis.md              # Cleanup tracking
└── cleanup_plan.md                  # [DEPRECATED - see PROJECT_TODO.md]
```

---

## Technology Stack

### Core Technologies
- **Language**: Python 3.9+
- **AI Framework**: Ollama (local LLM runtime)
- **Models**: Qwen3:8b (8B), Qwen2.5:3b (3B)
- **UI Framework**: Rich (terminal UI)
- **Testing**: pytest, pytest-cov, pytest-mock
- **CI/CD**: GitHub Actions

### Key Libraries

#### Processing
- `pyyaml` - Configuration file parsing
- `requests` - HTTP client for Ollama API
- `json` - Data serialization
- `hashlib` - MD5 hashing for cache
- `re` - Regular expressions for parsing

#### UI & Visualization
- `rich` - Terminal dashboard and formatting
- `datetime` - Timestamps and time tracking
- `psutil` - System resource monitoring (optional)

#### Testing
- `pytest>=7.4.0` - Test framework
- `pytest-cov>=4.1.0` - Coverage reporting
- `pytest-mock>=3.11.1` - Mocking support
- `hypothesis>=6.88.0` - Property-based testing
- `faker>=19.6.0` - Test data generation

#### Logging
- `logging` (stdlib) - Application logging
- `logging.handlers.RotatingFileHandler` - Log rotation

---

## Design Patterns

### 1. Singleton Pattern
**Used in**: `LiveDashboard`
```python
class LiveDashboard:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
```
**Purpose**: Ensure only one dashboard instance exists globally

### 2. Wrapper/Decorator Pattern
**Used in**: Dashboard integration
```python
def wrapped_call_ollama(prompt, system_prompt="", max_retries=None):
    start_time = time.time()
    try:
        result = original_call_ollama(prompt, system_prompt, max_retries)
        elapsed = time.time() - start_time
        dashboard.add_ai_request(elapsed, success=True)
        return result
    except Exception as e:
        dashboard.add_ai_request(time.time() - start_time, success=False)
        raise
```
**Purpose**: Add monitoring without modifying original functions

### 3. Strategy Pattern
**Used in**: File ordering
```python
if file_ordering == 'recent':
    files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
elif file_ordering == 'alphabetical':
    files.sort()
elif file_ordering == 'size':
    files.sort(key=lambda x: os.path.getsize(x), reverse=True)
```
**Purpose**: Flexible file processing strategies

### 4. Cache-Aside Pattern
**Used in**: AI response caching
```python
content_hash = get_content_hash(content)
if content_hash in ai_cache:
    return ai_cache[content_hash]  # Cache hit
else:
    result = call_ollama(prompt)   # Cache miss
    ai_cache[content_hash] = result
    return result
```
**Purpose**: Reduce redundant expensive AI calls

### 5. Factory Pattern
**Used in**: Model selection
```python
def select_model(content, file_path):
    analysis = analyze_content_complexity(content, file_path)
    if analysis['complexity_score'] >= 5:
        return create_qwen3_config()
    else:
        return create_qwen2_5_config()
```
**Purpose**: Dynamic model instantiation based on criteria

### 6. Builder Pattern
**Used in**: Configuration construction
```python
config = ConfigBuilder()
    .set_model('qwen3:8b')
    .set_timeout(300)
    .set_temperature(0.1)
    .build()
```
**Purpose**: Flexible configuration creation

---

## Performance Considerations

### 1. Caching Strategy
- **Content Hashing**: MD5 hash of file content
- **Cache Persistence**: Saved to `ai_cache.json`
- **Hit Rate**: Typically 30-50% on repeated runs
- **Memory Impact**: ~10MB per 1000 cached entries

### 2. Model Selection
```
┌─────────────────────┬──────────┬──────────┬──────────────┐
│ Model               │ RAM      │ Speed    │ Accuracy     │
├─────────────────────┼──────────┼──────────┼──────────────┤
│ qwen2.5:3b          │ ~2GB     │ Fast     │ Good         │
│ qwen3:8b            │ ~5GB     │ Moderate │ Excellent    │
│ Hybrid (auto)       │ 2-5GB    │ Balanced │ Optimized    │
└─────────────────────┴──────────┴──────────┴──────────────┘
```

### 3. Memory Management
- **Batch Size**: Controls memory footprint
  - `batch_size: 1` = ~7GB RAM (safe for 16GB systems)
  - `batch_size: 10` = ~12GB+ RAM (requires 32GB+ systems)
- **Parallel Workers**: CPU vs Memory tradeoff
  - `parallel_workers: 1` = Sequential, low memory
  - `parallel_workers: 4` = Parallel, high memory

### 4. Network Optimization
- **Retry Logic**: Exponential backoff (1s, 2s, 4s, 8s, 16s)
- **Timeouts**: Configurable per model
  - qwen3:8b: 300s default
  - qwen2.5:3b: 60s default
- **Connection Pooling**: Reuse HTTP connections

### 5. File I/O Optimization
- **Backup Strategy**: Only backup when `dry_run: false`
- **Incremental Processing**: Resume from last processed file
- **Lazy Loading**: Load files one at a time

### 6. Dashboard Performance
- **Update Frequency**: 100ms refresh rate
- **Async Rendering**: Non-blocking UI updates
- **Resource Monitoring**: Optional CPU/Memory tracking

---

## Configuration Architecture

### Configuration Hierarchy
```
1. Command Line Args     (Highest Priority)
2. --config file.yaml
3. config.yaml (root)
4. Built-in defaults     (Lowest Priority)
```

### Configuration Categories

#### 1. **Core Settings**
```yaml
vault_path: /path/to/vault
dry_run: true
fast_dry_run: false
```

#### 2. **AI Model Settings**
```yaml
ollama_base_url: http://localhost:11434
ollama_model: qwen3:8b
ollama_temperature: 0.1
ollama_timeout: 300
ollama_max_retries: 3
ollama_max_tokens: 1024
```

#### 3. **Processing Settings**
```yaml
batch_size: 1
parallel_workers: 1
file_ordering: recent  # recent|alphabetical|size
```

#### 4. **Analytics Settings**
```yaml
analytics_enabled: true
generate_report: true
auto_open_report: true
```

#### 5. **Hybrid Mode Settings**
```yaml
use_hybrid_models: true
primary_ollama_model: qwen3:8b
secondary_ollama_model: qwen2.5:3b
model_switching_threshold: 1000
```

---

## Error Handling & Safety

### 1. Backup System
- **Automatic Backups**: Created before file modifications
- **Timestamped**: `backups/YYYY-MM-DD_HH-MM-SS/`
- **Full Copies**: Entire file snapshots
- **Rollback Support**: Manual restoration available

### 2. Dry Run Mode
- **Safe Testing**: Analyze without modifying files
- **Validation**: Test AI responses without writing
- **Configuration**: `dry_run: true` in config

### 3. Error Recovery
- **Retry Logic**: Exponential backoff for timeouts
- **Graceful Degradation**: Fallback from qwen3 to qwen2.5
- **Error Logging**: Detailed logs in `logs/obsidian_linker.log`

### 4. Validation
- **JSON Parsing**: Validates AI responses
- **File Existence**: Checks before processing
- **Configuration**: Validates YAML syntax
- **Ollama Connection**: Tests before processing

---

## Testing Architecture

### Test Categories

#### 1. **Unit Tests** (126+ tests)
- `test_ollama_integration.py` - AI API tests
- `test_cache.py` - Caching logic
- `test_content_processing.py` - Content parsing
- `test_analytics.py` - Analytics calculations
- `test_dashboard.py` - Dashboard logic
- `test_model_selector.py` - Model selection

#### 2. **Integration Tests**
- `test_integration.py` - End-to-end workflows
- `test_file_operations.py` - File I/O operations

#### 3. **CI/CD Pipeline**
```yaml
Jobs:
  - test (Python 3.9, 3.10, 3.11, 3.12)
  - test-fast (unit tests only)
  - test-slow (integration tests)
  - security-scan (Bandit)
```

#### 4. **Coverage Requirements**
- Minimum: 50%
- Target: 70%
- Current: ~50%

---

## Deployment Architecture

### Local Development
```bash
./scripts/setup_new_computer.sh  # Initial setup
source activate.sh               # Activate environment
python run.py                    # Run application
```

### Production Deployment
```bash
./scripts/setup_new_computer.sh
cp configs/config_qwen3_maximum_detail.yaml config.yaml
# Edit config.yaml with vault path
python run_with_dashboard.py
```

### Testing Deployment
```bash
source venv/bin/activate
pytest                           # Run all tests
./run_tests.sh fast             # Quick unit tests
./run_tests.sh coverage         # With coverage
```

---

## Future Architecture Considerations

### Planned Enhancements

#### 1. **Modular Plugin System**
- Plugin interface for custom processors
- Dynamic loading of extensions
- Community contributions

#### 2. **Web Dashboard**
- REST API backend
- React/Vue frontend
- Remote monitoring

#### 3. **Distributed Processing**
- Multi-machine processing
- Load balancing
- Distributed caching

#### 4. **Database Backend**
- SQLite for analytics
- PostgreSQL for scale
- Graph database for relationships

#### 5. **Advanced Caching**
- Redis integration
- Distributed cache
- Cache warming strategies

---

## Version History

| Version | Date | Key Changes |
|---------|------|-------------|
| 1.0.0 | Initial | Core processing engine |
| 1.1.0 | +Tests | 86+ test suite added |
| 1.2.0 | +Dashboard | Live monitoring |
| 1.3.0 | +Analytics | Enhanced metrics |
| 1.4.0 | +Hybrid | Intelligent model selection |
| 1.5.0 | +Organization | Code cleanup & architecture docs |

---

## References

### Internal Documentation
- [README.md](README.md) - Project overview
- [QUICK_START.md](QUICK_START.md) - Quick setup guide
- [USAGE.md](USAGE.md) - Usage instructions
- [DEPLOYMENT.md](DEPLOYMENT.md) - Deployment guide
- [configs/README.md](configs/README.md) - Configuration guide
- [PROJECT_TODO.md](PROJECT_TODO.md) - Task tracking

### External Resources
- [Ollama Documentation](https://ollama.ai/docs)
- [Rich Library](https://rich.readthedocs.io/)
- [Pytest Documentation](https://docs.pytest.org/)
- [Obsidian](https://obsidian.md/)

---

**Last Updated**: 2024-11-15
**Maintainer**: See [PROJECT_TODO.md](PROJECT_TODO.md)
**License**: See project root
