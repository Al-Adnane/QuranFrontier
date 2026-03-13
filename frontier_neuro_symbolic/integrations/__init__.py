"""Cross-Subsystem Integrations for FrontierQu.

Five high-value integration modules that bridge subsystem boundaries:

1. hrr_qiraat_binding     — HRR holographic memory for 7 Qiraat readings
2. moe_three_world        — MoE sparse gating for Three-World Architecture
3. temporal_substrate_sync — Gamma-synchronized substrate orchestration
4. hott_naskh_evolution    — HoTT type evolution for abrogation (naskh)
5. dream_tajweed_generator — Novel tajweed pattern discovery via PDE dreaming
"""

# Lazy imports to handle optional dependencies (Z3, etc.)
import importlib as _il

def __getattr__(name):
    _mapping = {
        "QiraatHolographicBinding": (".hrr_qiraat_binding", "QiraatHolographicBinding"),
        "ReadingVariant": (".hrr_qiraat_binding", "ReadingVariant"),
        "BoundReadingSet": (".hrr_qiraat_binding", "BoundReadingSet"),
        "RetrievalResult": (".hrr_qiraat_binding", "RetrievalResult"),
        "MoEThreeWorldRouter": (".moe_three_world", "MoEThreeWorldRouter"),
        "WorldRoutingResult": (".moe_three_world", "WorldRoutingResult"),
        "GammaSynchronizedOrchestrator": (".temporal_substrate_sync", "GammaSynchronizedOrchestrator"),
        "SubstrateHealth": (".temporal_substrate_sync", "SubstrateHealth"),
        "SynchronizedMoment": (".temporal_substrate_sync", "SynchronizedMoment"),
        "NaskhTypeEvolution": (".hott_naskh_evolution", "NaskhTypeEvolution"),
        "NaskhEvolutionEvent": (".hott_naskh_evolution", "NaskhEvolutionEvent"),
        "TypeEvolutionChain": (".hott_naskh_evolution", "TypeEvolutionChain"),
        "TajweedDreamGenerator": (".dream_tajweed_generator", "TajweedDreamGenerator"),
        "DreamPattern": (".dream_tajweed_generator", "DreamPattern"),
        "DreamSession": (".dream_tajweed_generator", "DreamSession"),
    }
    if name in _mapping:
        mod_name, attr = _mapping[name]
        mod = _il.import_module(mod_name, __name__)
        return getattr(mod, attr)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

__all__ = [
    "QiraatHolographicBinding", "ReadingVariant", "BoundReadingSet", "RetrievalResult",
    "MoEThreeWorldRouter", "WorldRoutingResult",
    "GammaSynchronizedOrchestrator", "SubstrateHealth", "SynchronizedMoment",
    "NaskhTypeEvolution", "NaskhEvolutionEvent", "TypeEvolutionChain",
    "TajweedDreamGenerator", "DreamPattern", "DreamSession",
]
