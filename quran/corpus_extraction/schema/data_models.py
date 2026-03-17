"""
Comprehensive data models for Quranic verse extraction.

This module defines the core data structures for extracting, organizing,
and verifying Quranic content across scientific domains, classical tafsirs,
and multiple verification layers.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional


@dataclass
class VerseExtraction:
    """Complete extraction for a single verse.

    This dataclass encapsulates all information extracted from a Quranic verse,
    including verse identification, translations, scientific domain analysis,
    classical tafsir references, contextual information, and verification metadata.

    Attributes:
        surah: Surah (chapter) number (1-114)
        ayah: Verse (ayah) number within the surah
        verse_key: Unique identifier in format "surah:ayah"
        arabic_text: Original Arabic text of the verse
        translation: English translation of the verse

        physics_content: Extracted physics-related content
        biology_content: Extracted biology-related content
        medicine_content: Extracted medicine/healthcare-related content
        engineering_content: Extracted engineering-related content
        agriculture_content: Extracted agriculture-related content

        mathematics_content: Extracted mathematics-related content (Tier 1, ceiling 0.85)
        hydrology_content: Extracted hydrology-related content (Tier 1, ceiling 0.85)
        oceanography_content: Extracted oceanography-related content (Tier 1, ceiling 0.85)
        geology_content: Extracted geology-related content (Tier 2, ceiling 0.75)

        tafsirs: Dictionary mapping tafsir names to their interpretations
        tafsir_agreement: Confidence score for tafsir consensus (0.0-1.0)

        asbab_nuzul: Reasons for revelation context
        semantic_analysis: Semantic and linguistic analysis

        verification_layers: Dictionary of verification check results
        confidence_score: Overall confidence in extraction (0.0-1.0)
        source_citations: List of source materials and citations
    """

    # Verse identification
    surah: int
    ayah: int
    verse_key: str
    arabic_text: str
    translation: str

    # 9 scientific domains (5 original + 4 new from P2)
    physics_content: Optional[Dict] = None
    biology_content: Optional[Dict] = None
    medicine_content: Optional[Dict] = None
    engineering_content: Optional[Dict] = None
    agriculture_content: Optional[Dict] = None

    # 4 new scientific domains (P2)
    mathematics_content: Optional[Dict] = None     # Q4:11-12 fractions, Q18:25 calendar math
    hydrology_content: Optional[Dict] = None        # Q23:18 water cycle, Q39:21 groundwater
    oceanography_content: Optional[Dict] = None     # Q55:19-20 halocline, Q24:40 aphotic zone
    geology_content: Optional[Dict] = None          # Q31:10 isostasy, Q16:15 mountain roots

    # 8 classical tafsirs
    tafsirs: Dict[str, str] = field(default_factory=dict)
    tafsir_agreement: float = 0.0

    # Context
    asbab_nuzul: Optional[Dict] = None
    semantic_analysis: Optional[Dict] = None

    # Verification
    verification_layers: Dict[str, bool] = field(default_factory=dict)
    confidence_score: float = 0.0
    source_citations: List[Dict] = field(default_factory=list)

    def __post_init__(self):
        """Validate verse identification after initialization."""
        if not (1 <= self.surah <= 114):
            raise ValueError(f"Surah must be between 1 and 114, got {self.surah}")
        if self.ayah < 1:
            raise ValueError(f"Ayah must be positive, got {self.ayah}")
        if not self.verse_key:
            self.verse_key = f"{self.surah}:{self.ayah}"

    def get_scientific_domains(self) -> Dict[str, Optional[Dict]]:
        """Return all scientific domain extractions as a dictionary."""
        return {
            "physics": self.physics_content,
            "biology": self.biology_content,
            "medicine": self.medicine_content,
            "engineering": self.engineering_content,
            "agriculture": self.agriculture_content,
            "mathematics": self.mathematics_content,
            "hydrology": self.hydrology_content,
            "oceanography": self.oceanography_content,
            "geology": self.geology_content,
        }

    def get_all_verification_results(self) -> Dict[str, bool]:
        """Return all verification layer results."""
        return self.verification_layers.copy()

    def is_fully_verified(self) -> bool:
        """Check if all verification layers have passed."""
        return all(self.verification_layers.values()) if self.verification_layers else False

    def has_scientific_content(self) -> bool:
        """Check if extraction contains any scientific domain content."""
        domains = self.get_scientific_domains()
        return any(content is not None for content in domains.values())


@dataclass
class TafsirEntry:
    """Single tafsir interpretation reference.

    Attributes:
        name: Name of the tafsir source (e.g., "Ibn Kathir")
        text: The actual tafsir text/interpretation
        source: Source reference or URL
        category: Category of tafsir (classical, contemporary, etc.)
    """
    name: str
    text: str
    source: str
    category: str = "classical"


@dataclass
class ScientificDomainContent:
    """Scientific domain analysis for a verse.

    Attributes:
        domain_name: Name of the scientific domain
        concepts: List of identified scientific concepts
        principles: Scientific principles referenced
        applications: Practical applications mentioned
        confidence: Confidence score for domain extraction
    """
    domain_name: str
    concepts: List[str] = field(default_factory=list)
    principles: List[str] = field(default_factory=list)
    applications: List[str] = field(default_factory=list)
    confidence: float = 0.0


@dataclass
class VerificationLayer:
    """Single verification layer result.

    Attributes:
        layer_name: Name of the verification layer
        passed: Whether the verification passed
        details: Additional verification details
        timestamp: When verification was performed
    """
    layer_name: str
    passed: bool
    details: Optional[str] = None
    timestamp: Optional[str] = None


@dataclass
class CorpusExtractionResult:
    """Complete corpus extraction result for batch processing.

    Attributes:
        total_verses_processed: Total verses processed
        verses: List of extracted verse data
        extraction_metadata: Metadata about the extraction process
        errors: List of any errors encountered
        summary_statistics: Summary statistics about the extraction
    """
    total_verses_processed: int
    verses: List[VerseExtraction] = field(default_factory=list)
    extraction_metadata: Optional[Dict] = None
    errors: List[Dict] = field(default_factory=list)
    summary_statistics: Optional[Dict] = None

    def add_verse(self, verse: VerseExtraction) -> None:
        """Add an extracted verse to the result."""
        self.verses.append(verse)

    def add_error(self, error_info: Dict) -> None:
        """Add an error that occurred during extraction."""
        self.errors.append(error_info)

    def get_verses_by_surah(self, surah: int) -> List[VerseExtraction]:
        """Get all verses from a specific surah."""
        return [v for v in self.verses if v.surah == surah]

    def get_scientifically_relevant_verses(self) -> List[VerseExtraction]:
        """Get all verses with scientific domain content."""
        return [v for v in self.verses if v.has_scientific_content()]
