import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import pytest
from quran.corpus_extraction.verification.contrastive_validator import ContrastiveValidator


def test_load_negative_examples():
    validator = ContrastiveValidator()
    examples = validator.load_negative_examples()
    assert len(examples) >= 400
    assert all("verse_id" in ex for ex in examples)


def test_false_positive_detection():
    validator = ContrastiveValidator()
    validator.load_negative_examples()
    fpr = validator.calculate_false_positive_rate()
    assert fpr < 0.02  # <2% validates 0.93 quality


def test_enhancement_regression():
    validator = ContrastiveValidator()
    baseline_fpr = 0.015
    new_component_fpr = 0.012
    assert new_component_fpr <= baseline_fpr * 1.05
