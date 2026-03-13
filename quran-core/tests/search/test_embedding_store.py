# tests/search/test_embedding_store.py
import numpy as np
from frontierqu.search.embedding_store import EmbeddingStore, SearchResult

def test_store_builds_from_tensor():
    """EmbeddingStore indexes the unified tensor"""
    store = EmbeddingStore.build(max_verses=50)
    assert store.num_verses == 50

def test_search_returns_results():
    """Search returns top-k results"""
    store = EmbeddingStore.build(max_verses=50)
    results = store.search("mercy", k=5)
    assert len(results) == 5
    assert all(isinstance(r, SearchResult) for r in results)

def test_search_result_has_fields():
    """SearchResult has verse, score, rank"""
    store = EmbeddingStore.build(max_verses=50)
    results = store.search("tawhid", k=3)
    for r in results:
        assert isinstance(r.verse, tuple)
        assert len(r.verse) == 2
        assert 0.0 <= r.score <= 1.0
        assert r.rank >= 0

def test_scores_are_ordered():
    """Results are returned in descending score order"""
    store = EmbeddingStore.build(max_verses=50)
    results = store.search("guidance", k=5)
    scores = [r.score for r in results]
    assert scores == sorted(scores, reverse=True)

def test_verse_lookup():
    """Can retrieve embedding for specific verse"""
    store = EmbeddingStore.build(max_verses=50)
    emb = store.get_embedding((1, 1))
    assert emb is not None
    assert len(emb) > 0

def test_similar_verses():
    """Find verses similar to a given verse"""
    store = EmbeddingStore.build(max_verses=100)
    similar = store.find_similar((1, 1), k=5)
    assert len(similar) <= 5
    # Verse 1:1 should not be in the results (self excluded)
    verses = [r.verse for r in similar]
    assert (1, 1) not in verses
