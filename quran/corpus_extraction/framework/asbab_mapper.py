"""Asbab Al-Nuzul Mapper for revelation context mapping in Quranic verses."""
from typing import Dict, List, Optional


class AsbabAlNuzulMapper:
    """Map and extract reasons for Quranic verse revelation (Asbab Al-Nuzul)."""

    # Meccan surahs (early revelation period)
    MECCAN_SURAHS = {
        1, 6, 7, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 25, 26,
        27, 28, 29, 30, 31, 32, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45,
        46, 50, 51, 52, 53, 54, 55, 56, 62, 67, 68, 69, 70, 71, 73, 74, 75, 76,
        77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94,
        95, 96, 97, 98, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109
    }

    # Medinan surahs (later revelation period)
    MEDINAN_SURAHS = {
        2, 3, 4, 5, 8, 9, 24, 33, 47, 48, 49, 57, 58, 59, 60, 61, 62, 63, 64,
        65, 66, 99, 110
    }

    # Inquiry markers
    INQUIRY_KEYWORDS = {
        "ask", "asks", "asked", "they ask", "question", "inquire", "what about",
        "how about", "say to them", "respond"
    }

    # Event markers (battles, historical events)
    EVENT_KEYWORDS = {
        "badr", "uhud", "khandaq", "hudaybiyah", "khaybar", "hijra", "migration",
        "battle", "war", "expedition", "campaign", "when", "during", "after"
    }

    # Conflict markers
    CONFLICT_KEYWORDS = {
        "dispute", "disagree", "argument", "accuse", "slander", "those who",
        "deny", "reject", "disbelief", "conflict", "against"
    }

    # Legislative markers
    LEGISLATIVE_KEYWORDS = {
        "forbidden", "forbid", "forbidden to", "you shall", "do not", "must not",
        "establish", "law", "command", "order", "ruling", "permitted", "lawful"
    }

    # Consolation markers
    CONSOLATION_KEYWORDS = {
        "grieve", "sorrow", "despair", "patience", "endure", "trust", "believe",
        "comfort", "reassure", "do not fear", "surely", "certainly", "indeed"
    }

    # Prophet and companion names
    Islamic_FIGURES = {
        "Muhammad", "Prophet", "messenger", "Abu Bakr", "Omar", "Othman", "Ali",
        "Aisha", "Khadijah", "companions", "believers", "Muslims"
    }

    # Textual context indicators
    CONTEXT_INDICATORS = {
        "they ask you", "O you who believe", "when they see", "when they hear",
        "if you ask them", "say to them", "this is", "thus we"
    }

    def __init__(self, cache_layer=None):
        """Initialize Asbab Al-Nuzul mapper.

        Args:
            cache_layer: Optional caching layer for storing results
        """
        self.cache_layer = cache_layer

    def extract_asbab(self, surah: int, ayah: int, verse_text: str) -> Dict:
        """
        Extract asbab al-nuzul (revelation context) for a verse.

        Args:
            surah: Surah number (1-114)
            ayah: Ayah (verse) number within surah
            verse_text: The text of the verse

        Returns:
            Dictionary containing:
                - surah: Surah number
                - ayah: Ayah number
                - verse_key: "surah:ayah" format
                - occasion_type: Type of revelation occasion
                - historical_period: Meccan or Medinan
                - key_events: List of historical events mentioned
                - involved_persons: List of persons involved/mentioned
                - scholarly_consensus: Whether occasion is universally accepted
                - confidence: Confidence score (0-1)
                - source_indicators: Quranic cues suggesting context
        """
        verse_key = f"{surah}:{ayah}"

        # Determine historical period
        historical_period = self._determine_period(surah, ayah)

        # Identify occasion type
        occasion_type = self._identify_occasion_type(verse_text, surah, ayah)

        # Extract key events
        key_events = self._extract_key_events(verse_text, surah, ayah)

        # Extract involved persons
        involved_persons = self._extract_persons(verse_text)

        # Identify source indicators
        source_indicators = self._identify_source_indicators(verse_text)

        # Calculate confidence score
        confidence = self._calculate_confidence(
            verse_text, occasion_type, key_events, involved_persons
        )

        # Determine scholarly consensus
        scholarly_consensus = self._determine_scholarly_consensus(
            surah, ayah, occasion_type
        )

        return {
            "surah": surah,
            "ayah": ayah,
            "verse_key": verse_key,
            "occasion_type": occasion_type,
            "historical_period": historical_period,
            "key_events": key_events,
            "involved_persons": involved_persons,
            "scholarly_consensus": scholarly_consensus,
            "confidence": confidence,
            "source_indicators": source_indicators,
        }

    def _identify_occasion_type(self, verse_text: str, surah: int, ayah: int) -> str:
        """Identify type of revelation occasion.

        Args:
            verse_text: Text of the verse
            surah: Surah number
            ayah: Ayah number

        Returns:
            Type: 'inquiry', 'event', 'conflict', 'legislative', or 'consolation'
        """
        verse_lower = verse_text.lower()

        # Check for inquiry type
        if any(keyword in verse_lower for keyword in self.INQUIRY_KEYWORDS):
            return "inquiry"

        # Check for legislative type
        if any(keyword in verse_lower for keyword in self.LEGISLATIVE_KEYWORDS):
            return "legislative"

        # Check for consolation type
        if any(keyword in verse_lower for keyword in self.CONSOLATION_KEYWORDS):
            return "consolation"

        # Check for conflict type
        if any(keyword in verse_lower for keyword in self.CONFLICT_KEYWORDS):
            return "conflict"

        # Check for event type
        if any(keyword in verse_lower for keyword in self.EVENT_KEYWORDS):
            return "event"

        # Default to event if no clear markers
        return "event"

    def _determine_period(self, surah: int, ayah: int) -> str:
        """Determine if verse is Meccan or Medinan.

        Args:
            surah: Surah number
            ayah: Ayah number

        Returns:
            "Meccan" or "Medinan"
        """
        if surah in self.MECCAN_SURAHS:
            return "Meccan"
        elif surah in self.MEDINAN_SURAHS:
            return "Medinan"
        else:
            # Default classification for any remaining surahs
            return "Meccan" if surah < 100 else "Medinan"

    def _extract_key_events(self, verse_text: str, surah: int, ayah: int) -> List[str]:
        """Extract historical events from verse content.

        Args:
            verse_text: Text of the verse
            surah: Surah number
            ayah: Ayah number

        Returns:
            List of detected historical events
        """
        events = []
        verse_lower = verse_text.lower()

        # Map of events to their keywords
        event_keywords = {
            "Battle of Badr": ["badr"],
            "Battle of Uhud": ["uhud"],
            "Battle of Khandaq": ["khandaq", "ditch"],
            "Treaty of Hudaybiyah": ["hudaybiyah"],
            "Conquest of Khaybar": ["khaybar"],
            "Hijra (Migration)": ["hijra", "migration", "migrate"],
            "Early Islamic conflict": ["war", "battle", "conflict"],
        }

        for event_name, keywords in event_keywords.items():
            if any(keyword in verse_lower for keyword in keywords):
                events.append(event_name)

        return events

    def _extract_persons(self, verse_text: str) -> List[str]:
        """Extract names/persons mentioned in verse.

        Args:
            verse_text: Text of the verse

        Returns:
            List of detected persons
        """
        persons = []
        verse_lower = verse_text.lower()

        # Specific figure mappings
        figure_keywords = {
            "Prophet Muhammad": ["prophet", "muhammad", "messenger", "seal of prophets"],
            "Abu Bakr": ["abu bakr", "abu bakr"],
            "Omar": ["omar", "umar"],
            "Othman": ["othman", "uthman"],
            "Ali": ["ali"],
            "Companions": ["companions", "believers", "muslims"],
        }

        for figure_name, keywords in figure_keywords.items():
            if any(keyword in verse_lower for keyword in keywords):
                persons.append(figure_name)

        return persons

    def _identify_source_indicators(self, verse_text: str) -> List[str]:
        """Identify textual cues suggesting revelation context.

        Args:
            verse_text: Text of the verse

        Returns:
            List of identified source indicators
        """
        indicators = []
        verse_lower = verse_text.lower()

        # Check for direct context indicators
        for indicator in self.CONTEXT_INDICATORS:
            if indicator in verse_lower:
                indicators.append(indicator)

        # Check for general categories of indicators
        if "they ask" in verse_lower:
            indicators.append("Companion inquiry")
        if "o you who" in verse_lower:
            indicators.append("Direct address to believers")
        if "when" in verse_lower:
            indicators.append("Temporal context")
        if "say" in verse_lower:
            indicators.append("Prophet commanded to say")

        return indicators

    def _calculate_confidence(
        self, verse_text: str, occasion_type: str, key_events: List[str],
        involved_persons: List[str]
    ) -> float:
        """Calculate confidence score for asbab extraction.

        Args:
            verse_text: Text of the verse
            occasion_type: Identified occasion type
            key_events: Extracted events
            involved_persons: Extracted persons

        Returns:
            Confidence score between 0.0 and 1.0
        """
        confidence = 0.3  # Base confidence

        # Increase confidence based on detected elements
        if occasion_type != "event":  # Specific occasion types increase confidence
            confidence += 0.2

        if key_events:
            confidence += 0.2

        if involved_persons:
            confidence += 0.15

        # Check for strong contextual markers
        verse_lower = verse_text.lower()
        if "they ask you" in verse_lower or "o you who believe" in verse_lower:
            confidence += 0.15

        # Normalize to 0-1 range
        return min(confidence, 1.0)

    def _determine_scholarly_consensus(
        self, surah: int, ayah: int, occasion_type: str
    ) -> bool:
        """Determine if asbab has scholarly consensus.

        Args:
            surah: Surah number
            ayah: Ayah number
            occasion_type: Type of occasion

        Returns:
            True if occasion is universally accepted, False otherwise
        """
        # Well-known asbab with strong consensus
        consensus_asbab = {
            (2, 219): True,   # Wine and gambling inquiry
            (24, 12): True,   # Incident of the lie regarding Aisha
            (33, 37): True,   # Zayd and Zaynab marriage
            (96, 1): True,    # First revelation to read
        }

        if (surah, ayah) in consensus_asbab:
            return consensus_asbab[(surah, ayah)]

        # Inquiry occasions generally have good consensus
        if occasion_type == "inquiry":
            return True

        # Default to False for uncertain asbab
        return False
