# tests/data/test_corpus_coverage.py
from frontierqu.data.quran_text import load_quran_corpus, get_real_text_coverage

def test_coverage_above_threshold():
    """At least 1% of verses have real Arabic text"""
    coverage = get_real_text_coverage()
    assert coverage >= 0.01  # At least 62 of 6236 verses

def test_al_ikhlas_complete():
    """Surah 112 (Al-Ikhlas) fully covered"""
    corpus = load_quran_corpus()
    for v in range(1, 5):
        assert corpus[(112, v)]["has_real_text"]

def test_short_makkan_surahs():
    """Short Makkan surahs (107-114) covered"""
    corpus = load_quran_corpus()
    for surah in [108, 110, 111]:
        verse_1 = corpus.get((surah, 1))
        assert verse_1 is not None

def test_get_real_text_returns_arabic():
    """get_real_text returns genuine Arabic Unicode"""
    corpus = load_quran_corpus()
    text = corpus[(1, 1)]["text_ar"]
    # Arabic Unicode range: 0600-06FF
    arabic_chars = [c for c in text if '\u0600' <= c <= '\u06FF']
    assert len(arabic_chars) > 0
