"""
Pytest configuration for ontology tests
"""

import sys
from pathlib import Path

# Add ontology directory to sys.path so tests can import modules directly
ontology_dir = Path(__file__).parent
if str(ontology_dir) not in sys.path:
    sys.path.insert(0, str(ontology_dir))
