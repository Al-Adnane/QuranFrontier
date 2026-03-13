"""Derived Algebraic Geometry for Naskh Solver.

This module implements a sophisticated framework for detecting Quranic abrogation
(naskh) using derived algebraic geometry. The key components are:

1. **Derived Stacks** (stacks.py): Represent verses and their interpretations
   as points in derived algebraic geometric spaces

2. **Cohomology Computation** (cohomology.py): Compute topological and
   homological invariants of interpretation spaces

3. **Naskh Solver** (naskh_solver.py): Main solver that detects abrogation
   by computing derived intersections

Mathematical Framework:
- Verses are embedded in a derived stack (algebraic geometric space)
- Naskh (abrogation) is modeled as a derived intersection
- Homological memory preserves the "trace" of abrogated verses
- Cohomological methods detect semantic coherence and abrogation patterns
"""

from .stacks import DerivedStack, DerivedPoint
from .cohomology import CohomologyComputer, BettiAnalyzer
from .naskh_solver import NaskhSolver

__all__ = [
    "DerivedStack",
    "DerivedPoint",
    "CohomologyComputer",
    "BettiAnalyzer",
    "NaskhSolver",
]

__version__ = "1.0.0"
__description__ = "Derived Algebraic Geometry for Quranic Naskh (Abrogation) Solver"
