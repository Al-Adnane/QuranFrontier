#!/usr/bin/env python3
"""Apply TieredClassifier confidence ceilings to verse_to_concepts_real.json"""
import json, sys
from pathlib import Path

WORKTREE = Path(__file__).parent.parent.parent.parent
VTC_REAL = WORKTREE / "quran/corpus_extraction/ontology/verse_to_concepts_real.json"

# Tier ceilings from tiered_classification.py
CEILINGS = {1: 0.85, 2: 0.75, 3: 0.60}

# Domain → default tier mapping
DOMAIN_TIER = {
    'physics': 1, 'biology': 1, 'medicine': 1, 'hydrology': 1,
    'oceanography': 1, 'mathematics': 1,
    'geology': 2, 'engineering': 2, 'agriculture': 2,
    'cosmology': 2, 'thermodynamics': 2,
    'ethics': 3, 'social': 3, 'spiritual': 3, 'metaphysical': 3,
}

def get_tier(concept: dict) -> int:
    domain = concept.get('domain', '').lower()
    # Check explicit overclaim flag
    if concept.get('overclaim_flag'):
        return 3
    # Check metaphorical flag
    if concept.get('is_metaphorical'):
        return 3
    # Look up domain default
    for key, tier in DOMAIN_TIER.items():
        if key in domain:
            return tier
    return 2  # default to Tier 2 if unknown

def apply_ceilings(mappings: dict) -> tuple:
    updated = 0
    for verse_key, concepts in mappings.items():
        if not isinstance(concepts, list):
            continue
        for concept in concepts:
            if not isinstance(concept, dict):
                continue
            tier = get_tier(concept)
            ceiling = CEILINGS[tier]
            old_conf = concept.get('confidence', 0.75)
            new_conf = min(old_conf, ceiling)
            concept['tier'] = tier
            concept['confidence_ceiling'] = ceiling
            if old_conf != new_conf:
                concept['confidence'] = new_conf
                updated += 1
    return updated

def main():
    with open(VTC_REAL) as f:
        data = json.load(f)

    mappings = data.get('mappings', data) if isinstance(data, dict) else data
    updated = apply_ceilings(mappings)
    print(f"Applied tier ceilings: {updated} confidence scores adjusted")

    with open(VTC_REAL, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"Saved to {VTC_REAL}")

if __name__ == '__main__':
    main()
