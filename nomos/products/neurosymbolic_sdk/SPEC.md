# NeuroSymbolic SDK — Build AI That Explains Why

> "pip install nomos — the developer SDK"

## What It Does
A Python SDK giving developers access to the full 5-layer NOMOS stack.
218 pre-built neural architectures + symbolic reasoning + formal verification.
`model.explain()` returns a logical deduction tree, not just attention heatmaps.

## Target Developers
- ML engineers building regulated AI (healthcare, finance, legal)
- Enterprise teams that need explainable AI for compliance
- AI safety researchers
- Academic researchers in neuro-symbolic AI

## Core SDK Classes
```python
from nomos import NomosEngine, TriModalReasoner, NormativeEngine
from nomos.architectures import list_architectures, load_architecture
from nomos.traditions import get_tradition

# Load the full 5-layer pipeline
engine = NomosEngine(domain="finance")
result = engine.run("Should we approve this loan application?",
                    traditions=["utilitarian", "kantian"])

# Use just the neuro-symbolic layer
reasoner = TriModalReasoner()
output = reasoner.reason(query, mode="hybrid")
print(output.explanation)  # "Physical: credit score 720. Conceptual: stable employment. Abstract: satisfies fairness F3."

# Use just the normative engine
norms = NormativeEngine(legal_system="US_NY")
norms.add_norm("ECOA", "prohibited", "discriminate_by_race", 1.0)
result = norms.solve()
```

## Key Features
- `model.explain()` → logical deduction tree
- `model.verify()` → Lean 4 proof of output property
- `model.measure()` → consciousness/safety metrics
- `traditions=["utilitarian", "kantian"]` → multi-tradition analysis
- 218 pre-built architectures: `load_architecture("iit_network")`

## Pricing
- Core SDK: Apache 2.0 (free, open source)
- Cloud API: usage-based (pay for compute)
- Enterprise: self-hosted + support contract

## Distribution
```bash
pip install nomos                    # Core SDK
pip install nomos[cloud]             # Cloud API client
pip install nomos[enterprise]        # Enterprise features
docker pull nomos/engine:latest      # Self-hosted
```

## Implementation Notes
- Thin wrapper around existing `pipeline_orchestrator.py`
- Architectures from `frontier_models/` (218 existing)
- Consciousness from `frontier_qu_v5/` (6 modules)
- Clean public API hiding internal complexity
