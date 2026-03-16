"""
Verse Extractor Coordinator - Phase 2 Integration Framework.

Orchestrates all 5 Phase 2 framework components into a unified extraction
pipeline for a single verse. This is the final Phase 2 task that coordinates:

1. Domain Analyzer (5 scientific domains)
2. Tafsir Consolidator (8 classical scholars)
3. Asbab Al-Nuzul Mapper (revelation context)
4. Semantic Field Analyzer (lexical relationships)
5. Verification Pipeline (5-layer verification)
"""

from typing import Dict, Optional
import logging

from quran.corpus_extraction.framework.domain_analyzer import DomainAnalyzer
from quran.corpus_extraction.framework.tafsir_consolidator import TafsirConsolidator
from quran.corpus_extraction.framework.asbab_mapper import AsbabAlNuzulMapper
from quran.corpus_extraction.framework.semantic_analyzer import SemanticFieldAnalyzer
from quran.corpus_extraction.infrastructure.verification_pipeline import VerificationPipeline
from quran.corpus_extraction.schema.data_models import VerseExtraction

logger = logging.getLogger(__name__)


class VerseExtractorCoordinator:
    """
    Orchestrate extraction of all components for a single verse.

    Coordinates all 5 Phase 2 framework components to extract complete
    verse information including domain analysis, tafsir consolidation,
    revelation context, semantic analysis, and verification.
    """

    def __init__(self,
                 domain_analyzer: Optional[DomainAnalyzer] = None,
                 tafsir_consolidator: Optional[TafsirConsolidator] = None,
                 asbab_mapper: Optional[AsbabAlNuzulMapper] = None,
                 semantic_analyzer: Optional[SemanticFieldAnalyzer] = None,
                 verification_pipeline: Optional[VerificationPipeline] = None,
                 cache_layer=None):
        """
        Initialize the VerseExtractorCoordinator with all framework components.

        Args:
            domain_analyzer: DomainAnalyzer instance for 5 scientific domains.
            tafsir_consolidator: TafsirConsolidator for 8 classical scholars.
            asbab_mapper: AsbabAlNuzulMapper for revelation context.
            semantic_analyzer: SemanticFieldAnalyzer for lexical relationships.
            verification_pipeline: VerificationPipeline for 5-layer verification.
            cache_layer: Optional cache layer for storing results.
        """
        self.domain_analyzer = domain_analyzer
        self.tafsir_consolidator = tafsir_consolidator
        self.asbab_mapper = asbab_mapper
        self.semantic_analyzer = semantic_analyzer
        self.verification_pipeline = verification_pipeline
        self.cache_layer = cache_layer

    def extract_complete_verse(self,
                               surah: int,
                               ayah: int,
                               verse_text: str,
                               tafsir_texts: Dict[str, str] = None) -> VerseExtraction:
        """
        Complete extraction for single verse using all 5 domain analyzers.

        Returns VerseExtraction dataclass with ALL fields populated.

        Args:
            surah: Surah (chapter) number (1-114).
            ayah: Verse (ayah) number within the surah.
            verse_text: The Arabic text of the verse.
            tafsir_texts: Optional dictionary of tafsir names to texts.

        Returns:
            VerseExtraction dataclass with all fields populated.

        Raises:
            ValueError: If verse identification is invalid.
        """
        # Verify verse exists
        if not (1 <= surah <= 114):
            raise ValueError(f"Surah must be between 1 and 114, got {surah}")
        if ayah < 1:
            raise ValueError(f"Ayah must be positive, got {ayah}")

        # Step 1: Extract verse metadata
        metadata = self._extract_verse_metadata(surah, ayah)

        # Step 2: Run 5 domain analyses
        domain_results = self._run_domain_analyses(verse_text)

        # Step 3: Consolidate 8 tafsirs
        if tafsir_texts is None:
            tafsir_texts = {}
        tafsir_results = self._consolidate_tafsirs(surah, ayah, tafsir_texts)

        # Step 4: Get asbab al-nuzul (revelation context)
        asbab_results = self._get_asbab_context(surah, ayah, verse_text)

        # Step 5: Get semantic field analysis
        semantic_results = self._get_semantic_analysis(verse_text)

        # Step 6: Build extraction for verification
        extraction_for_verify = self._build_extraction_dict(
            metadata, domain_results, tafsir_results, asbab_results, semantic_results
        )

        # Step 7: Run 5-layer verification pipeline
        verification_results = self._verify_extraction(extraction_for_verify)

        # Step 8: Calculate overall confidence score
        overall_confidence = self._calculate_overall_confidence(
            domain_results, tafsir_results, verification_results
        )

        # Step 9: Populate VerseExtraction dataclass with all results
        verse_extraction = VerseExtraction(
            surah=surah,
            ayah=ayah,
            verse_key=metadata['verse_key'],
            arabic_text=verse_text,
            translation=metadata.get('translation', ''),
            physics_content=domain_results.get('physics'),
            biology_content=domain_results.get('biology'),
            medicine_content=domain_results.get('medicine'),
            engineering_content=domain_results.get('engineering'),
            agriculture_content=domain_results.get('agriculture'),
            tafsirs=tafsir_results.get('tafsirs', {}),
            tafsir_agreement=tafsir_results.get('consensus_confidence', 0.0),
            asbab_nuzul=asbab_results,
            semantic_analysis=semantic_results,
            verification_layers=verification_results.get('layers', {}),
            confidence_score=overall_confidence,
            source_citations=metadata.get('source_citations', [])
        )

        # Step 10: Return complete structured extraction
        return verse_extraction

    def _extract_verse_metadata(self, surah: int, ayah: int) -> Dict:
        """
        Extract basic verse identification.

        Args:
            surah: Surah number.
            ayah: Ayah number.

        Returns:
            Dictionary with verse metadata including verse_key, translation.
        """
        verse_key = f"{surah}:{ayah}"
        return {
            'verse_key': verse_key,
            'translation': '',  # Translation would come from API in production
            'source_citations': []
        }

    def _run_domain_analyses(self, verse_text: str) -> Dict:
        """
        Run all 5 scientific domain analyzers.

        Returns dictionary with physics, biology, medicine, engineering,
        and agriculture analysis results.

        Args:
            verse_text: The verse text to analyze.

        Returns:
            Dictionary with keys: physics, biology, medicine, engineering,
            agriculture. Each value is either a dict or None.
        """
        if not self.domain_analyzer:
            return {
                'physics': None,
                'biology': None,
                'medicine': None,
                'engineering': None,
                'agriculture': None
            }

        try:
            results = self.domain_analyzer.analyze_verse(verse_text, '')
            return results
        except Exception as e:
            logger.warning(f"Domain analysis error: {str(e)}")
            return {
                'physics': None,
                'biology': None,
                'medicine': None,
                'engineering': None,
                'agriculture': None
            }

    def _consolidate_tafsirs(self,
                             surah: int,
                             ayah: int,
                             tafsir_texts: Dict[str, str]) -> Dict:
        """
        Get consolidated tafsir analysis.

        Consolidates 8 classical scholars with semantic agreement matrix.

        Args:
            surah: Surah number.
            ayah: Ayah number.
            tafsir_texts: Dictionary of tafsir names to texts.

        Returns:
            Dictionary with consolidated tafsir analysis including:
            - tafsirs: Dictionary of tafsir names to texts
            - consensus_confidence: Agreement percentage
            - consensus_themes: Common themes
            - madhab_differences: School-specific interpretations
        """
        if not self.tafsir_consolidator:
            return {
                'tafsirs': tafsir_texts or {},
                'consensus_confidence': 0.0,
                'consensus_themes': [],
                'madhab_differences': {}
            }

        try:
            consolidation = self.tafsir_consolidator.consolidate_tafsirs(
                surah, ayah, tafsir_texts or {}
            )
            return {
                'tafsirs': tafsir_texts or {},
                'consensus_confidence': consolidation.get('consensus_confidence', 0.0),
                'consensus_themes': consolidation.get('consensus_themes', []),
                'madhab_differences': consolidation.get('madhab_differences', {}),
                'semantic_agreement_matrix': consolidation.get('semantic_agreement_matrix', {}),
                'key_concepts': consolidation.get('key_concepts', []),
                'tafsir_coverage': consolidation.get('tafsir_coverage', 0.0)
            }
        except Exception as e:
            logger.warning(f"Tafsir consolidation error: {str(e)}")
            return {
                'tafsirs': tafsir_texts or {},
                'consensus_confidence': 0.0,
                'consensus_themes': [],
                'madhab_differences': {}
            }

    def _get_asbab_context(self,
                           surah: int,
                           ayah: int,
                           verse_text: str) -> Optional[Dict]:
        """
        Get revelation context (Asbab Al-Nuzul).

        Maps the historical and contextual reasons for the verse's revelation.

        Args:
            surah: Surah number.
            ayah: Ayah number.
            verse_text: The verse text.

        Returns:
            Dictionary with asbab al-nuzul information or None.
        """
        if not self.asbab_mapper:
            return None

        try:
            asbab = self.asbab_mapper.extract_asbab(surah, ayah, verse_text)
            return asbab
        except Exception as e:
            logger.warning(f"Asbab extraction error: {str(e)}")
            return None

    def _get_semantic_analysis(self, verse_text: str) -> Optional[Dict]:
        """
        Get semantic field analysis.

        Analyzes lexical relationships, roots, synonyms, antonyms, and
        metaphorical expressions.

        Args:
            verse_text: The verse text.

        Returns:
            Dictionary with semantic analysis or None.
        """
        if not self.semantic_analyzer:
            return None

        try:
            semantic = self.semantic_analyzer.analyze_verse_semantics(verse_text, '')
            return semantic
        except Exception as e:
            logger.warning(f"Semantic analysis error: {str(e)}")
            return None

    def _build_extraction_dict(self,
                               metadata: Dict,
                               domain_results: Dict,
                               tafsir_results: Dict,
                               asbab_results: Optional[Dict],
                               semantic_results: Optional[Dict]) -> Dict:
        """
        Build extraction dictionary for verification pipeline.

        Args:
            metadata: Verse metadata.
            domain_results: Domain analysis results.
            tafsir_results: Tafsir consolidation results.
            asbab_results: Asbab al-nuzul results.
            semantic_results: Semantic analysis results.

        Returns:
            Dictionary with all extraction information for verification.
        """
        # Extract domain concepts
        domain_concepts = []
        for domain_name, domain_content in domain_results.items():
            if domain_content and 'concepts' in domain_content:
                domain_concepts.extend(domain_content['concepts'])

        # Build tafsir info
        tafsir_info = {
            'name': 'consolidated',
            'count': len(tafsir_results.get('tafsirs', {}))
        }

        return {
            'verse_key': metadata['verse_key'],
            'text': metadata['verse_key'],
            'tafsir': tafsir_info,
            'source_citations': metadata.get('source_citations', []),
            'domain_concepts': domain_concepts,
            'claims': []
        }

    def _verify_extraction(self, extraction: Dict) -> Dict:
        """
        Run 5-layer verification pipeline on extraction.

        Args:
            extraction: The extraction to verify.

        Returns:
            Dictionary with verification results and layers.
        """
        if not self.verification_pipeline:
            return {
                'layers': {},
                'overall_confidence': 0.0
            }

        try:
            # Add missing fields for verification
            surah_ayah = extraction['verse_key'].split(':')
            surah = int(surah_ayah[0])
            ayah = int(surah_ayah[1])

            overall_passed, verify_results = self.verification_pipeline.verify_extraction(
                surah, ayah, extraction
            )

            # Convert to layers format
            layers = {}
            for layer_name, layer_result in verify_results.items():
                if layer_name.startswith('layer_'):
                    layers[layer_name] = layer_result.get('passed', False)

            return {
                'layers': layers,
                'overall_confidence': verify_results.get('confidence_score', 0.0),
                'overall_passed': overall_passed
            }
        except Exception as e:
            logger.warning(f"Verification error: {str(e)}")
            return {
                'layers': {},
                'overall_confidence': 0.0
            }

    def _calculate_overall_confidence(self,
                                      domain_results: Dict,
                                      tafsir_results: Dict,
                                      verification_results: Dict) -> float:
        """
        Calculate overall confidence score.

        Averages: domain confidence, tafsir consensus, verification confidence.

        Args:
            domain_results: Domain analysis results.
            tafsir_results: Tafsir consolidation results.
            verification_results: Verification results.

        Returns:
            Overall confidence score (0.0-1.0).
        """
        scores = []

        # Domain confidence: average of domain confidences
        domain_confidences = []
        for domain_name, domain_content in domain_results.items():
            if domain_content and 'confidence' in domain_content:
                domain_confidences.append(domain_content['confidence'])

        if domain_confidences:
            avg_domain_confidence = sum(domain_confidences) / len(domain_confidences)
            scores.append(avg_domain_confidence)

        # Tafsir consensus
        tafsir_confidence = tafsir_results.get('consensus_confidence', 0.0)
        if tafsir_confidence > 0:
            scores.append(tafsir_confidence)

        # Verification confidence
        verify_confidence = verification_results.get('overall_confidence', 0.0)
        if verify_confidence >= 0:
            scores.append(verify_confidence)

        # Calculate average
        if scores:
            overall = sum(scores) / len(scores)
        else:
            overall = 0.0

        return min(max(overall, 0.0), 1.0)  # Clamp to 0.0-1.0
