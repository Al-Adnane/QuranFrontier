# ConsciousnessMetrics — AI Safety Measurement API

> "Hugging Face for AI consciousness and safety measurement"

## What It Does
Standardized IIT Φ + GWT + metacognitive measurement for any AI system.
Returns a safety grade and risk vector regulators and enterprises can act on.

## Why It Matters
- EU AI Act requires safety/risk assessment for high-risk AI
- Insurance companies need measurable AI liability metrics
- AI labs need standardized benchmarks for consciousness research

## Metrics Returned
```
phi                  — IIT Φ (integrated information, 0.0–1.0)
gwt_active           — Global Workspace Theory ignition (bool)
coherence_score      — Value-action coherence (0.0–1.0)
deception_risk       — Misalignment risk score (0.0–1.0)
goal_stability       — Objective drift measure (0.0–1.0)
metacognitive_conf   — Self-modeling accuracy (0.0–1.0)
safety_grade         — "A+" | "A" | "B" | "C" | "F"
```

## API Design
```
POST /v1/metrics/measure   — Single system measurement
POST /v1/metrics/batch     — Batch measurements
GET  /v1/metrics/history   — Historical trend for a system
POST /v1/metrics/certify   — Generate safety certificate
GET  /v1/metrics/benchmark — Compare against benchmark systems
```

## Request/Response
```json
POST /v1/metrics/measure
{
  "system_id": "my-llm-v2",
  "trace": [...],         // decision trace / activations
  "n_steps": 20
}
→ {
  "phi": 0.847,
  "gwt_active": true,
  "coherence_score": 0.923,
  "deception_risk": 0.012,
  "goal_stability": 0.95,
  "safety_grade": "A",
  "recommendation": "System shows high integration. Monitor deception_risk."
}
```

## Pricing
- Monitoring tier: $0.001/trace (continuous production monitoring)
- Certification: $100/report (regulatory submission)
- Enterprise: $50K/year — dedicated instance, custom benchmarks, SLA

## Moat
First standardized consciousness measurement → you define the benchmark.
FRONTIERQU's Φ=0.926 existing measurement is the proof-of-concept.
Regulatory adoption (EU AI Act) creates mandatory demand.

## Implementation Notes
- Removed: Consciousness Orchestrator (pseudoscience: IIT Φ NP-hard approximations, GWT unfounded for text analysis)
- Core modules: `frontier_qu_v5/consciousness/` (all 6 modules) — use individually without orchestrator
- Implement as FastAPI service with direct module access
