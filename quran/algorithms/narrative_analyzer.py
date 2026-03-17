"""
Algorithm 2: Narrative Structure and Story Arc

Analyzes Quranic surahs for narrative structure by:
1. Segmenting surahs into scenes using structural signals
2. Extracting characters (prophets/figures) referenced in each scene
3. Classifying story arc type (MONOMYTH, REDEMPTION, REVELATION, etc.)
4. Tracking theme saturation across scenes
5. Extracting the central theological/moral lesson
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Tuple
from enum import Enum
import json
import re
from pathlib import Path


class ConflictType(Enum):
    INTERNAL = "nafs_struggle"
    EXTERNAL = "antagonist"
    COSMIC = "divine_will"
    MORAL = "ethical_dilemma"
    NONE = "no_conflict"


class StoryArcType(Enum):
    MONOMYTH = "hero_journey"
    TRAGEDY = "fall_from_grace"
    REDEMPTION = "transformation"
    QUEST = "journey_to_goal"
    REVELATION = "divine_disclosure"
    DIDACTIC = "teaching_parable"


@dataclass
class Scene:
    number: int
    verse_range: Tuple[int, int]  # (start_ayah, end_ayah)
    text: str  # combined translation text
    characters: Set[str]
    conflict: ConflictType
    moral_weight: float  # 0-1
    themes: List[str]


@dataclass
class NarrativeStructure:
    surah_number: int
    surah_name: str
    arc_type: StoryArcType
    scenes: List[Scene]
    primary_themes: List[str]
    central_lesson: str
    character_appearances: Dict[str, List[int]]  # char -> scene numbers
    arc_intensity: float  # 0-1


class QuranicNarrativeAnalyzer:
    # Known Quranic narrative surahs (number -> name, main story)
    NARRATIVE_SURAHS = {
        12: ("Yusuf", "story_of_joseph"),
        28: ("Al-Qasas", "story_of_moses"),
        18: ("Al-Kahf", "companions_of_cave"),
        27: ("An-Naml", "solomon_sheba"),
        19: ("Maryam", "mary_zachariah"),
        20: ("Ta-Ha", "moses_pharaoh"),
        11: ("Hud", "multiple_prophets"),
        7: ("Al-Araf", "multiple_prophets"),
    }

    # Character name patterns in English translations
    CHARACTER_PATTERNS = {
        "Moses": ["Moses", "Musa"],
        "Joseph": ["Joseph", "Yusuf"],
        "Abraham": ["Abraham", "Ibrahim"],
        "Jesus": ["Jesus", "Isa"],
        "Mary": ["Mary", "Maryam"],
        "Noah": ["Noah", "Nuh"],
        "Solomon": ["Solomon", "Sulayman"],
        "David": ["David", "Dawud"],
        "Pharaoh": ["Pharaoh", "Fir'awn"],
        "Adam": ["Adam"],
        "Satan": ["Satan", "Iblis", "Shaytan"],
        "Gabriel": ["Gabriel", "Jibreel"],
    }

    # Theme keyword patterns in translations
    THEME_KEYWORDS = {
        "patience": ["patient", "patience", "persevere", "endure"],
        "gratitude": ["grateful", "gratitude", "thankful", "thank"],
        "guidance": ["guide", "guidance", "path", "way", "straight"],
        "justice": ["justice", "just", "judge", "fair", "right"],
        "mercy": ["mercy", "merciful", "compassion", "kind"],
        "trust_in_god": ["trust", "reliance", "tawakkul", "rely on Allah"],
        "repentance": ["repent", "forgive", "return", "turn back"],
        "divine_power": ["power", "might", "capable", "omnipotent"],
        "prophecy": ["prophet", "messenger", "revelation", "message"],
        "trial": ["test", "trial", "affliction", "hardship"],
    }

    # Conflict signal words in translations
    CONFLICT_SIGNALS = {
        ConflictType.INTERNAL: ["tempt", "desire", "soul", "nafs", "struggle within"],
        ConflictType.EXTERNAL: ["refuse", "oppose", "deny", "reject", "enemy"],
        ConflictType.COSMIC: ["Allah said", "We commanded", "decree", "divine"],
        ConflictType.MORAL: ["should", "ought", "forbidden", "permitted", "halal", "haram"],
    }

    # Scene break trigger phrases (ordered by specificity, most specific first)
    SCENE_BREAK_PATTERNS = [
        r"\bAnd remember when\b",
        r"\bAnd when\b",
        r"\bRemember when\b",
        r"\bAnd We said\b",
        r"\bHe said\b",
        r"\bThey said\b",
        r"\bShe said\b",
        r"\bThen\b",
        r"\bWhen\b",
        r"\bAfter\b",
    ]

    def __init__(self, corpus_path: Optional[str] = None):
        self.corpus: Dict[int, List[Tuple[int, str]]] = {}  # surah_number -> list of (ayah, text)
        if corpus_path:
            self._load_corpus(corpus_path)

    def _load_corpus(self, path: str) -> None:
        """Load and index corpus by surah number."""
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Support both {"verses": [...]} and flat list formats
        if isinstance(data, list):
            verses = data
        elif isinstance(data, dict) and "verses" in data:
            verses = data["verses"]
        else:
            verses = []

        for verse in verses:
            # Handle verse_key like "12:5" or separate surah/ayah fields
            if "verse_key" in verse:
                parts = verse["verse_key"].split(":")
                surah = int(parts[0])
                ayah = int(parts[1])
            elif "surah" in verse and "ayah" in verse:
                surah = int(verse["surah"])
                ayah = int(verse["ayah"])
            else:
                continue

            translation = verse.get("translation", "")
            if surah not in self.corpus:
                self.corpus[surah] = []
            self.corpus[surah].append((ayah, translation))

        # Sort each surah's verses by ayah number
        for surah in self.corpus:
            self.corpus[surah].sort(key=lambda x: x[0])

    def segment_into_scenes(self, verses: List[Tuple[int, str]]) -> List[Scene]:
        """
        Segment verse list into narrative scenes.

        Scene breaks occur at:
        - Verse transitions with temporal markers ("Then", "When", "After")
        - Character changes (new character introduced)
        - Dialogue boundaries (quote starts/ends)
        - Explicit breaks ("And remember when...")

        Minimum scene size: 2 verses. Returns list of Scene objects.
        """
        if not verses:
            return []

        # Compile all break patterns
        combined_pattern = re.compile(
            "|".join(self.SCENE_BREAK_PATTERNS), re.IGNORECASE
        )

        # Identify verse indices that start a new scene
        scene_start_indices = [0]
        for i in range(1, len(verses)):
            ayah, text = verses[i]
            # Check if this verse starts with a scene-break marker
            stripped = text.strip()
            if combined_pattern.match(stripped):
                # Only break if the current scene already has >= 2 verses
                if i - scene_start_indices[-1] >= 2:
                    scene_start_indices.append(i)

        # Build scenes from the identified boundaries
        scenes: List[Scene] = []
        boundaries = scene_start_indices + [len(verses)]

        for scene_idx, (start, end) in enumerate(
            zip(boundaries[:-1], boundaries[1:]), start=1
        ):
            scene_verses = verses[start:end]
            combined_text = " ".join(t for _, t in scene_verses)
            start_ayah = scene_verses[0][0]
            end_ayah = scene_verses[-1][0]

            characters = self.extract_characters(combined_text)
            conflict = self.detect_conflict(combined_text)
            themes = self.extract_themes(combined_text)
            moral_weight = self.calculate_moral_weight(
                combined_text, scene_idx, len(boundaries) - 1
            )

            scenes.append(
                Scene(
                    number=scene_idx,
                    verse_range=(start_ayah, end_ayah),
                    text=combined_text,
                    characters=characters,
                    conflict=conflict,
                    moral_weight=moral_weight,
                    themes=themes,
                )
            )

        return scenes

    def extract_characters(self, text: str) -> Set[str]:
        """Extract Quranic character names from translation text."""
        found: Set[str] = set()
        for character, patterns in self.CHARACTER_PATTERNS.items():
            for pattern in patterns:
                # Word-boundary match, case-insensitive
                if re.search(r"\b" + re.escape(pattern) + r"\b", text, re.IGNORECASE):
                    found.add(character)
                    break  # No need to check other patterns for same character
        return found

    def detect_conflict(self, text: str) -> ConflictType:
        """Detect primary conflict type from scene text."""
        scores: Dict[ConflictType, int] = {ct: 0 for ct in ConflictType}

        text_lower = text.lower()
        for conflict_type, signals in self.CONFLICT_SIGNALS.items():
            for signal in signals:
                if signal.lower() in text_lower:
                    scores[conflict_type] += 1

        # Return the highest-scoring conflict type; NONE if no signals found
        best = max(scores, key=lambda ct: scores[ct])
        if scores[best] == 0:
            return ConflictType.NONE
        return best

    def extract_themes(self, text: str) -> List[str]:
        """Extract themes present in scene text."""
        found: List[str] = []
        text_lower = text.lower()
        for theme, keywords in self.THEME_KEYWORDS.items():
            for keyword in keywords:
                if keyword.lower() in text_lower:
                    found.append(theme)
                    break  # Only add theme once
        return found

    def calculate_moral_weight(
        self, scene_text: str, scene_number: int, total_scenes: int
    ) -> float:
        """
        Scenes near the climax (middle-to-end) have higher moral weight.
        Also weight scenes with explicit lesson language higher.
        """
        if total_scenes == 0:
            return 0.5

        # Position weight: peaks at 2/3 through the narrative
        position_ratio = scene_number / total_scenes
        # Bell-curve-ish peak near 0.67
        position_weight = 1.0 - abs(position_ratio - 0.67) * 1.5
        position_weight = max(0.1, min(1.0, position_weight))

        # Lesson-language bonus
        lesson_keywords = [
            "indeed", "verily", "truly", "therefore", "so remember",
            "lesson", "warning", "example", "parable", "sign"
        ]
        text_lower = scene_text.lower()
        lesson_bonus = sum(0.05 for kw in lesson_keywords if kw in text_lower)
        lesson_bonus = min(0.3, lesson_bonus)

        raw = position_weight * 0.7 + lesson_bonus
        return min(1.0, raw)

    def classify_arc(self, scenes: List[Scene]) -> StoryArcType:
        """Classify the overall narrative arc type from scenes."""
        if not scenes:
            return StoryArcType.DIDACTIC

        # Aggregate all characters and themes
        all_characters: Set[str] = set()
        all_themes: List[str] = []
        for scene in scenes:
            all_characters.update(scene.characters)
            all_themes.extend(scene.themes)

        # Multiple prophets each with their people => DIDACTIC (check first, highest priority)
        prophet_chars = all_characters & {
            "Moses", "Abraham", "Noah", "Solomon", "David",
            "Jesus", "Mary", "Adam"
        }
        if len(prophet_chars) >= 2:
            return StoryArcType.DIDACTIC

        # Presence of Satan and Adam => fall arc
        if "Satan" in all_characters and "Adam" in all_characters:
            return StoryArcType.TRAGEDY

        # Joseph's story: hardship -> triumph -> reconciliation => REDEMPTION
        if "Joseph" in all_characters:
            return StoryArcType.REDEMPTION

        # Moses vs Pharaoh (liberation journey)
        if "Moses" in all_characters and "Pharaoh" in all_characters:
            return StoryArcType.QUEST

        # Pure divine revelation with no explicit antagonist
        if "Moses" in all_characters and "Pharaoh" not in all_characters:
            return StoryArcType.REVELATION

        # Mostly COSMIC conflicts with prophetic themes => REVELATION
        cosmic_count = sum(
            1 for s in scenes if s.conflict == ConflictType.COSMIC
        )
        if cosmic_count > len(scenes) * 0.5 and "prophecy" in all_themes:
            return StoryArcType.REVELATION

        # Default
        return StoryArcType.DIDACTIC

    def extract_central_lesson(
        self, scenes: List[Scene], themes: List[str]
    ) -> str:
        """Synthesize the central moral/theological lesson."""
        if not themes:
            return "This surah calls the believer to reflect on divine signs and seek guidance."

        # Count theme frequencies
        from collections import Counter
        theme_counts = Counter(themes)
        most_common_theme, _ = theme_counts.most_common(1)[0]

        lesson_templates = {
            "patience": (
                "The central lesson is that patience in the face of hardship "
                "leads to ultimate triumph and divine reward."
            ),
            "gratitude": (
                "The central lesson is that gratitude to Allah for His blessings "
                "invites greater abundance and closeness to the Divine."
            ),
            "guidance": (
                "The central lesson is that following divine guidance is the "
                "only path to success in this life and the Hereafter."
            ),
            "justice": (
                "The central lesson is that Allah's justice prevails; truth and "
                "righteousness ultimately overcome oppression and falsehood."
            ),
            "mercy": (
                "The central lesson is that Allah's mercy encompasses all things; "
                "those who turn to Him in sincerity will find forgiveness and grace."
            ),
            "trust_in_god": (
                "The central lesson is that complete trust in Allah (tawakkul) "
                "is the foundation of the believer's strength and resilience."
            ),
            "repentance": (
                "The central lesson is that sincere repentance opens the door to "
                "divine forgiveness and spiritual renewal."
            ),
            "divine_power": (
                "The central lesson is that Allah's power over all creation demands "
                "humility, worship, and recognition of our dependence on Him."
            ),
            "prophecy": (
                "The central lesson is that prophetic guidance is a mercy to humanity; "
                "heeding the messenger leads to salvation."
            ),
            "trial": (
                "The central lesson is that trials are a means of purification and "
                "elevation; those who endure with faith emerge stronger in spirit."
            ),
        }

        return lesson_templates.get(
            most_common_theme,
            f"The central lesson revolves around {most_common_theme.replace('_', ' ')}, "
            "calling believers to deeper reflection and righteous action."
        )

    def analyze_surah(self, surah_number: int) -> Optional[NarrativeStructure]:
        """
        Analyze a surah's narrative structure.
        Returns None if surah has no significant narrative content.
        """
        surah_info = self.NARRATIVE_SURAHS.get(surah_number)
        if surah_info is None:
            return None

        surah_name, _ = surah_info

        verses = self.corpus.get(surah_number, [])
        if not verses:
            return None

        scenes = self.segment_into_scenes(verses)
        if not scenes:
            return None

        # Aggregate themes across all scenes
        all_themes: List[str] = []
        for scene in scenes:
            all_themes.extend(scene.themes)

        # Count primary themes
        from collections import Counter
        theme_counter = Counter(all_themes)
        primary_themes = [t for t, _ in theme_counter.most_common(5)]

        arc_type = self.classify_arc(scenes)
        central_lesson = self.extract_central_lesson(scenes, all_themes)

        # Build character appearances map
        character_appearances: Dict[str, List[int]] = {}
        for scene in scenes:
            for char in scene.characters:
                character_appearances.setdefault(char, []).append(scene.number)

        # Arc intensity: average moral weight across scenes, normalized
        if scenes:
            arc_intensity = sum(s.moral_weight for s in scenes) / len(scenes)
        else:
            arc_intensity = 0.0

        return NarrativeStructure(
            surah_number=surah_number,
            surah_name=surah_name,
            arc_type=arc_type,
            scenes=scenes,
            primary_themes=primary_themes,
            central_lesson=central_lesson,
            character_appearances=character_appearances,
            arc_intensity=arc_intensity,
        )

    def analyze_all_narratives(self) -> Dict[int, NarrativeStructure]:
        """Analyze all known narrative surahs that are present in the corpus."""
        results: Dict[int, NarrativeStructure] = {}
        for surah_number in self.NARRATIVE_SURAHS:
            structure = self.analyze_surah(surah_number)
            if structure is not None:
                results[surah_number] = structure
        return results


# --------------------------------------------------------------------------- #
# Main entry point
# --------------------------------------------------------------------------- #

if __name__ == "__main__":
    import os

    # Resolve corpus path relative to this file
    _here = Path(__file__).resolve().parent
    _corpus = _here.parent / "corpus_extraction" / "output" / "complete_corpus.json"

    if not _corpus.exists():
        print(f"Corpus not found at {_corpus}")
        raise SystemExit(1)

    analyzer = QuranicNarrativeAnalyzer(str(_corpus))
    structure = analyzer.analyze_surah(12)  # Surah Yusuf

    if structure is None:
        print("No narrative structure found for Surah 12.")
        raise SystemExit(1)

    print(f"Surah {structure.surah_number}: {structure.surah_name}")
    print(f"Arc Type     : {structure.arc_type.name} ({structure.arc_type.value})")
    print(f"Arc Intensity: {structure.arc_intensity:.3f}")
    print(f"Scenes       : {len(structure.scenes)}")
    print(f"Primary Themes: {structure.primary_themes}")
    print(f"Central Lesson: {structure.central_lesson}")
    print()
    print(f"Characters found: {list(structure.character_appearances.keys())}")
    print()
    for scene in structure.scenes[:5]:  # Print first 5 scenes
        print(
            f"  Scene {scene.number} [v{scene.verse_range[0]}-{scene.verse_range[1]}]: "
            f"chars={scene.characters or '{}'} conflict={scene.conflict.name} "
            f"weight={scene.moral_weight:.2f} themes={scene.themes}"
        )
    if len(structure.scenes) > 5:
        print(f"  ... ({len(structure.scenes) - 5} more scenes)")
