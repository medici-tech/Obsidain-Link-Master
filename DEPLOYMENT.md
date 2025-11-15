# 🚀 Deployment Guide

Quick guide for porting the Enhanced Obsidian Auto-Linker to a new computer.

## 📋 Prerequisites Checklist

- [ ] **Python 3.9+** installed
- [ ] **Git** installed
- [ ] **8GB+ RAM** available
- [ ] **Internet connection** for model downloads
- [ ] **Obsidian vault** path ready

## 🚀 Quick Deployment (Automated)

### 1. Clone and Setup
```bash
# Clone the repository
git clone <repository-url>
cd "Obsidain Link Master"

# Run automated setup
./scripts/setup_new_computer.sh
```

### 2. Configure Your Vault
```bash
# Edit configuration
nano config.yaml

# Update vault path
vault_path: /path/to/your/obsidian/vault
```

### 3. First Run
```bash
# Activate environment
source venv/bin/activate

# Run in dry run mode
python3 obsidian_auto_linker_enhanced.py
```

## 🔧 Manual Deployment

### 1. System Requirements
```bash
# Install Python 3.9+
# macOS
brew install python@3.9

# Ubuntu/Debian
sudo apt update
sudo apt install python3.9 python3.9-venv

# Windows
# Download from python.org
```

### 2. Install Ollama
```bash
# macOS
brew install ollama

# Linux
curl -fsSL https://ollama.ai/install.sh | sh

# Windows
# Download from https://ollama.ai/download
```

### 3. Setup Environment
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 4. Install AI Models
```bash
# Start Ollama
ollama serve

# Install models (in another terminal)
ollama pull qwen3:8b
ollama pull qwen2.5:3b
```

### 5. Configure Application
```bash
# Copy and edit configuration
cp config.yaml config_local.yaml
nano config_local.yaml

# Update vault path
vault_path: /path/to/your/obsidian/vault
```

## 🧪 Testing Your Setup

### 1. System Verification
```bash
# Run system check
python3 scripts/verify_system.py

# Expected output:
# ✅ Python version: 3.9+
# ✅ Virtual environment: Active
# ✅ Dependencies: Installed
# ✅ Ollama service: Running
# ✅ Models: Available
```

### 2. Test Run
```bash
# Run in dry run mode
python3 obsidian_auto_linker_enhanced.py

# Should process 10 files and show interactive menu
```

### 3. Performance Test
```bash
# Test model performance
python3 scripts/model_performance_test.py

# Check processing speed and accuracy
```

## ⚙️ Configuration Options

### Basic Configuration
```yaml
# Essential settings
vault_path: "/path/to/your/vault"
dry_run: true
confidence_threshold: 0.8
dry_run_limit: 10
```

### Performance Tuning
```yaml
# For faster processing
ollama_model: "qwen2.5:3b"
ollama_timeout: 120
batch_size: 1

# For maximum accuracy
ollama_model: "qwen3:8b"
ollama_timeout: 600
```

### Memory Optimization
```yaml
# For limited RAM
memory_optimization: true
max_memory_usage: 8
ollama_model: "qwen2.5:3b"
```

## 🚨 Troubleshooting

### Common Issues

#### Ollama Not Starting
```bash
# Check if Ollama is installed
which ollama

# Start Ollama manually
ollama serve

# Check if service is running
ps aux | grep ollama
```

#### Model Download Fails
```bash
# Check internet connection
ping ollama.ai

# Try manual model pull
ollama pull qwen3:8b

# Check available models
ollama list
```

#### Python Dependencies Fail
```bash
# Update pip
pip install --upgrade pip

# Install requirements manually
pip install pyyaml requests tqdm psutil

# Check Python version
python3 --version
```

#### Memory Issues
```bash
# Use smaller model
ollama pull qwen2.5:3b

# Update config to use smaller model
ollama_model: "qwen2.5:3b"
```

### System Verification
```bash
# Full system check
python3 scripts/verify_system.py

# Test Ollama connection
python3 -c "import requests; print(requests.get('http://localhost:11434/api/tags').json())"

# Test model availability
ollama list
```

## 📊 Performance Optimization

### Hardware Requirements
- **Minimum**: 8GB RAM, 4 CPU cores
- **Recommended**: 16GB RAM, 8 CPU cores
- **Optimal**: 32GB RAM, 16 CPU cores

### Model Selection
- **qwen2.5:3b**: Fast, less accurate, 2GB RAM
- **qwen3:8b**: Balanced, good accuracy, 8GB RAM
- **qwen3:14b**: Maximum accuracy, 16GB RAM

### Configuration Tuning
```yaml
# Fast processing
ollama_model: "qwen2.5:3b"
ollama_timeout: 120
batch_size: 1

# Balanced processing
ollama_model: "qwen3:8b"
ollama_timeout: 300
batch_size: 1

# Maximum accuracy
ollama_model: "qwen3:14b"
ollama_timeout: 600
batch_size: 1
```

## 🔄 Backup and Recovery

### Before First Run
```bash
# Backup your Obsidian vault
cp -r /path/to/vault /path/to/vault_backup

# Or use Obsidian's built-in backup
```

### Resume Processing
```bash
# The system automatically saves progress
# Resume from where you left off
python3 obsidian_auto_linker_enhanced.py
```

### Recovery from Issues
```bash
# Check progress files
ls -la .processing_progress.json
ls -la .ai_cache.json

# Clear cache if needed
rm .ai_cache.json
rm .processing_progress.json
```

## 📚 Additional Resources

### Documentation
- `README.md` - Complete documentation
- `USAGE.md` - Usage examples
- `docs/` - Detailed guides

### Scripts
- `scripts/verify_system.py` - System verification
- `scripts/optimize_performance.py` - Performance tuning
- `scripts/model_performance_test.py` - Model testing

### Reports
- `reports/` - Analytics and reports
- `reviews/` - Manual review files

## 🆘 Getting Help

### Self-Help
1. Check system verification: `python3 scripts/verify_system.py`
2. Review error logs in console output
3. Check Ollama service: `ollama serve`
4. Verify model installation: `ollama list`

### Common Solutions
- **Restart Ollama**: `pkill ollama && ollama serve`
- **Reinstall models**: `ollama pull qwen3:8b`
- **Clear cache**: `rm .ai_cache.json`
- **Check permissions**: Ensure write access to vault directory

---

**⚠️ Important**: Always backup your Obsidian vault before running real processing!
