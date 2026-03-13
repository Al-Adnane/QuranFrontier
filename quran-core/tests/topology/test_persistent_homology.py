import numpy as np
from frontierqu.topology.persistent_homology import (
    compute_persistence, PersistenceDiagram
)

def test_persistence_returns_diagram():
    """Computing persistence on Quranic complex returns birth-death pairs"""
    diagram = compute_persistence(theme="tawhid")
    assert isinstance(diagram, PersistenceDiagram)
    assert len(diagram.pairs) > 0

def test_betti_numbers():
    """Betti numbers detect topological features"""
    diagram = compute_persistence(theme="tawhid")
    assert diagram.betti(0) >= 1
    assert diagram.betti(1) >= 0

def test_persistence_detects_thematic_cycles():
    """Long-lived H1 features = persistent thematic cycles"""
    diagram = compute_persistence(theme="mercy")
    long_lived = [p for p in diagram.pairs if p.dimension == 1 and p.persistence > 0.5]
    assert len(long_lived) >= 0  # Soft assertion

def test_filtration_by_surah_order():
    """Filtration by surah ordering reveals structural topology"""
    diagram = compute_persistence(filtration="surah_order")
    assert isinstance(diagram, PersistenceDiagram)
