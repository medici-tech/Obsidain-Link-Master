#!/usr/bin/env python3
"""
Embedding-Based Similarity Search for Obsidian Notes
Uses local embedding models (Qwen3-Embedding, nomic-embed-text) to find similar notes
"""

import json
import os
import time
from typing import Dict, List, Tuple, Optional, Any
import requests
import numpy as np
from pathlib import Path


class EmbeddingManager:
    """Manages embeddings for similarity search"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.base_url = config.get('embedding_base_url', 'http://localhost:11434')
        self.model = config.get('embedding_model', 'nomic-embed-text:latest')
        self.enabled = config.get('embedding_enabled', False)
        self.threshold = config.get('embedding_similarity_threshold', 0.75)
        self.top_k = config.get('embedding_top_k', 10)

        # Cache embeddings to disk
        vault_path = config.get('vault_path', '')
        cache_dir = Path(vault_path).parent / '.embeddings_cache'
        cache_dir.mkdir(exist_ok=True)
        self.cache_file = cache_dir / f'{self.model.replace(":", "_").replace("/", "_")}_embeddings.json'

        # Load existing embeddings
        self.embeddings_cache: Dict[str, List[float]] = {}
        self._load_cache()

    def _load_cache(self):
        """Load embeddings from disk cache"""
        if self.cache_file.exists():
            try:
                with open(self.cache_file, 'r') as f:
                    self.embeddings_cache = json.load(f)
                print(f"✅ Loaded {len(self.embeddings_cache)} cached embeddings")
            except Exception as e:
                print(f"⚠️  Failed to load embeddings cache: {e}")
                self.embeddings_cache = {}

    def _save_cache(self):
        """Save embeddings to disk cache"""
        try:
            with open(self.cache_file, 'w') as f:
                json.dump(self.embeddings_cache, f)
        except Exception as e:
            print(f"⚠️  Failed to save embeddings cache: {e}")

    def get_embedding(self, text: str, file_path: str = "") -> Optional[List[float]]:
        """
        Get embedding vector for text

        Args:
            text: Text content to embed
            file_path: Optional file path for cache key

        Returns:
            Embedding vector (list of floats) or None if failed
        """
        if not self.enabled:
            return None

        # Use file_path as cache key if provided, otherwise hash the text
        cache_key = file_path if file_path else str(hash(text))

        # Check cache first
        if cache_key in self.embeddings_cache:
            return self.embeddings_cache[cache_key]

        try:
            # Call Ollama embedding API
            url = f"{self.base_url}/api/embeddings"
            payload = {
                "model": self.model,
                "prompt": text[:8000]  # Limit text length to avoid timeout
            }

            response = requests.post(url, json=payload, timeout=30)
            response.raise_for_status()

            result = response.json()
            embedding = result.get('embedding', [])

            if not embedding:
                print(f"⚠️  Empty embedding returned for {file_path}")
                return None

            # Cache the embedding
            self.embeddings_cache[cache_key] = embedding

            # Periodically save cache (every 100 embeddings)
            if len(self.embeddings_cache) % 100 == 0:
                self._save_cache()

            return embedding

        except requests.exceptions.Timeout:
            print(f"⏰ Embedding request timed out for {file_path}")
            return None
        except Exception as e:
            print(f"❌ Failed to get embedding for {file_path}: {e}")
            return None

    def cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """
        Calculate cosine similarity between two vectors

        Returns:
            Similarity score between 0 and 1 (1 = identical)
        """
        v1 = np.array(vec1)
        v2 = np.array(vec2)

        # Calculate cosine similarity
        dot_product = np.dot(v1, v2)
        norm1 = np.linalg.norm(v1)
        norm2 = np.linalg.norm(v2)

        if norm1 == 0 or norm2 == 0:
            return 0.0

        similarity = dot_product / (norm1 * norm2)

        # Normalize to 0-1 range (cosine similarity can be -1 to 1)
        return float((similarity + 1) / 2)

    def find_similar_notes(
        self,
        current_note_path: str,
        current_note_content: str,
        all_notes: Dict[str, str]
    ) -> List[Tuple[str, float]]:
        """
        Find notes similar to the current note using embeddings

        Args:
            current_note_path: Path to the current note
            current_note_content: Content of the current note
            all_notes: Dict mapping note paths to their content

        Returns:
            List of (note_name, similarity_score) tuples, sorted by similarity
        """
        if not self.enabled:
            return []

        print(f"  🔍 Finding similar notes using embeddings...")
        start_time = time.time()

        # Get embedding for current note
        current_embedding = self.get_embedding(current_note_content, current_note_path)
        if current_embedding is None:
            print(f"  ⚠️  Failed to get embedding for current note")
            return []

        # Calculate similarities
        similarities = []
        for note_path, note_content in all_notes.items():
            # Skip the current note
            if note_path == current_note_path:
                continue

            # Get embedding for this note
            note_embedding = self.get_embedding(note_content, note_path)
            if note_embedding is None:
                continue

            # Calculate similarity
            similarity = self.cosine_similarity(current_embedding, note_embedding)

            # Only include if above threshold
            if similarity >= self.threshold:
                note_name = os.path.splitext(os.path.basename(note_path))[0]
                similarities.append((note_name, similarity))

        # Sort by similarity (highest first) and limit to top_k
        similarities.sort(key=lambda x: x[1], reverse=True)
        top_similar = similarities[:self.top_k]

        elapsed = time.time() - start_time
        print(f"  ✅ Found {len(top_similar)} similar notes in {elapsed:.1f}s")

        return top_similar

    def __del__(self):
        """Save cache on cleanup"""
        self._save_cache()


def integrate_embeddings_with_ai_analysis(
    embedding_manager: EmbeddingManager,
    current_note_path: str,
    current_note_content: str,
    all_notes: Dict[str, str],
    ai_result: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Enhance AI analysis results with embedding-based similarity

    Args:
        embedding_manager: EmbeddingManager instance
        current_note_path: Path to current note
        current_note_content: Content of current note
        all_notes: All notes in the vault
        ai_result: Result from AI analysis (from qwen2.5-coder)

    Returns:
        Enhanced AI result with embedding-based sibling notes
    """
    if not embedding_manager.enabled:
        return ai_result

    # Get embedding-based similar notes
    similar_notes = embedding_manager.find_similar_notes(
        current_note_path,
        current_note_content,
        all_notes
    )

    # Combine AI-suggested siblings with embedding-based similarity
    ai_siblings = set(ai_result.get('sibling_notes', []))
    embedding_siblings = {note for note, score in similar_notes}

    # Merge both approaches (preference to AI suggestions)
    combined_siblings = list(ai_siblings) + [
        note for note in embedding_siblings
        if note not in ai_siblings
    ]

    # Update result
    enhanced_result = ai_result.copy()
    enhanced_result['sibling_notes'] = combined_siblings[:10]  # Limit to 10
    enhanced_result['embedding_similarity_scores'] = {
        note: score for note, score in similar_notes
    }
    enhanced_result['hybrid_approach'] = True

    return enhanced_result


# Example usage
if __name__ == "__main__":
    # Test configuration
    test_config = {
        'embedding_base_url': 'http://localhost:11434',
        'embedding_model': 'nomic-embed-text:latest',
        'embedding_enabled': True,
        'embedding_similarity_threshold': 0.75,
        'embedding_top_k': 5,
        'vault_path': '/Users/medici/Documents/MediciVault'
    }

    # Create embedding manager
    manager = EmbeddingManager(test_config)

    # Test with sample texts
    text1 = "This is a note about machine learning and neural networks."
    text2 = "A discussion of deep learning architectures and AI models."
    text3 = "How to bake a chocolate cake with butter and flour."

    print("Getting embeddings...")
    emb1 = manager.get_embedding(text1, "test1.md")
    emb2 = manager.get_embedding(text2, "test2.md")
    emb3 = manager.get_embedding(text3, "test3.md")

    if emb1 and emb2 and emb3:
        print(f"\nSimilarity between ML texts: {manager.cosine_similarity(emb1, emb2):.3f}")
        print(f"Similarity between ML and cooking: {manager.cosine_similarity(emb1, emb3):.3f}")
        print(f"Similarity between AI and cooking: {manager.cosine_similarity(emb2, emb3):.3f}")
