# NormativeEngine — Universal Deontic Solver

> "Z3 for laws — any legal system, any jurisdiction"

## What It Does
Given a jurisdiction, a time, an action, and context:
returns whether the action is permitted/obligatory/prohibited + conditions + explanation.
Handles temporal conflicts (newer law supersedes older), jurisdictional conflicts,
and multi-tradition analysis.

## Target Markets
- Legal Tech: Automated legal reasoning, contract drafting
- Identity Management: Dynamic RBAC/ABAC on steroids
- Autonomous Vehicles: Real-time legal compliance during operation
- Enterprise Policy: HR policies, data governance, procurement rules
- Government: Legislative impact simulation

## Deontic Categories
```
OBLIGATORY  — Must do (O)
RECOMMENDED — Should do (R)
PERMITTED   — May do (P)
DISCOURAGED — Should not do (D)
PROHIBITED  — Must not do (F)
UNDETERMINED — No applicable norm found
```

## API Design
```
POST /v1/norms/query      — Query norm status for an action
POST /v1/norms/add        — Add a norm to the system
POST /v1/norms/conflicts  — Detect conflicts in a norm set
POST /v1/norms/resolve    — Resolve conflicts
GET  /v1/norms/explain    — Explain a decision in natural language
```

## Request/Response
```json
POST /v1/norms/query
{
  "action": "collect_biometric_data",
  "legal_system": "EU",
  "jurisdiction": "Germany",
  "effective_date": "2025-01-01",
  "context": {"consent": false, "purpose": "marketing"}
}
→ {
  "status": "PROHIBITED",
  "norms_triggered": ["GDPR-Art-9", "BDSG-§26"],
  "conditions": ["Would be PERMITTED with explicit consent"],
  "explanation": "Processing biometric data without explicit consent is prohibited under GDPR Art. 9(1).",
  "confidence": 0.97
}
```

## Conflict Resolution Strategies
```
temporal     — Later norm supersedes earlier (generalizes NaskhTheory)
specificity  — More specific norm overrides general
hierarchy    — Higher-authority norm wins
utility      — Choose norm maximizing aggregate welfare
tradition    — Apply tradition-specific resolution rules
```

## Pricing
- Developer: $299/month — 10K queries, 5 legal systems
- Business: $2,999/month — 100K queries, all jurisdictions
- Enterprise: $10K–$100K/year — custom legal systems, SLA

## Implementation Notes
- Builds on: `frontier_neuro_symbolic/advanced_solvers/smt_solver.py`
- Temporal resolution: generalizes `quran_core/neuro_symbolic/dag_naskh/`
- Expose as standalone FastAPI microservice
