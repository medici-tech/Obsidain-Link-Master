#!/usr/bin/env python3
"""Comprehensive embedding verification script for Ollama.

This script performs several smoke tests to validate embedding readiness
before running full vault processing:
- Basic embedding generation
- Semantic similarity comparisons
- Vault-like note matching simulation
- Embedding consistency checks
- Performance benchmarking

Example usage:
    python scripts/test_embeddings.py --model nomic-embed-text:latest

Exit status is non-zero if any required check fails.
"""

from __future__ import annotations

import argparse
import math
import time
from dataclasses import dataclass
from typing import Dict, List, Tuple

import numpy as np
import requests


@dataclass
class TestResult:
    name: str
    passed: bool
    details: str
    duration: float


class EmbeddingTester:
    def __init__(self, base_url: str, model: str, timeout: int) -> None:
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.timeout = timeout

    def _fetch_embedding(self, text: str) -> List[float]:
        url = f"{self.base_url}/api/embeddings"
        response = requests.post(
            url, json={"model": self.model, "prompt": text}, timeout=self.timeout
        )
        response.raise_for_status()
        data = response.json()
        embedding = data.get("embedding")
        if not embedding:
            raise ValueError("Empty embedding returned")
        return embedding

    @staticmethod
    def _cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
        v1 = np.array(vec1)
        v2 = np.array(vec2)
        if v1.size == 0 or v2.size == 0:
            return 0.0
        denom = np.linalg.norm(v1) * np.linalg.norm(v2)
        if denom == 0:
            return 0.0
        return float(np.dot(v1, v2) / denom)

    def test_basic_embedding(self) -> TestResult:
        start = time.perf_counter()
        try:
            embedding = self._fetch_embedding("Hello from Obsidian Link Master!")
            duration = time.perf_counter() - start
            return TestResult(
                name="Basic embedding generation",
                passed=len(embedding) > 0,
                details=f"Generated vector of length {len(embedding)} in {duration:.2f}s",
                duration=duration,
            )
        except Exception as exc:  # pylint: disable=broad-except
            duration = time.perf_counter() - start
            return TestResult(
                name="Basic embedding generation",
                passed=False,
                details=f"Failed to generate embedding: {exc}",
                duration=duration,
            )

    def test_semantic_similarity(self) -> TestResult:
        start = time.perf_counter()
        try:
            close_texts = (
                "How to integrate Qwen embeddings with Obsidian",
                "Guide for connecting Obsidian notes to Qwen embedding pipeline",
            )
            far_text = "Grocery list with apples, bananas, and milk"
            emb_a = self._fetch_embedding(close_texts[0])
            emb_b = self._fetch_embedding(close_texts[1])
            emb_c = self._fetch_embedding(far_text)

            sim_close = self._cosine_similarity(emb_a, emb_b)
            sim_far = self._cosine_similarity(emb_a, emb_c)
            duration = time.perf_counter() - start

            passed = sim_close > sim_far + 0.05
            detail = (
                f"close={sim_close:.3f} vs far={sim_far:.3f}. "
                "Expected close > far by at least 0.05"
            )
            return TestResult("Semantic similarity", passed, detail, duration)
        except Exception as exc:  # pylint: disable=broad-except
            duration = time.perf_counter() - start
            return TestResult(
                name="Semantic similarity",
                passed=False,
                details=f"Similarity test failed: {exc}",
                duration=duration,
            )

    def test_vault_matching(self) -> TestResult:
        start = time.perf_counter()
        try:
            notes = {
                "ai_planning.md": "Using embeddings to plan projects and prioritize tasks.",
                "meal_prep.md": "Weekly meal prep ideas with recipes and shopping lists.",
                "obsidian_links.md": "Strategies for linking Obsidian notes with AI assistance.",
                "fitness.md": "Strength training plan and cardio schedule.",
            }
            query_note = "How to auto-link Obsidian notes using embedding similarity"

            query_embedding = self._fetch_embedding(query_note)
            note_embeddings = {
                name: self._fetch_embedding(content) for name, content in notes.items()
            }
            scores: List[Tuple[str, float]] = []
            for name, embedding in note_embeddings.items():
                score = self._cosine_similarity(query_embedding, embedding)
                scores.append((name, score))
            scores.sort(key=lambda x: x[1], reverse=True)
            top_match, top_score = scores[0]
            duration = time.perf_counter() - start

            passed = top_match == "obsidian_links.md" and top_score > 0.2
            details = f"Top match: {top_match} (score={top_score:.3f})"
            return TestResult("Vault note matching", passed, details, duration)
        except Exception as exc:  # pylint: disable=broad-except
            duration = time.perf_counter() - start
            return TestResult(
                name="Vault note matching",
                passed=False,
                details=f"Vault simulation failed: {exc}",
                duration=duration,
            )

    def test_consistency(self) -> TestResult:
        start = time.perf_counter()
        try:
            text = "Consistency check for embedding determinism"
            emb1 = self._fetch_embedding(text)
            emb2 = self._fetch_embedding(text)
            similarity = self._cosine_similarity(emb1, emb2)
            delta = abs(similarity - 1.0)
            duration = time.perf_counter() - start

            passed = similarity > 0.995 or delta < 0.01
            details = f"Self-similarity={similarity:.4f} (delta from 1.0: {delta:.4f})"
            return TestResult("Embedding consistency", passed, details, duration)
        except Exception as exc:  # pylint: disable=broad-except
            duration = time.perf_counter() - start
            return TestResult(
                name="Embedding consistency",
                passed=False,
                details=f"Consistency test failed: {exc}",
                duration=duration,
            )

    def benchmark_performance(self) -> TestResult:
        start = time.perf_counter()
        texts = [
            "Quick performance benchmark for embeddings",
            "Obsidian linking throughput test",
            "Short note about AI and embeddings",
            "Benchmarking latency and throughput",
            "Final performance sample for embeddings",
        ]
        try:
            latencies = []
            for text in texts:
                t0 = time.perf_counter()
                _ = self._fetch_embedding(text)
                latencies.append(time.perf_counter() - t0)
            total_duration = time.perf_counter() - start

            avg_latency = sum(latencies) / len(latencies)
            throughput = len(texts) / total_duration if total_duration else math.inf
            details = (
                f"Avg latency {avg_latency:.2f}s | p95 {np.percentile(latencies, 95):.2f}s | "
                f"Throughput {throughput:.2f} embeds/sec"
            )
            return TestResult(
                name="Performance benchmark",
                passed=avg_latency < self.timeout,
                details=details,
                duration=total_duration,
            )
        except Exception as exc:  # pylint: disable=broad-except
            duration = time.perf_counter() - start
            return TestResult(
                name="Performance benchmark",
                passed=False,
                details=f"Benchmark failed: {exc}",
                duration=duration,
            )

    def run_all(self) -> List[TestResult]:
        return [
            self.test_basic_embedding(),
            self.test_semantic_similarity(),
            self.test_vault_matching(),
            self.test_consistency(),
            self.benchmark_performance(),
        ]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate embedding readiness via Ollama")
    parser.add_argument(
        "--base-url",
        default="http://localhost:11434",
        help="Base URL for the Ollama server (default: http://localhost:11434)",
    )
    parser.add_argument(
        "--model",
        default="nomic-embed-text:latest",
        help="Embedding model to test (default: nomic-embed-text:latest)",
    )
    parser.add_argument(
        "--timeout", type=int, default=30, help="Request timeout per call in seconds"
    )
    return parser.parse_args()


def print_results(results: List[TestResult]) -> bool:
    print("\n=== Embedding Preflight Results ===")
    all_passed = True
    for result in results:
        status = "✅" if result.passed else "❌"
        print(f"{status} {result.name} ({result.duration:.2f}s) - {result.details}")
        all_passed = all_passed and result.passed

    passed_count = sum(r.passed for r in results)
    print(f"\nSummary: {passed_count}/{len(results)} checks passed")
    return all_passed


def main() -> None:
    args = parse_args()
    tester = EmbeddingTester(args.base_url, args.model, args.timeout)
    results = tester.run_all()
    success = print_results(results)
    if not success:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
