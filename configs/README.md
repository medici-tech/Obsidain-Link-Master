# Configuration Files Documentation

This directory contains specialized configuration presets for different use cases.

## Main Configuration

**`config.yaml`** (root directory)
- Primary configuration file used by default
- Balanced settings for general use
- Edit this file to customize your default behavior
- Defaults use `Qwen3-Embedding-8B:Q8_0` for Ollama requests

## Specialized Presets

### Performance Optimized

**`config_fast.yaml`**
- Fast dry run with minimal analysis
- Quick model (qwen2.5:3b)
- Reduced tokens and timeout
- Best for: Quick testing, small vaults
- Settings:
  - `fast_dry_run: true`
  - `ollama_timeout: 10s`
  - `ollama_max_tokens: 100`
  - `ollama_max_retries: 1`

**`config_ultra_fast.yaml`**
- Maximum speed configuration
- Minimal processing overhead
- Best for: Very quick scans

### Analysis Optimized

**`config_detailed_analytics.yaml`**
- Enhanced analytics and reporting
- Comprehensive metrics tracking
- Best for: In-depth analysis

**`config_qwen3_maximum_detail.yaml`**
- Uses Qwen3:8b for maximum accuracy
- Extended timeouts for complex reasoning
- Highest quality categorization
- Best for: Important vaults, production use
- Settings:
  - `ollama_model: qwen3:8b`
  - `ollama_timeout: 300s`
  - `ollama_max_tokens: 1024`

**`config_extended_timeout.yaml`**
- Extra time for complex processing
- Prevents timeout errors
- Best for: Large files, complex content

### Special Modes

**`config_hybrid_models.yaml`**
- Uses both Qwen3:8b and Qwen2.5:3b intelligently
- Automatically switches based on file complexity
- Optimized for MacBook Air M4 16GB
- Best for: Balancing speed and accuracy
- Settings:
  - `use_hybrid_models: true`
  - `primary_model: qwen3:8b` (complex files)
  - `secondary_model: qwen2.5:3b` (simple files)
  - `model_switching_threshold: 1000` words

## Configuration Status

### ✅ Actively Used Configurations
- **config_detailed_analytics.yaml** - Used by `run_detailed_analytics.py`
- **config_extended_timeout.yaml** - Used by `run_extended_timeout.py`
- **config_hybrid_models.yaml** - Used by `scripts/intelligent_model_selector.py`
- **config_qwen3_maximum_detail.yaml** - Used by `run_ultra_detailed.py`

### 📝 Template Configurations
- **config_fast.yaml** - Template for `scripts/optimize_performance.py` generation
- **config_ultra_fast.yaml** - Template for `scripts/optimize_performance.py` generation
- These are copied/modified when running the optimization script

## Usage

### Use a Preset Configuration

```bash
# Copy preset to main config
cp configs/config_fast.yaml config.yaml

# Or specify config in code
python run.py --config configs/config_detailed_analytics.yaml
```

### Configuration Selection Guide

| Use Case | Recommended Config | Why |
|----------|-------------------|-----|
| Quick test | `config_fast.yaml` | Fast feedback |
| Production processing | `config_qwen3_maximum_detail.yaml` | Best accuracy |
| Large vault | `config_extended_timeout.yaml` | Prevents timeouts |
| Balanced approach | `config_hybrid_models.yaml` | Speed + accuracy |
| Detailed analysis | `config_detailed_analytics.yaml` | Rich metrics |
| Small vault (<100 files) | `config_fast.yaml` | Quick completion |
| Large vault (1000+ files) | `config_hybrid_models.yaml` | Efficient processing |

## Key Settings Explained

### Model Selection
- **qwen2.5:3b**: Fast, uses ~2GB RAM, good for simple content
- **qwen3:8b**: Accurate, uses ~5GB RAM, better for complex content

### Processing Modes
- **dry_run**: Analyze without modifying files (recommended first time)
- **fast_dry_run**: Skip AI, use keyword matching (very fast)
- **live run**: Actually modify files with AI analysis

### Performance Tuning
- **batch_size**: Files to process at once (1 = safer, higher = faster)
- **parallel_workers**: Number of simultaneous processes
- **ollama_timeout**: Max wait time for AI response (seconds)
- **ollama_max_retries**: Retry attempts on failure

### Memory Management
- Batch size 1 + Sequential processing = ~7GB RAM
- Parallel workers 4 + Batch size 10 = ~12GB+ RAM
- Hybrid mode balances memory usage automatically

## Creating Custom Presets

1. Copy an existing config:
   ```bash
   cp configs/config_fast.yaml configs/config_mypreset.yaml
   ```

2. Edit the settings

3. Test with dry run:
   ```bash
   python run.py --config configs/config_mypreset.yaml --dry-run
   ```

4. Use for production:
   ```bash
   python run.py --config configs/config_mypreset.yaml
   ```

## Configuration Priority

1. Command line arguments (highest priority)
2. Specified config file via `--config`
3. `config.yaml` in root directory
4. Built-in defaults (lowest priority)

## Best Practices

- ✅ Always test new configs with `dry_run: true` first
- ✅ Start with `config_fast.yaml` for initial testing
- ✅ Use `config_qwen3_maximum_detail.yaml` for production
- ✅ Monitor memory usage with larger batch sizes
- ✅ Keep your customizations in a separate preset file
- ⚠️ Don't edit files in `configs/` directly (they may be overwritten)

## Troubleshooting

**Timeouts:** Use `config_extended_timeout.yaml`
**Out of memory:** Reduce batch_size to 1, parallel_workers to 1
**Slow processing:** Use `config_fast.yaml` or `config_hybrid_models.yaml`
**Low accuracy:** Use `config_qwen3_maximum_detail.yaml`

---

**Note:** All config files in this directory are presets. Your active configuration is `config.yaml` in the root directory.
