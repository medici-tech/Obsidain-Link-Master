# Obsidian Auto-Linker

An intelligent tool that automatically processes your Obsidian vault files and creates a Map of Content (MOC) structure with AI-powered linking.

## Features

- **Interactive Configuration**: Easy setup with guided prompts
- **Safe Processing**: Creates new `_linked.md` files instead of overwriting originals
- **Progress Tracking**: Real-time progress display with ETA
- **Resource Monitoring**: Track CPU and memory usage in real-time
- **Activity Tracking**: See exactly what the process is doing when you stop it
- **Easy Stop**: Press Ctrl+C to stop processing at any time with resource summary
- **Local AI**: Uses Ollama for privacy and cost-free processing
- **Smart Caching**: Avoids re-processing already analyzed files
- **Multiple Ordering**: Process files by recent, size, random, or alphabetical order

## Quick Start

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Start Ollama** (if not already running):
   ```bash
   ollama serve
   ```

3. **Run the Interactive Tool**:
   ```bash
   python3 run.py
   ```

4. **Follow the prompts**:
   - Choose your Obsidian vault path
   - Select file processing order
   - Choose between Dry Run (safe) or Live Run
   - Pick batch size
   - Confirm and start processing

## Usage

### Interactive Mode
```bash
python3 run.py
```

The script will guide you through:
- **Vault Path**: Location of your Obsidian vault
- **File Order**: How to process files (recent, size, random, alphabetical)
- **Processing Mode**: 
  - Dry Run: Safe testing mode (no file changes)
  - Live Run: Creates new `_linked.md` files
- **Batch Size**: How many files to process at once

### Stopping the Process
- Press **Ctrl+C** at any time to stop processing safely
- The script will gracefully terminate and save progress
- **Resource Summary**: When you stop, you'll see:
  - Total runtime
  - Peak CPU and memory usage
  - Average resource usage
  - What the process was doing when stopped
  - Recent resource trends

## Configuration

The tool automatically creates a `config.yaml` file with your preferences. You can also edit this file directly for advanced settings.

## Output

- **Dry Run**: Shows what would be processed without making changes
- **Live Run**: Creates new files with `_linked` suffix (e.g., `note.md` → `note_linked.md`)

## Troubleshooting

### Ollama Issues
If you get connection errors:
1. Make sure Ollama is running: `ollama serve`
2. Check if your model is loaded: `ollama list`
3. Pull the model if needed: `ollama pull qwen3:8b`

### Slow Processing
Local AI models can be slow (2-3 minutes per file). This is normal. The tool includes:
- Progress tracking with ETA
- Retry logic for timeouts
- Caching to avoid re-processing

## Files Created

- `config.yaml`: Configuration settings
- `.ai_cache.json`: AI response cache
- `.processing_progress.json`: Processing progress
- `*_linked.md`: New processed files (in Live mode)

## Safety Features

- **Dry Run Mode**: Test without making changes
- **Backup System**: Original files are never modified
- **Progress Saving**: Can resume interrupted processing
- **Error Handling**: Graceful failure recovery
- **Resource Monitoring**: Track system impact in real-time
- **Activity Tracking**: Know exactly what was happening when you stopped