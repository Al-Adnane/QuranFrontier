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

    # --- P2: 4 new domains ---

    # Tier 1 (confidence ceiling 0.85) — exact/demonstrable
    MATHEMATICS_KEYWORDS = {
        "fraction", "inheritance", "calculation", "ratio", "calendar",
        "lunar", "solar year", "prescribed", "shares", "portion"
    }

    # Tier 1 (confidence ceiling 0.85) — observable
    HYDROLOGY_KEYWORDS = {
        "water cycle", "rain", "clouds", "rivers", "springs",
        "groundwater", "sent down water", "stored", "measured amount"
    }

    # Tier 1 (confidence ceiling 0.85) — measurable
    OCEANOGRAPHY_KEYWORDS = {
        "two seas", "barrier", "salt water", "fresh water",
        "deep ocean", "darkness", "waves", "deep sea", "meeting"
    }

    # Tier 2 (confidence ceiling 0.75) — valid inference
    GEOLOGY_KEYWORDS = {
        "mountains", "pegs", "roots", "earth stability", "rock layers",
        "minerals", "firmly set", "anchored", "strata"
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
        # Mathematics (Tier 1, ceiling 0.85)
        "fraction": "Arithmetic fractions",
        "inheritance": "Applied mathematics — inheritance algebra",
        "calculation": "Mathematical computation",
        "ratio": "Ratio and proportion",
        "calendar": "Calendar mathematics",
        "lunar": "Lunar calendar computation",
        "solar year": "Solar calendar computation",
        "prescribed": "Prescribed fractional shares (faridah)",
        "shares": "Distribution mathematics",
        "portion": "Fractional allocation",
        # Hydrology (Tier 1, ceiling 0.85)
        "water cycle": "Hydrological cycle",
        "clouds": "Cloud formation and precipitation",
        "rivers": "Fluvial hydrology",
        "springs": "Groundwater discharge",
        "groundwater": "Hydrogeology",
        "sent down water": "Precipitation process",
        "stored": "Water storage / aquifer recharge",
        "measured amount": "Quantitative hydrology",
        # Oceanography (Tier 1, ceiling 0.85)
        "two seas": "Halocline / estuarine mixing",
        "barrier": "Oceanic density barrier",
        "salt water": "Marine salinity",
        "fresh water": "Freshwater-saltwater interface",
        "deep ocean": "Deep-sea oceanography",
        "darkness": "Aphotic zone / light attenuation",
        "waves": "Physical oceanography — wave mechanics",
        "deep sea": "Benthic oceanography",
        "meeting": "Estuarine mixing zone",
        # Geology (Tier 2, ceiling 0.75)
        "mountains": "Orography / isostasy",
        "pegs": "Mountain root isostasy",
        "roots": "Crustal root structure",
        "earth stability": "Tectonic stability",
        "rock layers": "Stratigraphy",
        "minerals": "Mineralogy",
        "firmly set": "Isostatic equilibrium",
        "anchored": "Crustal anchoring / isostasy",
        "strata": "Geological stratigraphy",
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
            # P2 new domains
            "mathematics": self._analyze_mathematics(verse_text, verse_key),
            "hydrology": self._analyze_hydrology(verse_text, verse_key),
            "oceanography": self._analyze_oceanography(verse_text, verse_key),
            "geology": self._analyze_geology(verse_text, verse_key),
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

    # --- P2: 4 new domain analyzers ---

    def _analyze_mathematics(self, verse_text: str, verse_key: str = "") -> Optional[Dict]:
        """Analyze verse for mathematics concepts (Tier 1, ceiling 0.85).

        Key verses: Q4:11-12 (prescribed inheritance fractions),
                    Q18:25 (300/309 lunar-solar calendar calculation).

        Args:
            verse_text: The text to analyze.
            verse_key: The verse reference key.

        Returns:
            Dictionary with analysis results or None if no mathematics keywords found.
        """
        return self._analyze_domain(
            verse_text, verse_key, self.MATHEMATICS_KEYWORDS, "mathematics",
            confidence_ceiling=0.85
        )

    def _analyze_hydrology(self, verse_text: str, verse_key: str = "") -> Optional[Dict]:
        """Analyze verse for hydrology concepts (Tier 1, ceiling 0.85).

        Key verses: Q23:18 (water sent down and stored in earth — hydrological cycle),
                    Q39:21 (springs/groundwater discharge).

        Args:
            verse_text: The text to analyze.
            verse_key: The verse reference key.

        Returns:
            Dictionary with analysis results or None if no hydrology keywords found.
        """
        return self._analyze_domain(
            verse_text, verse_key, self.HYDROLOGY_KEYWORDS, "hydrology",
            confidence_ceiling=0.85
        )

    def _analyze_oceanography(self, verse_text: str, verse_key: str = "") -> Optional[Dict]:
        """Analyze verse for oceanography concepts (Tier 1, ceiling 0.85).

        Key verses: Q55:19-20 (two seas meeting — halocline/estuarine mixing),
                    Q24:40 (layers of darkness in deep sea — aphotic zone).

        Args:
            verse_text: The text to analyze.
            verse_key: The verse reference key.

        Returns:
            Dictionary with analysis results or None if no oceanography keywords found.
        """
        return self._analyze_domain(
            verse_text, verse_key, self.OCEANOGRAPHY_KEYWORDS, "oceanography",
            confidence_ceiling=0.85
        )

    def _analyze_geology(self, verse_text: str, verse_key: str = "") -> Optional[Dict]:
        """Analyze verse for geology concepts (Tier 2, ceiling 0.75).

        Tier 2: valid scientific parallel but requires inference — hence lower ceiling.

        Key verses: Q31:10 (mountains as pegs — isostasy / crustal roots),
                    Q16:15 (firmly set mountains stabilizing the earth).

        Args:
            verse_text: The text to analyze.
            verse_key: The verse reference key.

        Returns:
            Dictionary with analysis results or None if no geology keywords found.
        """
        return self._analyze_domain(
            verse_text, verse_key, self.GEOLOGY_KEYWORDS, "geology",
            confidence_ceiling=0.75
        )

    def _analyze_domain(
        self,
        verse_text: str,
        verse_key: str,
        domain_keywords: set,
        domain_name: str,
        confidence_ceiling: float = 1.0,
    ) -> Optional[Dict]:
        """Generic domain analysis method.

        Args:
            verse_text: The text to analyze.
            verse_key: The verse reference key.
            domain_keywords: Set of keywords for this domain.
            domain_name: Name of the domain for logging.
            confidence_ceiling: Maximum allowed confidence for this domain tier.
                Tier 1 domains use 0.85; Tier 2 domains use 0.75.

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

        # Apply domain-specific confidence ceiling, then cap at 1.0
        confidence = min(confidence, confidence_ceiling, 1.0)

        return {
            "concepts": matched_keywords,
            "principles": principles,
            "references": verse_key,
            "confidence": confidence,
        }
