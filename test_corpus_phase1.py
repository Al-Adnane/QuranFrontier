import json
import pytest


def test_merged_corpus_has_6236_verses():
    """Corpus must have exactly 6,236 Quranic verses"""
    with open('/Users/mac/Desktop/QuranFrontier/corpus/merged_corpus.json') as f:
        corpus = json.load(f)
    assert 'verses' in corpus, "Corpus missing 'verses' key"
    assert len(corpus['verses']) == 6236, f"Expected 6,236 verses, got {len(corpus['verses'])}"


def test_merged_corpus_has_114_surahs():
    """Corpus must have exactly 114 Quranic surahs"""
    with open('/Users/mac/Desktop/QuranFrontier/corpus/merged_corpus.json') as f:
        corpus = json.load(f)
    assert 'surahs' in corpus, "Corpus missing 'surahs' key"
    assert len(corpus['surahs']) == 114, f"Expected 114 surahs, got {len(corpus['surahs'])}"


def test_merged_corpus_has_tafsirs():
    """Corpus must have tafsir entries (expect ~50K)"""
    with open('/Users/mac/Desktop/QuranFrontier/corpus/merged_corpus.json') as f:
        corpus = json.load(f)
    assert 'tafsirs' in corpus, "Corpus missing 'tafsirs' key"
    tafsir_count = len(corpus['tafsirs'])
    assert tafsir_count > 40000, f"Expected 40K+ tafsirs, got {tafsir_count}"


def test_merged_corpus_has_hadiths():
    """Corpus must have hadith entries (expect ~30K)"""
    with open('/Users/mac/Desktop/QuranFrontier/corpus/merged_corpus.json') as f:
        corpus = json.load(f)
    assert 'hadiths' in corpus, "Corpus missing 'hadiths' key"
    hadith_count = len(corpus['hadiths'])
    assert hadith_count > 25000, f"Expected 25K+ hadiths, got {hadith_count}"


def test_corpus_json_valid():
    """Corpus JSON must be valid"""
    with open('/Users/mac/Desktop/QuranFrontier/corpus/merged_corpus.json') as f:
        corpus = json.load(f)
    assert isinstance(corpus, dict), "Corpus must be a dictionary"


def test_corpus_utf8_encoded():
    """Corpus must be valid UTF-8"""
    with open('/Users/mac/Desktop/QuranFrontier/corpus/merged_corpus.json', encoding='utf-8') as f:
        content = f.read()
    assert len(content) > 0, "Corpus file is empty"


def test_validation_report_exists():
    """Validation report must exist and confirm corpus integrity"""
    with open('/Users/mac/Desktop/QuranFrontier/corpus/validation_report.json') as f:
        report = json.load(f)
    assert report.get('status') == 'valid', "Validation report must show status=valid"
    assert report.get('verses_count') == 6236, "Validation report must list 6,236 verses"
