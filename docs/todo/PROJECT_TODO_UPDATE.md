# 📋 Obsidian Auto-Linker - Updated TODO (Second Brain Focus)

**Last Updated:** 2025-03-29  \
**Scope:** Local-only vault processing with hybrid Qwen + embedding workflow

---

## 🚩 Status Recap (from latest review)
- Core categorization + linking pipeline is live (Qwen models, wikilinks, MOC assignment).
- Dashboard telemetry, caching, and resume scaffolding exist but need resilience upgrades.
- Parallel execution is scaffolded yet currently sequential; link-quality ranking is missing.
- Incremental/delta processing and exportable analytics are still pending.

---

## 🎯 High-Priority Actions (Quality & Resilience)
- [ ] **Parallel processing**: Implement bounded concurrency for note processing; add fail-fast and retry policies to keep runs stable on larger vaults.
- [ ] **Cache governance**: Add eviction (LRU/size + TTL) and cache stats to prevent unbounded growth during long sessions.
- [ ] **Link-quality scoring**: Score and rank candidate wikilinks (model + embedding signals) so only top-strength links are promoted.
- [ ] **Resume & checkpoints**: Persist per-note progress and last-processed hashes to resume gracefully after interruption.
- [ ] **Incremental runs**: Detect changed/added/removed notes and process deltas only; maintain a change index to avoid full re-runs.

## 📊 Analytics & Dashboard Enhancements
- [ ] **Exportable metrics**: Add CSV/JSON export for dashboard telemetry and run analytics for offline review.
- [ ] **Progress visibility**: Add progress-bar/percentage reporting to terminal + dashboard to communicate long-run status.
- [ ] **Similarity insights**: Surface embedding-based related-note suggestions in the dashboard to enrich the knowledge graph view.

## 🔧 Performance & Reliability
- [ ] **Batching & backpressure**: Batch AI requests (where safe) and add backpressure when queues grow to maintain steady throughput.
- [ ] **Memory safeguards**: Track memory footprint per batch and throttle when thresholds are hit to protect large-vault runs.
- [ ] **Profiling loop**: Add lightweight profiling hooks around hot paths (I/O, embeddings, model calls) and store samples in reports/.

## 🧠 Knowledge Graph Depth
- [ ] **Concept extraction refinements**: Tune concept/tag generation prompts for higher recall of domain-specific terms.
- [ ] **Connection enrichment**: Use embedding overlaps to propose cross-MOC links that the primary pass misses; gate by score threshold.

## ✅ Definition of Done (per task)
- Implementation landed with tests covering success + failure paths.
- Dashboard/CLI surfaces status and key metrics for the feature.
- Docs updated in-line with the change (README/USAGE or dedicated section).
- No regressions in existing processing or configuration defaults.
