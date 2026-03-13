"""
Islamic Tradition Adapter — NOMOS tradition plugin.

Wraps quran_core as a pluggable tradition adapter.
The Islamic implementations are preserved exactly in quran_core/;
this adapter exposes them through the universal TraditionAdapter interface.
"""

from typing import Any, Dict, List
from nomos.interfaces.protocols import TraditionAdapter


class IslamicTraditionAdapter(TraditionAdapter):
    """
    Plugs the Islamic/Quranic research layer (quran_core) into the
    universal NOMOS framework as one tradition among many.

    Norm types mapped to universal deontic:
        wajib (obligatory)   → "obligatory"
        mandub (recommended) → "recommended"
        mubah (permitted)    → "permitted"
        makruh (discouraged) → "discouraged"
        haram (forbidden)    → "prohibited"
    """

    DEONTIC_MAP = {
        "wajib": "obligatory",
        "fard": "obligatory",
        "mandub": "recommended",
        "mustahabb": "recommended",
        "mubah": "permitted",
        "halal": "permitted",
        "makruh": "discouraged",
        "haram": "prohibited",
        "forbidden": "prohibited",
    }

    MAQASID = [
        "preservation_of_religion",
        "preservation_of_life",
        "preservation_of_intellect",
        "preservation_of_lineage",
        "preservation_of_property",
    ]

    @property
    def name(self) -> str:
        return "islamic"

    def load_norms(self, domain: str = "general") -> List[Dict[str, Any]]:
        """Load norms from quran_core. Lazy import to avoid coupling."""
        # TODO: wire to quran_core.frontierqu.logic.deontic
        return []

    def resolve_conflict(self, norm_a: Dict, norm_b: Dict) -> Dict:
        """
        Islamic conflict resolution: temporal precedence (naskh).
        Later revelation supersedes earlier; specific overrides general.
        Wraps quran_core.neuro_symbolic.dag_naskh.naskh_solver.
        """
        # TODO: wire to quran_core.neuro_symbolic.dag_naskh
        return norm_b  # later norm wins by default

    def evaluate(self, action: Any, context: Any) -> float:
        """Score 0.0–1.0 using MaqasidOptimizer from quran_core."""
        # TODO: wire to quran_core.frontierqu.logic.deontic
        return 0.5

    def maqasid_weights(self) -> Dict[str, float]:
        """Return current maqasid objective weights."""
        return {m: 0.2 for m in self.MAQASID}
