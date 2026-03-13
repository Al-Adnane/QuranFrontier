# tests/data/test_morphology_lexicon.py
from frontierqu.data.morphology_lexicon import (
    MORPHOLOGY_LEXICON, get_root_family, get_all_roots,
    lookup_word, MorphEntry
)

def test_lexicon_has_100_plus_roots():
    assert len(MORPHOLOGY_LEXICON) >= 100

def test_root_family_returns_words():
    family = get_root_family("كتب")
    assert "كتاب" in family
    assert "كاتب" in family
    assert "مكتوب" in family

def test_lookup_word_finds_root():
    entry = lookup_word("الرحمن")
    assert entry is not None
    assert entry.root == "رحم"

def test_lookup_word_strips_al():
    entry = lookup_word("المؤمنون")
    assert entry is not None

def test_morph_entry_has_all_fields():
    entry = lookup_word("كتاب")
    assert entry.root != ""
    assert entry.pattern != ""
    assert entry.pos in ("noun", "verb", "particle", "adjective")

def test_all_roots_returns_list():
    roots = get_all_roots()
    assert len(roots) >= 100
    assert "رحم" in roots
    assert "علم" in roots
    assert "قرأ" in roots
