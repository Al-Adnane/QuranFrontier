"""
Test suite for CorpusMerger - Consolidates 32 parallel corpus extractions
"""
import pytest
import json
import os
import shutil
from pathlib import Path
from datetime import datetime

# Add parent directories to path for imports
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from quran.corpus_extraction.output.corpus_merger import CorpusMerger


class TestCorpusMergerInitialization:
    """Test corpus merger initialization"""

    def test_corpus_merger_initialization(self):
        """Verify merger initialized with correct paths"""
        merger = CorpusMerger()

        assert merger.input_dir == 'quran/corpus_extraction/output'
        assert merger.num_agents == 32
        assert merger.expected_verses == 6236
        assert hasattr(merger, 'merge_all_corpora')
        assert hasattr(merger, '_load_corpus_chunk')
        assert hasattr(merger, '_validate_corpus')
        assert hasattr(merger, '_sort_corpus')
        assert hasattr(merger, '_compute_checksums')
        assert hasattr(merger, '_save_complete_corpus')


class TestLoadSingleCorpusChunk:
    """Test loading individual corpus chunks"""

    @pytest.fixture
    def setup_test_corpus(self, tmp_path):
        """Create test corpus files"""
        # Create a sample corpus chunk
        test_corpus = [
            {
                "surah": 1,
                "ayah": 1,
                "verse_key": "1:1",
                "arabic_text": "بسم الله الرحمن الرحيم",
                "physics_content": {"concepts": []},
                "biology_content": {"concepts": []},
                "medicine_content": {"concepts": []},
                "engineering_content": {"concepts": []},
                "agriculture_content": {"concepts": []},
                "tafsirs": [],
                "asbab_nuzul": {},
                "semantic_analysis": {},
                "verification_layers": {
                    "layer_1_primary": True,
                    "layer_2_secondary": True,
                    "layer_3_peer_review": True,
                    "layer_4_semantic": True,
                    "layer_5_zero_fab": True,
                    "all_passed": True
                },
                "confidence_score": 0.95
            }
        ]

        # Write test corpus to temp directory
        corpus_path = tmp_path / "corpus_1.json"
        with open(corpus_path, 'w') as f:
            json.dump(test_corpus, f)

        return tmp_path

    def test_load_single_corpus_chunk(self, setup_test_corpus, monkeypatch):
        """Load corpus_1.json and verify contains verse list"""
        # Temporarily change input directory for testing
        merger = CorpusMerger()
        monkeypatch.setattr(merger, 'input_dir', str(setup_test_corpus))

        corpus = merger._load_corpus_chunk(1)

        assert corpus is not None
        assert isinstance(corpus, list)
        assert len(corpus) > 0
        assert corpus[0]['surah'] == 1
        assert corpus[0]['ayah'] == 1


class TestLoadAllCorpusChunks:
    """Test loading all corpus chunks"""

    @pytest.fixture
    def setup_all_test_corpus(self, tmp_path):
        """Create multiple test corpus files"""
        verses_per_chunk = 200

        for chunk_num in range(1, 4):  # Create 3 test chunks
            test_verses = []
            start_idx = (chunk_num - 1) * verses_per_chunk

            for i in range(verses_per_chunk):
                # Generate valid surah:ayah combinations
                ayah_idx = start_idx + i
                surah = min((ayah_idx // 195) + 1, 114)
                ayah = (ayah_idx % 195) + 1

                test_verses.append({
                    "surah": surah,
                    "ayah": ayah,
                    "verse_key": f"{surah}:{ayah}",
                    "arabic_text": f"Verse {ayah_idx}",
                    "physics_content": {"concepts": []},
                    "biology_content": {"concepts": []},
                    "medicine_content": {"concepts": []},
                    "engineering_content": {"concepts": []},
                    "agriculture_content": {"concepts": []},
                    "tafsirs": [],
                    "asbab_nuzul": {},
                    "semantic_analysis": {},
                    "verification_layers": {
                        "layer_1_primary": True,
                        "layer_2_secondary": True,
                        "layer_3_peer_review": True,
                        "layer_4_semantic": True,
                        "layer_5_zero_fab": True,
                        "all_passed": True
                    },
                    "confidence_score": 0.95
                })

            corpus_path = tmp_path / f"corpus_{chunk_num}.json"
            with open(corpus_path, 'w') as f:
                json.dump(test_verses, f)

        return tmp_path

    def test_load_all_corpus_chunks(self, setup_all_test_corpus, monkeypatch):
        """Load all chunks and verify each loads successfully"""
        merger = CorpusMerger()
        monkeypatch.setattr(merger, 'input_dir', str(setup_all_test_corpus))

        # Load first 3 chunks
        for i in range(1, 4):
            corpus = merger._load_corpus_chunk(i)
            assert corpus is not None
            assert isinstance(corpus, list)
            assert len(corpus) == 200


class TestMergeCorpora:
    """Test merging all corpus chunks"""

    @pytest.fixture
    def setup_merge_test_corpus(self, tmp_path):
        """Create test corpus files for merge testing"""
        num_chunks = 32
        verses_per_chunk = 195  # ~6,240 total verses

        for chunk_num in range(1, num_chunks + 1):
            test_verses = []
            start_idx = (chunk_num - 1) * verses_per_chunk

            for i in range(verses_per_chunk):
                ayah_idx = start_idx + i
                if ayah_idx >= 6236:
                    break

                surah = min((ayah_idx // 195) + 1, 114)
                ayah = (ayah_idx % 195) + 1

                test_verses.append({
                    "surah": surah,
                    "ayah": ayah,
                    "verse_key": f"{surah}:{ayah}",
                    "arabic_text": f"Verse {ayah_idx}",
                    "physics_content": {"concepts": []},
                    "biology_content": {"concepts": []},
                    "medicine_content": {"concepts": []},
                    "engineering_content": {"concepts": []},
                    "agriculture_content": {"concepts": []},
                    "tafsirs": [],
                    "asbab_nuzul": {},
                    "semantic_analysis": {},
                    "verification_layers": {
                        "layer_1_primary": True,
                        "layer_2_secondary": True,
                        "layer_3_peer_review": True,
                        "layer_4_semantic": True,
                        "layer_5_zero_fab": True,
                        "all_passed": True
                    },
                    "confidence_score": 0.95
                })

            corpus_path = tmp_path / f"corpus_{chunk_num}.json"
            with open(corpus_path, 'w') as f:
                json.dump(test_verses, f)

        return tmp_path

    def test_merge_corpora(self, setup_merge_test_corpus, monkeypatch):
        """Merge all 32 chunks and verify output contains ~6,236 verses"""
        merger = CorpusMerger()
        monkeypatch.setattr(merger, 'input_dir', str(setup_merge_test_corpus))

        result = merger.merge_all_corpora()

        assert result is not None
        assert 'total_verses' in result
        assert 'verses' in result
        assert 'metadata' in result
        assert result['total_verses'] >= 6200
        assert result['total_verses'] <= 6236
        assert isinstance(result['verses'], list)


class TestSortByVerseOrder:
    """Test verse sorting by canonical order"""

    def test_sort_by_verse_order(self, tmp_path, monkeypatch):
        """Verify merged corpus sorted by surah:ayah"""
        merger = CorpusMerger()

        # Create unsorted verses
        verses = [
            {"surah": 2, "ayah": 5, "verse_key": "2:5"},
            {"surah": 1, "ayah": 2, "verse_key": "1:2"},
            {"surah": 1, "ayah": 1, "verse_key": "1:1"},
            {"surah": 2, "ayah": 1, "verse_key": "2:1"},
            {"surah": 114, "ayah": 6, "verse_key": "114:6"},
        ]

        sorted_verses = merger._sort_corpus(verses)

        # Verify sort order
        assert sorted_verses[0]['verse_key'] == "1:1"
        assert sorted_verses[-1]['verse_key'] == "114:6"

        # Verify proper ordering
        for i in range(len(sorted_verses) - 1):
            current = sorted_verses[i]
            next_verse = sorted_verses[i + 1]
            current_key = (current['surah'], current['ayah'])
            next_key = (next_verse['surah'], next_verse['ayah'])
            assert current_key < next_key


class TestValidateCorpusCompleteness:
    """Test corpus validation"""

    def test_validate_corpus_completeness(self, tmp_path):
        """Validate merged corpus completeness"""
        merger = CorpusMerger()

        # Create test corpus with all required fields
        corpus = [
            {
                "surah": 1,
                "ayah": 1,
                "verse_key": "1:1",
                "arabic_text": "Test",
                "physics_content": {"concepts": []},
                "biology_content": {"concepts": []},
                "medicine_content": {"concepts": []},
                "engineering_content": {"concepts": []},
                "agriculture_content": {"concepts": []},
                "tafsirs": [],
                "asbab_nuzul": {},
                "semantic_analysis": {},
                "verification_layers": {
                    "layer_1_primary": True,
                    "layer_2_secondary": True,
                    "layer_3_peer_review": True,
                    "layer_4_semantic": True,
                    "layer_5_zero_fab": True,
                    "all_passed": True
                },
                "confidence_score": 0.95
            }
        ]

        validation = merger._validate_corpus(corpus)

        assert 'total_verses' in validation
        assert 'verses_with_all_fields' in validation
        assert 'verses_with_verification' in validation
        assert 'coverage_percentage' in validation
        assert 'issues' in validation
        assert isinstance(validation['issues'], list)
        assert validation['total_verses'] == 1
        assert validation['verses_with_all_fields'] >= 1


class TestComputeChecksums:
    """Test integrity checksum computation"""

    def test_compute_checksums(self):
        """Compute integrity checksums for all agents"""
        merger = CorpusMerger()

        test_data = {
            'verses': [
                {"surah": 1, "ayah": 1, "verse_key": "1:1", "text": "Test"}
            ],
            'metadata': {
                'source_agents': 32
            }
        }

        checksums = merger._compute_checksums(test_data)

        assert isinstance(checksums, dict)
        assert 'overall_hash' in checksums or len(checksums) > 0
        # Verify checksums are valid SHA256 hex strings
        for key, value in checksums.items():
            assert isinstance(value, str)
            # SHA256 hashes are 64 hex characters
            if len(value) == 64:
                try:
                    int(value, 16)  # Verify it's valid hex
                except ValueError:
                    pytest.fail(f"Invalid hex hash: {value}")


class TestSaveCompleteCorpus:
    """Test saving complete corpus to JSON"""

    def test_save_complete_corpus(self, tmp_path, monkeypatch):
        """Save complete_corpus.json and verify file created"""
        merger = CorpusMerger()
        monkeypatch.setattr(merger, 'input_dir', str(tmp_path))

        test_verses = [
            {
                "surah": 1,
                "ayah": 1,
                "verse_key": "1:1",
                "arabic_text": "Test",
                "physics_content": {"concepts": []},
                "biology_content": {"concepts": []},
                "medicine_content": {"concepts": []},
                "engineering_content": {"concepts": []},
                "agriculture_content": {"concepts": []},
                "tafsirs": [],
                "asbab_nuzul": {},
                "semantic_analysis": {},
                "verification_layers": {
                    "layer_1_primary": True,
                    "layer_2_secondary": True,
                    "layer_3_peer_review": True,
                    "layer_4_semantic": True,
                    "layer_5_zero_fab": True,
                    "all_passed": True
                },
                "confidence_score": 0.95
            }
        ]

        metadata = {
            'merge_timestamp': datetime.now().isoformat(),
            'source_agents': 32,
            'source_files': [f'corpus_{i}.json' for i in range(1, 33)]
        }

        output_path = merger._save_complete_corpus(test_verses, metadata)

        assert output_path is not None
        assert os.path.exists(output_path)

        # Verify file can be loaded and parsed
        with open(output_path, 'r') as f:
            loaded_data = json.load(f)

        assert 'verses' in loaded_data
        assert 'metadata' in loaded_data
        assert len(loaded_data['verses']) == 1


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
