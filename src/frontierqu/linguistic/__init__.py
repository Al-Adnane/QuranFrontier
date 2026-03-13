"""Quranic linguistic analysis modules.

- tashkeel: Arabic diacritics analysis (harakat, tanwin, shadda, sukun)
- ner: Named Entity Recognition for Quranic entities (prophets, places, angels, events)
- discourse: Discourse coherence and thematic transition analysis (munasabat)
"""

from .tashkeel import TashkeelAnalyzer
from .ner import QuranicNER
from .discourse import DiscourseAnalyzer

__all__ = [
    "TashkeelAnalyzer",
    "QuranicNER",
    "DiscourseAnalyzer",
]
