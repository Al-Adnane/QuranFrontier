"""
Q-SDK: Quran-Inspired Sciences Development Kit

The foundation of the "Quran Inspired Sciences" framework - extracting
mathematical and algorithmic principles from the Quran and implementing
them as real systems across all sectors (HealthTech, AgriTech, FinTech, etc.).

Core modules:
- mirah_models: Data structures for inheritance (Heir, InheritanceCase, etc.)
- mirah_core: Q4:11 inheritance algorithm implementation
- validation: Maqasid al-Shariah verification

Project Mirath-Chain (Phase 1): Q4:11 Inheritance Algorithm
- Library: Python implementation with full test coverage
- Smart Contract: Ethereum/Polygon Solidity implementation
- Governance: Dual-key council (2 engineers + 2 Islamic scholars)

Public API:
"""

from .mirah_models import (
    Relationship,
    Gender,
    HeritageDisqualification,
    MadhabSchool,
    ValidationStatus,
    Heir,
    Bequest,
    InheritanceCase,
    ShareDistribution,
    InheritanceDistributionResult,
)

from .mirah_core import (
    MirahAlgorithm,
    MirahAlgorithmError,
    NoQualifiedHeirsError,
    NegativeEstateError,
    create_inheritance_case_from_dict,
    calculate_q411_distribution,
)

from .validation import (
    MaqasidObjective,
    MaqasidValidationResult,
    MaqasidValidator,
)

__version__ = "1.0.0"
__author__ = "Dual-Key Governance Council"
__description__ = "Q4:11 Inheritance Algorithm (Foundation of Q-SDK)"

__all__ = [
    # Models
    "Relationship",
    "Gender",
    "HeritageDisqualification",
    "MadhabSchool",
    "ValidationStatus",
    "Heir",
    "Bequest",
    "InheritanceCase",
    "ShareDistribution",
    "InheritanceDistributionResult",
    # Algorithm
    "MirahAlgorithm",
    "MirahAlgorithmError",
    "NoQualifiedHeirsError",
    "NegativeEstateError",
    "create_inheritance_case_from_dict",
    "calculate_q411_distribution",
    # Validation
    "MaqasidObjective",
    "MaqasidValidationResult",
    "MaqasidValidator",
]
