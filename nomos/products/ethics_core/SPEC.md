# EthicsCore — Multi-Tradition Ethical Reasoning Middleware

> "Pluggable ethical reasoning for any AI system"

## What It Does
Given a situation, runs it through multiple ethical traditions simultaneously.
Returns where traditions agree, where they diverge, and what irreducible
tensions exist — honest about moral uncertainty.

## Target Markets
- Autonomous systems (self-driving, drones, medical robots)
- Content moderation (what speech rules apply?)
- HR / hiring AI (multi-framework fairness analysis)
- Government policy (simulate policy under multiple ethical lenses)
- Healthcare AI (bioethics consultation)
- Financial AI (investment ethics screening)

## Supported Traditions (v1)
```
utilitarian     — Maximize aggregate welfare (Bentham/Mill)
kantian         — Categorical imperative (Kant)
virtue          — Character-based reasoning (Aristotle/MacIntyre)
care            — Relationships and context (Gilligan/Noddings)
contractarian   — Veil of ignorance (Rawls)
islamic         — Maqasid al-shariah (wraps quran_core)
```
*Extensible: anyone can add a tradition via TraditionAdapter protocol*

## API Design
```python
from nomos.products.ethics_core import EthicsCore

core = EthicsCore(traditions=["utilitarian", "kantian", "virtue"])

result = core.analyze(
    situation="Autonomous vehicle must choose between hitting 1 adult vs 3 children",
    context={"certainty": 0.9, "domain": "transportation"}
)

print(result.consensus)    # Where all traditions agree
print(result.divergence)   # Where they disagree
print(result.recommendation)  # Best action given pluralism
print(result.uncertainty)  # Irreducible moral uncertainty score
```

## Output Structure
```json
{
  "situation": "...",
  "tradition_scores": {
    "utilitarian": {"action": "save_3", "confidence": 0.92, "reasoning": "3 > 1"},
    "kantian": {"action": "undetermined", "confidence": 0.45, "reasoning": "no universalizable rule"},
    "virtue": {"action": "save_3", "confidence": 0.71, "reasoning": "courage and justice align"}
  },
  "consensus": ["save_3"],
  "divergence": ["kantian abstains"],
  "recommendation": "save_3",
  "moral_uncertainty": 0.31,
  "minority_view": "Kantian abstention signals deeper moral dilemma"
}
```

## Pricing
- Open source core (Apache 2.0): Free
- ISO-certified tradition modules: $5K/year per tradition
- Enterprise middleware (SLA, audit, custom traditions): $25K+/year

## Moat
- Only system that honestly reports moral uncertainty and minority views
- Islamic tradition is already formally verified (quran_core/formal/)
- Extensible registry: community adds traditions, enterprise pays for certified ones

## Implementation Notes
- Thin orchestrator over tradition adapters in `nomos/traditions/`
- Each tradition is a TraditionAdapter plugin
- Aggregation strategy: weighted vote + consensus detection
- Output includes full reasoning trace per tradition
