"""Shared test fixtures for FrontierQu test suite."""

import pytest


@pytest.fixture
def al_fatihah_verses():
    """The 7 verses of Surah Al-Fatihah with Arabic text and English translations."""
    return [
        {
            "surah": 1,
            "ayah": 1,
            "arabic": "\u0628\u0650\u0633\u0652\u0645\u0650 \u0627\u0644\u0644\u0651\u064e\u0647\u0650 \u0627\u0644\u0631\u0651\u064e\u062d\u0652\u0645\u064e\u0640\u0646\u0650 \u0627\u0644\u0631\u0651\u064e\u062d\u0650\u064a\u0645\u0650",
            "translation": "In the name of Allah, the Most Gracious, the Most Merciful.",
        },
        {
            "surah": 1,
            "ayah": 2,
            "arabic": "\u0627\u0644\u0652\u062d\u064e\u0645\u0652\u062f\u064f \u0644\u0650\u0644\u0651\u064e\u0647\u0650 \u0631\u064e\u0628\u0651\u0650 \u0627\u0644\u0652\u0639\u064e\u0627\u0644\u064e\u0645\u0650\u064a\u0646\u064e",
            "translation": "All praise is due to Allah, Lord of all the worlds.",
        },
        {
            "surah": 1,
            "ayah": 3,
            "arabic": "\u0627\u0644\u0631\u0651\u064e\u062d\u0652\u0645\u064e\u0640\u0646\u0650 \u0627\u0644\u0631\u0651\u064e\u062d\u0650\u064a\u0645\u0650",
            "translation": "The Most Gracious, the Most Merciful.",
        },
        {
            "surah": 1,
            "ayah": 4,
            "arabic": "\u0645\u064e\u0627\u0644\u0650\u0643\u0650 \u064a\u064e\u0648\u0652\u0645\u0650 \u0627\u0644\u062f\u0651\u0650\u064a\u0646\u0650",
            "translation": "Master of the Day of Judgment.",
        },
        {
            "surah": 1,
            "ayah": 5,
            "arabic": "\u0625\u0650\u064a\u0651\u064e\u0627\u0643\u064e \u0646\u064e\u0639\u0652\u0628\u064f\u062f\u064f \u0648\u064e\u0625\u0650\u064a\u0651\u064e\u0627\u0643\u064e \u0646\u064e\u0633\u0652\u062a\u064e\u0639\u0650\u064a\u0646\u064f",
            "translation": "You alone we worship, and You alone we ask for help.",
        },
        {
            "surah": 1,
            "ayah": 6,
            "arabic": "\u0627\u0647\u0652\u062f\u0650\u0646\u064e\u0627 \u0627\u0644\u0635\u0651\u0650\u0631\u064e\u0627\u0637\u064e \u0627\u0644\u0652\u0645\u064f\u0633\u0652\u062a\u064e\u0642\u0650\u064a\u0645\u064e",
            "translation": "Guide us to the straight path.",
        },
        {
            "surah": 1,
            "ayah": 7,
            "arabic": "\u0635\u0650\u0631\u064e\u0627\u0637\u064e \u0627\u0644\u0651\u064e\u0630\u0650\u064a\u0646\u064e \u0623\u064e\u0646\u0652\u0639\u064e\u0645\u0652\u062a\u064e \u0639\u064e\u0644\u064e\u064a\u0652\u0647\u0650\u0645\u0652 \u063a\u064e\u064a\u0652\u0631\u0650 \u0627\u0644\u0652\u0645\u064e\u063a\u0652\u0636\u064f\u0648\u0628\u0650 \u0639\u064e\u0644\u064e\u064a\u0652\u0647\u0650\u0645\u0652 \u0648\u064e\u0644\u064e\u0627 \u0627\u0644\u0636\u0651\u064e\u0627\u0644\u0651\u0650\u064a\u0646\u064e",
            "translation": "The path of those upon whom You have bestowed favor, not of those who have earned anger nor of those who are astray.",
        },
    ]


@pytest.fixture
def sample_cross_references():
    """Known cross-references between Quranic verses.

    Each entry maps a verse (surah, ayah) to related verses with
    the type of relationship.
    """
    return [
        {
            "source": (1, 6),
            "target": (2, 142),
            "relationship": "thematic",
            "description": "Guidance to the straight path / direction of prayer",
        },
        {
            "source": (1, 7),
            "target": (2, 61),
            "relationship": "thematic",
            "description": "Those who earned anger",
        },
        {
            "source": (2, 255),
            "target": (3, 2),
            "relationship": "attribute",
            "description": "Ayat al-Kursi / divine attributes",
        },
        {
            "source": (112, 1),
            "target": (2, 163),
            "relationship": "theological",
            "description": "Oneness of Allah (Tawhid)",
        },
        {
            "source": (2, 285),
            "target": (2, 286),
            "relationship": "sequential",
            "description": "Final verses of Al-Baqarah",
        },
    ]


@pytest.fixture
def quran_metadata():
    """Load Quran metadata from the frontierqu.data module."""
    from frontierqu.data import quran_metadata as qm

    return {
        "surah_metadata": qm.SURAH_METADATA,
        "total_surahs": qm.TOTAL_SURAHS,
        "total_verses": qm.TOTAL_VERSES,
        "total_words": qm.TOTAL_WORDS,
        "total_letters": qm.TOTAL_LETTERS,
        "get_surah_metadata": qm.get_surah_metadata,
    }
