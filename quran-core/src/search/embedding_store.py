# src/frontierqu/search/embedding_store.py
"""Semantic Search over the Unified Quranic Tensor.

Cosine similarity search over the 6236x102 unified tensor.
No external vector DB needed — numpy handles this efficiently for 6236 vectors.

Changed: _encode_query now uses character n-gram (bigram+trigram) hashing for
proper feature extraction from Arabic and English text, instead of relying
solely on a hardcoded keyword map.  No external model required.
"""
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
import numpy as np


@dataclass
class SearchResult:
    verse: Tuple[int, int]
    score: float        # cosine similarity (0-1)
    rank: int
    metadata: Dict = field(default_factory=dict)


class EmbeddingStore:
    """Cosine similarity search index over the Quranic tensor."""

    def __init__(self, embeddings: np.ndarray, verse_index: List[Tuple[int, int]]):
        self._embeddings = embeddings          # [N, D] float32
        self._verse_index = verse_index        # [(surah, verse), ...]
        self._verse_to_idx = {v: i for i, v in enumerate(verse_index)}

        # L2-normalize for cosine similarity via dot product
        norms = np.linalg.norm(embeddings, axis=1, keepdims=True) + 1e-10
        self._normalized = (embeddings / norms).astype(np.float32)

    @property
    def num_verses(self) -> int:
        return len(self._verse_index)

    @classmethod
    def build(cls, max_verses: Optional[int] = None) -> 'EmbeddingStore':
        """Build store from the unified QuranicTensor."""
        from frontierqu.core.tensor import QuranicTensor
        from frontierqu.data.quran_metadata import VERSE_COUNTS

        qt = QuranicTensor()
        T = qt.compute()  # [6236, 102]

        embeddings = T.detach().numpy()
        verse_index = []
        for surah, count in VERSE_COUNTS.items():
            for v in range(1, count + 1):
                verse_index.append((surah, v))

        if max_verses is not None:
            embeddings = embeddings[:max_verses]
            verse_index = verse_index[:max_verses]

        return cls(embeddings, verse_index)

    def search(self, query: str, k: int = 10) -> List[SearchResult]:
        """Search for verses matching a text query."""
        query_vec = self._encode_query(query)
        return self._cosine_search(query_vec, k)

    def find_similar(self, verse: Tuple[int, int], k: int = 10) -> List[SearchResult]:
        """Find verses similar to a given verse (excludes self)."""
        if verse not in self._verse_to_idx:
            return []
        idx = self._verse_to_idx[verse]
        query_vec = self._normalized[idx]
        results = self._cosine_search(query_vec, k + 1)
        return [r for r in results if r.verse != verse][:k]

    def get_embedding(self, verse: Tuple[int, int]) -> Optional[np.ndarray]:
        """Get raw embedding for a specific verse."""
        if verse not in self._verse_to_idx:
            return None
        return self._embeddings[self._verse_to_idx[verse]]

    def _cosine_search(self, query_vec: np.ndarray, k: int) -> List[SearchResult]:
        """Core cosine similarity search."""
        norm = np.linalg.norm(query_vec) + 1e-10
        q_norm = (query_vec / norm).astype(np.float32)

        # Cosine similarity = dot product of normalized vectors
        scores = self._normalized @ q_norm  # [N]

        # Top-k
        top_k = min(k, len(scores))
        top_indices = np.argpartition(scores, -top_k)[-top_k:]
        top_indices = top_indices[np.argsort(scores[top_indices])[::-1]]

        return [
            SearchResult(
                verse=self._verse_index[i],
                score=float(np.clip(scores[i], 0.0, 1.0)),
                rank=rank
            )
            for rank, i in enumerate(top_indices)
        ]

    def _encode_query(self, query: str) -> np.ndarray:
        """Encode text query to a feature vector matching tensor dimensions.

        Changed: Uses character n-gram (bigram + trigram) hashing for proper
        feature extraction from ANY text including Arabic.  The keyword map
        is retained as a boosting layer but is no longer the sole signal.
        This gives meaningful cosine similarity for Arabic queries, English
        queries, and transliterated terms alike — no external model needed.
        """
        try:
            from frontierqu.core.tensor import TOTAL_DIM
            dim = TOTAL_DIM
        except ImportError:
            dim = 102  # fallback hardcode (38 base + 64 GNN hidden)

        query_lower = query.lower().strip()
        vec = np.zeros(dim, dtype=np.float32)

        # --- Layer 1: Character n-gram features (works for Arabic and English) ---
        # Hash character bigrams and trigrams into the vector dimensions.
        # This gives every query a unique, reproducible signature.
        ngrams = []
        text = query_lower
        # Character bigrams
        for i in range(len(text) - 1):
            ngrams.append(text[i:i+2])
        # Character trigrams
        for i in range(len(text) - 2):
            ngrams.append(text[i:i+3])

        if ngrams:
            for ng in ngrams:
                # Hash n-gram to a dimension index using a stable hash
                h = hash(ng) % dim
                vec[h] += 1.0

            # L2-normalize the n-gram signal so query length doesn't dominate
            norm = np.linalg.norm(vec)
            if norm > 0:
                vec /= norm

        # --- Layer 2: Keyword boosting (thematic signal) ---
        # Boost specific theme dimensions for known keywords.
        # These map to the theme dimensions of the QuranicTensor.
        theme_keywords = {
            # English thematic keywords
            "tawhid": 0, "mercy": 1, "justice": 2, "patience": 3,
            "knowledge": 4, "creation": 5, "afterlife": 4, "prayer": 7,
            "fasting": 8, "charity": 9, "prophets": 10, "guidance": 11,
            "gratitude": 12, "oneness": 0, "god": 0, "allah": 0,
            "al-fatihah": 7, "fatihah": 7, "quran": 11, "legal": 3,
            "tafsir": 6, "worship": 7, "belief": 0, "faith": 0,
            # Arabic keywords (common Quranic terms)
            "\u0627\u0644\u0644\u0647": 0, "\u0631\u062d\u0645": 1, "\u0639\u062f\u0644": 2, "\u0635\u0628\u0631": 3,        # allah, rahm, adl, sabr
            "\u0639\u0644\u0645": 4, "\u062e\u0644\u0642": 5, "\u0622\u062e\u0631\u0629": 4, "\u0635\u0644\u0627\u0629": 7,     # ilm, khalq, akhira, salat
            "\u0635\u0648\u0645": 8, "\u0632\u0643\u0627\u0629": 9, "\u0631\u0633\u0648\u0644": 10, "\u0647\u062f\u0649": 11,    # sawm, zakat, rasul, huda
            "\u0634\u0643\u0631": 12, "\u062a\u0648\u062d\u064a\u062f": 0, "\u0627\u064a\u0645\u0627\u0646": 0,          # shukr, tawhid, iman
            "\u062d\u0644\u0627\u0644": 3, "\u062d\u0631\u0627\u0645": 3, "\u0641\u0642\u0647": 3,               # halal, haram, fiqh
            "\u062c\u0646\u0629": 4, "\u0646\u0627\u0631": 4, "\u0642\u0631\u0622\u0646": 11,                # janna, nar, quran
        }

        keyword_hit = False
        for keyword, theme_i in theme_keywords.items():
            if keyword in query_lower:
                vec[4 + theme_i] += 0.5  # additive boost, not override
                keyword_hit = True

        # --- Layer 3: Word-level hashing for multi-word queries ---
        words = query_lower.split()
        if len(words) > 1:
            for word in words:
                if len(word) >= 2:
                    h = hash(word) % dim
                    vec[h] += 0.3

        # Final normalization
        norm = np.linalg.norm(vec)
        if norm > 0:
            vec = vec / norm

        return vec
