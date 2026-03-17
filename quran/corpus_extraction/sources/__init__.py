"""
Sources layer for semantic discovery and integration.
Provides API wrappers for Semantic Scholar and CrossRef to discover peer-reviewed
papers and preprints for scientific concepts extracted from the Quran.
"""

from .semantic_scholar_client import SemanticScholarClient
from .crossref_client import CrossRefClient
from .source_discovery import SourceDiscovery

__all__ = [
    'SemanticScholarClient',
    'CrossRefClient',
    'SourceDiscovery'
]
