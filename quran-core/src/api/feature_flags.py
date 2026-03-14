"""Feature flag system for progressive deployment and Phase 4 unblocking."""
import os
from enum import Enum
from typing import Dict, Any
from functools import lru_cache
from datetime import datetime


class FeatureFlag(str, Enum):
    """Available feature flags."""
    SEMANTIC_SEARCH = "FEATURE_FLAG_SEMANTIC_SEARCH"
    EMBEDDING_INDEX_READY = "FEATURE_FLAG_EMBEDDING_INDEX_READY"
    PHASE_4_QA_MODE = "FEATURE_FLAG_PHASE_4_QA_MODE"


@lru_cache(maxsize=16)
def get_flag(flag: FeatureFlag) -> bool:
    """Get feature flag value from environment.

    Args:
        flag: FeatureFlag enum value

    Returns:
        Boolean flag value. Defaults to False if not set.
    """
    value = os.getenv(flag.value, "false").lower()
    return value in ("true", "1", "yes", "on")


@lru_cache(maxsize=16)
def is_semantic_search_enabled() -> bool:
    """Check if semantic search is enabled (for mock or real)."""
    return get_flag(FeatureFlag.SEMANTIC_SEARCH)


@lru_cache(maxsize=16)
def is_embedding_index_ready() -> bool:
    """Check if real embeddings index is ready for production use."""
    return get_flag(FeatureFlag.EMBEDDING_INDEX_READY)


@lru_cache(maxsize=16)
def is_phase_4_qa_enabled() -> bool:
    """Check if Phase 4 QA mode is enabled (mock semantic search for QA)."""
    return get_flag(FeatureFlag.PHASE_4_QA_MODE)


def should_use_mock_embeddings() -> bool:
    """Determine if mock embeddings should be used.

    Returns True if:
    - Semantic search is enabled AND
    - Embedding index is NOT ready (Phase 3 still processing)
    - OR Phase 4 QA mode is explicitly enabled
    """
    if is_phase_4_qa_enabled():
        return True

    if is_semantic_search_enabled() and not is_embedding_index_ready():
        return True

    return False


def should_use_real_embeddings() -> bool:
    """Determine if real embeddings should be used.

    Returns True only if:
    - Semantic search is enabled AND
    - Embedding index is ready for production
    """
    return is_semantic_search_enabled() and is_embedding_index_ready()


def get_flag_status() -> Dict[str, Any]:
    """Get current status of all feature flags.

    Returns:
        Dictionary with flag statuses and behavior implications.
    """
    return {
        "timestamp": datetime.utcnow().isoformat(),
        "flags": {
            "semantic_search": is_semantic_search_enabled(),
            "embedding_index_ready": is_embedding_index_ready(),
            "phase_4_qa_enabled": is_phase_4_qa_enabled(),
        },
        "behavior": {
            "use_mock_embeddings": should_use_mock_embeddings(),
            "use_real_embeddings": should_use_real_embeddings(),
            "phase_4_status": "enabled for QA" if is_phase_4_qa_enabled() else "blocked waiting for Phase 3",
        },
        "phase_status": {
            "phase_3_embeddings": "building" if not is_embedding_index_ready() else "ready",
            "phase_4_qa": "ready" if should_use_mock_embeddings() else "waiting",
        }
    }
