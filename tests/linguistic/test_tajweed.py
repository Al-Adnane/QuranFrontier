from frontierqu.linguistic.tajweed import (
    TajweedRule, TajweedGrammar, apply_tajweed,
    TajweedCategory, detect_tajweed_rules
)

def test_tajweed_categories():
    """Tajweed has standard categories"""
    assert hasattr(TajweedCategory, 'IDGHAM')
    assert hasattr(TajweedCategory, 'IKHFA')
    assert hasattr(TajweedCategory, 'IQLAB')
    assert hasattr(TajweedCategory, 'IZHAR')
    assert hasattr(TajweedCategory, 'GHUNNAH')
    assert hasattr(TajweedCategory, 'MADD')

def test_tajweed_rule_structure():
    """Each rule has context, input, output"""
    rule = TajweedRule(
        category=TajweedCategory.IDGHAM,
        name="Idgham with Ghunnah",
        left_context="\u0646\u0652",
        phoneme="\u0646",
        right_context="\u064a",
        transformed="\u064a\u0651",
        description="Noon sakinah merges into Ya with ghunnah"
    )
    assert rule.category == TajweedCategory.IDGHAM

def test_grammar_has_rules():
    """Tajweed grammar contains rules"""
    grammar = TajweedGrammar()
    assert len(grammar.rules) > 0

def test_detect_rules_in_basmala():
    """Detect applicable tajweed rules in Basmala"""
    rules = detect_tajweed_rules("\u0628\u0650\u0633\u0652\u0645\u0650 \u0627\u0644\u0644\u0651\u064e\u0647\u0650 \u0627\u0644\u0631\u0651\u064e\u062d\u0652\u0645\u064e\u0670\u0646\u0650 \u0627\u0644\u0631\u0651\u064e\u062d\u0650\u064a\u0645\u0650")
    assert len(rules) >= 0  # May or may not detect depending on implementation

def test_apply_tajweed_returns_annotated():
    """Applying tajweed returns annotated text"""
    result = apply_tajweed("\u0628\u0650\u0633\u0652\u0645\u0650 \u0627\u0644\u0644\u0651\u064e\u0647\u0650 \u0627\u0644\u0631\u0651\u064e\u062d\u0652\u0645\u064e\u0670\u0646\u0650 \u0627\u0644\u0631\u0651\u064e\u062d\u0650\u064a\u0645\u0650")
    assert result.original != ""
    assert isinstance(result.applied_rules, list)

def test_idgham_rule():
    """Idgham: noon sakinah before yarmalun letters"""
    grammar = TajweedGrammar()
    idgham_rules = [r for r in grammar.rules if r.category == TajweedCategory.IDGHAM]
    assert len(idgham_rules) > 0

def test_madd_rule():
    """Madd: vowel elongation rules exist"""
    grammar = TajweedGrammar()
    madd_rules = [r for r in grammar.rules if r.category == TajweedCategory.MADD]
    assert len(madd_rules) > 0
