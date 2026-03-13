"""
NOMOS Tradition Registry.

Each tradition adapter plugs the universal NOMOS pipeline into a
specific ethical/legal reasoning framework.

Available adapters:
    islamic     — IslamicTraditionAdapter (wraps quran_core)
    utilitarian — UtilitarianAdapter
    kantian     — KantianAdapter

Usage:
    from nomos.traditions import get_tradition
    adapter = get_tradition("islamic")
    norms = adapter.load_norms(domain="finance")
"""

from nomos.traditions.islamic_adapter import IslamicTraditionAdapter
from nomos.traditions.utilitarian_adapter import UtilitarianAdapter
from nomos.traditions.kantian_adapter import KantianAdapter

REGISTRY = {
    "islamic": IslamicTraditionAdapter,
    "utilitarian": UtilitarianAdapter,
    "kantian": KantianAdapter,
    # TODO: virtue_ethics, care_ethics, contractarian, confucian, ubuntu, ...
}


def get_tradition(name: str):
    """Get a tradition adapter instance by name."""
    cls = REGISTRY.get(name)
    if cls is None:
        raise ValueError(f"Unknown tradition '{name}'. Available: {list(REGISTRY.keys())}")
    return cls()


def list_traditions():
    return list(REGISTRY.keys())
