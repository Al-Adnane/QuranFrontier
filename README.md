# QuranFrontier

Two distinct namespaces live here. Do not mix them.

---

## `quran-core/` — Quran & Islamic Sciences

Everything specific to the Quran and Islamic intellectual tradition:

- **Arabic NLP** — nahw (syntax), sarf (morphology), tajweed rules, qiraat variants
- **Naskh theory** — abrogation DAG, Lean 4 formal proofs (`formal/lean/`)
- **Qiraat engine** — quantum_qiraat, dag_naskh, embodied_tajweed
- **Knowledge base** — hypergraph_kb (Quranic concept graph)
- **Cosmology** — three_world (Nafs / Aql / Ruh model)
- **Sheaf theory** — sheaf_nn applied to Quranic structure
- **Spiritual tradition models** — 23 PyTorch models (`models/spiritual_traditions/`)
- **Tests** — all Quran-specific tests in `quran-core/tests/`

```
quran-core/
├── reasoning/          # dag_naskh, embodied_tajweed, quantum_qiraat, rql,
│                       # hypergraph_kb, three_world, sheaf_nn, integrations, multi_agent
├── models/
│   └── spiritual_traditions/
├── formal/
│   └── lean/           # Lean 4 NaskhTheory proofs
├── src/                # linguistic/, logic/, geometry/, physics/, search/, topology/
└── tests/              # all Quran-specific test files
```

---

## `nomos/` — NOMOS Ethics AI System

General-purpose multi-tradition ethical reasoning, not tied to any single religion:

- **ConsensusEngine** — cross-tradition ethical consensus (`core/`)
- **Tradition adapters** — Islamic, Utilitarian, Kantian, Virtue ethics (`traditions/`)
- **Consciousness metrics** — IIT Phi, GWT, orchestrator (`consciousness/`)
- **Products** — ethics_core, complianceos, consciousness_metrics, formalverify,
  neurosymbolic_sdk, normative_engine (`products/`)
- **218+ neural architectures** — 40+ domain families (`architectures/`)
- **General reasoning** — advanced_solvers (SMT/probabilistic), system_integration (`reasoning/`)
- **ML infra** — automl, distributed, compression (`infra/`)
- **Tests** — NOMOS-specific tests in `nomos/tests/`

```
nomos/
├── core/               # ConsensusEngine, ConsensusReport
├── traditions/         # TraditionAdapter implementations
├── consciousness/      # IIT Phi, GWT, orchestrator
├── interfaces/         # TraditionAdapter protocol
├── products/           # deployable products
├── reasoning/          # advanced_solvers, system_integration (general AI only)
├── architectures/      # 218+ neural architectures
├── infra/              # automl, distributed, compression, deployment
├── integrations/       # external integrations
├── research/           # research infrastructure
├── viz/                # visualizations
├── engine/             # dashboard / demos
└── tests/              # test_consensus_engine.py, test_tradition_adapters.py,
                        # test_consciousness_metrics.py, test_complianceos.py, ...
```

---

## Quick Start

```bash
pip install -r requirements.txt

# Run NOMOS core tests (must pass 70/70)
python -m pytest nomos/tests/test_consensus_engine.py \
                 nomos/tests/test_tradition_adapters.py \
                 nomos/tests/test_consciousness_metrics.py \
                 nomos/tests/test_complianceos.py -v --tb=short -q

# Run Quran-specific tests
python -m pytest quran-core/tests/ -v --tb=short -q
```

---

## Decision Rule

When adding new code, ask: "Is this Quran/Islam-specific?"

- **Yes** — `quran-core/`
- **No** (general AI, ethics, multi-tradition) — `nomos/`
