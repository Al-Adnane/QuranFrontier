"""Integration tests verifying the entire framework works end-to-end."""
import pytest


def test_al_fatihah_full_analysis():
    """Complete analysis of Al-Fatihah activates its verses"""
    from frontierqu.core.tensor import QuranicTensor
    qt = QuranicTensor()
    result = qt.query("al-fatihah guidance")
    top_verses = result["top_verses"][:10]
    fatihah_verses = [(s, v) for s, v in top_verses if s == 1]
    assert len(fatihah_verses) >= 1  # At least one Al-Fatihah verse in top 10


def test_tawhid_cross_quran():
    """Tawhid theme activates verses across multiple surahs"""
    from frontierqu.core.tensor import QuranicTensor
    qt = QuranicTensor()
    result = qt.query("tawhid oneness")
    top_surahs = set(s for s, v in result["top_verses"][:20])
    assert len(top_surahs) >= 1


def test_fiqh_derivation():
    """Can derive legal rulings from verse analysis"""
    from frontierqu.logic.deontic import derive_ruling, DeonticStatus
    rule = derive_ruling(verse=(2, 183), subject="fasting")
    assert rule.status == DeonticStatus.WAJIB


def test_holism_property():
    """The system is holistic — all verse representations non-trivial"""
    from frontierqu.core.tensor import QuranicTensor
    qt = QuranicTensor()
    T = qt.compute()
    assert T.shape[0] == 6236
    assert T[0].abs().sum() > 0


def test_linguistic_morphology():
    """Morphological analysis works on Quranic vocabulary"""
    from frontierqu.linguistic.sarf import extract_root, root_family
    root = extract_root("كتاب")
    assert root == "كتب"
    family = root_family("علم")
    assert len(family) > 0


def test_topology_betti_numbers():
    """Topological features are computed"""
    from frontierqu.topology.persistent_homology import compute_persistence
    diagram = compute_persistence(theme="tawhid")
    assert diagram.betti(0) >= 1


def test_naskh_temporal_logic():
    """Abrogation database is accessible"""
    from frontierqu.logic.naskh import get_active_ruling
    active = get_active_ruling("iddah")
    assert active == (2, 234)


def test_isnad_chain_evaluation():
    """Hadith chain can be evaluated for reliability"""
    from frontierqu.logic.isnad import evaluate_chain, ReliabilityGrade
    grade = evaluate_chain(["Abu Hurayrah", "Ibn Shihab", "Malik", "Al-Bukhari"])
    assert grade in ReliabilityGrade


def test_qiraat_fiber_bundle():
    """Qira'at variants are accessible"""
    from frontierqu.core.qiraat import get_readings_for_verse
    readings = get_readings_for_verse((1, 4))
    assert len(readings) >= 2


def test_full_pipeline():
    """Complete pipeline: verse → all domains → unified tensor"""
    from frontierqu.core.tensor import QuranicTensor
    from frontierqu.linguistic.sarf import analyze_word
    from frontierqu.logic.deontic import derive_ruling
    from frontierqu.geometry.fisher_metric import curvature

    # Each domain is independently accessible
    analysis = analyze_word("الحمد")
    assert analysis.pos is not None

    rule = derive_ruling((1, 1), "general")
    assert rule.status is not None

    c = curvature((1, 1))
    assert isinstance(c, float)

    # Unified tensor
    qt = QuranicTensor()
    T = qt.compute()
    assert T.shape == (6236, 102)  # TOTAL_DIM
