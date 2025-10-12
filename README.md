# Obsidian Auto-Linker

An AI-powered tool that automatically processes conversations in your Obsidian vault and creates a MOC-based wiki structure with intelligent linking and tagging.

## 🚀 Features

- **AI-Powered Analysis**: Uses local Ollama models for content analysis
- **Smart Linking**: Automatically identifies and creates links between related notes
- **MOC Structure**: Creates Map of Content (MOC) files for better organization
- **Progress Tracking**: Real-time progress display with detailed statistics
- **File Ordering**: Process files by recent, size, random, or alphabetical order
- **Safe Processing**: Creates new files instead of modifying originals
- **Resume Capability**: Skip already processed files
- **Backup System**: Automatic backups before processing

## 📋 Requirements

- Python 3.7+
- Ollama installed and running
- Obsidian vault with markdown files

## 🛠️ Installation

1. **Clone the repository:**
   ```bash
   git clone <your-repo-url>
   cd obsidian-auto-linker
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Install and setup Ollama:**
   ```bash
   # Install Ollama (if not already installed)
   curl -fsSL https://ollama.ai/install.sh | sh
   
   # Pull a model (recommended: qwen3:8b or llama3.2:3b)
   ollama pull qwen3:8b
   ```

4. **Configure the tool:**
   ```bash
   # Edit config.yaml with your vault path and preferences
   nano config.yaml
   ```

## ⚙️ Configuration

Edit `config.yaml` to configure the tool:

```yaml
# Vault configuration
vault_path: /path/to/your/obsidian/vault
dry_run: true  # Set to false when ready to process

# Processing settings
batch_size: 1  # Process one file at a time
file_ordering: 'recent'  # Options: 'recent', 'size', 'random', 'alphabetical'

# Ollama configuration
ollama_base_url: http://localhost:11434
ollama_model: qwen3:8b  # or your preferred model
```

## 🚀 Usage

### Basic Usage

```bash
# Run with default settings (dry run mode)
python3 obsidian_auto_linker_enhanced.py
```

### Configuration Options

- **`dry_run: true`**: Test mode - shows what would be processed without making changes
- **`dry_run: false`**: Production mode - actually processes files
- **`file_ordering`**: Choose how files are ordered:
  - `'recent'`: Newest files first (recommended)
  - `'size'`: Largest files first
  - `'random'`: Random order
  - `'alphabetical'`: A-Z order

## 📊 File Ordering Options

| Option | Description | Best For |
|--------|-------------|----------|
| `recent` | Newest files first | Processing recent conversations |
| `size` | Largest files first | Tackling big conversations |
| `random` | Random order | Unbiased processing |
| `alphabetical` | A-Z order | Systematic processing |

## 🔧 Model Recommendations

### Fast Models (Recommended for testing)
- `llama3.2:3b` - Fastest, good quality
- `qwen2.5:3b` - Fast, very good quality
- `phi3:3.8b` - Fast, excellent quality

### High-Quality Models (Slower)
- `qwen3:8b` - High quality, slower
- `llama3.1:8b` - Very high quality, slow
- `mistral:7b` - Good balance of speed/quality

## 📈 Progress Tracking

The tool provides detailed progress information:

```
📊 Progress: 5/20 (25.0%) | ⏱️ 0:05:23 | 🏃 1.2/min | ⏳ 12min | 📁 conversation.md... | 🔄 Processing
```

- **Progress**: Current file / Total files (percentage)
- **⏱️ Time**: Elapsed time
- **🏃 Speed**: Files processed per minute
- **⏳ ETA**: Estimated time remaining
- **📁 File**: Current file being processed
- **🔄 Stage**: Processing status

## 📄 Output Files

The tool creates new files with `_linked` suffix:
- **Original**: `conversation.md` (preserved)
- **New**: `conversation_linked.md` (with links and tags)
- **Backup**: `conversation.md.backup` (safety backup)

## 🛡️ Safety Features

- **Dry run mode**: Test without making changes
- **Backup system**: Automatic backups before processing
- **New files**: Creates new files instead of modifying originals
- **Resume capability**: Skip already processed files
- **Progress tracking**: Monitor processing in real-time

## 🔧 Troubleshooting

### Ollama Connection Issues
```bash
# Check if Ollama is running
ollama ps

# Test model response
ollama run qwen3:8b "Hello"

# Restart Ollama if needed
pkill ollama
ollama serve
```

### Performance Issues
- Use smaller models for faster processing
- Close other memory-intensive applications
- Ensure sufficient RAM (8GB+ recommended)

### Configuration Issues
- Verify vault path is correct
- Check Ollama URL and model name
- Ensure all dependencies are installed

## 📝 License

This project is open source. Feel free to modify and distribute.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit issues and pull requests.

## 📞 Support

If you encounter issues:
1. Check the troubleshooting section
2. Verify your configuration
3. Test with a small batch of files first
4. Check Ollama is running and responding

---

**Happy linking! 🔗**