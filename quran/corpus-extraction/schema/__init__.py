"""
Schema module for Quranic corpus extraction.

This module provides comprehensive data models and JSON schema definitions
for organizing and validating extracted Quranic verse information across
scientific domains, classical tafsirs, and verification layers.
"""

from .data_models import (
    VerseExtraction,
    TafsirEntry,
    ScientificDomainContent,
    VerificationLayer,
    CorpusExtractionResult,
)

__all__ = [
    "VerseExtraction",
    "TafsirEntry",
    "ScientificDomainContent",
    "VerificationLayer",
    "CorpusExtractionResult",
]

__version__ = "1.0.0"
__author__ = "QuranFrontier Team"
