import numpy as np
from frontierqu.geometry.fisher_metric import (
    fisher_matrix, geodesic_distance, curvature,
    TafsirDistribution, SEMANTIC_CATEGORIES
)

def test_semantic_categories_exist():
    """Tafsir semantic categories defined"""
    assert len(SEMANTIC_CATEGORIES) >= 5
    assert "legal" in SEMANTIC_CATEGORIES
    assert "theological" in SEMANTIC_CATEGORIES

def test_fisher_matrix_is_symmetric_positive():
    """Fisher matrix is symmetric positive semi-definite"""
    fm = fisher_matrix(verse=(1, 1))
    assert fm.shape[0] == fm.shape[1]
    assert np.allclose(fm, fm.T)  # Symmetric
    eigenvalues = np.linalg.eigvalsh(fm)
    assert all(ev >= -1e-10 for ev in eigenvalues)  # PSD

def test_geodesic_distance_nonnegative():
    """Geodesic distance is non-negative"""
    d = geodesic_distance((1, 1), (1, 2))
    assert d >= 0.0

def test_geodesic_distance_same_verse_is_zero():
    """Distance from verse to itself is zero"""
    d = geodesic_distance((1, 1), (1, 1))
    assert d < 1e-10

def test_curvature_returns_scalar():
    """Curvature returns a finite scalar"""
    c = curvature((1, 1))
    assert isinstance(c, float)
    assert np.isfinite(c)

def test_tafsir_distribution_sums_to_one():
    """Tafsir probability distribution sums to 1"""
    dist = TafsirDistribution.for_verse((1, 1))
    assert abs(sum(dist.probabilities.values()) - 1.0) < 1e-10
