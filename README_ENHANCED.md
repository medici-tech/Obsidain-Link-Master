# Obsidian Auto-Linker - Enhanced Edition

![Version](https://img.shields.io/badge/version-2.0-blue)
![Python](https://img.shields.io/badge/python-3.9+-green)
![Platform](https://img.shields.io/badge/platform-macOS%20%7C%20Linux-lightgrey)

An intelligent tool that automatically processes your Obsidian vault files and creates a Map of Content (MOC) structure with AI-powered linking, featuring a **stunning live terminal dashboard** optimized for modern hardware.

## 🎯 What's New in Enhanced Edition

### ✨ Ultra-Detailed Live Monitoring Dashboard
- **Real-time terminal dashboard** with 30-second updates
- **M4-optimized monitoring** - Performance core vs Efficiency core tracking
- **Comprehensive metrics** - AI performance, cache stats, file analysis
- **Resource tracking** - CPU, memory, disk I/O, network I/O
- **Activity logging** - See exactly what's happening in real-time
- **Error tracking** - Immediate visibility into issues

### 🚀 Performance Improvements
- **Proper logging system** - Structured logging with file rotation
- **Configuration validation** - Safe config loading with error handling
- **Optimized code structure** - Modular design for maintainability
- **Enhanced error handling** - Better exception handling throughout

### 📊 Dashboard Features

The live dashboard shows:

```
╔══════════════════════════════════════════════════════════════════════╗
║              OBSIDIAN AUTO-LINKER - LIVE DASHBOARD                   ║
║                   Running on MacBook Air M4 2025                     ║
╚══════════════════════════════════════════════════════════════════════╝

┌─ PROCESSING STATUS ─────────────────────────────────────────────────┐
│ Files: 127/500 (25.4%)  [████████░░░░░░░░░░░░░░░░░░░░░░]           │
│ Current: client-acquisition-strategies.md                            │
│ Stage: AI Analysis (12.3s elapsed)                                  │
│ Speed: 3.2 files/min (↑ from 2.8)  ETA: 1h 56min (±8min)           │
└──────────────────────────────────────────────────────────────────────┘

┌─ SYSTEM RESOURCES (MacBook Air M4) ────────────────────────────────┐
│ CPU: [████████████░░░░░░░░] 62%  (P-cores: 85%  E-cores: 42%)      │
│ Memory: 4.2 GB / 16 GB (26%)  [████░░░░░░░░░░░░░░░░░]              │
│ Disk I/O: ↓ 12 MB/s  ↑ 3 MB/s                                      │
│ Network: ↓ 145 KB/s  ↑ 12 KB/s                                      │
└──────────────────────────────────────────────────────────────────────┘

┌─ AI PERFORMANCE (Ollama) ──────────────────────────────────────────┐
│ Requests: 127 total  ✓ 124 success  ✗ 3 failed  (97.6%)            │
│ Response Time: 8.2s avg  [6.1s min  14.5s max  8.9s p95]           │
│ Tokens/sec: 42.3  Generation: 346 tokens avg                        │
└──────────────────────────────────────────────────────────────────────┘

┌─ CACHE PERFORMANCE ────────────────────────────────────────────────┐
│ Hit Rate: 34.6%  [████████░░░░░░░░░░░░░░]                          │
│ Time Saved: 6min 24s (from cache hits)                              │
└──────────────────────────────────────────────────────────────────────┘
```

## 🎯 Features

### Core Features
- ✅ **Interactive Configuration** - Easy setup with guided prompts
- ✅ **Safe Processing** - Creates new `_linked.md` files instead of overwriting
- ✅ **Live Dashboard** - Ultra-detailed real-time monitoring
- ✅ **Progress Tracking** - Real-time progress with accurate ETA
- ✅ **Resource Monitoring** - M4-optimized CPU, memory, I/O tracking
- ✅ **Activity Tracking** - See exactly what's happening
- ✅ **Graceful Shutdown** - Press Ctrl+C to stop safely with summary
- ✅ **Local AI** - Uses Ollama for privacy and cost-free processing
- ✅ **Smart Caching** - Avoids re-processing identical content
- ✅ **Multiple Ordering** - Process by recent, size, random, or alphabetical

### Advanced Features
- ✅ **Structured Logging** - Comprehensive logging with file rotation
- ✅ **Config Validation** - Safe configuration with error checking
- ✅ **AI Performance Metrics** - Response time, token rate, success rate
- ✅ **Cache Analytics** - Hit rate, time saved, lookup performance
- ✅ **File Analysis** - Processing time by size, MOC distribution
- ✅ **Error Tracking** - Real-time error visibility with categorization
- ✅ **M4 Optimization** - Performance + Efficiency core monitoring

## 📋 Requirements

### System Requirements
- **OS**: macOS 10.15+ or Linux
- **Python**: 3.9 or higher
- **RAM**: 8GB minimum (16GB recommended for large vaults)
- **Disk**: 1GB free space minimum

### Software Requirements
- **Ollama**: Local AI model server
- **Python packages**: Listed in `requirements.txt`

> **Why Python 3.9+?** The real-time dashboard and monitoring stack depends on current releases of `rich`, `psutil`, and `requests`. These packages — as pinned in `requirements.txt` — only publish wheels for Python 3.9 and newer, so earlier interpreters no longer receive security or compatibility fixes.

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

This installs:
- `requests` - HTTP client for Ollama API
- `pyyaml` - Configuration file parsing
- `tqdm` - Progress bars
- `psutil` - System resource monitoring
- `rich` - Beautiful terminal UI (NEW!)

### 2. Start Ollama

If not already running:
```bash
ollama serve
```

Pull a model if needed:
```bash
ollama pull qwen2.5:3b
```

### 3. Choose Your Runner

#### Option A: Enhanced Dashboard (Recommended)
```bash
python3 run_with_dashboard.py
```

**Features:**
- Live terminal dashboard
- Real-time metrics
- M4-optimized monitoring
- Activity logging
- 30-second updates

#### Option B: Original Runner
```bash
python3 run.py
```

**Features:**
- Interactive setup
- Basic resource monitoring
- Simple progress display

### 4. Follow the Prompts

The tool will guide you through:

1. **Vault Path** - Location of your Obsidian vault
   - Default: `/Users/medici/Documents/MediciVault`
   - Or enter custom path

2. **File Processing Order**
   - Recent (newest first) - Recommended
   - Size (largest first)
   - Random
   - Alphabetical

3. **Processing Mode**
   - **Fast Dry Run** - Quick test, no AI, no file changes
   - **Full Dry Run** - Complete test with AI, no file changes
   - **Live Run** - Creates `_linked.md` files

4. **Batch Size**
   - Single file (recommended for accuracy)
   - Small batch (5 files)
   - Medium batch (10 files)

## 📖 Usage Examples

### First Time Setup
```bash
python3 run_with_dashboard.py
```

Follow prompts:
```
📁 Vault Path: /Users/medici/Documents/MediciVault
📋 File Processing Order: 1 (Recent)
🔧 Processing Mode: 1 (Fast Dry Run)
📦 Batch Size: 1 (Single file)
Continue? y
```

### Testing Before Going Live
```bash
# Fast dry run - no AI, very quick
python3 run_with_dashboard.py
# Choose: Fast Dry Run

# Full dry run - with AI, no file changes
python3 run_with_dashboard.py
# Choose: Full Dry Run
```

### Production Run
```bash
python3 run_with_dashboard.py
# Choose: Live Run
```

**Warning**: Live run creates `_linked.md` files in your vault!

## 🎮 Dashboard Controls

While the dashboard is running:

- **Ctrl+C** - Stop processing gracefully
  - Shows final statistics
  - Saves progress
  - Clean shutdown

Updates automatically every **30 seconds** with:
- Processing progress
- System resources (M4-optimized)
- AI performance metrics
- Cache statistics
- File analysis
- Recent activity
- Errors and warnings

## 📊 Understanding the Metrics

### Processing Status
- **Files**: Current/Total (percentage)
- **Current**: File being processed
- **Stage**: Current operation (Reading, AI Analysis, Linking, Saving)
- **Speed**: Files per minute
- **ETA**: Estimated time to completion

### System Resources (M4-Optimized)
- **CPU**: Overall usage + P-core/E-core breakdown
- **Memory**: Used/Total with percentage
- **Disk I/O**: Read/Write speeds in MB/s
- **Network**: Download/Upload speeds for Ollama API
- **Temperature**: System temperature (if available)

### AI Performance
- **Requests**: Total, successful, failed with success rate
- **Response Time**: Average, min, max, median, p95
- **Tokens/sec**: Token generation rate
- **Timeouts**: Number of timeout occurrences
- **Retries**: Retry attempts and success rate

### Cache Performance
- **Hit Rate**: Percentage of cache hits
- **Hits/Misses**: Breakdown of cache lookups
- **Cache Size**: Memory usage and entry count
- **Time Saved**: Estimated time saved from cache hits

### File Analysis
- **Processing Time by Size**:
  - Small (<5KB): Average time and count
  - Medium (5-50KB): Average time and count
  - Large (>50KB): Average time and count
- **MOC Distribution**: Top 5 categories with percentages

## 🔧 Configuration

Configuration is stored in `config.yaml`:

```yaml
# Basic settings
vault_path: /path/to/your/vault
file_ordering: recent
batch_size: 1

# Processing modes
dry_run: true
fast_dry_run: true

# Ollama settings
ollama_base_url: http://localhost:11434
ollama_model: qwen2.5:3b
```

### Available Options

| Option | Values | Description |
|--------|--------|-------------|
| `vault_path` | Path | Location of Obsidian vault |
| `file_ordering` | recent, size, random, alphabetical | File processing order |
| `batch_size` | 1, 5, 10 | Files per batch |
| `dry_run` | true, false | Don't create files |
| `fast_dry_run` | true, false | Skip AI analysis |
| `ollama_model` | Model name | Ollama model to use |

## 📁 Project Structure

```
Obsidian-Link-Master/
├── run.py                              # Original interactive runner
├── run_with_dashboard.py               # Enhanced runner with live dashboard
├── obsidian_auto_linker_enhanced.py    # Core processing engine
├── live_dashboard.py                   # Live dashboard module
├── logger_config.py                    # Logging configuration
├── quick_report.py                     # Terminal report generator
├── generate_detailed_report.py         # HTML report generator
├── config.yaml                         # Configuration file
├── requirements.txt                    # Python dependencies
├── .gitignore                          # Git ignore rules
└── README_ENHANCED.md                  # This file
```

## 🐛 Troubleshooting

### Dashboard Not Updating

**Issue**: Dashboard seems frozen
**Solution**: Dashboard updates every 30 seconds. Wait for next update cycle.

### Ollama Connection Failed

**Issue**: "Ollama is not running"
**Solution**:
```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# Start Ollama if not running
ollama serve

# Check models are available
ollama list
```

### Slow Processing

**Issue**: Processing takes 2-3 minutes per file
**Solution**: This is normal for local AI models. Options:
1. Use Fast Dry Run mode for testing
2. Use smaller model (qwen2.5:3b instead of 7b)
3. Increase batch size (but may reduce accuracy)
4. Enable caching (automatically enabled)

### High Memory Usage

**Issue**: System running out of memory
**Solution**:
1. Reduce batch size to 1
2. Use Fast Dry Run mode
3. Close other applications
4. Process smaller vault sections

### Configuration Errors

**Issue**: "Missing required config fields"
**Solution**: Delete `config.yaml` and run setup again:
```bash
rm config.yaml
python3 run_with_dashboard.py
```

## 📈 Performance Tips

### For Large Vaults (1000+ files)
- Use **batch size 1** for better progress tracking
- Enable **caching** (default)
- Use **recent ordering** to process new files first
- Run **Full Dry Run** first to populate cache

### For Fast Testing
- Use **Fast Dry Run** mode
- Small vault subset
- Alphabetical ordering for consistency

### For Production
- Use **Full Dry Run** first to verify
- Then run **Live Run**
- Monitor dashboard for errors
- Check logs in `obsidian_linker.log`

## 🔒 Privacy & Security

- ✅ **100% Local Processing** - All AI runs on your machine
- ✅ **No Data Sent to Cloud** - Ollama runs locally
- ✅ **Safe File Handling** - Creates new files, doesn't overwrite
- ✅ **Config Protection** - `config.yaml` in `.gitignore`
- ✅ **Structured Logging** - Sensitive data not logged

## 📝 Logs & Reports

### Log Files
- **`obsidian_linker.log`** - Detailed application logs
  - Auto-rotating (10MB per file, 5 backups)
  - DEBUG level details
  - Error tracking
  - Performance metrics

### Reports
- **`processing_analytics.json`** - Processing statistics
- **`detailed_report.html`** - Beautiful HTML report
- **Dashboard** - Real-time metrics display

## 🤝 Contributing

Contributions welcome! Areas for improvement:
- Additional MOC categories
- Performance optimizations
- Better error handling
- More dashboard metrics
- Testing framework

## 📜 License

[Add your license here]

## 🙏 Acknowledgments

- **Ollama** - Local AI inference
- **Rich** - Beautiful terminal UI
- **Obsidian** - Knowledge management platform

## 📞 Support

- **Issues**: Report bugs and feature requests
- **Logs**: Check `obsidian_linker.log` for debugging
- **Dashboard**: Use live dashboard for real-time monitoring

---

**Made with ❤️ for the Obsidian community**

*Optimized for MacBook Air M4 2025 🚀*
