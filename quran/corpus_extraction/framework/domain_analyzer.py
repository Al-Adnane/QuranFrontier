"""Domain analyzer for scientific and technical concept detection in Quranic verses."""
from typing import Dict, Optional


class DomainAnalyzer:
    """Analyzes verses for scientific and technical domain concepts."""

    # Keyword mappings for each domain
    PHYSICS_KEYWORDS = {
        "sky", "heavens", "stars", "cosmos", "gravity", "water",
        "heat", "light", "motion", "layers", "expanding"
    }

    BIOLOGY_KEYWORDS = {
        "seed", "sperm", "creation stages", "growth", "creatures",
        "genetics", "immunity", "cells", "life"
    }

    MEDICINE_KEYWORDS = {
        "healing", "cure", "medicine", "remedy", "disease",
        "health", "treatment", "harm"
    }

    ENGINEERING_KEYWORDS = {
        "build", "structure", "craft", "architecture", "vessels",
        "brass", "iron", "strength"
    }

    AGRICULTURE_KEYWORDS = {
        "plants", "crops", "soil", "rain", "gardens", "trees",
        "fruits", "harvest", "vegetation"
    }

    # Principle mappings for each keyword
    PRINCIPLES_MAP = {
        # Physics
        "sky": "Celestial mechanics",
        "heavens": "Universal structure",
        "stars": "Stellar physics",
        "cosmos": "Cosmology",
        "gravity": "Gravitational forces",
        "water": "Fluid dynamics",
        "heat": "Thermodynamics",
        "light": "Optics",
        "motion": "Kinematics",
        "layers": "Stratification",
        "expanding": "Cosmic expansion",
        # Biology
        "seed": "Plant reproduction",
        "sperm": "Reproduction biology",
        "creation stages": "Developmental biology",
        "growth": "Developmental growth",
        "creatures": "Zoology",
        "genetics": "Heredity",
        "immunity": "Immunology",
        "cells": "Cell biology",
        "life": "Biology",
        # Medicine
        "healing": "Therapeutic treatment",
        "cure": "Curative medicine",
        "medicine": "Pharmacology",
        "remedy": "Therapeutic remedy",
        "disease": "Pathology",
        "health": "Preventive health",
        "treatment": "Medical treatment",
        "harm": "Toxicology",
        # Engineering
        "build": "Construction",
        "structure": "Structural engineering",
        "craft": "Craftsmanship",
        "architecture": "Architecture",
        "vessels": "Maritime engineering",
        "brass": "Metallurgy",
        "iron": "Metallurgy",
        "strength": "Materials science",
        # Agriculture
        "plants": "Botany",
        "crops": "Agronomy",
        "soil": "Soil science",
        "rain": "Precipitation",
        "gardens": "Horticulture",
        "trees": "Dendrology",
        "fruits": "Pomology",
        "harvest": "Harvesting",
        "vegetation": "Plant ecology",
    }

    def __init__(self, cache_layer=None):
        """Initialize the DomainAnalyzer.

        Args:
            cache_layer: Optional cache layer for storing analysis results.
        """
        self.cache_layer = cache_layer

    def analyze_verse(self, verse_text: str, verse_key: str) -> Dict[str, Optional[Dict]]:
        """Analyze a verse for all five scientific domains.

        Args:
            verse_text: The text of the verse to analyze.
            verse_key: The verse reference key (e.g., "1:1").

        Returns:
            Dictionary with keys for each domain, containing analysis results or None.
        """
        return {
            "physics": self._analyze_physics(verse_text, verse_key),
            "biology": self._analyze_biology(verse_text, verse_key),
            "medicine": self._analyze_medicine(verse_text, verse_key),
            "engineering": self._analyze_engineering(verse_text, verse_key),
            "agriculture": self._analyze_agriculture(verse_text, verse_key),
        }

    def _analyze_physics(self, verse_text: str, verse_key: str = "") -> Optional[Dict]:
        """Analyze verse for physics concepts.

        Args:
            verse_text: The text to analyze.
            verse_key: The verse reference key.

        Returns:
            Dictionary with analysis results or None if no physics keywords found.
        """
        return self._analyze_domain(
            verse_text, verse_key, self.PHYSICS_KEYWORDS, "physics"
        )

    def _analyze_biology(self, verse_text: str, verse_key: str = "") -> Optional[Dict]:
        """Analyze verse for biology concepts.

        Args:
            verse_text: The text to analyze.
            verse_key: The verse reference key.

        Returns:
            Dictionary with analysis results or None if no biology keywords found.
        """
        return self._analyze_domain(
            verse_text, verse_key, self.BIOLOGY_KEYWORDS, "biology"
        )

    def _analyze_medicine(self, verse_text: str, verse_key: str = "") -> Optional[Dict]:
        """Analyze verse for medicine concepts.

        Args:
            verse_text: The text to analyze.
            verse_key: The verse reference key.

        Returns:
            Dictionary with analysis results or None if no medicine keywords found.
        """
        return self._analyze_domain(
            verse_text, verse_key, self.MEDICINE_KEYWORDS, "medicine"
        )

    def _analyze_engineering(self, verse_text: str, verse_key: str = "") -> Optional[Dict]:
        """Analyze verse for engineering concepts.

        Args:
            verse_text: The text to analyze.
            verse_key: The verse reference key.

        Returns:
            Dictionary with analysis results or None if no engineering keywords found.
        """
        return self._analyze_domain(
            verse_text, verse_key, self.ENGINEERING_KEYWORDS, "engineering"
        )

    def _analyze_agriculture(self, verse_text: str, verse_key: str = "") -> Optional[Dict]:
        """Analyze verse for agriculture concepts.

        Args:
            verse_text: The text to analyze.
            verse_key: The verse reference key.

        Returns:
            Dictionary with analysis results or None if no agriculture keywords found.
        """
        return self._analyze_domain(
            verse_text, verse_key, self.AGRICULTURE_KEYWORDS, "agriculture"
        )

    def _analyze_domain(
        self,
        verse_text: str,
        verse_key: str,
        domain_keywords: set,
        domain_name: str,
    ) -> Optional[Dict]:
        """Generic domain analysis method.

        Args:
            verse_text: The text to analyze.
            verse_key: The verse reference key.
            domain_keywords: Set of keywords for this domain.
            domain_name: Name of the domain for logging.

        Returns:
            Dictionary with analysis results or None if no keywords found.
        """
        # Normalize verse text to lowercase for matching
        normalized_text = verse_text.lower()

        # Find matching concepts
        matched_keywords = []
        for keyword in domain_keywords:
            if keyword in normalized_text:
                matched_keywords.append(keyword)

        # If no keywords found, return None
        if not matched_keywords:
            return None

        # Build principles mapping from matched keywords
        principles = {}
        for keyword in matched_keywords:
            if keyword in self.PRINCIPLES_MAP:
                principles[keyword] = self.PRINCIPLES_MAP[keyword]

        # Calculate confidence score
        # Base confidence: 0.5
        # Add 0.1 per keyword (max 0.3 for 3+ keywords)
        # Add 0.2 if multiple concepts detected
        confidence = 0.5
        keyword_count = min(len(matched_keywords), 3)
        confidence += 0.1 * keyword_count

        if len(matched_keywords) > 1:
            confidence += 0.2

        # Cap confidence at 1.0
        confidence = min(confidence, 1.0)

        return {
            "concepts": matched_keywords,
            "principles": principles,
            "references": verse_key,
            "confidence": confidence,
        }
