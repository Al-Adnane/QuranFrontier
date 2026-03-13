"""Tests for QuranicComplex — the holistic simplicial complex of the Quran."""

import pytest
import torch

from frontierqu.core.simplicial import QuranicComplex


@pytest.fixture(scope="module")
def qc():
    """Build the complex once for all tests in this module."""
    return QuranicComplex()


# --- Vertex tests ---


def test_complex_has_all_vertices(qc):
    assert qc.num_vertices == 6236


# --- Sequential edge tests ---


def test_sequential_edges_within_surah(qc):
    assert qc.has_edge((1, 1), (1, 2))
    assert qc.has_edge((1, 6), (1, 7))
    assert qc.has_edge((2, 1), (2, 2))
    # No "sequential" edge between last of surah 1 and first of surah 2
    edge = qc.get_edge((1, 7), (2, 1))
    if edge:
        assert "munasabat" in edge["types"]
        assert "sequential" not in edge["types"]


# --- Cross-reference edge tests ---


def test_cross_reference_edges(qc):
    # Basmala: 1:1 connects to 27:30
    assert qc.has_edge((1, 1), (27, 30))


# --- Thematic edge tests ---


def test_thematic_edges(qc):
    # Tawhid theme: 112:1 and 2:255 are both in the tawhid group
    assert qc.has_edge((112, 1), (2, 255))


# --- Munasabat edge tests ---


def test_munasabat_edges(qc):
    # Last verse of Al-Fatihah connects to first of Al-Baqarah
    assert qc.has_edge((1, 7), (2, 1))
    edge = qc.get_edge((1, 7), (2, 1))
    assert edge is not None
    assert "munasabat" in edge["types"]


# --- Edge type and weight tests ---


def test_edge_types(qc):
    edge = qc.get_edge((1, 1), (1, 2))
    assert edge is not None
    assert "sequential" in edge["types"]
    assert edge["weight"] > 0


# --- Adjacency matrix tests ---


def test_adjacency_matrix_shape(qc):
    adj = qc.adjacency_matrix()
    assert adj.is_sparse
    assert adj.shape == (6236, 6236)


def test_adjacency_matrix_symmetric(qc):
    adj = qc.adjacency_matrix().to_dense()
    assert torch.allclose(adj, adj.T)


# --- filter_by_theme tests ---


def test_filter_by_theme(qc):
    mercy = qc.filter_by_theme("mercy")
    assert mercy.num_vertices < 6236
    assert mercy.num_vertices > 0


# --- Index roundtrip tests ---


def test_vertex_index_roundtrip(qc):
    assert qc.index_to_vertex(qc.vertex_to_index((1, 1))) == (1, 1)
    assert qc.index_to_vertex(qc.vertex_to_index((114, 6))) == (114, 6)


# --- Neighbor tests ---


def test_neighbors(qc):
    n = qc.neighbors((1, 1))
    assert (1, 2) in n  # Sequential neighbor


# --- Edge count tests ---


def test_edge_count_positive(qc):
    assert qc.edge_count() > 6000  # At least sequential edges


# --- Triangle (2-simplex) tests ---


def test_triangles_exist(qc):
    triangles = qc.get_simplices(dimension=2)
    assert len(triangles) > 0


def test_thematic_triangles_contain_known_verse(qc):
    t = qc.get_simplices(dimension=2, containing=(112, 1))
    assert len(t) > 0  # Al-Ikhlas should be in tawhid triangles
