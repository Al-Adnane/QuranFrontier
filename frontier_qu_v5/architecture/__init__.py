"""
FrontierQu v6.0 Year 2 — Architectural Extensions
Inter-substrate entanglement, consensus, lifecycle, emergent language,
formal verification, self-modifying HoTT types.
"""
from .entanglement import EntanglementProtocol
from .consensus import ByzantineConsensus
from .lifecycle import SubstrateLifecycle
from .emergent_language import EmergentLanguage
from .self_modifying_hott import SelfModifyingHoTT

__all__ = [
    'EntanglementProtocol',
    'ByzantineConsensus',
    'SubstrateLifecycle',
    'EmergentLanguage',
    'SelfModifyingHoTT',
]
