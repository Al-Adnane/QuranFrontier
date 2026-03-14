"""Mock semantic search implementation for Phase 4 QA while Phase 3 builds embeddings.

Provides keyword-based similarity matching with mock confidence scores.
All results are marked as mock in metadata to ensure transparency.
"""
from typing import List, Dict, Any, Optional
import re
from datetime import datetime


# Mock corpus of verses for keyword matching
MOCK_VERSES_CORPUS = {
    "2:1": {"surah": 2, "ayah": 1, "text": "Alif, Laam, Meem", "keywords": ["alif", "laam", "meem", "letters", "alphabet", "sign"]},
    "2:2": {"surah": 2, "ayah": 2, "text": "This is the Book about which there is no doubt, a guidance for those conscious of Allah", "keywords": ["book", "doubt", "guidance", "god", "consciousness", "faith"]},
    "2:3": {"surah": 2, "ayah": 3, "text": "Who believe in the unseen, establish prayer, and spend out of what We have provided", "keywords": ["believe", "unseen", "faith", "prayer", "spend", "charity"]},
    "2:4": {"surah": 2, "ayah": 4, "text": "And who believe in what has been revealed to you", "keywords": ["believe", "revelation", "faith", "belief", "messenger"]},
    "2:5": {"surah": 2, "ayah": 5, "text": "Those are upon guidance from their Lord, and it is those who are the successful", "keywords": ["guidance", "lord", "success", "righteous", "prosperity"]},
    "3:1": {"surah": 3, "ayah": 1, "text": "Alif, Laam, Meem", "keywords": ["alif", "laam", "meem", "letters", "alphabet"]},
    "3:2": {"surah": 3, "ayah": 2, "text": "Allah - there is no deity except Him", "keywords": ["allah", "god", "deity", "monotheism", "oneness"]},
    "3:3": {"surah": 3, "ayah": 3, "text": "He has sent down upon you, the Book, in truth", "keywords": ["book", "revelation", "truth", "sending", "scripture"]},
    "4:1": {"surah": 4, "ayah": 1, "text": "O mankind, fear your Lord who created you from one soul", "keywords": ["mankind", "fear", "lord", "creation", "soul", "responsibility"]},
    "5:1": {"surah": 5, "ayah": 1, "text": "O you who believe, fulfill your contracts", "keywords": ["believe", "contracts", "covenant", "agreement", "fulfillment"]},
}


def _extract_keywords(text: str) -> List[str]:
    """Extract keywords from text by splitting and lowercasing."""
    # Remove punctuation and split into words
    words = re.findall(r'\b\w+\b', text.lower())
    # Filter out common stopwords
    stopwords = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'is', 'are', 'am', 'was', 'were', 'be', 'been', 'being'}
    return [w for w in words if w not in stopwords and len(w) > 2]


def _calculate_similarity(query_keywords: List[str], verse_keywords: List[str]) -> float:
    """Calculate simple keyword overlap similarity score.

    Args:
        query_keywords: Keywords from user query
        verse_keywords: Keywords from verse corpus

    Returns:
        Similarity score between 0.7 and 0.95 (clearly in mock range)
    """
    if not query_keywords or not verse_keywords:
        return 0.65

    # Count matching keywords
    matches = len(set(query_keywords) & set(verse_keywords))
    total_possible = len(set(query_keywords) | set(verse_keywords))

    if total_possible == 0:
        return 0.65

    # Map overlap ratio to mock confidence range (0.65-0.85)
    overlap_ratio = matches / total_possible
    # Scale to 0.65-0.85 range to clearly mark as mock
    base_score = 0.65 + (overlap_ratio * 0.20)
    # Add small deterministic variation based on verse ID for variety
    return min(0.85, max(0.65, base_score))


def semantic_search_mock(
    query: str,
    limit: int = 10,
    min_confidence: float = 0.5
) -> Dict[str, Any]:
    """Perform mock semantic search using keyword matching.

    This is a placeholder implementation for Phase 4 QA while real embeddings
    are being built in Phase 3. Results use keyword matching instead of
    semantic embeddings.

    Args:
        query: Search query string
        limit: Maximum number of results to return
        min_confidence: Minimum confidence threshold (0.5 for mock)

    Returns:
        Dictionary with mock search results and metadata
    """
    query_keywords = _extract_keywords(query)

    results = []
    scored_verses = []

    # Score all verses against query
    for verse_id, verse_data in MOCK_VERSES_CORPUS.items():
        similarity = _calculate_similarity(query_keywords, verse_data["keywords"])

        if similarity >= min_confidence:
            scored_verses.append({
                "verse_id": verse_id,
                "surah": verse_data["surah"],
                "ayah": verse_data["ayah"],
                "text": verse_data["text"],
                "similarity": similarity
            })

    # Sort by similarity descending and take top N
    scored_verses.sort(key=lambda x: x["similarity"], reverse=True)
    results = scored_verses[:limit]

    # If no results from keyword matching, return closest matches anyway
    if not results:
        for verse_id, verse_data in MOCK_VERSES_CORPUS.items():
            similarity = _calculate_similarity(query_keywords, verse_data["keywords"])
            results.append({
                "verse_id": verse_id,
                "surah": verse_data["surah"],
                "ayah": verse_data["ayah"],
                "text": verse_data["text"],
                "similarity": similarity
            })
        results.sort(key=lambda x: x["similarity"], reverse=True)
        results = results[:limit]

    return {
        "query": query,
        "query_keywords": query_keywords,
        "results": results,
        "result_count": len(results),
        "metadata": {
            "implementation": "mock_keyword_matching",
            "confidence_range": "0.65-0.85",
            "reason": "Real embeddings index still building in Phase 3",
            "generated_at": datetime.utcnow().isoformat(),
            "phase": "phase_4_qa_unblock"
        }
    }


def get_mock_search_metadata() -> Dict[str, Any]:
    """Get metadata describing mock search behavior.

    Returns:
        Dictionary explaining mock implementation details.
    """
    return {
        "search_type": "mock_semantic_search",
        "implementation": "keyword_matching_with_mock_confidence",
        "confidence_scores": {
            "range": "0.65-0.85",
            "meaning": "Clearly marked as mock - not real semantic similarity",
            "note": "Scores in this range indicate Phase 4 QA mode"
        },
        "corpus_size": len(MOCK_VERSES_CORPUS),
        "verses_indexed": list(MOCK_VERSES_CORPUS.keys()),
        "phase_status": {
            "phase_3": "Building real embeddings (in progress)",
            "phase_4": "QA testing with mock search (enabled)",
            "production": "Real embeddings ready (pending Phase 3)"
        },
        "transition": {
            "trigger": "FEATURE_FLAG_EMBEDDING_INDEX_READY=true",
            "effect": "Automatically switches to real embeddings"
        }
    }
