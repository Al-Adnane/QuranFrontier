#!/usr/bin/env python3
"""
Uncertainty Scoring Adapter

Connects existing meta_principle_framework.py (22KB, 6 axioms) to uncertainty quantification.

Existing Infrastructure:
- 6-Axiom Scoring System → Factual Accuracy component (40% weight)
- IJAZ Discriminator (24KB, 7 dimensions) → Uncertainty Calibration (20% weight)
- Ijma Monitor (17KB, consensus tracking) → Consistency component (10% weight)
- Concept Sources → Source Attribution (30% weight)

4-Component Composite Metric:
1. Factual Accuracy (40%) - from meta_principle_framework
2. Source Attribution (30%) - from concept_sources
3. Uncertainty Calibration (20%) - from ijaz_discriminator
4. Consistency (10%) - from ijma_monitor
"""

import sys
from pathlib import Path
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from datetime import datetime

# Import from existing modules
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'quran-core' / 'src'))


@dataclass
class UncertaintyScore:
    """4-component composite uncertainty score"""
    verse_id: str
    factual_accuracy: float = 0.0  # 40% weight (meta_principle_framework)
    source_attribution: float = 0.0  # 30% weight (concept_sources)
    uncertainty_calibration: float = 0.0  # 20% weight (ijaz_discriminator)
    consistency: float = 0.0  # 10% weight (ijma_monitor)
    composite_score: float = 0.0
    brier_score: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def __post_init__(self):
        # Calculate composite score with weights
        self.composite_score = (
            0.40 * self.factual_accuracy +
            0.30 * self.source_attribution +
            0.20 * self.uncertainty_calibration +
            0.10 * self.consistency
        )
        
        # Calculate Brier score (lower is better)
        self.brier_score = (1.0 - self.composite_score) ** 2


class UncertaintyScoringAdapter:
    """Adapter connecting existing modules to uncertainty quantification"""
    
    def __init__(self):
        self.weights = {
            'factual_accuracy': 0.40,
            'source_attribution': 0.30,
            'uncertainty_calibration': 0.20,
            'consistency': 0.10,
        }
        self.scores = {}
    
    def calculate_uncertainty(self, verse_data: Dict) -> UncertaintyScore:
        """Calculate 4-component uncertainty score for a verse"""
        verse_id = verse_data.get('verse_id', verse_data.get('id', ''))
        
        # Component 1: Factual Accuracy (40%) - from meta_principle_framework
        factual_accuracy = self._calculate_factual_accuracy(verse_data)
        
        # Component 2: Source Attribution (30%) - from concept_sources
        source_attribution = self._calculate_source_attribution(verse_data)
        
        # Component 3: Uncertainty Calibration (20%) - from ijaz_discriminator
        uncertainty_calibration = self._calculate_uncertainty_calibration(verse_data)
        
        # Component 4: Consistency (10%) - from ijma_monitor
        consistency = self._calculate_consistency(verse_data)
        
        score = UncertaintyScore(
            verse_id=verse_id,
            factual_accuracy=factual_accuracy,
            source_attribution=source_attribution,
            uncertainty_calibration=uncertainty_calibration,
            consistency=consistency,
            metadata={
                'weights': self.weights,
                'source': 'uncertainty_scoring_adapter',
            }
        )
        
        self.scores[verse_id] = score
        return score
    
    def _calculate_factual_accuracy(self, verse_data: Dict) -> float:
        """Calculate factual accuracy from meta_principle_framework (6 axioms)"""
        # Placeholder - would call meta_principle_framework.py
        # 6-axiom scoring system
        return 0.85  # Placeholder
    
    def _calculate_source_attribution(self, verse_data: Dict) -> float:
        """Calculate source attribution from concept_sources"""
        # Placeholder - would call concept_sources.json
        # DOI-validated sources
        return 0.90  # Placeholder
    
    def _calculate_uncertainty_calibration(self, verse_data: Dict) -> float:
        """Calculate uncertainty calibration from ijaz_discriminator (7 dimensions)"""
        # Placeholder - would call ijaz_discriminator.py
        # 7-dimension weighted scoring
        return 0.80  # Placeholder
    
    def _calculate_consistency(self, verse_data: Dict) -> float:
        """Calculate consistency from ijma_monitor (consensus tracking)"""
        # Placeholder - would call ijma_monitor.py
        # Consensus-based confidence adjustment
        return 0.88  # Placeholder
    
    def calculate_all_uncertainties(self, verses: List[Dict]) -> Dict[str, UncertaintyScore]:
        """Calculate uncertainty scores for all verses"""
        for verse in verses:
            self.calculate_uncertainty(verse)
        
        logger.info(f"Calculated uncertainty for {len(self.scores)} verses")
        return self.scores
    
    def save_scores(self, output_path: str):
        """Save uncertainty scores to JSON"""
        data = {
            'metadata': {
                'generated': datetime.now().isoformat(),
                'total_verses': len(self.scores),
                'weights': self.weights,
            },
            'scores': {
                vid: {
                    'verse_id': s.verse_id,
                    'factual_accuracy': s.factual_accuracy,
                    'source_attribution': s.source_attribution,
                    'uncertainty_calibration': s.uncertainty_calibration,
                    'consistency': s.consistency,
                    'composite_score': s.composite_score,
                    'brier_score': s.brier_score,
                    'metadata': s.metadata,
                }
                for vid, s in self.scores.items()
            }
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        
        logger.info(f"Saved uncertainty scores to {output_path}")


if __name__ == '__main__':
    # Test adapter
    adapter = UncertaintyScoringAdapter()
    sample_verse = {'verse_id': '1:1', 'surah': 1, 'ayah': 1}
    score = adapter.calculate_uncertainty(sample_verse)
    print(f"Verse {score.verse_id}: Composite={score.composite_score:.3f}, Brier={score.brier_score:.3f}")
