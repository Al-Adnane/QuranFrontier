from frontierqu.linguistic.sarf import (
    extract_root, extract_pattern, root_family,
    MorphologicalAnalysis, analyze_word
)

def test_extract_root_kitab():
    """كتب (k-t-b) is the root of كتاب (kitab/book)"""
    assert extract_root("كتاب") == "كتب"

def test_extract_root_alim():
    """علم (ayn-lam-mim) is the root of عالم (world/scholar)"""
    assert extract_root("عالم") == "علم"

def test_extract_pattern_kitab():
    """كتاب follows the فعال pattern"""
    assert extract_pattern("كتاب", "كتب") == "فعال"

def test_root_family():
    """All words from same root form a family"""
    family = root_family("كتب")
    assert "كتاب" in family
    assert "كاتب" in family
    assert "مكتوب" in family

def test_analyze_word_returns_full_analysis():
    result = analyze_word("بِسْمِ")
    assert isinstance(result, MorphologicalAnalysis)
    assert result.root is not None
    assert result.pos is not None

def test_trilateral_root_group_structure():
    """Trilateral roots with same pattern form algebraic groups"""
    from frontierqu.linguistic.sarf import root_pattern_group
    group = root_pattern_group("فعل")
    assert len(group) > 0
