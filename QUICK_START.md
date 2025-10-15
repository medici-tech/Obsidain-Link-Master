# 🚀 Quick Start Guide

**Enhanced Obsidian Auto-Linker** - Get up and running in 5 minutes!

## 📋 Prerequisites
- Python 3.9+
- 8GB+ RAM
- Internet connection (for model downloads)

## 🚀 Super Quick Setup

### 1. Clone and Setup (Automated)
```bash
git clone <repository-url>
cd "Obsidain Link Master"
./setup_new_computer.sh
```

### 2. Configure Your Vault
```bash
nano config.yaml
# Update: vault_path: /path/to/your/obsidian/vault
```

### 3. Run the Application
```bash
./activate.sh
# Choose option 1 to run the auto-linker
```

## 🎯 What Happens Next

1. **Dry Run Mode**: Processes first 10 files safely
2. **Interactive Menu**: Choose to continue, switch to real processing, or stop
3. **Quality Control**: Files below 80% confidence are flagged for review
4. **Analytics**: Comprehensive reports generated automatically

## ⚙️ Key Features

- **🤖 AI-Powered**: Uses local Qwen3:8b model for privacy
- **🎯 Quality Control**: 80% confidence threshold with review queue
- **🛡️ Safe Mode**: Dry run limits and automatic backups
- **📊 Analytics**: Detailed reporting and performance metrics
- **🔄 Resume**: Continue from where you left off

## 🚨 Important Notes

- **Always backup your Obsidian vault before real processing**
- **Start with dry run mode to test configuration**
- **Review confidence scores before switching to real processing**
- **Check the `reviews/` directory for flagged files**

## 📚 Documentation

- `README.md` - Complete documentation
- `DEPLOYMENT.md` - Detailed deployment guide
- `USAGE.md` - Usage examples and tips

## 🆘 Need Help?

1. Run system check: `python3 scripts/verify_system.py`
2. Check Ollama: `ollama serve`
3. Verify models: `ollama list`
4. Review logs in console output

---

**Ready to go? Run `./activate.sh` and choose option 1!**
