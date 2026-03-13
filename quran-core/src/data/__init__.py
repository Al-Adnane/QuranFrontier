"""Quran data layer: metadata, corpus text, and cross-references."""

from frontierqu.data.quran_metadata import (
    SURAH_METADATA,
    VERSE_COUNTS,
    TOTAL_SURAHS,
    TOTAL_VERSES,
    get_surah_metadata,
    get_verse_count,
    get_total_surahs,
    get_total_verses,
)
from frontierqu.data.quran_text import load_quran_corpus
from frontierqu.data.cross_references import CROSS_REFERENCES, THEMATIC_GROUPS

__all__ = [
    "SURAH_METADATA",
    "VERSE_COUNTS",
    "TOTAL_SURAHS",
    "TOTAL_VERSES",
    "get_surah_metadata",
    "get_verse_count",
    "get_total_surahs",
    "get_total_verses",
    "load_quran_corpus",
    "CROSS_REFERENCES",
    "THEMATIC_GROUPS",
]
