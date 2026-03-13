"""Quranic Named Entity Recognition (NER).

Identifies and classifies named entities in Quranic text:
    - Prophets (Anbiya)
    - Places (Amaken)
    - Angels (Malaika)
    - Historical events (Ahdath)
    - Tribes/peoples (Aqwam)
    - Celestial bodies (Aflak)

Uses built-in knowledge bases with Arabic and transliterated forms.
No external model dependency — rule-based for deterministic reproducibility.
"""
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Tuple
import re


# ============================================================================
# Data Structures
# ============================================================================

@dataclass
class Entity:
    """A recognized named entity."""
    name: str
    arabic: str
    entity_type: str        # 'prophet', 'place', 'angel', 'event', 'tribe', 'celestial'
    verse_ref: Optional[str] = None   # e.g., "2:127" (surah:ayah)
    confidence: float = 1.0
    span: Optional[Tuple[int, int]] = None  # (start, end) character offsets

    def __repr__(self) -> str:
        return f"Entity({self.name!r}, type={self.entity_type}, conf={self.confidence:.2f})"


# ============================================================================
# Knowledge Bases
# ============================================================================

# 25 Prophets mentioned in the Quran
PROPHETS: Dict[str, str] = {
    'آدم': 'Adam',
    'إدريس': 'Idris',
    'نوح': 'Nuh',
    'هود': 'Hud',
    'صالح': 'Salih',
    'إبراهيم': 'Ibrahim',
    'لوط': 'Lut',
    'إسماعيل': 'Ismail',
    'إسحاق': 'Ishaq',
    'يعقوب': 'Yaqub',
    'يوسف': 'Yusuf',
    'أيوب': 'Ayyub',
    'شعيب': 'Shuayb',
    'موسى': 'Musa',
    'هارون': 'Harun',
    'داود': 'Dawud',
    'سليمان': 'Sulayman',
    'إلياس': 'Ilyas',
    'اليسع': 'Al-Yasa',
    'يونس': 'Yunus',
    'ذو الكفل': 'Dhul-Kifl',
    'زكريا': 'Zakariya',
    'يحيى': 'Yahya',
    'عيسى': 'Isa',
    'محمد': 'Muhammad',
}

# Alternate Quranic names for prophets
PROPHET_ALIASES: Dict[str, str] = {
    'أحمد': 'Muhammad',       # Saf 61:6
    'المسيح': 'Isa',          # Al-Masih
    'ابن مريم': 'Isa',        # Son of Maryam
    'خليل الله': 'Ibrahim',   # Friend of Allah
    'كليم الله': 'Musa',      # One spoken to by Allah
    'ذا النون': 'Yunus',      # The one of the fish
    'خاتم النبيين': 'Muhammad',  # Seal of Prophets
}

# Places mentioned in the Quran (20+)
PLACES: Dict[str, str] = {
    'مكة': 'Makkah',
    'بكة': 'Bakkah',          # alternate name for Makkah (3:96)
    'المدينة': 'Madinah',
    'يثرب': 'Yathrib',        # old name for Madinah (33:13)
    'مصر': 'Misr',            # Egypt
    'بابل': 'Babylon',
    'سيناء': 'Sinai',
    'طور': 'Tur',             # Mount Sinai
    'الأقصى': 'Al-Aqsa',
    'سبأ': 'Saba',            # Sheba
    'الأحقاف': 'Al-Ahqaf',
    'مدين': 'Madyan',
    'إرم': 'Iram',            # Iram of the Pillars
    'الحجر': 'Al-Hijr',       # Thamud territory
    'بدر': 'Badr',
    'حنين': 'Hunayn',
    'الجودي': 'Al-Judi',      # where the Ark rested
    'عرفات': 'Arafat',
    'الصفا': 'Al-Safa',
    'المروة': 'Al-Marwah',
    'جهنم': 'Jahannam',
    'الجنة': 'Jannah',
    'الأعراف': 'Al-Araf',
    'سدرة المنتهى': 'Sidrat al-Muntaha',
}

# Angels (Malaika)
ANGELS: Dict[str, str] = {
    'جبريل': 'Jibril',
    'ميكائيل': 'Mikail',
    'إسرافيل': 'Israfil',
    'عزرائيل': 'Azrail',
    'مالك': 'Malik',           # guardian of Hellfire
    'هاروت': 'Harut',
    'ماروت': 'Marut',
    'الروح': 'Ar-Ruh',        # the Spirit (often identified with Jibril)
}

# Historical events referenced in the Quran
EVENTS: Dict[str, str] = {
    'بدر': 'Battle of Badr',
    'أحد': 'Battle of Uhud',
    'الأحزاب': 'Battle of the Trench',
    'الحديبية': 'Treaty of Hudaybiyyah',
    'حنين': 'Battle of Hunayn',
    'الفتح': 'Conquest of Makkah',
    'الإسراء': 'Night Journey',
    'المعراج': 'Ascension',
    'الهجرة': 'Hijrah',
    'الطوفان': 'The Flood',
    'فرعون': 'Pharaoh narrative',
}

# Tribes and peoples
TRIBES: Dict[str, str] = {
    'عاد': 'Aad',
    'ثمود': 'Thamud',
    'قريش': 'Quraysh',
    'بنو إسرائيل': 'Banu Israel',
    'أصحاب الكهف': 'Companions of the Cave',
    'أصحاب الأخدود': 'Companions of the Trench',
    'أصحاب الفيل': 'Companions of the Elephant',
    'أصحاب الرس': 'Companions of Ar-Rass',
    'أصحاب الأيكة': 'Companions of the Wood',
    'يأجوج': 'Yajuj',
    'مأجوج': 'Majuj',
}

# Celestial bodies mentioned
CELESTIAL: Dict[str, str] = {
    'الشمس': 'Sun',
    'القمر': 'Moon',
    'النجم': 'Star',
    'الكواكب': 'Planets',
    'السماء': 'Heaven/Sky',
    'البروج': 'Constellations',
    'الطارق': 'Morning Star',
}


# ============================================================================
# NER Engine
# ============================================================================

class QuranicNER:
    """Named Entity Recognition for Quranic Arabic text.

    Uses built-in knowledge bases for deterministic, reproducible entity
    extraction. No ML model dependency.
    """

    def __init__(self):
        # Build unified lookup: arabic_form -> (english_name, entity_type)
        self._lookup: Dict[str, Tuple[str, str]] = {}
        self._build_lookup()

        # Precompile strip regex for diacritics
        self._strip_re = re.compile(r'[\u064B-\u065F\u0670]')

    def _build_lookup(self):
        """Populate the unified lookup dictionary from all knowledge bases."""
        for ar, en in PROPHETS.items():
            self._lookup[ar] = (en, 'prophet')
        for ar, en in PROPHET_ALIASES.items():
            self._lookup[ar] = (en, 'prophet')
        for ar, en in PLACES.items():
            self._lookup[ar] = (en, 'place')
        for ar, en in ANGELS.items():
            self._lookup[ar] = (en, 'angel')
        for ar, en in EVENTS.items():
            # Events may overlap with places (e.g., 'بدر'); events take precedence only
            # if not already a place. We store both by appending _event suffix internally.
            if ar not in self._lookup:
                self._lookup[ar] = (en, 'event')
        for ar, en in TRIBES.items():
            self._lookup[ar] = (en, 'tribe')
        for ar, en in CELESTIAL.items():
            self._lookup[ar] = (en, 'celestial')

    def _strip(self, text: str) -> str:
        """Remove tashkeel for matching."""
        return self._strip_re.sub('', text)

    def extract_entities(self, text: str) -> Dict[str, List[Entity]]:
        """Extract named entities from Arabic text.

        Searches for known entities in the text using exact substring matching
        on diacritic-stripped forms. Returns entities grouped by type.

        Args:
            text: Arabic text (verse, passage, or surah).

        Returns:
            Dict mapping entity type to list of Entity objects found.
        """
        results: Dict[str, List[Entity]] = {
            'prophet': [],
            'place': [],
            'angel': [],
            'event': [],
            'tribe': [],
            'celestial': [],
        }

        stripped = self._strip(text)

        # Sort by length descending so longer matches take priority
        sorted_entries = sorted(self._lookup.items(), key=lambda x: len(x[0]), reverse=True)

        matched_spans: List[Tuple[int, int]] = []

        for arabic, (english, etype) in sorted_entries:
            arabic_stripped = self._strip(arabic)
            search_start = 0
            while True:
                idx = stripped.find(arabic_stripped, search_start)
                if idx == -1:
                    break

                span = (idx, idx + len(arabic_stripped))

                # Avoid overlapping matches
                overlap = False
                for ms, me in matched_spans:
                    if not (span[1] <= ms or span[0] >= me):
                        overlap = True
                        break

                if not overlap:
                    # Confidence based on match quality
                    confidence = 1.0 if arabic in text else 0.9  # exact vs stripped match

                    entity = Entity(
                        name=english,
                        arabic=arabic,
                        entity_type=etype,
                        confidence=confidence,
                        span=span,
                    )
                    results[etype].append(entity)
                    matched_spans.append(span)

                search_start = idx + 1

        return results

    def extract_entities_flat(self, text: str) -> List[Entity]:
        """Extract all entities as a flat list sorted by position.

        Args:
            text: Arabic text.

        Returns:
            List of Entity objects sorted by span start position.
        """
        grouped = self.extract_entities(text)
        entities = []
        for etype_list in grouped.values():
            entities.extend(etype_list)
        entities.sort(key=lambda e: e.span[0] if e.span else 0)
        return entities

    def count_by_type(self, text: str) -> Dict[str, int]:
        """Count entities by type.

        Args:
            text: Arabic text.

        Returns:
            Dict mapping entity type to count.
        """
        grouped = self.extract_entities(text)
        return {etype: len(entities) for etype, entities in grouped.items()}

    def annotate_text(self, text: str) -> str:
        """Return text with entity annotations in bracket notation.

        Example: "قال موسى" -> "قال [موسى|prophet:Musa]"

        Args:
            text: Arabic text.

        Returns:
            Annotated text string.
        """
        entities = self.extract_entities_flat(text)
        if not entities:
            return text

        # Work on stripped text for span accuracy, but annotate original
        stripped = self._strip(text)
        # Build offset map from stripped positions to original positions
        orig_positions = []
        si = 0
        for oi, ch in enumerate(text):
            if self._strip_re.match(ch):
                continue
            orig_positions.append(oi)
            si += 1

        result_parts = []
        last_end_orig = 0

        for entity in entities:
            if entity.span is None:
                continue
            start_s, end_s = entity.span

            # Map stripped positions to original positions
            if start_s >= len(orig_positions) or end_s > len(orig_positions):
                continue

            start_orig = orig_positions[start_s]
            end_orig = orig_positions[end_s - 1] + 1 if end_s <= len(orig_positions) else len(text)
            # Extend end to include any trailing diacritics
            while end_orig < len(text) and self._strip_re.match(text[end_orig]):
                end_orig += 1

            if start_orig < last_end_orig:
                continue

            result_parts.append(text[last_end_orig:start_orig])
            matched_text = text[start_orig:end_orig]
            result_parts.append(f"[{matched_text}|{entity.entity_type}:{entity.name}]")
            last_end_orig = end_orig

        result_parts.append(text[last_end_orig:])
        return ''.join(result_parts)
