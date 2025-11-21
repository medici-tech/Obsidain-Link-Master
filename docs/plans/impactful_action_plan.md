# Impactful Action Plan: Toward an Automated "Second Brain"

## Current Foundations (already implemented)
- Local AI-powered MOC categorization and tag-style linking using Qwen models (qwen3:8b or qwen2.5:3b).
- Wikilink creation, hashing-based caching, and basic resume support to keep runs consistent.
- Dashboard telemetry, local Ollama access, hybrid model selection, and analytics reporting.

## Highest-Impact Next Steps (ranked)
1. **Make parallel processing real and resilient**
   - Turn the existing scaffold into true concurrent processing with safe resource limits.
   - Add progress/resume checkpoints per batch so partial runs survive interruptions.
2. **Bounded cache governance**
   - Introduce size/age-based eviction policies and observability for cache hits/misses.
   - Guard against unbounded memory usage while keeping warm paths fast.
3. **Link-quality scoring and enrichment**
   - Score generated links to prioritize the strongest connections in the vault.
   - Layer semantic similarity (nomic-embed-text) to surface relationships AI analysis might miss.
4. **Incremental processing and re-run efficiency**
   - Detect and process only changed conversations/notes.
   - Export dashboard metrics for each run to track improvements over time.
5. **Operational hardening**
   - Improve error handling and retries around Ollama/local model calls.
   - Add lightweight health checks and smoke tests to catch regressions early.

## Work Sequencing
- **Sprint 1:** Parallelism + bounded cache (concrete performance wins, prevents blow-ups).
- **Sprint 2:** Link-quality scoring + embedding-based enrichment (better graph quality).
- **Sprint 3:** Incremental runs + dashboard exports (efficiency + observability).
- **Sprint 4:** Resume/operational hardening (stability under real-world vaults).

## Definition of Done (per item)
- Measurable performance gain (throughput/latency) and no memory regressions.
- Link graph shows ranked edges with clear thresholds and rationale.
- Incremental mode skips untouched files and records run metrics.
- Resilience validated via interrupted-run drills and recovery tests.

## Traceability
- Aligns with open TODO items for parallel execution, cache eviction, link-quality scoring, resume hardening, and incremental/dashboard enhancements.
- Extends the organizational guidance that **new files live in subfolders** for clarity.
