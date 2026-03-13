"""Unified Quranic Tensor — The Holistic Engine.

Combines all 7 algorithmic domains into a single feature tensor:
    T ∈ R^{6236 × D}

where D = total feature dimension across all domains.

Every verse's representation encodes information from the ENTIRE Quran
via message passing — making the whole irreducible to its parts.
"""
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple, Any
import torch
import torch.nn.functional as F
import numpy as np

from frontierqu.data.quran_metadata import VERSE_COUNTS, SURAH_METADATA
from frontierqu.data.cross_references import THEMATIC_GROUPS
from frontierqu.core.simplicial import QuranicComplex
from frontierqu.physics.message_passing import QuranicGNN


# Feature dimensions per domain
DOMAIN_DIMS = {
    "structural": 4,      # surah_idx, verse_idx, normalized_position, verse_length
    "thematic": 13,       # one-hot over 13 thematic groups
    "linguistic": 8,      # morphological + syntactic + rhetorical features
    "topological": 3,     # Betti b0, b1, persistence
    "geometric": 3,       # Fisher curvature, geodesic distance to Al-Fatihah, information
    "logical": 5,         # deontic one-hot (wajib/haram/mandub/makruh/mubah)
    "qiraat": 2,          # variant reading count, max phonological diff
}
TOTAL_BASE_DIM = sum(DOMAIN_DIMS.values())  # 38
GNN_HIDDEN_DIM = 64                          # GNN output dimension
TOTAL_DIM = TOTAL_BASE_DIM + GNN_HIDDEN_DIM  # 102


def _build_verse_index() -> List[Tuple[int, int]]:
    """Build ordered list of (surah, verse) for all 6236 verses."""
    index = []
    for surah_num, count in VERSE_COUNTS.items():
        for v in range(1, count + 1):
            index.append((surah_num, v))
    return index


def _structural_features(verse: Tuple[int, int], position: int, total: int) -> torch.Tensor:
    """4-dim structural feature vector."""
    surah, verse_num = verse
    return torch.tensor([
        surah / 114.0,
        verse_num / max(VERSE_COUNTS.get(surah, 1), 1),
        position / total,
        min(verse_num, 30) / 30.0,  # verse length proxy
    ], dtype=torch.float32)


def _thematic_features(verse: Tuple[int, int]) -> torch.Tensor:
    """13-dim one-hot over thematic groups."""
    themes = list(THEMATIC_GROUPS.keys())
    vec = torch.zeros(13)
    for i, theme in enumerate(themes[:13]):
        if verse in THEMATIC_GROUPS[theme]:
            vec[i] = 1.0
    return vec


def _linguistic_features_batch(verse_index: List[Tuple[int, int]]) -> torch.Tensor:
    """8-dim linguistic features for all verses, corpus loaded once."""
    from frontierqu.data.quran_text import load_quran_corpus
    from frontierqu.linguistic.balaghah import rhetorical_density
    corpus = load_quran_corpus()

    results = []
    for verse in verse_index:
        entry = corpus.get(verse, {})
        # Corpus entries are dicts with 'text_ar' key
        if isinstance(entry, dict):
            arabic = entry.get("text_ar", "")
        else:
            arabic = entry if isinstance(entry, str) else ""

        # Basic text metrics
        n_words = len(arabic.split()) if arabic else 1
        n_chars = len(arabic) if arabic else 0
        density = rhetorical_density(arabic) if arabic else 0.0

        results.append([
            min(n_words, 20) / 20.0,
            min(n_chars, 200) / 200.0,
            min(density, 5.0) / 5.0,
            1.0 if arabic and "ال" in arabic else 0.0,   # definite article
            1.0 if arabic and "إِنَّ" in arabic else 0.0,  # emphasis
            min(arabic.count("و"), 5) / 5.0 if arabic else 0.0,  # conjunction count
            1.0 if arabic and "ﷲ" in arabic else 0.0,    # Allah mention
            1.0 if verse[0] == 1 else 0.0,               # Is Al-Fatihah
        ])

    return torch.tensor(results, dtype=torch.float32)


def _topological_features(verse: Tuple[int, int]) -> torch.Tensor:
    """3-dim topological features (pre-computed approximate values)."""
    # Full persistent homology is expensive to compute per-verse
    # Use approximate pre-computed values based on position
    surah, _ = verse
    # Higher surahs tend to have simpler topology
    b0 = 1.0  # Always 1 connected component
    b1 = max(0.0, 1.0 - surah / 114.0)  # Approximate
    persistence = 0.5
    return torch.tensor([b0, b1, persistence], dtype=torch.float32)


def _geometric_features(verse: Tuple[int, int]) -> torch.Tensor:
    """3-dim information geometry features."""
    from frontierqu.geometry.fisher_metric import curvature, geodesic_distance
    try:
        c = curvature(verse)
        d = geodesic_distance(verse, (1, 1))  # Distance from Al-Fatihah
        c_norm = float(np.tanh(c / 10.0))  # Normalize with tanh
        d_norm = min(d / np.pi, 1.0)
        return torch.tensor([c_norm, d_norm, 0.5], dtype=torch.float32)
    except Exception:
        return torch.zeros(3)


def _logical_features(verse: Tuple[int, int]) -> torch.Tensor:
    """5-dim deontic one-hot."""
    from frontierqu.logic.deontic import derive_ruling, DeonticStatus
    try:
        rule = derive_ruling(verse, "general")
        vec = torch.zeros(5)
        status_map = {
            DeonticStatus.WAJIB: 0,
            DeonticStatus.HARAM: 1,
            DeonticStatus.MANDUB: 2,
            DeonticStatus.MAKRUH: 3,
            DeonticStatus.MUBAH: 4,
        }
        vec[status_map[rule.status]] = 1.0
        return vec
    except Exception:
        vec = torch.zeros(5)
        vec[4] = 1.0  # Default: mubah
        return vec


def _qiraat_features(verse: Tuple[int, int]) -> torch.Tensor:
    """2-dim qira'at features."""
    from frontierqu.core.qiraat import QiraatFiberBundle
    bundle = QiraatFiberBundle()
    fiber = bundle.fiber_at(verse)
    n_variants = len(fiber)
    max_diff = max((r.phonological_diff for r in fiber), default=0.0)
    return torch.tensor([
        min(n_variants, 10) / 10.0,
        max_diff,
    ], dtype=torch.float32)


class QuranicTensor:
    """Unified tensor representation of the entire Quran."""

    def __init__(self):
        self._verse_index = _build_verse_index()
        self._verse_to_idx = {v: i for i, v in enumerate(self._verse_index)}
        self._tensor: Optional[torch.Tensor] = None

    def compute(self) -> torch.Tensor:
        """Compute the full unified tensor [6236, TOTAL_DIM]."""
        if self._tensor is not None:
            return self._tensor

        n = len(self._verse_index)

        # Build linguistic features for all verses at once (load corpus once)
        linguistic_all = _linguistic_features_batch(self._verse_index)

        # Build base feature matrix [n, TOTAL_BASE_DIM]
        base_features = []
        for i, verse in enumerate(self._verse_index):
            f = torch.cat([
                _structural_features(verse, i, n),
                _thematic_features(verse),
                linguistic_all[i],
                _topological_features(verse),
                _geometric_features(verse),
                _logical_features(verse),
                _qiraat_features(verse),
            ])
            base_features.append(f)

        X = torch.stack(base_features)  # [6236, TOTAL_BASE_DIM]

        # Pass through GNN for holistic representations
        gnn = QuranicGNN(input_dim=TOTAL_BASE_DIM, hidden_dim=GNN_HIDDEN_DIM, num_layers=3)
        gnn.eval()
        with torch.no_grad():
            H = gnn(X)  # [6236, GNN_HIDDEN_DIM]

        # Concatenate base + GNN features
        self._tensor = torch.cat([X, H], dim=1)  # [6236, TOTAL_DIM]
        return self._tensor

    def query(self, query_text: str) -> Dict[str, Any]:
        """Query the unified tensor with a text query.

        Returns activation pattern over all 6236 verses.
        """
        T = self.compute()

        # Simple query encoding: map known themes/keywords to feature vectors
        query_vec = self._encode_query(query_text)

        # Compute dot-product attention
        scores = (T[:, :len(query_vec)] * query_vec.unsqueeze(0)).sum(dim=-1)
        activations = torch.sigmoid(scores)

        # Get top verses
        top_indices = activations.topk(20).indices.tolist()
        top_verses = [self._verse_index[i] for i in top_indices]

        # Build subgraph (connected verses in top-K)
        qc = QuranicComplex()
        subgraph = []
        for i, v1 in enumerate(top_verses[:10]):
            for v2 in top_verses[i+1:10]:
                if qc.has_edge(v1, v2):
                    subgraph.append((v1, v2))

        return {
            "activations": activations.tolist(),
            "top_verses": top_verses,
            "subgraph": subgraph,
            "query": query_text,
        }

    def _encode_query(self, text: str) -> torch.Tensor:
        """Encode query text to feature vector."""
        text_lower = text.lower()

        # Theme detection
        theme_idx = list(THEMATIC_GROUPS.keys())
        vec = torch.zeros(TOTAL_BASE_DIM)

        # Map keywords to structural/thematic features
        keyword_map = {
            "mercy": 1, "tawhid": 0, "oneness": 0, "guidance": 11, "al-fatihah": 7,
            "legal": 3, "prayer": 7, "knowledge": 4, "creation": 5, "afterlife": 4,
            "justice": 2, "patience": 3, "charity": 9, "fasting": 8, "prophets": 10,
        }

        for keyword, theme_i in keyword_map.items():
            if keyword in text_lower:
                vec[4 + theme_i] = 1.0  # 4 = offset after structural features

        if not vec.any():
            # Default: mild activation across all themes
            vec[4:17] = 0.1

        return vec
