#!/usr/bin/env python3
"""
BLOCKER 0: Wire real Quranic text into complete_corpus.json.

The corpus has 6,236 synthetic placeholder verses in a fake 32-surah structure.
The real Quran has 114 surahs with exactly 6,236 verses in total.

Strategy: map each corpus entry (by sequential index 0..6235) to the real
Quran verse (surah:ayah) using the official verse counts per surah.
Real Arabic (ar.uthmani) and English (en.sahih = Saheeh International)
are fetched from api.alquran.cloud (public, no authentication required).

Usage:
    python wire_real_text.py
"""

import json
import hashlib
import re
import shutil
import time
import urllib.request
from pathlib import Path
from typing import Dict, List, Tuple

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
SCRIPT_DIR = Path(__file__).parent
CORPUS_EXTRACTION_DIR = SCRIPT_DIR.parent
QURAN_DIR = CORPUS_EXTRACTION_DIR.parent
REPO_ROOT = QURAN_DIR.parent

CORPUS_PATH = CORPUS_EXTRACTION_DIR / "output" / "complete_corpus.json"
OUTPUT_PATH = CORPUS_PATH  # overwrite in-place after backup

# alquran.cloud API — public, no authentication required
ALQURAN_API_BASE = "https://api.alquran.cloud/v1"
ARABIC_EDITION = "ar.uthmani"
ENGLISH_EDITION = "en.sahih"
API_DELAY = 0.3   # seconds between chapter requests


# ---------------------------------------------------------------------------
# Real Quran verse counts (114 surahs, total = 6,236)
# Source: api.alquran.cloud/v1/meta
# ---------------------------------------------------------------------------
VERSE_COUNTS = [
    7, 286, 200, 176, 120, 165, 206, 75, 129, 109,   # 1-10
    123, 111, 43, 52, 99, 128, 111, 110, 98, 135,     # 11-20
    112, 78, 118, 64, 77, 227, 93, 88, 69, 60,        # 21-30
    34, 30, 73, 54, 45, 83, 182, 88, 75, 85,          # 31-40
    54, 53, 89, 59, 37, 35, 38, 29, 18, 45,           # 41-50
    60, 49, 62, 55, 78, 96, 29, 22, 24, 13,           # 51-60
    14, 11, 11, 18, 12, 12, 30, 52, 52, 44,           # 61-70
    28, 28, 20, 56, 40, 31, 50, 40, 46, 42,           # 71-80
    29, 19, 36, 25, 22, 17, 19, 26, 30, 20,           # 81-90
    15, 21, 11, 8, 8, 19, 5, 8, 8, 11,                # 91-100
    11, 8, 3, 9, 5, 4, 7, 3, 6, 3,                    # 101-110
    5, 4, 5, 6,                                         # 111-114
]

assert len(VERSE_COUNTS) == 114, f"Expected 114 surahs, got {len(VERSE_COUNTS)}"
assert sum(VERSE_COUNTS) == 6236, f"Expected 6236 total verses, got {sum(VERSE_COUNTS)}"


# ---------------------------------------------------------------------------
# Build sequential index → (surah, ayah) mapping
# ---------------------------------------------------------------------------

def build_sequential_mapping() -> List[Tuple[int, int]]:
    """
    Returns a list of (surah, ayah) tuples in order, 0-indexed.
    Index 0 → (1, 1), index 1 → (1, 2), ..., index 6 → (1, 7),
    index 7 → (2, 1), ..., index 6235 → (114, 6).
    """
    mapping = []
    for surah_num, count in enumerate(VERSE_COUNTS, start=1):
        for ayah_num in range(1, count + 1):
            mapping.append((surah_num, ayah_num))
    assert len(mapping) == 6236
    return mapping


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _http_get(url: str) -> dict:
    req = urllib.request.Request(
        url,
        headers={"Accept": "application/json", "User-Agent": "QuranFrontier/1.0"},
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def _strip_html(text: str) -> str:
    return re.sub(r"<[^>]+>", "", text).strip()


# ---------------------------------------------------------------------------
# Fetch real Quranic data from alquran.cloud
# ---------------------------------------------------------------------------

def fetch_chapter(chapter: int) -> Tuple[Dict[int, str], Dict[int, str]]:
    """
    Fetch both Arabic and English for one chapter.
    Returns (arabic_map, translation_map) keyed by ayah number (int).
    """
    url = (
        f"{ALQURAN_API_BASE}/surah/{chapter}"
        f"/editions/{ARABIC_EDITION},{ENGLISH_EDITION}"
    )
    data = _http_get(url)
    editions = data["data"]

    # Find the right editions by identifier
    ar_edition = next(
        (e for e in editions if ARABIC_EDITION in e["edition"]["identifier"]),
        editions[0],
    )
    en_edition = next(
        (e for e in editions if ENGLISH_EDITION in e["edition"]["identifier"]),
        editions[1],
    )

    arabic_map: Dict[int, str] = {}
    for ayah in ar_edition["ayahs"]:
        arabic_map[ayah["numberInSurah"]] = ayah["text"].replace('\ufeff', '').strip()

    translation_map: Dict[int, str] = {}
    for ayah in en_edition["ayahs"]:
        translation_map[ayah["numberInSurah"]] = _strip_html(ayah["text"])

    return arabic_map, translation_map


def fetch_all_verses() -> Dict[str, Dict[str, str]]:
    """
    Fetch all 6,236 verses from alquran.cloud.
    Returns dict keyed by 'surah:ayah' -> {'arabic': ..., 'translation': ...}
    """
    print(f"  Fetching 114 chapters from alquran.cloud...")
    lookup: Dict[str, Dict[str, str]] = {}
    errors: List[int] = []

    for chapter in range(1, 115):
        try:
            arabic_map, translation_map = fetch_chapter(chapter)
            for ayah_num in arabic_map:
                key = f"{chapter}:{ayah_num}"
                lookup[key] = {
                    "arabic": arabic_map[ayah_num],
                    "translation": translation_map.get(ayah_num, ""),
                }
        except Exception as e:
            errors.append(chapter)
            print(f"  WARNING: Chapter {chapter} failed: {e}")

        if chapter % 20 == 0:
            print(f"    ... {chapter}/114 chapters done ({len(lookup)} verses)")

        time.sleep(API_DELAY)

    print(f"  Fetched {len(lookup)} verses ({len(errors)} errors).")
    if errors:
        print(f"  Failed chapters: {errors}")
    return lookup


# ---------------------------------------------------------------------------
# Wiring
# ---------------------------------------------------------------------------

def wire_corpus(verses: list, real_data: Dict[str, Dict[str, str]]) -> Tuple[list, dict]:
    """
    Wire real text into corpus using sequential index mapping.

    Each corpus entry at index i is mapped to the real Quran verse
    (surah, ayah) = sequential_mapping[i].

    The original synthetic surah/ayah/verse_key fields are REPLACED with
    the real Quranic references.
    """
    sequential_mapping = build_sequential_mapping()
    assert len(verses) == 6236, f"Expected 6236 verses, got {len(verses)}"

    stats = {"updated": 0, "not_found": 0, "total": len(verses)}
    not_found_keys: List[str] = []

    for idx, verse in enumerate(verses):
        real_surah, real_ayah = sequential_mapping[idx]
        real_key = f"{real_surah}:{real_ayah}"

        if real_key in real_data:
            entry = real_data[real_key]
            # Update the verse with real data
            verse["surah"] = real_surah
            verse["ayah"] = real_ayah
            verse["verse_key"] = real_key
            verse["arabic_text"] = entry["arabic"]
            verse["translation"] = entry["translation"]
            # SHA-256 integrity hash
            content = f"{verse['arabic_text']}:{verse['translation']}"
            verse["integrity_hash"] = hashlib.sha256(content.encode("utf-8")).hexdigest()
            stats["updated"] += 1
        else:
            not_found_keys.append(real_key)
            stats["not_found"] += 1

    if not_found_keys:
        print(f"  WARNING: {len(not_found_keys)} keys not found in API data. "
              f"Sample: {not_found_keys[:5]}")

    return verses, stats


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    print("=" * 60)
    print("BLOCKER 0: Wiring real Quranic text into corpus")
    print("=" * 60)

    if not CORPUS_PATH.exists():
        print(f"ERROR: Corpus not found at {CORPUS_PATH}")
        return 1

    # Load corpus from backup (ensure we start from synthetic state)
    backup_path = CORPUS_PATH.with_suffix(".json.synthetic_backup")
    if backup_path.exists():
        print(f"Loading from backup: {backup_path.name}")
        with open(backup_path, "r", encoding="utf-8") as f:
            raw = json.load(f)
    else:
        print(f"Loading corpus: {CORPUS_PATH.name}")
        with open(CORPUS_PATH, "r", encoding="utf-8") as f:
            raw = json.load(f)
        # Create backup
        shutil.copy2(CORPUS_PATH, backup_path)
        print(f"Backup saved: {backup_path.name}")

    is_dict = isinstance(raw, dict)
    verses = raw.get("verses", []) if is_dict else raw
    print(f"Corpus: {len(verses)} verses")

    if len(verses) != 6236:
        print(f"ERROR: Expected 6236 verses, got {len(verses)}")
        return 1

    # Fetch real data
    print("\nFetching real Quranic text from alquran.cloud...")
    try:
        real_data = fetch_all_verses()
    except Exception as e:
        print(f"ERROR: API fetch failed: {e}")
        return 1

    if len(real_data) < 6200:
        print(f"ERROR: Only fetched {len(real_data)} verses. Aborting.")
        return 1

    # Wire text using sequential mapping
    print("\nWiring real text into corpus (sequential index mapping)...")
    updated_verses, stats = wire_corpus(verses, real_data)
    print(f"  Updated: {stats['updated']}/{stats['total']}")
    print(f"  Not found: {stats['not_found']}")

    # Rebuild corpus
    if is_dict:
        raw["verses"] = updated_verses
        output = raw
    else:
        output = updated_verses

    # Save
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    print(f"\nSaved: {OUTPUT_PATH}")

    if stats["not_found"] > 0:
        print(f"WARNING: {stats['not_found']} verses could not be mapped.")
        return 1

    print("\nDONE. Run tests:")
    print("  python3 -m pytest quran/corpus_extraction/tests/test_corpus_text_wiring.py -v")
    return 0


if __name__ == "__main__":
    exit(main())
