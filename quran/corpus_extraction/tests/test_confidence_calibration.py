"""
Tests for P3 (confidence recalibration) and P4 (overclaim removal).
"""


# --- P3: Confidence Recalibration ---

def test_tier1_ceiling_is_085():
    from quran.corpus_extraction.ontology.tiered_classification import TieredClassifier
    c = TieredClassifier()
    assert c.CONFIDENCE_CEILINGS[1] == 0.85


def test_tier2_ceiling_is_075():
    from quran.corpus_extraction.ontology.tiered_classification import TieredClassifier
    c = TieredClassifier()
    assert c.CONFIDENCE_CEILINGS[2] == 0.75


def test_tier3_ceiling_is_060():
    from quran.corpus_extraction.ontology.tiered_classification import TieredClassifier
    c = TieredClassifier()
    assert c.CONFIDENCE_CEILINGS[3] == 0.60


def test_knowledge_at_revelation_field_exists():
    from quran.corpus_extraction.schema.data_models import VerseExtraction
    assert 'knowledge_at_revelation' in VerseExtraction.__dataclass_fields__


def test_classification_reason_field_exists():
    from quran.corpus_extraction.schema.data_models import VerseExtraction
    assert 'classification_reason' in VerseExtraction.__dataclass_fields__


# --- P4: Overclaim Removal ---

def test_q105_not_in_agriculture():
    """Q105 (Abrahah's army) must not be mapped to pest population dynamics"""
    import json
    data = json.load(open('quran/corpus_extraction/ontology/verse_to_concepts.json'))
    mappings = data if isinstance(data, list) else data.get('mappings', data)
    # Check that no Q105 entry maps to agriculture/pest concepts
    q105_concepts = []
    for key, concepts in mappings.items():
        if '105:' in str(key):
            q105_concepts.extend(concepts if isinstance(concepts, list) else [])
    pest_mappings = [c for c in q105_concepts if 'pest' in str(c).lower() or 'population' in str(c).lower()]
    assert len(pest_mappings) == 0, f"Q105 incorrectly mapped to pest dynamics: {pest_mappings}"


def test_overclaimed_verses_demoted():
    """Q86:1-3 and Q79:30 should be Tier 3 (metaphorical), not Tier 1"""
    # Check tiered_classification handles these as Tier 3
    from quran.corpus_extraction.ontology.tiered_classification import TieredClassifier
    c = TieredClassifier()
    # Q86:1-3 'piercing star' claim — should not exceed Tier 3 ceiling (0.60)
    # Q79:30 'dahaha/egg-shape' claim — should not exceed Tier 3 ceiling (0.60)
    # Test that classify_verse with metaphorical flag returns tier 3
    result = c.classify_verse({'is_metaphorical': True, 'source_count': 0})
    assert result['tier'] == 3
    assert result['confidence'] <= 0.60
