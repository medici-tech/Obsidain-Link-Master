# 🔧 Troubleshooting Guide

**Enhanced Obsidian Auto-Linker** - Common Issues and Solutions

---

## 📋 Table of Contents

1. [Installation Issues](#installation-issues)
2. [Ollama Connection Problems](#ollama-connection-problems)
3. [Timeout Errors](#timeout-errors)
4. [Memory Issues](#memory-issues)
5. [File Processing Errors](#file-processing-errors)
6. [Configuration Issues](#configuration-issues)
7. [Performance Problems](#performance-problems)
8. [Dashboard Issues](#dashboard-issues)
9. [Cache Problems](#cache-problems)
10. [Testing Issues](#testing-issues)

---

## Installation Issues

### Problem: `ModuleNotFoundError: No module named 'yaml'`

**Symptoms:**
```bash
ModuleNotFoundError: No module named 'yaml'
```

**Solutions:**
```bash
# Activate virtual environment first
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Verify installation
python -c "import yaml; print('OK')"
```

**Root Cause**: Dependencies not installed or virtual environment not activated

---

### Problem: Virtual Environment Not Found

**Symptoms:**
```bash
❌ Virtual environment not found!
Please run ./scripts/setup_new_computer.sh first
```

**Solutions:**
```bash
# Run automated setup
./scripts/setup_new_computer.sh

# Or manual setup
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

---

### Problem: Permission Denied on Scripts

**Symptoms:**
```bash
-bash: ./activate.sh: Permission denied
```

**Solutions:**
```bash
# Make scripts executable
chmod +x activate.sh
chmod +x run_tests.sh
chmod +x scripts/*.sh

# Then run
./activate.sh
```

---

## Ollama Connection Problems

### Problem: Ollama Service Not Running

**Symptoms:**
```bash
❌ Ollama connection failed
ConnectionRefusedError: [Errno 61] Connection refused
```

**Solutions:**

**Check if Ollama is running:**
```bash
# Check process
pgrep -f "ollama serve"

# Test connection
curl http://localhost:11434/api/tags
```

**Start Ollama:**
```bash
# macOS/Linux
ollama serve

# Or in background
nohup ollama serve > ollama.log 2>&1 &

# Verify it's running
ollama list
```

**Check port:**
```bash
# Verify Ollama is on port 11434
lsof -i :11434
netstat -an | grep 11434
```

---

### Problem: Model Not Found

**Symptoms:**
```bash
Error: model 'qwen3:8b' not found
```

**Solutions:**
```bash
# List available models
ollama list

# Pull required models
ollama pull qwen3:8b       # ~4.7GB download
ollama pull qwen2.5:3b     # ~1.9GB download

# Verify models
ollama list | grep qwen
```

---

### Problem: Ollama API Timeout

**Symptoms:**
```bash
requests.exceptions.Timeout: HTTPConnectionPool...
Read timed out.
```

**Solutions:**

**Option 1: Use extended timeout config**
```bash
cp configs/config_extended_timeout.yaml config.yaml
```

**Option 2: Increase timeout in config.yaml**
```yaml
ollama_timeout: 600  # 10 minutes (default: 120)
ollama_max_retries: 5  # More retries (default: 3)
```

**Option 3: Use faster model**
```yaml
ollama_model: qwen2.5:3b  # Faster than qwen3:8b
```

---

## Timeout Errors

### Problem: Frequent Timeout Errors

**Symptoms:**
```bash
⚠️ Timeout occurred, retrying... (attempt 1/3)
⚠️ Timeout occurred, retrying... (attempt 2/3)
⚠️ Timeout occurred, retrying... (attempt 3/3)
```

**Diagnostic Steps:**
```bash
# Check system resources
top
htop

# Check Ollama logs
tail -f ollama.log

# Check available memory
free -h   # Linux
vm_stat   # macOS
```

**Solutions:**

**1. Use Extended Timeout Config:**
```bash
python run_extended_timeout.py
# Or
cp configs/config_extended_timeout.yaml config.yaml
```

**2. Reduce Content Size:**
```yaml
# In config.yaml
ollama_max_tokens: 512  # Reduce from 1024
```

**3. Switch to Hybrid Mode:**
```bash
cp configs/config_hybrid_models.yaml config.yaml
# Automatically uses faster model for simple content
```

**4. Close Other Applications:**
- Close memory-intensive apps
- Stop other Ollama instances
- Free up RAM before processing

**5. Process in Smaller Batches:**
```yaml
batch_size: 1  # Process one at a time
parallel_workers: 1  # No parallel processing
```

---

## Memory Issues

### Problem: Out of Memory / System Hang

**Symptoms:**
```bash
# System becomes unresponsive
# Ollama crashes
killed
```

**Diagnostic:**
```bash
# Check memory usage
# macOS
vm_stat | grep "Pages active"
top -l 1 | grep PhysMem

# Linux
free -h
ps aux --sort=-%mem | head
```

**Solutions:**

**1. Use Smaller Model:**
```yaml
# config.yaml
ollama_model: qwen2.5:3b  # Uses ~2GB vs 5GB for qwen3:8b
```

**2. Reduce Batch Size:**
```yaml
batch_size: 1  # Process one file at a time
```

**3. Disable Parallel Processing:**
```yaml
parallel_workers: 1  # No parallelization
```

**4. Use Hybrid Mode (Recommended for 16GB RAM):**
```bash
cp configs/config_hybrid_models.yaml config.yaml
# Automatically switches between models based on complexity
```

**5. Clear Ollama Cache:**
```bash
# Stop Ollama
pkill ollama

# Clear cache (macOS)
rm -rf ~/.ollama/models/cache

# Restart Ollama
ollama serve
```

**Memory Usage Guide:**
```
Configuration             | RAM Required | Best For
--------------------------|--------------|------------------
qwen2.5:3b + batch:1     | ~7GB         | 8GB systems
qwen3:8b + batch:1       | ~10GB        | 16GB systems
Hybrid mode + batch:1    | ~7-10GB      | 16GB systems (recommended)
qwen3:8b + batch:10      | ~15GB+       | 32GB+ systems
```

---

## File Processing Errors

### Problem: Files Not Being Processed

**Symptoms:**
```bash
Found 0 markdown files to process
```

**Diagnostic:**
```bash
# Check vault path
ls -la /path/to/your/vault

# Verify config
grep vault_path config.yaml
```

**Solutions:**

**1. Fix Vault Path:**
```yaml
# config.yaml - use absolute path
vault_path: /Users/username/Documents/ObsidianVault
```

**2. Check File Filters:**
```python
# Temporarily disable filters for testing
# In obsidian_auto_linker_enhanced.py
# Comment out filter logic
```

**3. Verify File Permissions:**
```bash
# Check read permissions
ls -la /path/to/vault/*.md

# Fix permissions if needed
chmod +r /path/to/vault/**/*.md
```

---

### Problem: Backup Creation Failed

**Symptoms:**
```bash
Error: Permission denied when creating backup
```

**Solutions:**
```bash
# Check write permissions
ls -ld backups/

# Create backup directory
mkdir -p backups
chmod 755 backups

# Or disable backups for testing
# In config.yaml:
dry_run: true  # Won't create backups
```

---

### Problem: Invalid JSON Response from AI

**Symptoms:**
```bash
JSONDecodeError: Expecting value: line 1 column 1 (char 0)
MOC category set to default: Life & Misc
```

**Root Cause**: AI didn't return valid JSON

**Solutions:**

**1. Use More Reliable Model:**
```yaml
ollama_model: qwen3:8b  # More reliable than qwen2.5:3b
```

**2. Adjust Temperature:**
```yaml
ollama_temperature: 0.05  # Lower = more consistent (default: 0.1)
```

**3. Check Ollama Model:**
```bash
# Re-pull model if corrupted
ollama rm qwen3:8b
ollama pull qwen3:8b
```

**4. Inspect Logs:**
```bash
tail -f logs/obsidian_linker.log
# Look for malformed responses
```

---

## Configuration Issues

### Problem: Config File Not Found

**Symptoms:**
```bash
FileNotFoundError: [Errno 2] No such file or directory: 'config.yaml'
```

**Solutions:**
```bash
# Create from template
cp config.yaml.example config.yaml

# Or copy a preset
cp configs/config_fast.yaml config.yaml

# Edit with your vault path
nano config.yaml
```

---

### Problem: YAML Syntax Error

**Symptoms:**
```bash
yaml.scanner.ScannerError: while scanning...
```

**Solutions:**
```bash
# Validate YAML syntax
python -c "import yaml; yaml.safe_load(open('config.yaml'))"

# Common issues:
# - Inconsistent indentation (use spaces, not tabs)
# - Missing colons
# - Unquoted special characters
```

**Example Fixes:**
```yaml
# ❌ Wrong (tabs, no space after colon)
vault_path:/path/to/vault

# ✅ Correct
vault_path: /path/to/vault

# ❌ Wrong (inconsistent indentation)
  dry_run: true
    fast_dry_run: false

# ✅ Correct (consistent 2-space indentation)
  dry_run: true
  fast_dry_run: false
```

---

### Problem: Changes Not Taking Effect

**Symptoms:**
- Modified config.yaml but behavior unchanged

**Solutions:**

**1. Restart Application:**
```bash
# Config is loaded at startup
# Must restart to see changes
python run.py
```

**2. Check Config Priority:**
```bash
# Command line args override config file
# Remove CLI args if testing config changes
python run.py  # Uses config.yaml
# NOT: python run.py --model qwen2.5:3b  # Overrides config
```

**3. Verify Correct Config File:**
```bash
# If using --config flag, edit that file
python run.py --config configs/config_fast.yaml
# Must edit configs/config_fast.yaml, not config.yaml
```

---

## Performance Problems

### Problem: Very Slow Processing

**Symptoms:**
- Taking >2 minutes per file
- Low CPU usage
- High network wait time

**Diagnostic:**
```bash
# Monitor Ollama
top | grep ollama

# Check network latency
ping localhost

# Profile Python
python -m cProfile run.py > profile.txt
```

**Solutions:**

**1. Use Fast Config:**
```bash
cp configs/config_fast.yaml config.yaml
# Or
python run_detailed_analytics.py  # Uses fast settings
```

**2. Enable Cache (should be enabled by default):**
```python
# Verify cache is working
# Check logs for "Cache hit" messages
tail -f logs/obsidian_linker.log | grep "Cache"
```

**3. Use Hybrid Model Selection:**
```bash
# Automatically uses faster model when possible
cp configs/config_hybrid_models.yaml config.yaml
```

**4. Optimize Ollama:**
```bash
./scripts/optimize_ollama.sh
# Configures Ollama for best performance
```

**5. Reduce Token Limit:**
```yaml
ollama_max_tokens: 256  # Lower = faster (default: 1024)
```

---

### Problem: High CPU Usage

**Symptoms:**
- CPU at 100%
- System lag
- Fan noise

**Solutions:**

**1. Reduce Parallel Workers:**
```yaml
parallel_workers: 1  # Single-threaded
```

**2. Add Delays Between Requests:**
```python
# In obsidian_auto_linker_enhanced.py
import time
time.sleep(0.5)  # 500ms delay between files
```

**3. Close Other Applications:**
- Close browsers, IDEs
- Stop background processes
- Monitor with Activity Monitor (macOS) or System Monitor (Linux)

---

## Dashboard Issues

### Problem: Dashboard Not Showing

**Symptoms:**
- Running `run_with_dashboard.py` but no dashboard appears

**Solutions:**

**1. Check Rich Library:**
```bash
pip install rich --upgrade
python -c "from rich.console import Console; print('OK')"
```

**2. Check Terminal Compatibility:**
```bash
# Rich requires terminal with color support
echo $TERM  # Should show something like 'xterm-256color'

# Test colors
python -c "from rich.console import Console; Console().print('[bold red]Test[/]')"
```

**3. Disable Dashboard if Issues Persist:**
```bash
# Use regular runner instead
python run.py
```

---

### Problem: Dashboard Rendering Errors

**Symptoms:**
```bash
# Garbled output
# Unicode errors
# Layout issues
```

**Solutions:**

**1. Update Rich:**
```bash
pip install rich --upgrade
```

**2. Set Terminal Encoding:**
```bash
export LANG=en_US.UTF-8
export LC_ALL=en_US.UTF-8
```

**3. Use Different Terminal:**
- iTerm2 (macOS)
- Windows Terminal (Windows)
- GNOME Terminal (Linux)

---

## Cache Problems

### Problem: Cache Not Working

**Symptoms:**
- Same files processed multiple times
- No "Cache hit" messages in logs

**Diagnostic:**
```bash
# Check if cache file exists
ls -la ai_cache.json

# Check cache size
wc -l ai_cache.json

# Inspect cache
cat ai_cache.json | python -m json.tool | head
```

**Solutions:**

**1. Verify Cache Enabled:**
```python
# Should be enabled by default
# Check obsidian_auto_linker_enhanced.py
# Look for ai_cache dictionary
```

**2. Clear Corrupted Cache:**
```bash
# Backup first
cp ai_cache.json ai_cache.json.bak

# Clear cache
echo "{}" > ai_cache.json

# Or delete entirely
rm ai_cache.json
```

**3. Check File Permissions:**
```bash
# Must be writable
chmod 644 ai_cache.json
```

---

### Problem: Cache Hit Rate Too Low

**Symptoms:**
- Expected 50%+ cache hits
- Getting <10% hits

**Diagnostic:**
```bash
# Check analytics
cat analytics.json | python -m json.tool | grep cache

# Monitor processing
tail -f logs/obsidian_linker.log | grep -i cache
```

**Root Causes:**
- Files being modified between runs
- Content hash changing
- Cache file deleted

**Solutions:**
- Use `dry_run: true` for testing (doesn't modify files)
- Don't modify files between runs
- Keep `ai_cache.json` file

---

## Testing Issues

### Problem: Tests Failing

**Symptoms:**
```bash
FAILED tests/test_ollama_integration.py::test_call_ollama_success
```

**Solutions:**

**1. Run Tests with Verbose Output:**
```bash
pytest -v
pytest tests/test_ollama_integration.py -v
```

**2. Check Test Dependencies:**
```bash
pip install -r requirements-test.txt
```

**3. Run Specific Test:**
```bash
pytest tests/test_ollama_integration.py::test_call_ollama_success -v
```

**4. Skip Slow Tests:**
```bash
pytest -m "not integration"  # Skip integration tests
pytest -m "unit"             # Only unit tests
```

---

### Problem: Coverage Report Not Generated

**Symptoms:**
- Tests pass but no HTML coverage report

**Solutions:**
```bash
# Install coverage tool
pip install pytest-cov

# Run with coverage
pytest --cov=. --cov-report=html

# Open report
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
```

---

## Common Error Messages & Solutions

### `ImportError: cannot import name 'X'`
```bash
# Solution: Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### `FileNotFoundError: config.yaml`
```bash
# Solution: Create config file
cp configs/config_fast.yaml config.yaml
nano config.yaml  # Edit vault path
```

### `ConnectionRefusedError: [Errno 61]`
```bash
# Solution: Start Ollama
ollama serve
```

### `yaml.scanner.ScannerError`
```bash
# Solution: Fix YAML syntax
python -c "import yaml; yaml.safe_load(open('config.yaml'))"
# Fix indentation, add missing colons
```

### `JSONDecodeError: Expecting value`
```bash
# Solution: Use more reliable model
# In config.yaml:
ollama_model: qwen3:8b
ollama_temperature: 0.05
```

### `MemoryError` or System Hang
```bash
# Solution: Reduce memory usage
# In config.yaml:
ollama_model: qwen2.5:3b  # Smaller model
batch_size: 1
parallel_workers: 1
```

---

## Getting Help

### 1. Check Logs
```bash
# Application logs
tail -f logs/obsidian_linker.log

# Ollama logs
tail -f ollama.log

# Test logs
pytest --log-cli-level=DEBUG
```

### 2. Enable Debug Mode
```python
# In your script
import logging
logging.basicConfig(level=logging.DEBUG)
```

### 3. Run Diagnostics
```bash
# System verification
python scripts/verify_system.py

# Test Ollama
curl http://localhost:11434/api/tags

# Test Python environment
python -c "import yaml, requests, rich; print('All imports OK')"
```

### 4. Collect System Information
```bash
# For bug reports
python --version
pip list | grep -E "(yaml|requests|rich|pytest)"
ollama --version
uname -a  # System info
```

### 5. Report Issues
```
GitHub Issues: https://github.com/medici-tech/Obsidain-Link-Master/issues

Include:
- Error message (full traceback)
- config.yaml (sanitized)
- System info
- Steps to reproduce
- Logs (last 50 lines)
```

---

## Quick Reference: Common Commands

```bash
# Setup
./scripts/setup_new_computer.sh
source venv/bin/activate

# Run
python run.py                    # Interactive mode
python run_with_dashboard.py     # With live dashboard
python run_detailed_analytics.py # With analytics

# Test
pytest                          # All tests
./run_tests.sh fast            # Quick tests
./run_tests.sh coverage        # With coverage

# Debug
tail -f logs/obsidian_linker.log  # Watch logs
ollama list                        # Check models
ollama serve                       # Start Ollama

# Optimize
./scripts/optimize_ollama.sh       # Optimize Ollama
cp configs/config_hybrid_models.yaml config.yaml  # Best config

# Clean
rm ai_cache.json              # Clear cache
rm -rf backups/*              # Clear backups
```

---

## Performance Tuning Checklist

- [ ] Use hybrid model configuration
- [ ] Enable caching (default)
- [ ] Set appropriate timeout values
- [ ] Reduce batch size if memory constrained
- [ ] Use dry_run for testing
- [ ] Monitor system resources
- [ ] Close unnecessary applications
- [ ] Optimize Ollama settings
- [ ] Use SSD for vault storage
- [ ] Keep software updated

---

**Last Updated**: 2024-11-15
**For More Help**: See [ARCHITECTURE.md](ARCHITECTURE.md), [README.md](README.md), or open an issue on GitHub
