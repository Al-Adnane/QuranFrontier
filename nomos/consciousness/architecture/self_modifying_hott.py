"""
Self-Modifying HoTT Type Universes
Types that evolve based on computation results.
Reflexive universes where the type system rewrites itself.

Key concepts:
- Universe polymorphism: types can reference their own universe level
- Path induction: equality proofs that modify the type graph
- Transport: moving values between equivalent types
- Univalence: equivalence IS equality (types evolve by proving equivalences)
"""

import numpy as np
import hashlib
import time
from typing import Dict, List, Any, Optional, Set, Tuple
from dataclasses import dataclass, field
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@dataclass
class HoTTType:
    """A type in the self-modifying universe."""
    name: str
    universe_level: int
    attributes: Dict[str, Any] = field(default_factory=dict)
    creation_time: float = field(default_factory=time.time)
    parent: Optional[str] = None
    children: List[str] = field(default_factory=list)


@dataclass
class PathEquality:
    """A proof of equality (path) between two types."""
    source: str
    target: str
    proof_hash: str
    transport_fn: str  # Description of how to transport values
    timestamp: float = field(default_factory=time.time)
    is_reflexive: bool = False  # Self-referential path


@dataclass
class UnivalenceWitness:
    """Witness that an equivalence between types IS an equality."""
    type_a: str
    type_b: str
    forward_map: str   # A → B
    inverse_map: str   # B → A
    coherence: float   # How well round-trip preserves structure (0-1)


class SelfModifyingHoTT:
    """
    A self-modifying type universe implementing core HoTT concepts.
    Types can evolve, merge, split, and reference themselves.
    The universe tracks its own modification history.
    """

    def __init__(self, max_universe_levels: int = 10):
        self.max_levels = max_universe_levels
        self.types: Dict[str, HoTTType] = {}
        self.paths: List[PathEquality] = []
        self.univalence_witnesses: List[UnivalenceWitness] = []
        self.modification_log: List[Dict[str, Any]] = []
        self._strange_loops: List[List[str]] = []  # Self-referential cycles

    def register_type(self, name: str, level: int = 0,
                      attributes: Optional[Dict] = None,
                      parent: Optional[str] = None) -> HoTTType:
        """Register a new type in the universe."""
        t = HoTTType(
            name=name,
            universe_level=min(level, self.max_levels - 1),
            attributes=attributes or {},
            parent=parent,
        )
        self.types[name] = t
        if parent and parent in self.types:
            self.types[parent].children.append(name)

        self._log("register", name, {"level": level})
        return t

    def assert_path(self, source: str, target: str,
                    proof: str = "computational") -> PathEquality:
        """Assert a path equality between two types."""
        proof_hash = hashlib.sha256(
            f"{source}:{target}:{proof}".encode()
        ).hexdigest()[:16]

        path = PathEquality(
            source=source,
            target=target,
            proof_hash=proof_hash,
            transport_fn=f"transport_{source}_to_{target}",
            is_reflexive=(source == target),
        )
        self.paths.append(path)
        self._log("path", f"{source}≃{target}", {"proof": proof})

        # Check for strange loops
        self._detect_strange_loops(source, target)
        return path

    def evolve_type(self, name: str, new_attributes: Dict[str, Any],
                    reason: str = "computation_result") -> bool:
        """
        Self-modification: a type changes its own attributes based on
        computation results. This is the key innovation — types learn.
        """
        if name not in self.types:
            return False

        old_attrs = dict(self.types[name].attributes)
        self.types[name].attributes.update(new_attributes)

        # Record the evolution as a path from old to new
        self.assert_path(
            f"{name}@v{len(self.modification_log)}",
            f"{name}@v{len(self.modification_log) + 1}",
            proof=reason,
        )

        self._log("evolve", name, {
            "old": old_attrs,
            "new": new_attributes,
            "reason": reason,
        })
        return True

    def merge_types(self, name_a: str, name_b: str,
                    merged_name: str) -> Optional[HoTTType]:
        """
        Merge two types into a product type.
        The merged type has attributes from both.
        """
        if name_a not in self.types or name_b not in self.types:
            return None

        ta = self.types[name_a]
        tb = self.types[name_b]

        merged_attrs = {**ta.attributes, **tb.attributes}
        merged_level = max(ta.universe_level, tb.universe_level)

        merged = self.register_type(
            merged_name,
            level=merged_level,
            attributes=merged_attrs,
        )

        # Record merge paths
        self.assert_path(name_a, merged_name, proof="projection_left")
        self.assert_path(name_b, merged_name, proof="projection_right")

        self._log("merge", merged_name, {
            "sources": [name_a, name_b],
        })
        return merged

    def split_type(self, name: str, split_key: str) -> Tuple[Optional[HoTTType], Optional[HoTTType]]:
        """
        Split a type into two subtypes based on an attribute key.
        """
        if name not in self.types:
            return None, None

        t = self.types[name]
        attrs_a = {k: v for k, v in t.attributes.items() if k <= split_key}
        attrs_b = {k: v for k, v in t.attributes.items() if k > split_key}

        ta = self.register_type(f"{name}_L", t.universe_level, attrs_a, parent=name)
        tb = self.register_type(f"{name}_R", t.universe_level, attrs_b, parent=name)

        self._log("split", name, {"into": [ta.name, tb.name]})
        return ta, tb

    def witness_univalence(self, type_a: str, type_b: str,
                           coherence: float = 1.0) -> UnivalenceWitness:
        """
        Witness that equivalence A ≃ B is the same as equality A = B.
        The univalence axiom: types that are equivalent are equal.
        """
        witness = UnivalenceWitness(
            type_a=type_a,
            type_b=type_b,
            forward_map=f"equiv_{type_a}_to_{type_b}",
            inverse_map=f"equiv_{type_b}_to_{type_a}",
            coherence=coherence,
        )
        self.univalence_witnesses.append(witness)
        self._log("univalence", f"{type_a}={type_b}", {"coherence": coherence})
        return witness

    def transport(self, value: Any, source_type: str,
                  target_type: str) -> Any:
        """
        Transport a value from source type to target type along a path.
        If no direct path exists, find shortest path through type graph.
        """
        # Check for direct path
        for path in self.paths:
            if path.source == source_type and path.target == target_type:
                return self._apply_transport(value, path)

        # BFS for path through type graph
        path_chain = self._find_path_chain(source_type, target_type)
        if path_chain is None:
            raise ValueError(f"No path from {source_type} to {target_type}")

        result = value
        for path in path_chain:
            result = self._apply_transport(result, path)
        return result

    def _apply_transport(self, value: Any, path: PathEquality) -> Any:
        """Apply transport along a single path (identity for simulation)."""
        # In real HoTT, this would transform the value
        # Here we tag it with transport metadata
        if isinstance(value, dict):
            value['_transported_via'] = path.proof_hash
        return value

    def _find_path_chain(self, source: str, target: str) -> Optional[List[PathEquality]]:
        """BFS to find chain of paths from source to target."""
        from collections import deque
        visited = {source}
        queue = deque([(source, [])])

        while queue:
            current, chain = queue.popleft()
            for path in self.paths:
                if path.source == current and path.target not in visited:
                    new_chain = chain + [path]
                    if path.target == target:
                        return new_chain
                    visited.add(path.target)
                    queue.append((path.target, new_chain))
        return None

    def _detect_strange_loops(self, new_source: str, new_target: str):
        """Detect self-referential cycles in the type graph."""
        # Check if adding this edge creates a cycle
        chain = self._find_path_chain(new_target, new_source)
        if chain is not None:
            loop = [new_source, new_target] + [p.target for p in chain]
            self._strange_loops.append(loop)
            self._log("strange_loop_detected", str(loop), {
                "length": len(loop),
                "winding_number": len(self._strange_loops),
            })

    def compute_winding_number(self) -> int:
        """
        Strange loop winding number: count of non-trivial self-referential
        cycles in the type graph. Used by consciousness monitor.
        """
        return len(self._strange_loops)

    def _log(self, action: str, target: str, details: Dict[str, Any]):
        self.modification_log.append({
            'action': action,
            'target': target,
            'details': details,
            'timestamp': time.time(),
            'universe_size': len(self.types),
        })

    def get_metrics(self) -> Dict[str, Any]:
        return {
            'total_types': len(self.types),
            'total_paths': len(self.paths),
            'univalence_witnesses': len(self.univalence_witnesses),
            'strange_loops': len(self._strange_loops),
            'winding_number': self.compute_winding_number(),
            'modifications': len(self.modification_log),
            'max_universe_level': max(
                (t.universe_level for t in self.types.values()), default=0
            ),
        }
