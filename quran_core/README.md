# quran_core — Quranic & Islamic Research Layer

This directory contains all Quranic-specific and Islamic-tradition-specific
implementations. It is the **original research domain** for which the
FRONTIERQU 5-layer architecture was built.

**Do not modify these files when working on universal abstractions.**
The original implementations are preserved here exactly as built.

---

## Structure

```
quran_core/
├── frontierqu/         — Original frontierqu package (qiraat, tajweed, nahw,
│                         sarf, balaghah, deontic, naskh, isnad, quran data)
├── formal/             — Lean 4 proofs for Islamic jurisprudence
│   ├── DeonticLogic.lean       (obligation/permission/prohibition)
│   ├── MaqasidOptimality.lean  (maqasid al-shariah formal model)
│   ├── NaskhTheory.lean        (abrogation as homological algebra)
│   ├── QiraatEquivalence.lean  (semantic equivalence of readings)
│   ├── SheafConsistency.lean   (global/local consistency)
│   └── TajweedAxioms.lean      (recitation rule axioms)
├── models/             — Quranic/Islamic-specific neural architectures
│   ├── quranic_gnn.py          (graph neural network over Quran structure)
│   ├── nahw_constraint.py      (Arabic grammar constraint network)
│   ├── sarf_group.py           (Arabic morphology group theory)
│   ├── balaghah_bottleneck.py  (Arabic rhetoric bottleneck)
│   ├── deontic.py              (deontic logic network)
│   └── spiritual_traditions/   (I Ching, Kabbalah, Vedic, Sufi, etc.)
└── neuro_symbolic/     — Quranic neuro-symbolic reasoning modules
    ├── quantum_qiraat/     (7 canonical readings as quantum superposition)
    ├── dag_naskh/          (abrogation as directed acyclic graph / homology)
    ├── embodied_tajweed/   (vocal tract PDE for recitation physics)
    ├── rql/                (Relational Query Language for Quran)
    ├── multi_agent/        (scholar debate: Proposer/Verifier/Critic)
    └── integrations/       (cross-module integrations)
```

---

## What This Enables (Unique Capabilities)

| Capability | File(s) | World-First |
|-----------|---------|-------------|
| Formal proof of abrogation logic | `formal/NaskhTheory.lean` | ✅ First formal model of naskh as homological algebra |
| Quantum semantic superposition of readings | `neuro_symbolic/quantum_qiraat/` | ✅ First Hilbert space model of hermeneutics |
| Physics-based recitation coaching | `neuro_symbolic/embodied_tajweed/` | ✅ PDE vocal tract simulation for Tajweed |
| Multi-agent scholarly debate | `neuro_symbolic/multi_agent/` | ✅ Proposer/Verifier/Critic grounded in usul al-fiqh |
| Formal Maqasid optimality proofs | `formal/MaqasidOptimality.lean` | ✅ Machine-verified Islamic legal theory |

---

## Relationship to Universal Framework

The **NOMOS** universal framework (`../nomos/`) was inspired by and
generalizes from this layer. The mapping is:

| quran_core concept | NOMOS universal equivalent |
|-------------------|---------------------------|
| MaqasidOptimizer | TelosOptimizer |
| DeonticSolver | NormativeEngine |
| NaskhTheory | RevisionLogic |
| QiraatQuantum | VariaCore |
| ThreeWorldArchitecture | TriModalEngine |

The Islamic implementations live here as **tradition adapters** in the
universal system — one tradition among many, fully preserved.
