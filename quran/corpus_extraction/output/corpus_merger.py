"""
CorpusMerger - Consolidates 32 parallel corpus extractions into a single complete corpus
"""
import json
import os
import hashlib
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime


class CorpusMerger:
    """Merge 32 corpus chunks into complete corpus with integrity verification"""

    def __init__(self):
        """Initialize corpus merger with configuration"""
        self.input_dir = 'quran/corpus_extraction/output'
        self.num_agents = 32
        self.expected_verses = 6236
        self.output_filename = 'complete_corpus.json'

    def merge_all_corpora(self) -> Dict:
        """
        Merge all 32 corpus_<N>.json files into unified corpus.

        Returns: {
            'total_verses': int,
            'verses': List[Dict],
            'metadata': {
                'merge_timestamp': str,
                'source_agents': int,
                'source_files': List[str],
                'validation_report': Dict
            },
            'integrity': Dict  # SHA256 checksums per agent
        }
        """
        all_verses = []
        source_files = []
        agent_checksums = {}

        # Load all corpus chunks
        for agent_num in range(1, self.num_agents + 1):
            corpus = self._load_corpus_chunk(agent_num)
            if corpus:
                all_verses.extend(corpus)
                source_files.append(f'corpus_{agent_num}.json')
                # Compute checksum for this agent's corpus
                agent_checksums[f'agent_{agent_num}'] = hashlib.sha256(
                    json.dumps(corpus, sort_keys=True).encode()
                ).hexdigest()

        # Sort verses by surah:ayah canonical order
        sorted_verses = self._sort_corpus(all_verses)

        # Validate corpus completeness
        validation_report = self._validate_corpus(sorted_verses)

        # Compute overall integrity checksums
        corpus_data = {
            'verses': sorted_verses,
            'metadata': {
                'merge_timestamp': datetime.now().isoformat(),
                'source_agents': self.num_agents,
                'source_files': source_files,
                'validation_report': validation_report
            }
        }

        integrity_checksums = self._compute_checksums(corpus_data)
        integrity_checksums.update(agent_checksums)

        # Save complete corpus to file
        output_path = self._save_complete_corpus(sorted_verses, corpus_data['metadata'])

        return {
            'total_verses': len(sorted_verses),
            'verses': sorted_verses,
            'metadata': corpus_data['metadata'],
            'integrity': integrity_checksums,
            'output_path': output_path
        }

    def _load_corpus_chunk(self, agent_num: int) -> Optional[List[Dict]]:
        """
        Load corpus_<N>.json for specified agent.

        Args:
            agent_num: Agent number (1-32)

        Returns:
            List of verse dictionaries or None if file not found
        """
        corpus_file = Path(self.input_dir) / f'corpus_{agent_num}.json'

        try:
            if not corpus_file.exists():
                return None

            with open(corpus_file, 'r', encoding='utf-8') as f:
                corpus = json.load(f)

            return corpus if isinstance(corpus, list) else None

        except (json.JSONDecodeError, IOError) as e:
            print(f"Error loading {corpus_file}: {e}")
            return None

    def _validate_corpus(self, corpus: List[Dict]) -> Dict:
        """
        Validate merged corpus completeness.

        Checks:
        - All 6,236 verses present (or close to it)
        - No duplicates
        - All required fields populated
        - All verses verified (5-layer verification passed)

        Returns:
            {
                'total_verses': int,
                'verses_with_all_fields': int,
                'verses_with_verification': int,
                'coverage_percentage': float,
                'issues': List[str]
            }
        """
        issues = []
        required_fields = [
            'surah', 'ayah', 'verse_key', 'arabic_text',
            'physics_content', 'biology_content', 'medicine_content',
            'engineering_content', 'agriculture_content',
            'tafsirs', 'asbab_nuzul', 'semantic_analysis',
            'verification_layers', 'confidence_score'
        ]

        verse_count = len(corpus)
        verses_with_all_fields = 0
        verses_with_verification = 0
        verse_keys = set()
        duplicates = []

        for verse in corpus:
            # Check for duplicates
            verse_key = verse.get('verse_key', f"{verse.get('surah')}:{verse.get('ayah')}")
            if verse_key in verse_keys:
                duplicates.append(verse_key)
            verse_keys.add(verse_key)

            # Check for all required fields
            has_all_fields = all(field in verse for field in required_fields)
            if has_all_fields:
                verses_with_all_fields += 1

            # Check verification layers
            verification_layers = verse.get('verification_layers', {})
            if verification_layers.get('all_passed', False):
                verses_with_verification += 1

        # Validation checks
        if verse_count < 6200:
            issues.append(f"Verse count too low: {verse_count} (expected ~6,236)")

        if duplicates:
            issues.append(f"Duplicate verses found: {duplicates}")

        if verses_with_all_fields < verse_count * 0.95:
            issues.append(f"Many verses missing fields: {verses_with_all_fields}/{verse_count}")

        return {
            'total_verses': verse_count,
            'verses_with_all_fields': verses_with_all_fields,
            'verses_with_verification': verses_with_verification,
            'coverage_percentage': (verses_with_all_fields / verse_count * 100) if verse_count > 0 else 0,
            'issues': issues
        }

    def _sort_corpus(self, verses: List[Dict]) -> List[Dict]:
        """
        Sort verses by surah:ayah to ensure canonical Quranic order.

        Args:
            verses: List of verse dictionaries

        Returns:
            Sorted list of verses
        """
        return sorted(
            verses,
            key=lambda v: (v.get('surah', 0), v.get('ayah', 0))
        )

    def _compute_checksums(self, corpus_data: Dict) -> Dict:
        """
        Compute SHA256 checksums for integrity verification.

        Args:
            corpus_data: Dictionary containing verses and metadata

        Returns:
            Dictionary of checksums
        """
        checksums = {}

        # Overall corpus hash
        corpus_json = json.dumps(corpus_data, sort_keys=True)
        checksums['overall_hash'] = hashlib.sha256(corpus_json.encode()).hexdigest()

        # Hash of just the verses
        verses_json = json.dumps(corpus_data['verses'], sort_keys=True)
        checksums['verses_hash'] = hashlib.sha256(verses_json.encode()).hexdigest()

        # Hash of metadata
        metadata_json = json.dumps(corpus_data['metadata'], sort_keys=True)
        checksums['metadata_hash'] = hashlib.sha256(metadata_json.encode()).hexdigest()

        return checksums

    def _save_complete_corpus(self, verses: List[Dict], metadata: Dict) -> str:
        """
        Save merged corpus to complete_corpus.json.

        Args:
            verses: List of sorted verse dictionaries
            metadata: Metadata about the merge

        Returns:
            Path to the saved file
        """
        # Ensure output directory exists
        output_dir = Path(self.input_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        # Create complete corpus structure
        complete_corpus = {
            'verses': verses,
            'metadata': metadata
        }

        # Save to file
        output_path = output_dir / self.output_filename
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(complete_corpus, f, ensure_ascii=False, indent=2)

        return str(output_path)
