# Quick Model Setup Guide

## ⚡ TL;DR - What To Do Right Now

Your current config uses **Qwen3-Embedding** which **CANNOT generate text**. You need to change it.

### Recommended Configuration

**Edit `config.yaml` and change line 7**:

```yaml
# BEFORE (❌ BROKEN):
ollama_model: Qwen3-Embedding-8B:Q8_0

# AFTER (✅ WORKS):
ollama_model: qwen2.5-coder:7b
```

Then pull the model:
```bash
ollama pull qwen2.5-coder:7b
```

## Model Comparison: Your Options

| Model Name | Type | Use Case | Speed | Quality | Memory |
|------------|------|----------|-------|---------|--------|
| **qwen2.5-coder:7b** | Generation | **BEST CHOICE** for technical content | ⚡⚡⚡⚡ | ⭐⭐⭐⭐⭐ | 8GB |
| qwen2.5:3b | Generation | Fast, general purpose | ⚡⚡⚡⚡⚡ | ⭐⭐⭐⭐ | 4GB |
| goekdenizguelmez/JOSIEFIED-Qwen3 | Generation | Unknown variant | ❓ | ❓ | ❓ |
| nomic-embed-text | Embedding | Similarity search (optional) | ⚡⚡⚡⚡⚡ | ⭐⭐⭐⭐ | 1GB |
| dengcao/Qwen3-Embedding-8B | Embedding | Similarity search (optional) | ⚡⚡⚡ | ⭐⭐⭐⭐⭐ | 8GB |

## Three Setup Strategies

### Strategy 1: Generation Only (Simplest) ⭐ RECOMMENDED TO START

**Best for**: Testing, learning, simple vaults

```yaml
# config.yaml
ollama_model: qwen2.5-coder:7b
embedding_enabled: false
```

**Setup**:
```bash
ollama pull qwen2.5-coder:7b
python3 run.py
```

**Pros**:
✅ Simplest setup
✅ Fast
✅ Works immediately
✅ 8GB RAM sufficient

**Cons**:
❌ May miss some similar notes
❌ Only AI-based similarity

---

### Strategy 2: Fast Hybrid (Best Balance) ⭐⭐ RECOMMENDED

**Best for**: Most users, daily use, large vaults

```yaml
# config.yaml
ollama_model: qwen2.5-coder:7b
embedding_enabled: true
embedding_model: nomic-embed-text:latest
embedding_similarity_threshold: 0.75
embedding_top_k: 10
```

**Setup**:
```bash
ollama pull qwen2.5-coder:7b
ollama pull nomic-embed-text:latest
python3 run.py
```

**Pros**:
✅ Best accuracy/speed balance
✅ Finds more similar notes
✅ Fast embeddings
✅ 8GB RAM sufficient

**Cons**:
❌ Slightly more complex
❌ Initial embedding generation time

---

### Strategy 3: Quality Hybrid (Maximum Accuracy) ⭐⭐⭐

**Best for**: Technical vaults, research, maximum quality

```yaml
# config.yaml
ollama_model: qwen2.5-coder:7b
embedding_enabled: true
embedding_model: dengcao/Qwen3-Embedding-8B:Q8_0
embedding_similarity_threshold: 0.75
embedding_top_k: 10
```

**Setup**:
```bash
ollama pull qwen2.5-coder:7b
ollama pull dengcao/Qwen3-Embedding-8B:Q8_0
python3 run.py
```

**Pros**:
✅ Best possible accuracy
✅ Best embedding quality
✅ Excellent for technical content

**Cons**:
❌ Slower embeddings
❌ 16GB RAM recommended
❌ Longer processing time

---

## Quick Decision Matrix

**Choose Generation Only if**:
- You're just testing the system
- You have limited RAM (<8GB)
- You want simplest setup
- Speed is critical

**Choose Fast Hybrid if**:
- You want best results
- You have 8GB+ RAM
- You want good speed + accuracy
- Your vault has 100+ notes

**Choose Quality Hybrid if**:
- You have technical/research notes
- You have 16GB+ RAM
- Quality > Speed
- Your vault is your knowledge base

## Performance Estimates

### Processing 100 Notes

| Strategy | Time | RAM Usage | Accuracy |
|----------|------|-----------|----------|
| Generation Only | 15 min | 8GB | 85% |
| Fast Hybrid | 20 min | 9GB | 93% |
| Quality Hybrid | 35 min | 14GB | 97% |

*Estimates based on average note size of 2KB*

## Common Mistakes

### ❌ MISTAKE 1: Using Embedding Model for Generation
```yaml
ollama_model: Qwen3-Embedding-8B:Q8_0  # WRONG!
```
**Error**: "Invalid JSON response" or empty output

**Fix**: Change to generation model
```yaml
ollama_model: qwen2.5-coder:7b  # CORRECT!
```

### ❌ MISTAKE 2: Not Pulling Models
**Error**: "model not found"

**Fix**: Pull all models first
```bash
ollama pull qwen2.5-coder:7b
ollama pull nomic-embed-text:latest
```

### ❌ MISTAKE 3: Wrong Model Names
```yaml
embedding_model: Qwen3-Embedding-8B:Q8_0  # WRONG!
```

**Fix**: Use full name with author
```yaml
embedding_model: dengcao/Qwen3-Embedding-8B:Q8_0  # CORRECT!
```

## Verification Checklist

Before running, verify:

- [ ] Generation model is set correctly
  ```bash
  grep "ollama_model:" config.yaml
  # Should show: ollama_model: qwen2.5-coder:7b (or qwen2.5:3b)
  ```

- [ ] Models are pulled
  ```bash
  ollama list | grep qwen2.5-coder
  # Should show model in list
  ```

- [ ] Ollama is running
  ```bash
  curl http://localhost:11434/api/tags
  # Should return JSON list of models
  ```

- [ ] Config is valid
  ```bash
  python3 -c "import yaml; yaml.safe_load(open('config.yaml'))"
  # Should have no errors
  ```

## Next Steps

1. **Update config.yaml**
   ```bash
   nano config.yaml  # or your preferred editor
   # Change ollama_model to: qwen2.5-coder:7b
   ```

2. **Pull models**
   ```bash
   ollama pull qwen2.5-coder:7b
   ollama pull nomic-embed-text:latest  # Optional but recommended
   ```

3. **Test**
   ```bash
   python3 run.py
   # Choose "Fast Dry Run" to test quickly
   ```

4. **Verify output**
   - Check terminal for errors
   - Look for structured JSON responses
   - Verify notes are being processed

## Getting Help

If issues persist:

1. Check `TROUBLESHOOTING.md`
2. View logs in terminal output
3. Test Ollama directly:
   ```bash
   ollama run qwen2.5-coder:7b "Test prompt"
   ```
4. Review `EMBEDDING_INTEGRATION_GUIDE.md` for details

---

**Quick Answer**: Use `qwen2.5-coder:7b` for generation, optionally add `nomic-embed-text` for better similarity matching.
