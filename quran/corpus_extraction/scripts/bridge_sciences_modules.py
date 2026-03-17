"""
BLOCKER 2: Bridge sciences modules and knowledge-graph into corpus concepts.

This script combines:
1. quran/corpus_extraction/ontology/verse_to_concepts.json (2236 real mappings already)
2. quran/corpus_extraction/ontology/scientific_concepts.json (quranic_references per concept)
3. quran/sciences/principles/*.json (named principles with quranic_reference fields)

Output: quran/corpus_extraction/ontology/verse_to_concepts_real.json
"""

import json
import re
from pathlib import Path

# Paths — try worktree first, then main repo
WORKTREE = Path(__file__).parent.parent.parent.parent

CORPUS_ONTOLOGY = WORKTREE / "quran" / "corpus_extraction" / "ontology"
SCIENTIFIC_CONCEPTS_JSON = CORPUS_ONTOLOGY / "scientific_concepts.json"
EXISTING_VTC_JSON = CORPUS_ONTOLOGY / "verse_to_concepts.json"
OUTPUT = CORPUS_ONTOLOGY / "verse_to_concepts_real.json"

# Knowledge-graph mappings (concept_N ids, but useful themes)
KG_MAPPINGS = WORKTREE / "quran" / "knowledge-graph" / "verse_concept_mappings_enhanced.json"
if not KG_MAPPINGS.exists():
    KG_MAPPINGS = Path(
        "/Users/mac/Desktop/QuranFrontier/quran/knowledge-graph/verse_concept_mappings_enhanced.json"
    )

# Sciences principles directory
PRINCIPLES_DIR = WORKTREE / "quran" / "sciences" / "principles"
if not PRINCIPLES_DIR.exists():
    PRINCIPLES_DIR = Path(
        "/Users/mac/Desktop/QuranFrontier/quran/sciences/principles"
    )

# Regex to detect synthetic placeholder concept names/ids
SYNTHETIC_PATTERN = re.compile(r"^concept_\d+(_\w+)?$", re.IGNORECASE)

# Parse verse references like "Q39:5", "Q55:7-9", "2:164", "Q40:64, Q29:20"
VERSE_REF_PATTERN = re.compile(r"Q?(\d+):(\d+)(?:-(\d+))?")


def normalize_verse_key(surah: int, ayah: int) -> str:
    """Normalize to 'surah:ayah' format."""
    return f"{surah}:{ayah}"


def parse_quranic_reference(ref_str: str) -> list:
    """
    Parse a quranic_reference string (may contain multiple refs, ranges).
    Returns list of 'surah:ayah' strings.
    """
    verse_keys = []
    for match in VERSE_REF_PATTERN.finditer(ref_str):
        surah = int(match.group(1))
        start_ayah = int(match.group(2))
        end_ayah = int(match.group(3)) if match.group(3) else start_ayah
        for ayah in range(start_ayah, end_ayah + 1):
            verse_keys.append(normalize_verse_key(surah, ayah))
    return verse_keys


def load_existing_vtc(path: Path) -> dict:
    """
    Load existing verse_to_concepts.json and convert to
    {verse_key: [list of concept dicts]} with real concept info.
    """
    verse_map = {}
    if not path.exists():
        print(f"  WARNING: {path} not found")
        return verse_map

    with open(path, encoding="utf-8") as f:
        data = json.load(f)

    mappings = data.get("verse_concept_mappings", [])
    for entry in mappings:
        verse_id = entry.get("verse_id", "")
        concepts = entry.get("concepts", [])
        if not verse_id or not concepts:
            continue

        # Filter out any synthetic concept ids (safety check)
        real_concepts = []
        for c in concepts:
            cid = c.get("concept_id", "")
            cname = c.get("concept_name", "")
            if SYNTHETIC_PATTERN.match(cid):
                continue  # skip synthetic
            if not cname or re.match(r"^[Cc]oncept\s+\d+$", cname):
                continue  # skip placeholder names
            real_concepts.append({
                "concept_id": cid,
                "concept_name": cname,
                "domain": c.get("domain", "general"),
                "confidence": c.get("mapping_confidence", c.get("confidence", 0.8)),
                "source": "corpus_extraction_ontology",
            })

        if real_concepts:
            if verse_id not in verse_map:
                verse_map[verse_id] = []
            verse_map[verse_id].extend(real_concepts)

    print(f"  Loaded {len(verse_map)} verses from existing verse_to_concepts.json")
    return verse_map


def load_scientific_concepts_refs(path: Path) -> dict:
    """
    Load scientific_concepts.json and build verse -> concepts map
    from the quranic_references field on each concept.
    """
    verse_map = {}
    if not path.exists():
        print(f"  WARNING: {path} not found")
        return verse_map

    with open(path, encoding="utf-8") as f:
        data = json.load(f)

    concepts = data.get("concepts", [])
    added = 0
    for concept in concepts:
        cid = concept.get("id", "")
        cname = concept.get("name", "")
        domain = concept.get("domain", "general")
        confidence = concept.get("confidence", 0.85)
        refs = concept.get("quranic_references", [])

        if not refs:
            continue
        if SYNTHETIC_PATTERN.match(cid) or re.match(r"^[Cc]oncept\s+\d+$", cname):
            continue

        for verse_key in refs:
            # Normalize: might already be '2:164' format
            if not re.match(r"^\d+:\d+$", verse_key):
                parsed = parse_quranic_reference(verse_key)
                keys_to_add = parsed
            else:
                keys_to_add = [verse_key]

            for vk in keys_to_add:
                if vk not in verse_map:
                    verse_map[vk] = []
                verse_map[vk].append({
                    "concept_id": cid,
                    "concept_name": cname,
                    "domain": domain,
                    "confidence": confidence,
                    "source": "scientific_concepts_json",
                })
                added += 1

    print(f"  Loaded {len(verse_map)} verses from scientific_concepts.json "
          f"({added} concept-verse pairs)")
    return verse_map


def load_principles_files(principles_dir: Path) -> dict:
    """
    Load all principles JSON files from sciences/principles/ and extract
    verse-concept mappings from quranic_reference fields.
    """
    verse_map = {}
    if not principles_dir.exists():
        print(f"  WARNING: Principles dir not found: {principles_dir}")
        return verse_map

    principle_files = list(principles_dir.glob("*.json"))
    total_principles = 0

    for fpath in principle_files:
        # Derive domain from filename (physics_principles.json -> physics)
        domain = fpath.stem.replace("_principles", "").replace("_", " ")

        with open(fpath, encoding="utf-8") as f:
            data = json.load(f)

        principles = data.get("principles", [])
        total_principles += len(principles)

        for principle in principles:
            pid = principle.get("id", "")
            name = principle.get("name", "")
            if not name:
                continue

            # Build a clean concept_id from the principle name
            concept_id = pid.lower() if pid else name.lower().replace(" ", "_").replace(
                "(", ""
            ).replace(")", "").replace("-", "_")[:50]

            confidence = principle.get("confidence", 0.82)
            domains = principle.get("domains", [domain])
            primary_domain = domains[0] if domains else domain

            # Parse quranic_reference (may have multiple refs)
            qref = principle.get("quranic_reference", "")
            if not qref:
                continue

            verse_keys = parse_quranic_reference(qref)
            for vk in verse_keys:
                if vk not in verse_map:
                    verse_map[vk] = []
                verse_map[vk].append({
                    "concept_id": concept_id,
                    "concept_name": name,
                    "domain": primary_domain,
                    "confidence": confidence,
                    "source": f"principles_json:{fpath.name}",
                })

    print(f"  Loaded principles from {len(principle_files)} files "
          f"({total_principles} principles, {len(verse_map)} verses)")
    return verse_map


def merge_verse_maps(*maps: dict) -> dict:
    """
    Merge multiple {verse_key: [concepts]} dicts.
    Deduplicate by concept_id within each verse.
    """
    combined = {}
    for verse_map in maps:
        for verse_key, concepts in verse_map.items():
            if verse_key not in combined:
                combined[verse_key] = []
            # Deduplicate by concept_id
            existing_ids = {c["concept_id"] for c in combined[verse_key]}
            for concept in concepts:
                if concept["concept_id"] not in existing_ids:
                    combined[verse_key].append(concept)
                    existing_ids.add(concept["concept_id"])
    return combined


def validate_output(verse_map: dict) -> dict:
    """Run basic validation and return stats."""
    total_verses = len(verse_map)
    total_concept_assignments = sum(len(v) for v in verse_map.values())
    domains = set()
    synthetic_count = 0
    for verse_key, concepts in verse_map.items():
        for c in concepts:
            domains.add(c.get("domain", ""))
            if SYNTHETIC_PATTERN.match(c.get("concept_id", "")):
                synthetic_count += 1

    return {
        "total_verses": total_verses,
        "total_concept_assignments": total_concept_assignments,
        "domains": sorted(d for d in domains if d),
        "synthetic_concepts": synthetic_count,
    }


def main():
    print("=" * 60)
    print("BLOCKER 2: Bridging sciences modules into corpus concepts")
    print("=" * 60)

    # Step 1: Load from existing verse_to_concepts.json (primary source — 2236 real mappings)
    print("\n[1] Loading existing corpus_extraction ontology mappings...")
    vtc_map = load_existing_vtc(EXISTING_VTC_JSON)

    # Step 2: Load from scientific_concepts.json quranic_references
    print("\n[2] Loading from scientific_concepts.json quranic_references...")
    sc_map = load_scientific_concepts_refs(SCIENTIFIC_CONCEPTS_JSON)

    # Step 3: Load from sciences/principles/*.json
    print("\n[3] Loading from sciences/principles/ files...")
    principles_map = load_principles_files(PRINCIPLES_DIR)

    # Step 4: Merge all sources
    print("\n[4] Merging all sources...")
    verse_map = merge_verse_maps(vtc_map, sc_map, principles_map)
    print(f"  Combined: {len(verse_map)} unique verses with real concepts")

    # Step 5: Validate
    print("\n[5] Validating output...")
    stats = validate_output(verse_map)
    print(f"  Total verses: {stats['total_verses']}")
    print(f"  Total concept assignments: {stats['total_concept_assignments']}")
    print(f"  Domains represented: {stats['domains']}")
    print(f"  Synthetic concept IDs (should be 0): {stats['synthetic_concepts']}")

    if stats["total_verses"] < 500:
        print(f"  WARNING: Only {stats['total_verses']} verses — need >= 500")
    if stats["synthetic_concepts"] > 0:
        print(f"  ERROR: Found {stats['synthetic_concepts']} synthetic concept IDs!")

    # Step 6: Write output
    output = {
        "version": "2.0-real",
        "source": "corpus_extraction/ontology + scientific_concepts + sciences/principles",
        "generated": "2026-03-17",
        "verse_count": stats["total_verses"],
        "total_concept_assignments": stats["total_concept_assignments"],
        "domains": stats["domains"],
        "mappings": verse_map,
    }

    with open(OUTPUT, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"\n[6] Saved to {OUTPUT}")
    print(f"    Size: {OUTPUT.stat().st_size / 1024:.1f} KB")
    print("\nDone.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
