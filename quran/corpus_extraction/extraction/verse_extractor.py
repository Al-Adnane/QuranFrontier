"""
Verse Extractor for Phase 3 Parallel Extraction.

Extracts complete verse information using the Phase 2 VerseExtractorCoordinator.
Each verse extraction goes through 5-layer verification and includes:
- Arabic text and translation
- 5 scientific domain analyses
- 8 classical tafsirs
- Revelation context (Asbab Al-Nuzul)
- Semantic and linguistic analysis
- Multi-layer verification
"""

from typing import Optional, Dict, Any
import logging
import json

from quran.corpus_extraction.framework.verse_coordinator import VerseExtractorCoordinator
from quran.corpus_extraction.infrastructure.api_integration import ApiIntegrationLayer
from quran.corpus_extraction.infrastructure.cache_layer import CacheLayer
from quran.corpus_extraction.schema.data_models import VerseExtraction

logger = logging.getLogger(__name__)


class VerseExtractor:
    """Extract complete verse information using Phase 2 framework."""

    def __init__(self,
                 coordinator: Optional[VerseExtractorCoordinator] = None,
                 api_layer: Optional[ApiIntegrationLayer] = None,
                 cache_layer: Optional[CacheLayer] = None):
        """
        Initialize the VerseExtractor.

        Args:
            coordinator: VerseExtractorCoordinator from Phase 2
            api_layer: ApiIntegrationLayer for API calls
            cache_layer: Optional CacheLayer for caching results
        """
        self.coordinator = coordinator
        self.api = api_layer or ApiIntegrationLayer()
        self.cache = cache_layer or CacheLayer()

    def extract_verse_complete(self,
                               surah: int,
                               ayah: int) -> Optional[VerseExtraction]:
        """
        Complete extraction for a single verse using Phase 2 framework.

        Returns VerseExtraction dataclass with all fields populated.

        Args:
            surah: Surah (chapter) number (1-114)
            ayah: Verse (ayah) number within the surah

        Returns:
            VerseExtraction dataclass with all fields populated, or None if
            extraction fails

        Raises:
            ValueError: If surah/ayah are invalid
        """
        # Validate verse identification
        if not (1 <= surah <= 114):
            raise ValueError(f"Surah must be between 1 and 114, got {surah}")
        if ayah < 1:
            raise ValueError(f"Ayah must be positive, got {ayah}")

        verse_key = f"{surah}:{ayah}"
        logger.info(f"Extracting verse {verse_key}")

        # Try cache first (L1 cache for verse basics)
        cached = self.cache.get('L1', verse_key)
        if cached:
            logger.debug(f"Cache hit for {verse_key}")
            return self._dict_to_verse_extraction(cached)

        # Get verse text from API
        verse_data = self.api.get_verse_from_quran(surah, ayah)
        if not verse_data or "error" in verse_data:
            logger.error(f"Failed to fetch verse {verse_key}: {verse_data}")
            return None

        verse_text = verse_data.get("text_ar", "")
        translation = verse_data.get("translation", "")

        if not verse_text:
            logger.error(f"Empty verse text for {verse_key}")
            return None

        # Extract using Phase 2 coordinator
        try:
            extraction = self.coordinator.extract_complete_verse(
                surah=surah,
                ayah=ayah,
                verse_text=verse_text,
                tafsir_texts={}  # Tafsirs fetched by coordinator
            )

            if extraction:
                # Update translation field
                extraction.translation = translation

                # Cache the result (L1 cache for verse basics)
                self.cache.set('L1', verse_key, extraction.to_dict())

                logger.info(f"Successfully extracted {verse_key}")
                return extraction
            else:
                logger.warning(f"Coordinator returned None for {verse_key}")
                return None

        except Exception as e:
            logger.error(f"Extraction error for {verse_key}: {str(e)}")
            return None

    def extract_verse_batch(self,
                            verses: list) -> Dict[str, Optional[VerseExtraction]]:
        """
        Extract multiple verses efficiently.

        Args:
            verses: List of (surah, ayah) tuples

        Returns:
            Dictionary mapping verse_key to VerseExtraction or None
        """
        results = {}
        for surah, ayah in verses:
            verse_key = f"{surah}:{ayah}"
            try:
                extraction = self.extract_verse_complete(surah, ayah)
                results[verse_key] = extraction
            except Exception as e:
                logger.error(f"Batch extraction error for {verse_key}: {e}")
                results[verse_key] = None

        return results

    def _dict_to_verse_extraction(self, data: Dict[str, Any]) -> Optional[VerseExtraction]:
        """
        Convert dictionary to VerseExtraction dataclass.

        Args:
            data: Dictionary with verse extraction data

        Returns:
            VerseExtraction instance or None
        """
        try:
            return VerseExtraction(
                surah=data.get("surah"),
                ayah=data.get("ayah"),
                verse_key=data.get("verse_key"),
                arabic_text=data.get("arabic_text"),
                translation=data.get("translation"),
                physics_content=data.get("physics_content"),
                biology_content=data.get("biology_content"),
                medicine_content=data.get("medicine_content"),
                engineering_content=data.get("engineering_content"),
                agriculture_content=data.get("agriculture_content"),
                tafsirs=data.get("tafsirs", {}),
                tafsir_agreement=data.get("tafsir_agreement", 0.0),
                asbab_nuzul=data.get("asbab_nuzul"),
                semantic_analysis=data.get("semantic_analysis"),
                verification_layers=data.get("verification_layers", {}),
                confidence_score=data.get("confidence_score", 0.0),
                source_citations=data.get("source_citations", [])
            )
        except Exception as e:
            logger.error(f"Failed to convert dict to VerseExtraction: {e}")
            return None

    def get_api_stats(self) -> Dict[str, Any]:
        """Get API usage statistics."""
        return {
            "total_requests": self.api.get_request_count(),
            "remaining_quota": self.api.get_remaining_quota(),
            "rate_limit": self.api.rate_limit
        }
