import json
import os
from typing import List, Dict
from pathlib import Path


class ContrastiveValidator:
    """
    Contrastive Verification System for establishing baseline false-positive rate.

    This validates that the extraction system doesn't incorrectly identify
    non-scientific verses as containing scientific content.
    """

    def __init__(self):
        """Initialize the ContrastiveValidator with baseline FPR."""
        self.negative_examples: List[Dict] = []
        self.baseline_fpr: float = 0.0
        self._data_path = Path(__file__).parent.parent / "data" / "negative_examples.json"

    def load_negative_examples(self) -> List[Dict]:
        """
        Load 500 verified non-scientific verses from JSON file.

        Returns:
            List[Dict]: List of negative examples with verse_id, text_ar, category, reason
        """
        # Try to load from JSON file
        if self._data_path.exists():
            try:
                with open(self._data_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.negative_examples = data.get('negative_examples', [])
            except (json.JSONDecodeError, IOError):
                # Fall back to default examples if file read fails
                self._set_default_examples()
        else:
            # Use default examples if file doesn't exist
            self._set_default_examples()

        return self.negative_examples

    def _set_default_examples(self) -> None:
        """Set default negative examples if JSON file is unavailable."""
        self.negative_examples = [
            {
                "verse_id": "1:1",
                "text_ar": "بسم الله الرحمن الرحيم",
                "category": "invocation",
                "reason": "Purely invocational - Basmala"
            },
            {
                "verse_id": "1:5",
                "text_ar": "إياك نعبد وإياك نستعين",
                "category": "invocation",
                "reason": "Purely devotional supplication"
            },
            {
                "verse_id": "1:6",
                "text_ar": "اهدنا الصراط المستقيم",
                "category": "emotional",
                "reason": "Supplication for guidance"
            },
            {
                "verse_id": "4:11",
                "text_ar": "يوصيكم الله في أولادكم للذكر مثل حظ الأنثيين",
                "category": "legal",
                "reason": "Legal prescription for inheritance"
            },
            {
                "verse_id": "2:34",
                "text_ar": "وإذ قلنا للملائكة اسجدوا لآدم",
                "category": "narrative",
                "reason": "Religious narrative without scientific content"
            }
        ]

    def calculate_false_positive_rate(self) -> float:
        """
        Calculate false positive rate by running extraction on negative examples.

        For MVP: Returns mocked FPR value. In production, this would run the
        extraction system on negative examples and calculate the rate of false
        positives (verses incorrectly identified as scientific).

        Returns:
            float: False positive rate (0.0 to 1.0)
        """
        # MVP: Return baseline FPR value
        # In production, this would:
        # 1. Run extraction on all negative examples
        # 2. Count how many are incorrectly flagged as scientific
        # 3. Return: false_positives / total_negatives

        self.baseline_fpr = 0.0
        return self.baseline_fpr

    def validate_component(self, name: str, fpr: float) -> bool:
        """
        Validate that a component's FPR is below acceptable threshold.

        Args:
            name: Component name for logging/tracking
            fpr: False positive rate for the component

        Returns:
            bool: True if FPR < 1%, False otherwise
        """
        threshold = 0.01  # 1% threshold
        is_valid = fpr < threshold
        return is_valid
