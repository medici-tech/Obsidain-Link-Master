# 🚀 Enhanced Obsidian Auto-Linker

![CI Tests](https://github.com/medici-tech/Obsidain-Link-Master/workflows/Test%20Suite/badge.svg)
![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)
![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)

An intelligent AI-powered system for automatically categorizing and linking Obsidian vault files using local LLM models with advanced quality control features.

> **Why it exists:** Obsidian vaults grow messy quickly. The Auto-Linker scans your notes, proposes consistent MOC categories, and creates safe backlinks so you can focus on writing instead of bookkeeping.

## 📚 Documentation Quick Links

| Document | Description |
|----------|-------------|
| **[README.md](README.md)** (this file) | Quick start and overview |
| **[QUICK_START.md](QUICK_START.md)** | 5-minute setup guide |
| **[README_ENHANCED.md](README_ENHANCED.md)** | Comprehensive guide (450+ lines) |
| **[CLAUDE.md](CLAUDE.md)** | Developer/AI assistant guide |
| **[ARCHITECTURE.md](ARCHITECTURE.md)** | System architecture |
| **[ROADMAP.md](ROADMAP.md)** | Development roadmap |
| **[TROUBLESHOOTING.md](TROUBLESHOOTING.md)** | Problem solving |
| **[COMPREHENSIVE_REVIEW.md](COMPREHENSIVE_REVIEW.md)** | Project review |
| **[CHANGELOG.md](CHANGELOG.md)** | Release notes |
| **[configs/](configs/)** | Configuration examples |
| **[tests/](tests/)** | Test suite (~324 collected tests) |

## ✨ Features

### 🤖 AI-Powered Analysis
- **Local LLM Integration**: Uses Ollama with Qwen models for privacy and cost-effectiveness
- **Smart Categorization**: Automatically categorizes files into MOC (Map of Content) structures
- **Intelligent Linking**: Creates sibling links and hierarchical tags based on content + vault context

### 🎯 Quality Control & Safety
- **Confidence Threshold**: Default 80% confidence requirement for automatic processing
- **Review Queue**: Low confidence files flagged for manual review
- **Backups & Dry Run**: Automatic backups and dry-run options keep vault changes safe

### ⚡ Performance & Resilience
- **Hash-Based Caching**: Response/hash caching is in place; bounded eviction is still pending
- **Parallel Processing**: ThreadPool scaffolding exists via CLI/config, but work currently runs sequentially
- **Resume & Progress Tracking**: Basic progress files and dashboard metrics; needs hardening for interruptions

## 🧭 Current Status Snapshot

- **Core pipeline** runs locally with Qwen models (`qwen3:8b` or `qwen2.5:3b`) to perform MOC categorization, wikilink creation, and tag-style linking.
- **Runtime foundations are live**: dashboard telemetry, local Ollama access, hybrid model selection, hashing-based caching, basic resume scaffolding, and analytics reporting.
- **Gaps to close**: parallel processing is scaffolded but effectively sequential; cache needs bounded eviction; link-quality scoring is unimplemented; resume tracking is basic; incremental processing and dashboard metric export are still planned.

## 📋 Prerequisites

- **Python 3.9+**
- **Ollama** running locally (`localhost:11434`)
- **Models**: `qwen3:8b` (accuracy) and optionally `qwen2.5:3b` (faster dry runs)
- **Hardware**: 8GB+ RAM recommended for `qwen3:8b`

## 🚀 Quick Start

### 1) Clone and install
```bash
git clone <repository-url>
cd Obsidain-Link-Master

python3 -m venv venv
source venv/bin/activate  # On Windows: venv\\Scripts\\activate

# Install base requirements (use -e .[dev] for editable install with dev tooling)
pip install -r requirements.txt
# Optional: pip install -e .[dev]
```

### 2) Install and start Ollama
```bash
brew install ollama          # macOS
# or download from https://ollama.ai/download
ollama serve
ollama pull qwen3:8b
ollama pull qwen2.5:3b
```

### 3) Configure your vault
Edit `config.yaml`:
```yaml
vault_path: /path/to/your/obsidian/vault
confidence_threshold: 0.8
parallel_workers: 1           # Increase to enable parallel processing
ollama_timeout_seconds: 600   # Adjust for larger models
```

### 4) Run the application
```bash
# Preferred packaged CLI
obsidian-link-master --config config.yaml --dashboard
obsidian-link-master --config config.yaml --non-interactive  # headless run

# Module entrypoint
python -m obsidian_link_master --config config.yaml --dashboard

# Legacy wrappers (delegate to the same runtime)
python run.py --config config.yaml
python run_with_dashboard.py --config config.yaml
```

## ⚙️ Configuration Notes

- **Caching & Incremental Runs**: Enabled by default; caches hashes and responses to skip unchanged files.
- **Parallelism**: Set `parallel_workers` in `config.yaml` or pass `--parallel-workers` to the CLI.
- **Backups**: Automatic backups occur before modifications; keep `backup_path` pointing to safe storage.
- **HTML analytics**: Disabled by default; set `generate_report: true` in `config.yaml` if you need standalone reports.

## 📁 File Structure

```
Obsidain-Link-Master/
├── obsidian_link_master/            # Packaged CLI (__main__.py, cli.py, configuration helpers)
├── obsidian_auto_linker_enhanced.py # Main processor
├── run.py / run_with_dashboard.py   # Legacy entrypoints
├── live_dashboard.py                # Live terminal dashboard
├── config_utils.py / config_schema.py / configuration.py
├── logger_config.py / memory_monitor.py / check_memory.py
├── enhanced_analytics.py / ultra_detailed_analytics.py
├── configs/                         # Sample presets + deprecated/
├── scripts/                         # Utilities (cache_utils, incremental_processing, model/model perf helpers)
├── tests/                           # 20 pytest modules (~324 collected tests)
├── docs/                            # Cleanup/vault documentation
├── archive/                         # Experimental runners/docs (reference only)
├── reports/ / reviews/              # Generated analytics and review queue outputs
└── README.md, CLAUDE.md, ROADMAP.md, ...
```

## 🧪 Testing

```bash
# Install test-only dependencies (property-based + snapshot tests)
pip install -r requirements-test.txt

# Run everything (requires hypothesis + freezegun)
pytest

# Quick smoke (skips slow markers)
pytest -m "not slow"

# With coverage
pytest --cov=. --cov-report=term-missing --cov-report=html
```

> Tip: `pytest --collect-only` will error if `hypothesis` or `freezegun` are missing; install from `requirements-test.txt` for a complete run.

## 🔧 Troubleshooting

- **Ollama connection issues**: Ensure `ollama serve` is running and models are pulled (`ollama list`).
- **Slow runs**: Lower `parallel_workers`, switch to `qwen2.5:3b`, or use `configs/config_ultra_fast.yaml`.
- **Memory pressure**: Keep `parallel_workers` conservative and use the bounded cache (enabled by default).

## 📚 Additional Resources

- `scripts/README.md` for utility scripts
- `configs/README.md` for configuration presets (including `configs/deprecated/` guidance)
- `TESTING_GUIDE.md` for marker conventions and tips
- `TROUBLESHOOTING.md` for deeper diagnostics
