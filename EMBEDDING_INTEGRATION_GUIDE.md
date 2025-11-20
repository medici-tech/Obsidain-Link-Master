# Embedding Integration Guide

## Overview

This guide explains how to integrate embedding models with text generation models for optimal note linking in your Obsidian Auto-Linker project.

## Understanding the Two Types of Models

### 1. Embedding Models (Semantic Similarity)
**What they do**: Convert text into numerical vectors (arrays of numbers)
**Use case**: Finding semantically similar content

**Your models**:
- `dengcao/Qwen3-Embedding-8B:Q8_0` - High quality, slower
- `nomic-embed-text:latest` - Fast, efficient

**Example**:
```
Input:  "Machine learning with neural networks"
Output: [0.123, -0.456, 0.789, ... ] (768 or 8192 dimensions)
```

### 2. Text Generation Models (Analysis & Output)
**What they do**: Generate structured text responses
**Use case**: Analyzing content, categorizing, extracting concepts

**Your models**:
- `qwen2.5-coder:7b` - **RECOMMENDED** (best for technical content)
- `qwen2.5:3b` - Fast, lightweight alternative

**Example**:
```
Input:  "Analyze this note and categorize it"
Output: {"moc_category": "Technical & Automation", "concepts": [...]}
```

## Why Can't You Use Embedding Models Alone?

❌ **Your current config.yaml has**:
```yaml
ollama_model: Qwen3-Embedding-8B:Q8_0
```

**This will fail** because:
1. Embedding models cannot generate structured JSON responses
2. They only output numerical vectors
3. The system expects text analysis and categorization

## Recommended Architecture: Hybrid Approach

### Strategy 1: Embeddings for Similarity + Generation for Analysis

```
┌─────────────────────────────────────────────┐
│  STEP 1: Text Generation (Primary)          │
│  Model: qwen2.5-coder:7b                    │
│  Purpose: Categorize, extract concepts      │
└─────────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────┐
│  STEP 2: Embedding Similarity (Enhancement) │
│  Model: qwen3-embedding-8b or nomic         │
│  Purpose: Find additional similar notes     │
└─────────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────┐
│  STEP 3: Merge Results                      │
│  Combine AI suggestions + embedding matches │
└─────────────────────────────────────────────┘
```

### Strategy 2: Fast Hybrid (Best Performance)

Use fast models for both:
- **Generation**: `qwen2.5:3b` (3B parameters, fast)
- **Embeddings**: `nomic-embed-text` (lightning fast)

### Strategy 3: Quality Hybrid (Best Accuracy)

Use high-quality models for both:
- **Generation**: `qwen2.5-coder:7b` (7B parameters, technical)
- **Embeddings**: `qwen3-embedding-8b` (best embeddings)

## Implementation Guide

### Step 1: Update Your Configuration

Edit `config.yaml`:

```yaml
# === PRIMARY MODEL (Text Generation) ===
ollama_model: qwen2.5-coder:7b  # CHANGE THIS!
ollama_timeout: 120
ollama_max_tokens: 2048

# === EMBEDDING MODEL (Similarity Search) ===
embedding_enabled: true
embedding_model: nomic-embed-text:latest  # Start with fast model
embedding_similarity_threshold: 0.75
embedding_top_k: 10
```

**OR** use the pre-configured file:
```bash
cp config_hybrid_embedding.yaml config.yaml
```

### Step 2: Verify Models Are Installed

```bash
# List installed models
ollama list

# Pull required models if needed
ollama pull qwen2.5-coder:7b
ollama pull nomic-embed-text:latest

# Optional: Pull high-quality embedding model
ollama pull dengcao/Qwen3-Embedding-8B:Q8_0
```

### Step 3: Test Embedding System

```bash
cd scripts
python3 embedding_similarity.py
```

Expected output:
```
✅ Loaded 0 cached embeddings
Getting embeddings...
Similarity between ML texts: 0.892
Similarity between ML and cooking: 0.234
Similarity between AI and cooking: 0.198
```

### Step 4: Integrate with Main Processor

The integration happens in `obsidian_auto_linker_enhanced.py`. You'll need to modify the `analyze_with_balanced_ai` function to use embeddings:

```python
# Import the embedding manager
from scripts.embedding_similarity import EmbeddingManager, integrate_embeddings_with_ai_analysis

# Initialize at startup (after loading config)
embedding_manager = EmbeddingManager(config) if config.get('embedding_enabled') else None

# In analyze_with_balanced_ai function:
def analyze_with_balanced_ai(content, existing_notes, context):
    # ... existing code for AI analysis ...

    # After getting AI result:
    if embedding_manager and ai_result:
        ai_result = integrate_embeddings_with_ai_analysis(
            embedding_manager,
            current_file_path,
            content,
            existing_notes,
            ai_result
        )

    return ai_result
```

### Step 5: Run a Test

```bash
# Start Ollama
ollama serve

# Run in dry-run mode to test
python3 run.py

# Or with dashboard
python3 run_with_dashboard.py
```

## Performance Comparison

### Option 1: Fast Hybrid (Recommended for Most Users)
```yaml
ollama_model: qwen2.5:3b
embedding_model: nomic-embed-text:latest
```
**Speed**: ⚡⚡⚡⚡⚡ (5/5)
**Quality**: ⭐⭐⭐⭐ (4/5)
**Memory**: 4GB RAM

### Option 2: Balanced Hybrid (Recommended for Technical Content)
```yaml
ollama_model: qwen2.5-coder:7b
embedding_model: nomic-embed-text:latest
```
**Speed**: ⚡⚡⚡⚡ (4/5)
**Quality**: ⭐⭐⭐⭐⭐ (5/5)
**Memory**: 8GB RAM

### Option 3: Quality Hybrid (Best Results)
```yaml
ollama_model: qwen2.5-coder:7b
embedding_model: dengcao/Qwen3-Embedding-8B:Q8_0
```
**Speed**: ⚡⚡⚡ (3/5)
**Quality**: ⭐⭐⭐⭐⭐ (5/5)
**Memory**: 12GB RAM

### Option 4: Generation Only (No Embeddings)
```yaml
ollama_model: qwen2.5-coder:7b
embedding_enabled: false
```
**Speed**: ⚡⚡⚡⚡ (4/5)
**Quality**: ⭐⭐⭐⭐ (4/5)
**Memory**: 8GB RAM

## Benefits of Hybrid Approach

### 1. **Better Sibling Note Discovery**
- AI understands **semantic** relationships
- Embeddings find **statistically similar** content
- Combined approach catches more connections

### 2. **Reduced AI Costs**
- Embeddings are **much faster** than generation
- Can find similar notes without expensive AI calls
- Cache embeddings for instant future lookups

### 3. **Improved Accuracy**
- AI can misunderstand context
- Embeddings provide objective similarity
- Cross-validation between approaches

### 4. **Flexible Trade-offs**
- Use fast models for simple notes
- Use quality models for complex content
- Adjust thresholds based on needs

## Troubleshooting

### Issue: "Embedding request timed out"
**Solution**: Use faster model
```yaml
embedding_model: nomic-embed-text:latest  # Much faster than qwen3-embedding
```

### Issue: "Too many similar notes"
**Solution**: Increase threshold
```yaml
embedding_similarity_threshold: 0.85  # Higher = more selective (0.75 default)
```

### Issue: "Not finding similar notes"
**Solution**: Lower threshold
```yaml
embedding_similarity_threshold: 0.65  # Lower = more matches
```

### Issue: "High memory usage"
**Solution**: Limit cache size or use smaller models
```yaml
max_cache_entries: 5000  # Reduce from 10000
embedding_model: nomic-embed-text:latest  # Smaller model
```

## Advanced: Intelligent Model Routing

For maximum efficiency, use different models based on content complexity:

```yaml
# Use hybrid model selection
hybrid_model_selection: true

# Simple content (<1000 words)
secondary_ollama_model: qwen2.5:3b

# Complex content (>1000 words)
primary_ollama_model: qwen2.5-coder:7b

# Threshold
model_switching_threshold: 1000
```

This is already implemented in `scripts/intelligent_model_selector.py`!

## Summary: What To Do Now

1. **Fix your config.yaml**:
   ```yaml
   ollama_model: qwen2.5-coder:7b  # NOT qwen3-embedding!
   ```

2. **Enable embeddings** (optional but recommended):
   ```yaml
   embedding_enabled: true
   embedding_model: nomic-embed-text:latest
   ```

3. **Pull required models**:
   ```bash
   ollama pull qwen2.5-coder:7b
   ollama pull nomic-embed-text:latest
   ```

4. **Test the system**:
   ```bash
   python3 run.py
   ```

## Next Steps

- [ ] Update config.yaml with correct models
- [ ] Test embedding similarity script
- [ ] Integrate embeddings into main processor
- [ ] Run full pipeline test
- [ ] Compare results with and without embeddings
- [ ] Adjust thresholds based on results
- [ ] Document findings in your notes

## Questions?

- **"Should I use embeddings?"**: YES, they significantly improve sibling note detection
- **"Which embedding model?"**: Start with `nomic-embed-text` (fast), upgrade to `qwen3-embedding-8b` if needed
- **"Which generation model?"**: Use `qwen2.5-coder:7b` for technical vaults, `qwen2.5:3b` for general notes
- **"Can I use only embeddings?"**: NO, you need a generation model for structured output

---

**Last Updated**: 2025-11-20
**Author**: Claude
**Version**: 1.0
