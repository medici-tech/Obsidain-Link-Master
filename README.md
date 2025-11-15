# 🚀 Enhanced Obsidian Auto-Linker

An intelligent AI-powered system for automatically categorizing and linking Obsidian vault files using local LLM models with advanced quality control features.

## ✨ Features

### 🤖 AI-Powered Analysis
- **Local LLM Integration**: Uses Ollama with Qwen3:8b for privacy and cost-effectiveness
- **Smart Categorization**: Automatically categorizes files into 12 MOC (Map of Content) categories
- **Intelligent Linking**: Creates sibling links and hierarchical tags
- **Context-Aware**: Analyzes file content and existing vault structure

### 🎯 Quality Control
- **Confidence Threshold**: 80% confidence requirement for automatic processing
- **Review Queue**: Low confidence files flagged for manual review
- **Dry Run Limits**: Process only 10 files initially with interactive prompts
- **Comprehensive Analytics**: Detailed reporting and performance metrics

### 🔧 Advanced Features
- **Resume Processing**: Continue from where you left off
- **Caching System**: Avoid re-processing analyzed files
- **Multiple Configurations**: Pre-built configs for different use cases
- **Backup System**: Automatic backups before modifications
- **Progress Tracking**: Real-time progress monitoring

## 📋 Prerequisites

### System Requirements
- **Python 3.9+**
- **Ollama** (for local LLM processing)
- **8GB+ RAM** (for Qwen3:8b model)
- **macOS/Linux/Windows**

### Required Models
- **Qwen3:8b** (primary model for analysis)
- **Qwen2.5:3b** (optional, for fast dry runs)

## 🚀 Quick Start

### 1. Clone the Repository
```bash
git clone <repository-url>
cd "Obsidain Link Master"
```

### 2. Install Dependencies
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install requirements
pip install -r requirements.txt
```

### 3. Install and Setup Ollama
```bash
# Install Ollama (macOS)
brew install ollama

# Or download from: https://ollama.ai/download

# Start Ollama service
ollama serve

# Pull required models (in another terminal)
ollama pull qwen3:8b
ollama pull qwen2.5:3b
```

### 4. Configure Your Vault
Edit `config.yaml`:
```yaml
# Update vault path
vault_path: /path/to/your/obsidian/vault

# Adjust settings as needed
confidence_threshold: 0.8  # 80% confidence required
dry_run_limit: 10         # Process 10 files in dry run
```

### 5. Run the Application
```bash
# Activate virtual environment
source venv/bin/activate

# Run the enhanced auto-linker
python3 obsidian_auto_linker_enhanced.py
```

## ⚙️ Configuration

### Core Settings
```yaml
# Vault and processing
vault_path: "/path/to/your/vault"
dry_run: true                    # Start in safe mode
dry_run_limit: 10               # Files to process in dry run
confidence_threshold: 0.8       # Quality control threshold

# AI Model settings
ollama_model: "qwen3:8b"        # Primary model
ollama_temperature: 0.1         # Low temperature for consistency
ollama_timeout: 600             # 10 minutes per file
```

### Quality Control
```yaml
# Confidence and review settings
confidence_threshold: 0.8       # Files below 80% flagged for review
enable_review_queue: true       # Enable manual review
review_queue_path: "reviews/"   # Where to store review files
```

### Performance
```yaml
# Processing settings
batch_size: 1                   # Process one file at a time
parallel_workers: 1             # Single-threaded for stability
max_retries: 5                  # Retry failed analyses
```

## 📊 Usage Workflow

### 1. Initial Dry Run
```bash
python3 obsidian_auto_linker_enhanced.py
```
- Processes first 10 files
- Shows confidence scores and categorization
- Displays interactive options

### 2. Review Results
- Check confidence scores (aim for 80%+)
- Review any flagged files in `reviews/` directory
- Examine analytics report

### 3. Switch to Real Processing
- Choose option 1 from interactive menu
- Confirm with "YES"
- Files will be modified with new structure

### 4. Monitor Progress
- Real-time progress updates
- Automatic backups created
- Resume capability if interrupted

## 📁 File Structure

```
Obsidain Link Master/
├── obsidian_auto_linker_enhanced.py    # Main application
├── config.yaml                         # Configuration file
├── requirements.txt                    # Python dependencies
├── configs/                            # Alternative configurations
│   ├── config_fast.yaml               # Fast processing
│   ├── config_detailed_analytics.yaml  # Detailed reporting
│   └── config_ultra_fast.yaml          # Ultra-fast mode
├── scripts/                            # Utility scripts
│   ├── intelligent_model_selector.py   # Model selection
│   ├── optimize_performance.py        # Performance tuning
│   └── verify_system.py              # System verification
├── reports/                            # Analytics reports
│   ├── comprehensive_analytics_report.html
│   └── processing_analytics.json
├── reviews/                            # Manual review files
└── docs/                              # Documentation
```

## 🎛️ Advanced Configuration

### Using Alternative Configs
```bash
# Copy a different config
cp configs/config_fast.yaml config.yaml

# Or use specific configs
python3 run_fast.py                    # Fast processing
python3 run_detailed_analytics.py      # Detailed analytics
python3 run_ultra_detailed.py          # Ultra-detailed mode
```

### Model Selection
```yaml
# For faster processing (less accurate)
ollama_model: "qwen2.5:3b"
ollama_timeout: 120

# For maximum accuracy (slower)
ollama_model: "qwen3:8b"
ollama_timeout: 600
```

### Performance Tuning
```yaml
# Memory optimization
memory_optimization: true
max_memory_usage: 12

# Caching
cache_enabled: true
resume_enabled: true
```

## 📊 Analytics and Reporting

### Generated Reports
- **HTML Analytics Report**: Comprehensive processing statistics
- **JSON Analytics**: Machine-readable processing data
- **Review Files**: Detailed analysis for manual review
- **Progress Tracking**: Resume capability with progress files

### Key Metrics
- **Processing Speed**: Files per minute
- **Confidence Distribution**: AI confidence scores
- **MOC Distribution**: Category breakdown
- **Error Analysis**: Failed processing reasons
- **Review Queue**: Files needing manual attention

## 🔧 Troubleshooting

### Common Issues

#### Ollama Connection Failed
```bash
# Check if Ollama is running
ollama serve

# Verify model is installed
ollama list

# Pull missing models
ollama pull qwen3:8b
```

#### Low Memory Issues
```bash
# Use smaller model
ollama pull qwen2.5:3b

# Update config
ollama_model: "qwen2.5:3b"
ollama_timeout: 120
```

#### Processing Too Slow
```bash
# Use fast configuration
cp configs/config_fast.yaml config.yaml

# Or adjust settings
ollama_model: "qwen2.5:3b"
ollama_timeout: 120
```

### System Verification
```bash
# Run system check
python3 scripts/verify_system.py

# Test model performance
python3 scripts/model_performance_test.py
```

## 🚀 Deployment to New Computer

### 1. System Setup
```bash
# Install Python 3.9+
# Install Ollama
# Clone repository
git clone <repository-url>
cd "Obsidain Link Master"
```

### 2. Environment Setup
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Ollama Setup
```bash
# Start Ollama
ollama serve

# Install models
ollama pull qwen3:8b
ollama pull qwen2.5:3b
```

### 4. Configuration
```bash
# Update vault path
nano config.yaml

# Test configuration
python3 scripts/verify_system.py
```

### 5. First Run
```bash
# Run in dry run mode
python3 obsidian_auto_linker_enhanced.py

# Review results and switch to real processing
```

## 📚 Additional Resources

### Documentation
- `docs/README.md` - Detailed documentation
- `USAGE.md` - Usage examples and tips
- `docs/cleanup_plan.md` - Vault cleanup strategies

### Scripts
- `scripts/optimize_performance.py` - Performance optimization
- `scripts/intelligent_model_selector.py` - Automatic model selection
- `scripts/dry_run_analysis.py` - Dry run analysis tools

### Reports
- `reports/` - Generated analytics and reports
- `reviews/` - Files flagged for manual review

## 🤝 Support

### Getting Help
1. Check the troubleshooting section
2. Review generated analytics reports
3. Examine review queue files for issues
4. Run system verification scripts

### Performance Tips
- Start with dry run to test configuration
- Use appropriate model for your hardware
- Monitor memory usage during processing
- Review confidence scores before real processing

## 📄 License

This project is designed for personal use with Obsidian vaults. Please ensure you have appropriate backups before processing your vault.

---

**⚠️ Important**: Always backup your Obsidian vault before running real processing. The system creates backups automatically, but additional backups are recommended.
