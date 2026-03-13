"""Isnad (Transmission Chains) as Directed Acyclic Graph.

The science of hadith authentication modeled as a weighted DAG:
    Nodes = narrators with reliability scores
    Edges = "narrated from" with grade weights
    Chain evaluation = min(narrator reliability scores)
"""
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import List, Dict, Optional, Tuple, Set


class ReliabilityGrade(Enum):
    SAHIH = auto()      # Authentic (highest)
    HASAN = auto()      # Good
    DAIF = auto()       # Weak
    MAWDU = auto()      # Fabricated (lowest)


class NarratorRank(Enum):
    SAHABI = auto()      # Companion of the Prophet
    TABII = auto()       # Successor (met Companions)
    TABA_TABII = auto()  # Successor of Successors
    MUHADDITH = auto()   # Hadith scholar
    COLLECTOR = auto()   # Hadith collection compiler


GRADE_SCORES = {
    ReliabilityGrade.SAHIH: 1.0,
    ReliabilityGrade.HASAN: 0.7,
    ReliabilityGrade.DAIF: 0.3,
    ReliabilityGrade.MAWDU: 0.0,
}


@dataclass
class Narrator:
    name: str
    arabic_name: str
    rank: NarratorRank
    reliability: float         # 0-1 scholarly assessment
    death_year_ah: Optional[int] = None
    narrations_count: int = 0


# Major narrators in hadith science
KNOWN_NARRATORS = {
    "Abu Hurayrah": Narrator("Abu Hurayrah", "\u0623\u0628\u0648 \u0647\u0631\u064a\u0631\u0629", NarratorRank.SAHABI, 0.95, 59, 5374),
    "Aisha": Narrator("Aisha", "\u0639\u0627\u0626\u0634\u0629", NarratorRank.SAHABI, 0.98, 58, 2210),
    "Ibn Umar": Narrator("Ibn Umar", "\u0627\u0628\u0646 \u0639\u0645\u0631", NarratorRank.SAHABI, 0.97, 73, 2630),
    "Anas ibn Malik": Narrator("Anas ibn Malik", "\u0623\u0646\u0633 \u0628\u0646 \u0645\u0627\u0644\u0643", NarratorRank.SAHABI, 0.95, 93, 2286),
    "Ibn Abbas": Narrator("Ibn Abbas", "\u0627\u0628\u0646 \u0639\u0628\u0627\u0633", NarratorRank.SAHABI, 0.97, 68, 1660),
    "Ibn Shihab": Narrator("Ibn Shihab al-Zuhri", "\u0627\u0628\u0646 \u0634\u0647\u0627\u0628 \u0627\u0644\u0632\u0647\u0631\u064a", NarratorRank.TABII, 0.95, 124, 2000),
    "Nafi'": Narrator("Nafi' mawla Ibn Umar", "\u0646\u0627\u0641\u0639 \u0645\u0648\u0644\u0649 \u0627\u0628\u0646 \u0639\u0645\u0631", NarratorRank.TABII, 0.93, 117, 800),
    "Al-Hasan al-Basri": Narrator("Al-Hasan al-Basri", "\u0627\u0644\u062d\u0633\u0646 \u0627\u0644\u0628\u0635\u0631\u064a", NarratorRank.TABII, 0.85, 110, 500),
    "Malik": Narrator("Malik ibn Anas", "\u0645\u0627\u0644\u0643 \u0628\u0646 \u0623\u0646\u0633", NarratorRank.TABA_TABII, 0.98, 179, 1720),
    "Sufyan al-Thawri": Narrator("Sufyan al-Thawri", "\u0633\u0641\u064a\u0627\u0646 \u0627\u0644\u062b\u0648\u0631\u064a", NarratorRank.TABA_TABII, 0.95, 161, 1500),
    "Al-Bukhari": Narrator("Al-Bukhari", "\u0627\u0644\u0628\u062e\u0627\u0631\u064a", NarratorRank.COLLECTOR, 0.99, 256, 7275),
    "Muslim": Narrator("Muslim ibn al-Hajjaj", "\u0645\u0633\u0644\u0645 \u0628\u0646 \u0627\u0644\u062d\u062c\u0627\u062c", NarratorRank.COLLECTOR, 0.98, 261, 3033),
    "Abu Dawud": Narrator("Abu Dawud", "\u0623\u0628\u0648 \u062f\u0627\u0648\u062f", NarratorRank.COLLECTOR, 0.90, 275, 4800),
    "Al-Tirmidhi": Narrator("Al-Tirmidhi", "\u0627\u0644\u062a\u0631\u0645\u0630\u064a", NarratorRank.COLLECTOR, 0.88, 279, 3956),
}

# Known transmission relationships: (from_narrator, to_narrator)
TRANSMISSIONS = [
    ("Abu Hurayrah", "Ibn Shihab"),
    ("Abu Hurayrah", "Nafi'"),
    ("Aisha", "Ibn Shihab"),
    ("Ibn Umar", "Nafi'"),
    ("Ibn Umar", "Ibn Shihab"),
    ("Anas ibn Malik", "Ibn Shihab"),
    ("Ibn Abbas", "Ibn Shihab"),
    ("Ibn Shihab", "Malik"),
    ("Ibn Shihab", "Sufyan al-Thawri"),
    ("Nafi'", "Malik"),
    ("Al-Hasan al-Basri", "Sufyan al-Thawri"),
    ("Malik", "Al-Bukhari"),
    ("Malik", "Muslim"),
    ("Sufyan al-Thawri", "Al-Bukhari"),
    ("Sufyan al-Thawri", "Al-Tirmidhi"),
    ("Malik", "Abu Dawud"),
]


class IsnadDAG:
    """Directed Acyclic Graph of hadith transmission chains."""

    def __init__(self):
        self.narrators = KNOWN_NARRATORS
        self.edges: List[Tuple[str, str]] = TRANSMISSIONS
        self._adjacency: Dict[str, List[str]] = {}
        self._build_adjacency()

    def _build_adjacency(self):
        for src, dst in self.edges:
            if src not in self._adjacency:
                self._adjacency[src] = []
            self._adjacency[src].append(dst)

    def is_acyclic(self) -> bool:
        """Check if the graph is acyclic using DFS."""
        visited: Set[str] = set()
        in_stack: Set[str] = set()

        def dfs(node: str) -> bool:
            visited.add(node)
            in_stack.add(node)
            for neighbor in self._adjacency.get(node, []):
                if neighbor in in_stack:
                    return False  # Cycle detected
                if neighbor not in visited:
                    if not dfs(neighbor):
                        return False
            in_stack.remove(node)
            return True

        for node in self.narrators:
            if node not in visited:
                if not dfs(node):
                    return False
        return True

    def longest_chain(self) -> int:
        """Find the longest transmission chain (longest path in DAG)."""
        memo: Dict[str, int] = {}

        def dfs_length(node: str) -> int:
            if node in memo:
                return memo[node]
            children = self._adjacency.get(node, [])
            if not children:
                memo[node] = 0
                return 0
            max_len = max(1 + dfs_length(c) for c in children)
            memo[node] = max_len
            return max_len

        return max(dfs_length(n) for n in self.narrators)

    def weakest_link(self, chain: List[str]) -> Optional[str]:
        """Find the narrator with lowest reliability in a chain."""
        min_reliability = float('inf')
        weakest = None

        for name in chain:
            if name in self.narrators:
                r = self.narrators[name].reliability
                if r < min_reliability:
                    min_reliability = r
                    weakest = name

        return weakest

    def get_chains_from(self, source: str) -> List[List[str]]:
        """Get all transmission chains originating from a narrator."""
        chains: List[List[str]] = []

        def dfs(node: str, path: List[str]):
            children = self._adjacency.get(node, [])
            if not children:
                chains.append(path[:])
                return
            for child in children:
                path.append(child)
                dfs(child, path)
                path.pop()

        dfs(source, [source])
        return chains


def evaluate_chain(chain: List[str]) -> ReliabilityGrade:
    """Evaluate the reliability grade of a transmission chain.

    Chain reliability = min(individual narrator reliability)
    Grade thresholds: >=0.9 sahih, >=0.7 hasan, >=0.3 da'if, <0.3 mawdu'
    """
    min_score = 1.0

    for name in chain:
        if name in KNOWN_NARRATORS:
            min_score = min(min_score, KNOWN_NARRATORS[name].reliability)
        else:
            min_score = min(min_score, 0.5)  # Unknown narrator

    if min_score >= 0.9:
        return ReliabilityGrade.SAHIH
    elif min_score >= 0.7:
        return ReliabilityGrade.HASAN
    elif min_score >= 0.3:
        return ReliabilityGrade.DAIF
    else:
        return ReliabilityGrade.MAWDU
