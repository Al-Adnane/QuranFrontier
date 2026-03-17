"""
P4: Remove and demote scientifically overclaimed verse-to-concept mappings.

Removes:
- 105:1-5  -> pest population dynamics (historical narrative, not biology)
- 9:14     -> immunotherapy (spiritual healing metaphor)
- 2:10     -> mental health/clinical psychiatry (moral/spiritual context)

Demotes to Tier 3 (adds tier: 3, confidence_ceiling: 0.60):
- 86:1, 86:2, 86:3  -- pulsars claim
- 79:30             -- egg-shape of Earth claim

Also adds Q105:1-5 to negative_examples.json.
"""

import json
from pathlib import Path

WORKTREE = Path(__file__).parent.parent.parent.parent
VTC_PATH = WORKTREE / "quran/corpus_extraction/ontology/verse_to_concepts.json"
VTC_REAL_PATH = WORKTREE / "quran/corpus_extraction/ontology/verse_to_concepts_real.json"
NEG_PATH = WORKTREE / "quran/corpus_extraction/data/negative_examples.json"

REMOVE_VERSES = ['105:1', '105:2', '105:3', '105:4', '105:5', '9:14', '2:10']
DEMOTE_VERSES = ['86:1', '86:2', '86:3', '79:30']


def remove_overclaims():
    with open(VTC_PATH, encoding='utf-8') as f:
        data = json.load(f)

    # verse_to_concepts.json uses a list under 'verse_concept_mappings'
    mappings_list = data.get('verse_concept_mappings', [])

    removed = []
    demoted = []
    kept = []

    for entry in mappings_list:
        verse_id = entry.get('verse_id', '')
        if verse_id in REMOVE_VERSES:
            removed.append(verse_id)
            # skip (do not add to kept)
            continue

        if verse_id in DEMOTE_VERSES:
            concepts = entry.get('concepts', [])
            for c in concepts:
                if isinstance(c, dict):
                    c['tier'] = 3
                    c['confidence_ceiling'] = 0.60
                    c['overclaim_flag'] = True
            demoted.append(verse_id)

        kept.append(entry)

    data['verse_concept_mappings'] = kept

    print(f"Removed: {removed}")
    print(f"Demoted to Tier 3: {demoted}")

    with open(VTC_PATH, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    # Add Q105 to negative examples
    with open(NEG_PATH, encoding='utf-8') as f:
        neg_data = json.load(f)

    neg_examples = neg_data.get('negative_examples', neg_data) if isinstance(neg_data, dict) else neg_data

    for i in range(1, 6):
        neg_examples.append({
            "verse_id": f"105:{i}",
            "category": "historical_narrative",
            "reason": (
                "Q105 describes Abrahah's army (historical event), not a scientific principle "
                "about pest population dynamics. Common overclaim in popular Islamic science literature."
            )
        })

    if isinstance(neg_data, dict):
        neg_data['negative_examples'] = neg_examples
        out = neg_data
    else:
        out = neg_examples

    with open(NEG_PATH, 'w', encoding='utf-8') as f:
        json.dump(out, f, ensure_ascii=False, indent=2)

    print("Added Q105 (5 verses) to negative_examples.json")

    # Also remove overclaims from verse_to_concepts_real.json
    remove_overclaims_from_real()


def remove_overclaims_from_real():
    """Remove overclaimed verse entries from verse_to_concepts_real.json."""
    with open(VTC_REAL_PATH, encoding='utf-8') as f:
        data = json.load(f)

    # verse_to_concepts_real.json uses a dict under 'mappings' key
    mappings = data.get('mappings', data) if isinstance(data, dict) else data

    removed = []
    for verse_key in REMOVE_VERSES:
        if verse_key in mappings:
            del mappings[verse_key]
            removed.append(verse_key)

    print(f"Removed from verse_to_concepts_real.json: {removed}")

    with open(VTC_REAL_PATH, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"Saved updated verse_to_concepts_real.json")


if __name__ == '__main__':
    remove_overclaims()
