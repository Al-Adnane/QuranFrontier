from frontierqu.logic.naskh import (
    NaskhRelation, NaskhDatabase, TemporalFormula,
    query_naskh, get_active_ruling, NaskhType
)

def test_naskh_types():
    """Three types of naskh recognized in usul al-fiqh"""
    assert hasattr(NaskhType, 'EXPLICIT')       # Naskh sarih
    assert hasattr(NaskhType, 'IMPLIED')         # Naskh dimni
    assert hasattr(NaskhType, 'PARTIAL')         # Naskh juz'i

def test_known_naskh_relations():
    """Database contains known naskh relationships"""
    db = NaskhDatabase()
    assert len(db.relations) > 0

def test_iddah_naskh():
    """2:234 abrogates 2:240 on iddah (waiting period)"""
    db = NaskhDatabase()
    result = db.query(topic="iddah")
    assert len(result) > 0
    r = result[0]
    assert r.abrogated_verse == (2, 240)
    assert r.abrogating_verse == (2, 234)

def test_qiblah_naskh():
    """2:144 abrogates 2:115 on qiblah direction"""
    db = NaskhDatabase()
    result = db.query(topic="qiblah")
    assert len(result) > 0

def test_get_active_ruling():
    """Get currently active verse for a topic after abrogation"""
    active = get_active_ruling("iddah")
    assert active is not None
    assert active == (2, 234)

def test_temporal_formula_once_valid():
    """diamond(A) = A was once valid"""
    formula = TemporalFormula.once_valid(verse=(2, 240), topic="iddah")
    assert formula.operator == "diamond"
    assert formula.was_valid is True

def test_temporal_formula_always_valid():
    """box(B) = B is always valid from now"""
    formula = TemporalFormula.always_valid(verse=(2, 234), topic="iddah")
    assert formula.operator == "box"
    assert formula.is_active is True
