"""
Test suite for Arabic text normalization

Verifies:
- Unicode NFC normalization correctness
- Diacritics removal accuracy
- Verse reference resolution
- Text integrity (zero text loss)
- Encoding safety
"""

import json
import unicodedata
import re
from pathlib import Path
from arabic_text_normalizer import ArabicTextNormalizer, DIACRITICS_PATTERN


def test_nfc_normalization():
    """Test NFC normalization consistency"""
    normalizer = ArabicTextNormalizer()
    
    # Test with NFD (decomposed) text
    nfd_text = "بِسْمِ"  # NFD form
    nfc_text = normalizer.normalize_text(nfd_text)
    
    # Verify it's in NFC form
    assert unicodedata.is_normalized('NFC', nfc_text), "Text should be NFC normalized"
    print("✓ NFC normalization test passed")


def test_diacritics_removal():
    """Test diacritics removal without text loss"""
    normalizer = ArabicTextNormalizer()
    
    # Test with diacritical text
    text_with_diacritics = "قَالَ رَسُولُ اللَّهِ"
    text_without_diacritics = normalizer.remove_diacritics(text_with_diacritics)
    
    # Verify diacritics are removed
    assert not re.search(DIACRITICS_PATTERN, text_without_diacritics), "No diacritics should remain"
    
    # Verify core text preserved
    assert "قال" in text_without_diacritics or "قال" == text_without_diacritics.replace(" ", ""), "Core text should be preserved"
    print("✓ Diacritics removal test passed")


def test_verse_reference_resolution():
    """Test verse reference parsing"""
    normalizer = ArabicTextNormalizer()
    
    test_cases = [
        ("Sura 2, Verse 183", "QURAN_2_183"),
        ("surah 112:1", "QURAN_112_1"),
        ("القرآن 36:1", "QURAN_36_1"),
        ("Chapter 1, V. 1", "QURAN_1_1"),
    ]
    
    for text, expected in test_cases:
        result = normalizer.resolve_verse_reference(text)
        assert result == expected, f"Expected {expected}, got {result}"
    
    print("✓ Verse reference resolution test passed")


def test_text_integrity():
    """Verify zero text loss during normalization"""
    normalizer = ArabicTextNormalizer()
    
    test_texts = [
        "الحمد لله رب العالمين",
        "قَالَ رَسُولُ اللَّهِ صَلَّى اللَّهُ عَلَيْهِ وَسَلَّمَ",
        "يس والقرآن الحكيم",
    ]
    
    for text in test_texts:
        normalized = normalizer.normalize_text(text)
        without_diacritics = normalizer.remove_diacritics(normalized)
        
        # Remove diacritics from original
        original_clean = re.sub(DIACRITICS_PATTERN, '', text)
        
        # Check preservation
        assert original_clean == without_diacritics, f"Text not preserved: {original_clean} != {without_diacritics}"
    
    print("✓ Text integrity test passed")


def test_output_files():
    """Verify output files exist and are valid JSON"""
    output_dir = Path("/Users/mac/Desktop/QuranFrontier/normalized_data")
    
    expected_files = [
        "normalized_quran.json",
        "normalized_quran_searchable.json",
        "normalized_tafsir.json",
        "normalized_hadith.json",
        "normalization_report.json",
    ]
    
    for file in expected_files:
        filepath = output_dir / file
        assert filepath.exists(), f"Output file {file} not found"
        
        # Verify valid JSON
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            assert data is not None, f"{file} contains no data"
            print(f"✓ {file} verified ({len(json.dumps(data))} bytes)")
        except json.JSONDecodeError as e:
            raise AssertionError(f"{file} is not valid JSON: {e}")


def test_quran_verse_counts():
    """Verify Quran has all 6236 verses"""
    with open("/Users/mac/Desktop/QuranFrontier/normalized_data/normalized_quran.json", 'r', encoding='utf-8') as f:
        quran_data = json.load(f)
    
    assert len(quran_data) == 6236, f"Expected 6236 verses, got {len(quran_data)}"
    
    # Verify verse numbering
    verse_keys = set()
    for verse in quran_data:
        key = (verse["surah"], verse["verse"])
        verse_keys.add(key)
    
    # Check a few key verses
    assert (1, 1) in verse_keys, "Surah 1 Verse 1 missing"
    assert (2, 183) in verse_keys, "Surah 2 Verse 183 missing"
    assert (114, 6) in verse_keys, "Surah 114 Verse 6 missing"
    
    print(f"✓ Quran verse count test passed (6236 verses verified)")


def test_diacritics_detection():
    """Test diacritics detection accuracy"""
    normalizer = ArabicTextNormalizer()
    
    # Text with diacritics
    text_with = "قَالَ رَسُولُ"
    assert normalizer.has_diacritics(text_with), "Should detect diacritics"
    
    # Text without diacritics
    text_without = "قال رسول"
    assert not normalizer.has_diacritics(text_without), "Should not detect diacritics"
    
    print("✓ Diacritics detection test passed")


def test_encoding_safety():
    """Verify UTF-8 encoding safety"""
    with open("/Users/mac/Desktop/QuranFrontier/normalized_data/normalized_quran.json", 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Should not contain replacement character
    assert '\ufffd' not in content, "Replacement character found in output"
    
    # Should be valid UTF-8
    try:
        content.encode('utf-8')
        print("✓ Encoding safety test passed")
    except UnicodeEncodeError as e:
        raise AssertionError(f"UTF-8 encoding error: {e}")


def run_all_tests():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("Running Normalization Test Suite")
    print("=" * 60 + "\n")
    
    tests = [
        test_nfc_normalization,
        test_diacritics_removal,
        test_verse_reference_resolution,
        test_text_integrity,
        test_diacritics_detection,
        test_output_files,
        test_quran_verse_counts,
        test_encoding_safety,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"✗ {test.__name__} FAILED: {e}")
            failed += 1
        except Exception as e:
            print(f"✗ {test.__name__} ERROR: {e}")
            failed += 1
    
    print("\n" + "=" * 60)
    print(f"Tests: {passed} passed, {failed} failed")
    print("=" * 60 + "\n")
    
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)
