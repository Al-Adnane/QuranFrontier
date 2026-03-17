#!/usr/bin/env python3
"""
Tafsir Integration Adapter

Connects existing tafsir_integration.py (42KB, 8 scholars) to corpus_extraction.

Existing Infrastructure:
- TafsirQuotation: Direct citations with full references
- MadhabPosition: School positions (Hanafi, Maliki, Shafi'i, Hanbali, Jafari, Zaidi)
- ConsensusLevel: Ijma classifications (Qati, Danni, Widespread, Disagreement, Disputed)
- InterpretationLevel: 4 layers (Zahir, Batin, Isharat, Haqiqah)

8 Classical Scholars:
1. Ibn Abbas (d. 687) - Companion, foundational
2. At-Tabari (d. 923) - Comprehensive historical
3. Al-Qurtubi (d. 1273) - Legal focus
4. Al-Zamakhshari (d. 1144) - Mu'tazili, rhetorical
5. Ibn Kathir (d. 1373) - Traditional, hadith-based
6. As-Suyuti (d. 1505) - Encyclopedic
7. Mawdudi (d. 1979) - Modern, socio-political
8. Ibn Arabi (d. 1240) - Sufi, mystical
"""

import sys
from pathlib import Path
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from datetime import datetime

# Import from existing tafsir_integration.py
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'quran-core' / 'src'))
from data.tafsir_integration import (
    TafsirQuotation,
    MadhabPosition,
    ConsensusLevel,
    InterpretationLevel,
    TafsirMetadata,
)


@dataclass
class VerseTafsirEnrichment:
    """Enriched tafsir data for a single verse"""
    verse_id: str
    surah: int
    ayah: int
    arabic_text: str
    tafsirs: Dict[str, TafsirQuotation]  # scholar_name -> quotation
    consensus_analysis: Optional[ConsensusLevel] = None
    madhab_positions: Dict[str, MadhabPosition] = field(default_factory=dict)
    interpretation_layers: Dict[str, InterpretationLevel] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


class TafsirEnrichmentAdapter:
    """Adapter connecting tafsir_integration.py to corpus_extraction"""
    
    def __init__(self):
        self.scholars = [
            'Ibn Abbas', 'At-Tabari', 'Al-Qurtubi', 'Al-Zamakhshari',
            'Ibn Kathir', 'As-Suyuti', 'Mawdudi', 'Ibn Arabi'
        ]
        self.enrichments = {}
    
    def enrich_verse(self, verse_data: Dict) -> VerseTafsirEnrichment:
        """Enrich a single verse with all 8 scholar tafsirs"""
        verse_id = verse_data.get('verse_id', verse_data.get('id', ''))
        
        # Create enrichment record
        enrichment = VerseTafsirEnrichment(
            verse_id=verse_id,
            surah=verse_data.get('surah', 1),
            ayah=verse_data.get('ayah', 1),
            arabic_text=verse_data.get('arabic_text', ''),
            tafsirs={},
            metadata={
                'source': 'tafsir_integration_adapter',
                'scholars_count': len(self.scholars),
            }
        )
        
        # Add tafsirs for each scholar (placeholder - would load from existing data)
        for scholar in self.scholars:
            # In production, this would load actual tafsir quotations
            enrichment.tafsirs[scholar] = {
                'scholar': scholar,
                'text': f'[Tafsir of {scholar} for {verse_id}]',
                'source': 'existing_tafsir_data',
            }
        
        self.enrichments[verse_id] = enrichment
        return enrichment
    
    def enrich_all_verses(self, verses: List[Dict]) -> Dict[str, VerseTafsirEnrichment]:
        """Enrich all verses with tafsirs"""
        for verse in verses:
            self.enrich_verse(verse)
        
        logger.info(f"Enriched {len(self.enrichments)} verses with tafsirs")
        return self.enrichments
    
    def save_enrichments(self, output_path: str):
        """Save enriched tafsirs to JSON"""
        data = {
            'metadata': {
                'generated': datetime.now().isoformat(),
                'total_verses': len(self.enrichments),
                'scholars': self.scholars,
            },
            'enrichments': {
                vid: {
                    'verse_id': e.verse_id,
                    'surah': e.surah,
                    'ayah': e.ayah,
                    'tafsirs': e.tafsirs,
                    'metadata': e.metadata,
                }
                for vid, e in self.enrichments.items()
            }
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Saved enrichments to {output_path}")


if __name__ == '__main__':
    # Test adapter
    adapter = TafsirEnrichmentAdapter()
    sample_verse = {'verse_id': '1:1', 'surah': 1, 'ayah': 1, 'arabic_text': 'بِسْمِ اللَّهِ'}
    enrichment = adapter.enrich_verse(sample_verse)
    print(f"Enriched verse {enrichment.verse_id} with {len(enrichment.tafsirs)} tafsirs")
