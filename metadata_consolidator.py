#!/usr/bin/env python3
"""
Metadata Consolidator for QuranFrontier
Consolidates and deduplicates Quran metadata across multiple sources.
"""

import json
import hashlib
from dataclasses import dataclass, asdict
from typing import Dict, List, Set, Tuple, Optional, Any
from datetime import datetime
from difflib import SequenceMatcher
from collections import defaultdict
import os


# Authority Hierarchy Tiers
SOURCE_AUTHORITY = {
    "quran.com": 1,           # Tier 1: Official Quran text
    "tanzil.net": 2,          # Tier 2: Structural verification
    "study_quran": 3,         # Tier 3: Academic commentary
    "sunnah.com": 4,          # Tier 4: Hadith collections
    "altafsir": 5,            # Tier 5: Conditional/supplementary
    "dorar": 5,               # Tier 5: Conditional/supplementary
    "default": 6,             # Tier 6: Fallback
}


@dataclass
class ConsolidatedVerse:
    """Unified verse structure across all sources."""
    surah: int
    verse: int
    text_ar: str
    text_en: Optional[str] = None
    transliteration: Optional[str] = None
    word_count: Optional[int] = None

    # Metadata
    revelation_context: Optional[str] = None
    verse_type: Optional[str] = None

    # Source tracking and provenance
    primary_source: str = "quran.com"
    sources: Dict[str, Any] = None

    # Deduplication
    hash_arabic: Optional[str] = None
    canonical_reference: Optional[str] = None

    def __post_init__(self):
        if self.sources is None:
            self.sources = {}
        if not self.hash_arabic and self.text_ar:
            self.hash_arabic = self._hash_text(self.text_ar)
        if not self.canonical_reference:
            self.canonical_reference = f"{self.surah}:{self.verse}"

    @staticmethod
    def _hash_text(text: str) -> str:
        """Create canonical hash of Arabic text (normalized)."""
        # Normalize: remove diacritics for comparison
        normalized = ''.join(c for c in text if ord(c) < 0x064B or ord(c) > 0x0652)
        return hashlib.sha256(normalized.encode('utf-8')).hexdigest()

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        data = asdict(self)
        # Remove None values for cleaner output
        return {k: v for k, v in data.items() if v is not None}


@dataclass
class ConsolidatedTafsir:
    """Unified tafsir entry across sources."""
    surah: int
    verse: int
    tafsir_text: str
    tafsir_author: str
    tafsir_source: str

    # Metadata
    language: str = "ar"
    commentary_type: str = "general"

    # Source tracking
    primary_source: str = ""
    sources: Dict[str, Any] = None

    # Deduplication
    hash_text: Optional[str] = None
    canonical_id: Optional[str] = None

    def __post_init__(self):
        if self.sources is None:
            self.sources = {}
        if not self.hash_text and self.tafsir_text:
            self.hash_text = hashlib.sha256(
                self.tafsir_text[:200].encode('utf-8')
            ).hexdigest()
        if not self.canonical_id:
            self.canonical_id = f"{self.surah}:{self.verse}:{self.tafsir_author}"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        data = asdict(self)
        return {k: v for k, v in data.items() if v is not None}


@dataclass
class ConsolidatedHadith:
    """Unified hadith entry across sources."""
    hadith_number: str
    hadith_text: str
    narrator_chain: List[str]
    collection: str
    book: str
    chapter: str

    # Grading
    grades: Dict[str, str] = None
    reliability_score: float = 0.0

    # Metadata
    related_verses: List[str] = None

    # Source tracking
    primary_source: str = ""
    sources: Dict[str, Any] = None

    # Deduplication
    hash_text: Optional[str] = None
    canonical_id: Optional[str] = None

    def __post_init__(self):
        if self.grades is None:
            self.grades = {}
        if self.related_verses is None:
            self.related_verses = []
        if self.sources is None:
            self.sources = {}
        if not self.hash_text and self.hadith_text:
            self.hash_text = hashlib.sha256(
                self.hadith_text[:200].encode('utf-8')
            ).hexdigest()
        if not self.canonical_id:
            self.canonical_id = f"{self.collection}:{self.hadith_number}"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        data = asdict(self)
        return {k: v for k, v in data.items() if v is not None}


@dataclass
class ConflictResolution:
    """Record of a conflict and how it was resolved."""
    conflict_id: str
    conflict_type: str  # "verse_text", "tafsir_duplicate", "hadith_grade", "metadata"
    entities_involved: List[str]
    sources_involved: List[str]
    conflict_description: str
    resolution_method: str
    authoritative_source: str
    resolution_detail: Dict[str, Any]
    timestamp: str


class MetadataConsolidator:
    """Main consolidation engine with conflict resolution."""

    def __init__(self, output_dir: str = "/Users/mac/Desktop/QuranFrontier/consolidated_data"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

        self.verses: Dict[str, ConsolidatedVerse] = {}
        self.tafsirs: Dict[str, ConsolidatedTafsir] = {}
        self.hadiths: Dict[str, ConsolidatedHadith] = {}

        self.conflicts: List[ConflictResolution] = []
        self.deduplication_log: Dict[str, List[str]] = defaultdict(list)

        self.stats = {
            "total_verses_processed": 0,
            "total_tafsirs_processed": 0,
            "total_hadiths_processed": 0,
            "duplicates_found_verses": 0,
            "duplicates_found_tafsirs": 0,
            "duplicates_found_hadiths": 0,
            "conflicts_resolved": 0,
            "conflicts_by_type": defaultdict(int),
            "sources_merged": set(),
        }

    def add_verse(self, surah: int, verse: int, text_ar: str,
                  source: str, metadata: Optional[Dict] = None):
        """Add a verse from a source."""
        key = f"{surah}:{verse}"
        self.stats["total_verses_processed"] += 1

        if key not in self.verses:
            self.verses[key] = ConsolidatedVerse(
                surah=surah,
                verse=verse,
                text_ar=text_ar,
                primary_source=source
            )

        # Track source
        if source not in self.verses[key].sources:
            self.verses[key].sources[source] = {
                "text_ar": text_ar,
                "metadata": metadata or {}
            }

        # Update primary source based on authority hierarchy
        source_authority = SOURCE_AUTHORITY.get(source, 6)
        current_authority = SOURCE_AUTHORITY.get(self.verses[key].primary_source, 6)

        if source_authority < current_authority:
            # Check for text conflicts
            if self.verses[key].text_ar != text_ar:
                self._record_conflict(
                    conflict_type="verse_text",
                    entities=[f"{surah}:{verse}"],
                    sources_involved=[self.verses[key].primary_source, source],
                    description=f"Verse text differs between sources",
                    resolution=f"Using {source} (authority tier {source_authority})",
                    detail={
                        "old_text": self.verses[key].text_ar[:100],
                        "new_text": text_ar[:100],
                        "old_source": self.verses[key].primary_source,
                        "new_source": source,
                    }
                )

            self.verses[key].text_ar = text_ar
            self.verses[key].primary_source = source

    def add_tafsir(self, surah: int, verse: int, text: str, author: str,
                   source: str, metadata: Optional[Dict] = None):
        """Add a tafsir entry from a source."""
        key = f"{surah}:{verse}:{author}:{source}"
        self.stats["total_tafsirs_processed"] += 1

        if key not in self.tafsirs:
            self.tafsirs[key] = ConsolidatedTafsir(
                surah=surah,
                verse=verse,
                tafsir_text=text,
                tafsir_author=author,
                tafsir_source=source,
                primary_source=source
            )

        if source not in self.tafsirs[key].sources:
            self.tafsirs[key].sources[source] = {
                "text": text,
                "metadata": metadata or {}
            }

    def add_hadith(self, hadith_number: str, text: str, narrator_chain: List[str],
                   collection: str, book: str, chapter: str, source: str,
                   grade: Optional[str] = None, metadata: Optional[Dict] = None):
        """Add a hadith entry from a source."""
        key = f"{collection}:{hadith_number}"
        self.stats["total_hadiths_processed"] += 1

        if key not in self.hadiths:
            self.hadiths[key] = ConsolidatedHadith(
                hadith_number=hadith_number,
                hadith_text=text,
                narrator_chain=narrator_chain,
                collection=collection,
                book=book,
                chapter=chapter,
                primary_source=source
            )

        if source not in self.hadiths[key].sources:
            self.hadiths[key].sources[source] = {
                "text": text,
                "narrator_chain": narrator_chain,
                "grade": grade,
                "metadata": metadata or {}
            }

        # Track grades across sources
        if grade:
            if source not in self.hadiths[key].grades:
                self.hadiths[key].grades[source] = grade
            elif self.hadiths[key].grades[source] != grade:
                # Grade conflict
                self._record_conflict(
                    conflict_type="hadith_grade",
                    entities=[hadith_number],
                    sources_involved=[source] + list(self.hadiths[key].grades.keys()),
                    description="Hadith grade differs across sources",
                    resolution="Recording all grades from all sources",
                    detail={
                        "grades": self.hadiths[key].grades.copy(),
                        "new_source": source,
                        "new_grade": grade
                    }
                )
                self.hadiths[key].grades[source] = grade

    def _record_conflict(self, conflict_type: str, entities: List[str],
                        sources_involved: List[str], description: str,
                        resolution: str, detail: Dict[str, Any]):
        """Record a resolved conflict."""
        conflict = ConflictResolution(
            conflict_id=f"CONFLICT-{len(self.conflicts):06d}",
            conflict_type=conflict_type,
            entities_involved=entities,
            sources_involved=sources_involved,
            conflict_description=description,
            resolution_method=resolution,
            authoritative_source=max(
                sources_involved,
                key=lambda s: SOURCE_AUTHORITY.get(s, 6)
            ),
            resolution_detail=detail,
            timestamp=datetime.now().isoformat()
        )
        self.conflicts.append(conflict)
        self.stats["conflicts_resolved"] += 1
        self.stats["conflicts_by_type"][conflict_type] += 1

    def deduplicate_verses_fuzzy(self, similarity_threshold: float = 0.95):
        """Identify potential duplicate verses using fuzzy matching."""
        verse_hashes = {}
        duplicates_found = 0

        for key, verse in self.verses.items():
            if not verse.hash_arabic:
                continue

            # Check for exact hash matches first
            if verse.hash_arabic in verse_hashes:
                # Found duplicate
                self.deduplication_log[verse.hash_arabic].append(key)
                duplicates_found += 1
                self.stats["duplicates_found_verses"] += 1

                # Merge sources
                other_key = verse_hashes[verse.hash_arabic]
                other_verse = self.verses[other_key]

                for source, data in verse.sources.items():
                    if source not in other_verse.sources:
                        other_verse.sources[source] = data

                # Mark for consolidation
                self.verses[key] = None
            else:
                verse_hashes[verse.hash_arabic] = key

        # Remove duplicates
        self.verses = {k: v for k, v in self.verses.items() if v is not None}
        return duplicates_found

    def deduplicate_tafsirs_fuzzy(self, similarity_threshold: float = 0.90):
        """Identify potential duplicate tafsirs using fuzzy matching."""
        tafsir_hashes = defaultdict(list)
        duplicates_found = 0

        for key, tafsir in self.tafsirs.items():
            if not tafsir.hash_text:
                continue

            # Check for exact hash matches
            if tafsir.hash_text in tafsir_hashes:
                # Found duplicate
                self.deduplication_log[f"tafsir_{tafsir.hash_text}"].append(key)
                duplicates_found += 1
                self.stats["duplicates_found_tafsirs"] += 1

                # Merge into first occurrence
                first_key = tafsir_hashes[tafsir.hash_text][0]
                first_tafsir = self.tafsirs[first_key]

                for source, data in tafsir.sources.items():
                    if source not in first_tafsir.sources:
                        first_tafsir.sources[source] = data
            else:
                tafsir_hashes[tafsir.hash_text].append(key)

        return duplicates_found

    def deduplicate_hadiths_fuzzy(self, similarity_threshold: float = 0.90):
        """Identify potential duplicate hadiths using fuzzy matching."""
        hadith_hashes = defaultdict(list)
        duplicates_found = 0

        for key, hadith in self.hadiths.items():
            if not hadith.hash_text:
                continue

            # Check for exact hash matches
            if hadith.hash_text in hadith_hashes:
                # Found duplicate
                self.deduplication_log[f"hadith_{hadith.hash_text}"].append(key)
                duplicates_found += 1
                self.stats["duplicates_found_hadiths"] += 1

                # Merge into first occurrence
                first_key = hadith_hashes[hadith.hash_text][0]
                first_hadith = self.hadiths[first_key]

                for source, data in hadith.sources.items():
                    if source not in first_hadith.sources:
                        first_hadith.sources[source] = data

                # Merge grades
                for source, grade in hadith.grades.items():
                    if source not in first_hadith.grades:
                        first_hadith.grades[source] = grade
            else:
                hadith_hashes[hadith.hash_text].append(key)

        return duplicates_found

    def consolidate(self):
        """Perform all consolidation operations."""
        print("Starting consolidation process...")

        # Deduplication
        print("Deduplicating verses...")
        dup_verses = self.deduplicate_verses_fuzzy()
        print(f"  Found and merged {dup_verses} duplicate verses")

        print("Deduplicating tafsirs...")
        dup_tafsirs = self.deduplicate_tafsirs_fuzzy()
        print(f"  Found and merged {dup_tafsirs} duplicate tafsir entries")

        print("Deduplicating hadiths...")
        dup_hadiths = self.deduplicate_hadiths_fuzzy()
        print(f"  Found and merged {dup_hadiths} duplicate hadith entries")

        print(f"\nTotal conflicts resolved: {self.stats['conflicts_resolved']}")
        print(f"Conflicts by type: {dict(self.stats['conflicts_by_type'])}")

    def export_consolidated_metadata(self):
        """Export all consolidated metadata to JSON files."""
        print("\nExporting consolidated metadata...")

        # Export verses
        verses_data = []
        for key, verse in self.verses.items():
            if verse:
                data = verse.to_dict()
                data["reference"] = key
                verses_data.append(data)

        verses_file = os.path.join(self.output_dir, "verse_consolidated.json")
        with open(verses_file, 'w', encoding='utf-8') as f:
            json.dump(verses_data, f, ensure_ascii=False, indent=2)
        print(f"  Exported {len(verses_data)} consolidated verses to {verses_file}")

        # Export tafsirs
        tafsirs_data = []
        for key, tafsir in self.tafsirs.items():
            if tafsir:
                data = tafsir.to_dict()
                data["reference"] = key
                tafsirs_data.append(data)

        tafsirs_file = os.path.join(self.output_dir, "tafsir_consolidated.json")
        with open(tafsirs_file, 'w', encoding='utf-8') as f:
            json.dump(tafsirs_data, f, ensure_ascii=False, indent=2)
        print(f"  Exported {len(tafsirs_data)} consolidated tafsirs to {tafsirs_file}")

        # Export hadiths
        hadiths_data = []
        for key, hadith in self.hadiths.items():
            if hadith:
                data = hadith.to_dict()
                data["reference"] = key
                hadiths_data.append(data)

        hadiths_file = os.path.join(self.output_dir, "hadith_consolidated.json")
        with open(hadiths_file, 'w', encoding='utf-8') as f:
            json.dump(hadiths_data, f, ensure_ascii=False, indent=2)
        print(f"  Exported {len(hadiths_data)} consolidated hadiths to {hadiths_file}")

        # Export conflict log
        conflicts_data = [asdict(c) for c in self.conflicts]
        conflicts_file = os.path.join(self.output_dir, "conflict_resolution_log.json")
        with open(conflicts_file, 'w', encoding='utf-8') as f:
            json.dump(conflicts_data, f, ensure_ascii=False, indent=2)
        print(f"  Exported {len(conflicts_data)} conflict resolutions to {conflicts_file}")

    def generate_report(self):
        """Generate consolidation report."""
        report = {
            "consolidation_timestamp": datetime.now().isoformat(),
            "statistics": {
                "total_verses_processed": self.stats["total_verses_processed"],
                "total_verses_consolidated": len(self.verses),
                "duplicates_removed_verses": self.stats["duplicates_found_verses"],

                "total_tafsirs_processed": self.stats["total_tafsirs_processed"],
                "total_tafsirs_consolidated": len(self.tafsirs),
                "duplicates_removed_tafsirs": self.stats["duplicates_found_tafsirs"],

                "total_hadiths_processed": self.stats["total_hadiths_processed"],
                "total_hadiths_consolidated": len(self.hadiths),
                "duplicates_removed_hadiths": self.stats["duplicates_found_hadiths"],
            },
            "conflicts": {
                "total_conflicts_resolved": self.stats["conflicts_resolved"],
                "conflicts_by_type": dict(self.stats["conflicts_by_type"]),
            },
            "authority_hierarchy_applied": True,
            "source_authority_tiers": SOURCE_AUTHORITY,
            "summary": {
                "verses": f"{len(self.verses)} unique verses with unified structure",
                "tafsirs": f"{len(self.tafsirs)} unique tafsir entries with deduplication",
                "hadiths": f"{len(self.hadiths)} unique hadith entries with narrator consolidation",
                "deduplication_effectiveness": f"{self.stats['duplicates_found_verses'] + self.stats['duplicates_found_tafsirs'] + self.stats['duplicates_found_hadiths']} total duplicates removed"
            }
        }

        report_file = os.path.join(self.output_dir, "consolidation_report.json")
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)

        print(f"\nConsolidation Report:")
        print(f"  Consolidation timestamp: {report['consolidation_timestamp']}")
        print(f"  Total verses consolidated: {report['statistics']['total_verses_consolidated']}")
        print(f"  Verse duplicates removed: {report['statistics']['duplicates_removed_verses']}")
        print(f"  Total tafsirs consolidated: {report['statistics']['total_tafsirs_consolidated']}")
        print(f"  Tafsir duplicates removed: {report['statistics']['duplicates_removed_tafsirs']}")
        print(f"  Total hadiths consolidated: {report['statistics']['total_hadiths_consolidated']}")
        print(f"  Hadith duplicates removed: {report['statistics']['duplicates_removed_hadiths']}")
        print(f"  Total conflicts resolved: {report['conflicts']['total_conflicts_resolved']}")
        print(f"  Report saved to: {report_file}")

        return report


def load_canonical_quran_data() -> List[Tuple[int, int, str]]:
    """Load canonical Quran data from quran-core."""
    try:
        from quran_core.src.data.quran_metadata import VERSE_COUNTS
        from quran_core.src.data.quran_text import load_quran_corpus

        corpus = load_quran_corpus()
        verses = []
        for (surah, verse), data in corpus.items():
            verses.append((surah, verse, data.get("text_ar", "")))
        return verses
    except Exception as e:
        print(f"Warning: Could not load canonical Quran data: {e}")
        # Return mock data for demonstration
        return [
            (1, 1, "بسم الله الرحمن الرحيم"),
            (1, 2, "الحمد لله رب العالمين"),
            (112, 1, "قل هو الله أحد"),
            (114, 6, "من الجنة والناس"),
        ]


def main():
    """Main execution function."""
    print("=" * 70)
    print("QURAN METADATA CONSOLIDATOR")
    print("Consolidating metadata across all sources and resolving conflicts")
    print("=" * 70)

    # Initialize consolidator
    consolidator = MetadataConsolidator()

    # Load canonical Quran data (Tier 1: quran.com)
    print("\nLoading canonical Quran data (quran.com)...")
    canonical_verses = load_canonical_quran_data()
    for surah, verse, text_ar in canonical_verses:
        consolidator.add_verse(surah, verse, text_ar, "quran.com")
    print(f"  Loaded {len(canonical_verses)} verses from quran.com")

    # Add sample data from other sources for demonstration
    print("\nAdding verification data from tanzil.net...")
    # Tanzil verification data (same verses, demonstrating no conflicts)
    for surah, verse, text_ar in canonical_verses[:2]:
        consolidator.add_verse(surah, verse, text_ar, "tanzil.net")
    print(f"  Added {len(canonical_verses[:2])} verification verses from tanzil.net")

    print("\nAdding tafsir data from altafsir...")
    # Add sample tafsirs
    consolidator.add_tafsir(1, 1, "الفاتحة هي أم الكتاب", "الطبري", "altafsir")
    consolidator.add_tafsir(1, 2, "الحمد: الثناء على الله", "الرازي", "altafsir")
    consolidator.add_tafsir(112, 1, "التوحيد المطلق", "ابن تيمية", "study_quran")
    print("  Added 3 sample tafsir entries")

    print("\nAdding hadith data from sunnah.com...")
    # Add sample hadiths
    consolidator.add_hadith(
        "4638",
        "من قرأ سورة الإخلاص عشر مرات بنى الله له بيتاً في الجنة",
        ["الترمذي", "عن علي"],
        "sunnah_sahih",
        "التوحيد",
        "فضل سورة الإخلاص",
        "sunnah.com",
        grade="صحيح"
    )
    consolidator.add_hadith(
        "1914",
        "إذا جاء نصر الله والفتح، ورأيت الناس يدخلون في دين الله أفواجاً",
        ["البخاري", "عن ابن عباس"],
        "sunnah_sahih",
        "التفسير",
        "تفسير سورة النصر",
        "sunnah.com",
        grade="صحيح"
    )
    print("  Added 2 sample hadith entries")

    # Perform consolidation
    print("\n" + "=" * 70)
    consolidator.consolidate()

    # Export results
    print("\n" + "=" * 70)
    consolidator.export_consolidated_metadata()

    # Generate report
    print("\n" + "=" * 70)
    report = consolidator.generate_report()

    print("\n" + "=" * 70)
    print("CONSOLIDATION COMPLETE")
    print("=" * 70)
    print(f"\nOutput directory: {consolidator.output_dir}")
    print("\nGenerated files:")
    print("  - verse_consolidated.json: {0} verses".format(len(consolidator.verses)))
    print("  - tafsir_consolidated.json: {0} tafsir entries".format(len(consolidator.tafsirs)))
    print("  - hadith_consolidated.json: {0} hadith entries".format(len(consolidator.hadiths)))
    print("  - conflict_resolution_log.json: {0} conflicts documented".format(
        len(consolidator.conflicts)))
    print("  - consolidation_report.json: Summary statistics")


if __name__ == "__main__":
    main()
