#!/usr/bin/env python3
"""
Phase 3 Extraction Agent 13 - Verses 2341-2535.

Extracts verses 2341-2535 and saves to corpus_13.json.
Uses checkpointing for recovery in case of interruption.
"""

import json
import os
import sys
import logging
from typing import List, Dict, Optional
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from quran.corpus_extraction.infrastructure.redis_manager import CheckpointManager
from quran.corpus_extraction.extraction.verse_extractor import VerseExtractor
from quran.corpus_extraction.extraction.verse_mapping import VerseMapper
from quran.corpus_extraction.framework.verse_coordinator import VerseExtractorCoordinator
from quran.corpus_extraction.infrastructure.api_integration import ApiIntegrationLayer
from quran.corpus_extraction.infrastructure.cache_layer import CacheLayer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - Agent-13 - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class Agent13Processor:
    """Extract verses 2341-2535 for Phase 3."""

    AGENT_ID = 'agent_13'
    VERSE_START = 2341
    VERSE_END = 2535

    def __init__(self):
        """Initialize the agent with required components."""
        self.checkpoint_mgr = CheckpointManager()
        self.verse_mapper = VerseMapper()

        # Initialize framework components
        api_layer = ApiIntegrationLayer()
        cache_layer = CacheLayer()

        # Initialize coordinator with framework components
        coordinator = VerseExtractorCoordinator(
            domain_analyzer=None,  # Optional, not required for basic extraction
            tafsir_consolidator=None,
            asbab_mapper=None,
            semantic_analyzer=None,
            verification_pipeline=None,
            cache_layer=cache_layer
        )

        # Initialize verse extractor
        self.verse_extractor = VerseExtractor(
            coordinator=coordinator,
            api_layer=api_layer,
            cache_layer=cache_layer
        )

        self.output_file = (
            '/Users/mac/Desktop/QuranFrontier/.claude/worktrees/magical-faraday'
            '/quran/corpus_extraction/output/corpus_13.json'
        )

        logger.info(f"Agent 13 initialized: verses {self.VERSE_START}-{self.VERSE_END}")

    def process(self) -> Dict:
        """
        Main extraction loop for this agent.

        Returns:
            Dictionary with processing results
        """
        logger.info(f"Starting extraction for {self.AGENT_ID}")

        # Get checkpoint to resume from
        checkpoint = self.checkpoint_mgr.get_checkpoint(self.AGENT_ID)
        start_verse = self.VERSE_START

        if checkpoint and checkpoint.get('status') == 'in_progress':
            start_verse = checkpoint.get('last_verse', self.VERSE_START - 1) + 1
            logger.info(f"Resuming from verse {start_verse}")

        results = []
        processed_count = 0
        skipped_count = 0
        failed_count = 0

        try:
            for global_verse in range(start_verse, self.VERSE_END + 1):
                try:
                    # Map global verse to surah:ayah
                    surah, ayah = self.verse_mapper.get_surah_ayah(global_verse)

                    # Extract verse
                    extraction = self.verse_extractor.extract_verse_complete(surah, ayah)

                    if extraction:
                        results.append(extraction.to_dict() if hasattr(extraction, 'to_dict') else {
                            'surah': extraction.surah,
                            'ayah': extraction.ayah,
                            'verse_key': extraction.verse_key,
                            'arabic_text': extraction.arabic_text,
                            'translation': extraction.translation,
                            'physics_content': extraction.physics_content,
                            'biology_content': extraction.biology_content,
                            'medicine_content': extraction.medicine_content,
                            'engineering_content': extraction.engineering_content,
                            'agriculture_content': extraction.agriculture_content,
                            'tafsirs': extraction.tafsirs,
                            'tafsir_agreement': extraction.tafsir_agreement,
                            'asbab_nuzul': extraction.asbab_nuzul,
                            'semantic_analysis': extraction.semantic_analysis,
                            'verification_layers': extraction.verification_layers,
                            'confidence_score': extraction.confidence_score,
                            'source_citations': extraction.source_citations,
                        })
                        processed_count += 1
                    else:
                        logger.warning(f"Extraction returned None for {surah}:{ayah}")
                        skipped_count += 1

                except Exception as e:
                    logger.error(f"Error extracting verse {global_verse}: {str(e)}")
                    failed_count += 1

                # Checkpoint every 50 verses
                if global_verse % 50 == 0:
                    self._save_checkpoint(global_verse, processed_count)
                    logger.info(
                        f"Checkpoint: verse {global_verse}, "
                        f"processed={processed_count}, skipped={skipped_count}, "
                        f"failed={failed_count}"
                    )

            # Save all results
            self._save_results(results)
            logger.info(f"Results saved to {self.output_file}")

            # Final checkpoint
            self._save_checkpoint(
                self.VERSE_END,
                processed_count,
                status='completed'
            )

            result = {
                'agent_id': self.AGENT_ID,
                'status': 'success',
                'verse_range': f'{self.VERSE_START}-{self.VERSE_END}',
                'processed': processed_count,
                'skipped': skipped_count,
                'failed': failed_count,
                'total_attempted': self.VERSE_END - self.VERSE_START + 1,
                'output_file': self.output_file
            }

            logger.info(f"Agent 13 completed: {result}")
            return result

        except Exception as e:
            logger.error(f"Critical error in agent processing: {str(e)}")
            return {
                'agent_id': self.AGENT_ID,
                'status': 'error',
                'error': str(e)
            }

    def _save_checkpoint(self,
                        last_verse: int,
                        processed_count: int,
                        status: str = 'in_progress') -> None:
        """Save checkpoint to Redis."""
        checkpoint = {
            'agent_id': self.AGENT_ID,
            'last_verse': last_verse,
            'processed': processed_count,
            'status': status,
            'timestamp': datetime.now().isoformat()
        }
        success = self.checkpoint_mgr.save_checkpoint(self.AGENT_ID, checkpoint)
        if not success:
            logger.warning(f"Failed to save checkpoint for verse {last_verse}")

    def _save_results(self, results: List[Dict]) -> None:
        """Save extraction results to JSON file."""
        os.makedirs(os.path.dirname(self.output_file), exist_ok=True)
        with open(self.output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        logger.info(f"Saved {len(results)} verses to {self.output_file}")


if __name__ == '__main__':
    agent = Agent13Processor()
    result = agent.process()
    sys.exit(0 if result.get('status') == 'success' else 1)
