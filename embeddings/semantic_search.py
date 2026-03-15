#!/usr/bin/env python3
"""
Semantic Search API for Islamic Corpus Embeddings

Provides query-based semantic search across Quran, tafsir, and hadith using
pre-computed AraBERT embeddings. Supports cosine similarity matching with
configurable thresholds.
"""

import json
import numpy as np
from pathlib import Path
from typing import List, Dict, Tuple, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SemanticSearchEngine:
    """Semantic search over Islamic corpus embeddings."""

    def __init__(self, embedding_dir: Path = None):
        """
        Initialize search engine.

        Args:
            embedding_dir: Directory containing embedding JSON files
        """
        if embedding_dir is None:
            embedding_dir = Path(__file__).parent

        self.embedding_dir = Path(embedding_dir)
        self.embeddings = {}
        self.metadata = {}
        self.model_name = None

        # Load embeddings
        self._load_embeddings()

    def _load_embeddings(self):
        """Load embeddings from JSON files."""
        logger.info(f"Loading embeddings from {self.embedding_dir}")

        for corpus_type in ['quran', 'tafsir', 'hadith']:
            filepath = self.embedding_dir / f'vectors_{corpus_type}.json'

            if filepath.exists():
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                # Convert to numpy arrays
                self.embeddings[corpus_type] = np.array([
                    e['vector'] for e in data['embeddings']
                ])

                self.metadata[corpus_type] = data['metadata']

                logger.info(
                    f"Loaded {len(self.embeddings[corpus_type])} {corpus_type} embeddings"
                )

                # Extract model info
                if 'statistics' in data and 'model_name' in data['statistics']:
                    self.model_name = data['statistics']['model_name']

    def search(self, query_embedding: List[float],
               corpus_types: List[str] = None,
               top_k: int = 10,
               threshold: float = 0.7) -> Dict:
        """
        Search for similar items using cosine similarity.

        Args:
            query_embedding: Query embedding vector (768-dim)
            corpus_types: Corpus types to search ('quran', 'tafsir', 'hadith')
            top_k: Number of results to return
            threshold: Minimum cosine similarity threshold

        Returns:
            Dict with search results and statistics
        """
        if corpus_types is None:
            corpus_types = ['quran', 'tafsir', 'hadith']

        # Validate query embedding
        if len(query_embedding) != 768:
            return {'error': f'Query embedding must be 768-dim, got {len(query_embedding)}'}

        # Normalize query embedding
        query_norm = np.array(query_embedding)
        query_norm = query_norm / (np.linalg.norm(query_norm) + 1e-8)

        results = []

        for corpus_type in corpus_types:
            if corpus_type not in self.embeddings:
                continue

            # Compute cosine similarities
            corpus_embeddings = self.embeddings[corpus_type]
            similarities = np.dot(corpus_embeddings, query_norm)

            # Filter by threshold
            above_threshold = np.where(similarities >= threshold)[0]

            # Sort and get top_k
            top_indices = np.argsort(similarities[above_threshold])[::-1][:top_k]

            for rank, idx in enumerate(top_indices, 1):
                actual_idx = above_threshold[idx]
                similarity = float(similarities[actual_idx])

                results.append({
                    'rank': rank,
                    'corpus_type': corpus_type,
                    'index': int(actual_idx),
                    'similarity_score': similarity,
                    'metadata': self.metadata[corpus_type][actual_idx]
                })

        # Sort all results by similarity
        results = sorted(results, key=lambda x: x['similarity_score'], reverse=True)[:top_k]

        return {
            'query_embedding_dim': len(query_embedding),
            'num_results': len(results),
            'threshold': threshold,
            'results': results,
            'search_metadata': {
                'corpus_types_searched': corpus_types,
                'model': self.model_name,
                'total_embeddings': sum(
                    len(self.embeddings.get(t, [])) for t in corpus_types
                )
            }
        }

    def batch_search(self, query_embeddings: List[List[float]],
                    corpus_types: List[str] = None,
                    top_k: int = 10,
                    threshold: float = 0.7) -> List[Dict]:
        """
        Batch search for multiple queries.

        Args:
            query_embeddings: List of query embeddings
            corpus_types: Corpus types to search
            top_k: Number of results per query
            threshold: Minimum similarity threshold

        Returns:
            List of search results
        """
        batch_results = []

        for i, query_emb in enumerate(query_embeddings):
            result = self.search(query_emb, corpus_types, top_k, threshold)
            result['query_index'] = i
            batch_results.append(result)

        return batch_results

    def get_statistics(self) -> Dict:
        """Get overall statistics about loaded embeddings."""
        stats = {
            'total_embeddings': sum(len(e) for e in self.embeddings.values()),
            'embedding_dimension': 768,
            'corpus_breakdown': {}
        }

        for corpus_type in ['quran', 'tafsir', 'hadith']:
            if corpus_type in self.embeddings:
                stats['corpus_breakdown'][corpus_type] = {
                    'count': len(self.embeddings[corpus_type]),
                    'metadata_keys': list(self.metadata[corpus_type][0].keys())
                    if self.metadata[corpus_type] else []
                }

        return stats


class QueryEmbedder:
    """Generate embeddings for search queries."""

    def __init__(self, model_name: str = "aubmindlab/bert-base-arabertv2"):
        """
        Initialize query embedder.

        Args:
            model_name: HuggingFace model identifier
        """
        self.model_name = model_name
        self.tokenizer = None
        self.model = None

    def load_model(self):
        """Load tokenizer and model."""
        try:
            from transformers import AutoTokenizer, AutoModel
            import torch

            logger.info(f"Loading model: {self.model_name}")
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
            self.model = AutoModel.from_pretrained(self.model_name).to(self.device)
            self.model.eval()
        except ImportError:
            logger.error("PyTorch and Transformers required for query embedding")
            raise

    def embed_query(self, query_text: str) -> List[float]:
        """
        Generate embedding for a query text.

        Args:
            query_text: Query text in Arabic

        Returns:
            768-dimensional embedding
        """
        if self.model is None:
            self.load_model()

        import torch

        with torch.no_grad():
            inputs = self.tokenizer(
                query_text,
                max_length=512,
                padding=True,
                truncation=True,
                return_tensors='pt'
            )

            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            outputs = self.model(**inputs)

            # Use CLS token embedding
            cls_embedding = outputs.last_hidden_state[:, 0, :].cpu().numpy()[0]

            # Normalize
            cls_embedding = cls_embedding / (np.linalg.norm(cls_embedding) + 1e-8)

        return cls_embedding.tolist()

    def embed_batch(self, query_texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple queries.

        Args:
            query_texts: List of query texts

        Returns:
            List of embeddings
        """
        embeddings = []

        for query_text in query_texts:
            embedding = self.embed_query(query_text)
            embeddings.append(embedding)

        return embeddings


def example_usage():
    """Example usage of semantic search."""
    # Load embeddings
    search_engine = SemanticSearchEngine()

    # Print statistics
    stats = search_engine.get_statistics()
    print("\nEmbedding Statistics:")
    print(f"  Total embeddings: {stats['total_embeddings']}")
    print(f"  Embedding dimension: {stats['embedding_dimension']}")
    print("  Corpus breakdown:")
    for corpus_type, corpus_stats in stats['corpus_breakdown'].items():
        print(f"    - {corpus_type}: {corpus_stats['count']} embeddings")

    # Example search (requires query embeddings)
    print("\nExample: To perform semantic search:")
    print("  1. Generate query embedding using QueryEmbedder")
    print("  2. Call search_engine.search(query_embedding)")
    print("  3. Retrieve similar verses/tafsir/hadith")

    # Example with mock embedding
    print("\nDemo with mock query embedding:")
    mock_query = np.random.randn(768)
    mock_query = mock_query / np.linalg.norm(mock_query)

    results = search_engine.search(
        mock_query.tolist(),
        corpus_types=['quran'],
        top_k=3,
        threshold=0.5
    )

    print(f"  Found {results['num_results']} results")
    if results['num_results'] > 0:
        print(f"  Top result similarity: {results['results'][0]['similarity_score']:.4f}")


if __name__ == '__main__':
    example_usage()
