# 🚀 Obsidian Auto-Linker - Production Ready

## 🎯 Quick Start

### Option 1: Using Virtual Environment (Recommended)
```bash
# Activate the environment
source activate.sh

# Run the script
python3 obsidian_auto_linker_enhanced.py
```

### Option 2: Direct Execution
```bash
python3 obsidian_auto_linker_enhanced.py
```

## 🔧 Setup & Troubleshooting

### If you get import errors:
1. **Run the setup script:**
   ```bash
   python3 scripts/setup_ide.py
   ```

2. **Configure your IDE:**
   - Press `Cmd+Shift+P` (Mac) or `Ctrl+Shift+P` (Windows/Linux)
   - Type "Python: Select Interpreter"
   - Choose the virtual environment Python: `./venv/bin/python3`

3. **Manual activation:**
   ```bash
   source venv/bin/activate
   pip install -r requirements.txt
   ```

## 📁 Project Structure
```
📄 Root Files:
   obsidian_auto_linker_enhanced.py  # Main script
   dry_run_analysis.py              # Testing script
   config.yaml                      # Main configuration

📁 configs/ - Configuration options
📁 scripts/ - Utility scripts  
📁 reports/ - Generated reports
📁 docs/ - Documentation
📁 backups/ - Backup files
```

## ⚙️ Configuration Options
- **Default**: `config.yaml` (Qwen3:8b, extended timeouts)
- **Fast**: `configs/config_fast.yaml` (faster processing)
- **Ultra Fast**: `configs/config_ultra_fast.yaml` (maximum speed)

## 🧪 Testing
```bash
python3 dry_run_analysis.py
```

## 📊 Reports
All reports are generated in `reports/` folder and open automatically.

## 🎯 Production Ready
- ✅ Clean, organized structure
- ✅ No redundant files
- ✅ Clear usage instructions
- ✅ Extended timeouts built-in
- ✅ Qwen3:8b for maximum accuracy
