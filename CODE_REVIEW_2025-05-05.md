# Code Review (2025-05-05)

## Overview
This review covers the configuration and launcher layers that orchestrate the Obsidian Link Master pipeline. It focuses on startup reliability and configuration hygiene because these components determine whether the system can even reach the main processing logic.

## Findings

1. **Configuration loader currently raises a `TypeError` before the app can start.**
   The `RuntimeConfig` constructor receives duplicate keyword arguments for `embedding_base_url`, `embedding_model`, and `embedding_similarity_threshold/embedding_top_k`, which causes Python to throw an error (“got multiple values for keyword argument ...”) during initialization. As a result, any code path that imports `obsidian_link_master.settings` will fail immediately, preventing CLI or tests from running until the duplication is removed.
   
   *Evidence:* Duplicate keywords passed at lines 211–223 in `obsidian_link_master/configuration.py`.

2. **Launcher enforces embeddings even when the feature is disabled.**
   `run.py` unconditionally requires an `embedding_model` and always calls `run_embedding_tests`, even if `embedding_enabled` is false. This makes a non-embedding deployment (or a config that relies solely on Claude) exit early with a runtime error, and it also forces network calls to the embeddings endpoint even when not needed.
   
   *Evidence:* Hard requirement and test invocation at lines 218–223 in `run.py`.

3. **Launcher always starts and checks Ollama regardless of the selected AI provider.**
   The main function calls `is_ollama_ready`, potentially starts `ollama serve`, and pulls Ollama models without checking `ai_provider`. If a user configures Claude only, the launcher still demands Ollama binaries and models, which breaks valid deployments and defeats provider switching.
   
   *Evidence:* Provider-agnostic Ollama startup flow at lines 188–224 in `run.py`.

## Recommendations
- Fix the duplicated embedding parameters in `load_runtime_config` and add a regression test to ensure the dataclass can be instantiated from defaults.
- Gate embedding validation and test calls behind the `embedding_enabled` flag so Claude-only or text-only runs succeed.
- Skip Ollama readiness checks and model pulls when `ai_provider != "ollama"`; only require embeddings if the feature is enabled.
