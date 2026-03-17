"""Phase 3: AraBERT Embedding Service Tests (TDD)

This test file uses test-driven development:
1. Tests are written FIRST
2. Tests FAIL initially (no implementation)
3. Implementation written to PASS tests
4. Tests verify AraBERT embeddings work correctly
"""
import pytest
import numpy as np
import json
import tempfile
import os
from pathlib import Path

# Import the service we're about to build
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))

from api.embeddings.arabert_service import AraBERTService


class TestAraBERTServiceInitialization:
    """Test AraBERTService can be initialized"""

    def test_arabert_service_initializes(self):
        """Test that AraBERTService can be created"""
        service = AraBERTService(use_dummy=True)
        assert service is not None

    def test_arabert_service_has_embedding_dimension(self):
        """Test that service knows the embedding dimension"""
        service = AraBERTService(use_dummy=True)
        assert service.embedding_dim == 768

    def test_arabert_service_dummy_mode_flag(self):
        """Test that dummy mode flag is set correctly"""
        service = AraBERTService(use_dummy=True)
        assert service.use_dummy is True


class TestAraBERTEmbedding:
    """Test AraBERT embedding generation"""

    def test_embed_text_returns_vector(self):
        """Test that embed_text returns a numpy array"""
        service = AraBERTService(use_dummy=True)
        text = "بسم الله الرحمن الرحيم"
        embedding = service.embed_text(text)
        assert isinstance(embedding, np.ndarray)

    def test_embedding_dimension_is_768(self):
        """Test that embeddings are 768-dimensional (AraBERT standard)"""
        service = AraBERTService(use_dummy=True)
        text = "الحمد لله رب العالمين"
        embedding = service.embed_text(text)
        assert embedding.shape == (768,), f"Expected shape (768,), got {embedding.shape}"

    def test_embedding_is_l2_normalized(self):
        """Test that embeddings are L2-normalized (||v|| = 1.0)"""
        service = AraBERTService(use_dummy=True)
        text = "قل هو الله أحد"
        embedding = service.embed_text(text)

        # L2 norm should be approximately 1.0
        l2_norm = np.linalg.norm(embedding, ord=2)
        assert np.isclose(l2_norm, 1.0, atol=1e-6), f"Expected L2 norm ~1.0, got {l2_norm}"

    def test_embedding_consistency(self):
        """Test that same text produces same embedding (deterministic)"""
        service = AraBERTService(use_dummy=True)
        text = "محمد رسول الله"

        embedding1 = service.embed_text(text)
        embedding2 = service.embed_text(text)

        assert np.allclose(embedding1, embedding2), "Same text should produce same embedding"

    def test_different_texts_produce_different_embeddings(self):
        """Test that different texts produce different embeddings"""
        service = AraBERTService(use_dummy=True)
        text1 = "صلاة الفجر"
        text2 = "صلاة العصر"

        embedding1 = service.embed_text(text1)
        embedding2 = service.embed_text(text2)

        # Different texts should produce different embeddings
        assert not np.allclose(embedding1, embedding2), "Different texts should produce different embeddings"

    def test_embedding_values_are_float(self):
        """Test that embedding values are floats"""
        service = AraBERTService(use_dummy=True)
        text = "إن الله مع الصابرين"
        embedding = service.embed_text(text)

        assert embedding.dtype == np.float32 or embedding.dtype == np.float64, \
            f"Expected float dtype, got {embedding.dtype}"

    def test_embedding_values_in_valid_range(self):
        """Test that embedding values are in reasonable range for normalized vectors"""
        service = AraBERTService(use_dummy=True)
        text = "والعصر إن الإنسان لفي خسر"
        embedding = service.embed_text(text)

        # For L2-normalized vectors, individual values should be in [-1, 1]
        assert np.all(embedding >= -1.0) and np.all(embedding <= 1.0), \
            f"Embedding values out of range: min={embedding.min()}, max={embedding.max()}"


class TestBatchEmbedding:
    """Test batch embedding generation"""

    def test_embed_batch_returns_array(self):
        """Test that embed_batch returns array of embeddings"""
        service = AraBERTService(use_dummy=True)
        texts = ["النص الأول", "النص الثاني", "النص الثالث"]
        embeddings = service.embed_batch(texts, batch_size=2)

        assert isinstance(embeddings, np.ndarray)
        assert len(embeddings) == 3

    def test_batch_dimensions(self):
        """Test that batch embeddings have correct dimensions"""
        service = AraBERTService(use_dummy=True)
        texts = ["آية واحدة", "آية اثنين"]
        embeddings = service.embed_batch(texts)

        assert embeddings.shape == (2, 768), \
            f"Expected shape (2, 768), got {embeddings.shape}"

    def test_batch_and_single_embeddings_match(self):
        """Test that batch processing produces same result as individual embeddings"""
        service = AraBERTService(use_dummy=True)
        texts = ["الفاتحة", "البقرة", "آل عمران"]

        # Embed individually
        single_embeddings = [service.embed_text(text) for text in texts]

        # Embed as batch
        batch_embeddings = service.embed_batch(texts)

        # Results should match
        for i, single_emb in enumerate(single_embeddings):
            assert np.allclose(single_emb, batch_embeddings[i]), \
                f"Batch embedding {i} doesn't match individual embedding"

    def test_batch_size_parameter(self):
        """Test that different batch sizes produce same result"""
        service = AraBERTService(use_dummy=True)
        texts = ["سورة المائدة", "سورة الأنعام", "سورة الأعراف", "سورة الأنفال"]

        embeddings_batch2 = service.embed_batch(texts, batch_size=2)
        embeddings_batch4 = service.embed_batch(texts, batch_size=4)

        assert np.allclose(embeddings_batch2, embeddings_batch4), \
            "Different batch sizes should produce same results"


class TestEmbeddingFileSerialization:
    """Test saving and loading embeddings"""

    def test_save_embeddings_creates_file(self):
        """Test that save_embeddings creates a JSON file"""
        service = AraBERTService(use_dummy=True)

        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, "test_embeddings.json")

            embeddings_data = {
                "embeddings": [
                    service.embed_text("النص الأول").tolist(),
                    service.embed_text("النص الثاني").tolist()
                ],
                "metadata": {
                    "model_name": "aubmindlab/bert-base-arabertv2",
                    "vector_dimension": 768,
                    "normalization": "L2",
                    "count": 2
                }
            }

            service.save_embeddings(embeddings_data, output_path)

            assert os.path.exists(output_path), "Embedding file should be created"

    def test_save_embeddings_json_valid(self):
        """Test that saved embeddings are valid JSON"""
        service = AraBERTService(use_dummy=True)

        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, "test_embeddings.json")

            embeddings_data = {
                "embeddings": [service.embed_text("اختبار").tolist()],
                "metadata": {
                    "model_name": "aubmindlab/bert-base-arabertv2",
                    "vector_dimension": 768,
                    "normalization": "L2",
                    "count": 1
                }
            }

            service.save_embeddings(embeddings_data, output_path)

            # Verify it's valid JSON
            with open(output_path, 'r', encoding='utf-8') as f:
                loaded = json.load(f)

            assert "embeddings" in loaded
            assert "metadata" in loaded

    def test_load_embeddings_returns_dict(self):
        """Test that load_embeddings returns proper dictionary"""
        service = AraBERTService(use_dummy=True)

        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, "test_embeddings.json")

            original_data = {
                "embeddings": [service.embed_text("قرآن").tolist()],
                "metadata": {
                    "model_name": "aubmindlab/bert-base-arabertv2",
                    "vector_dimension": 768,
                    "normalization": "L2",
                    "count": 1
                }
            }

            service.save_embeddings(original_data, output_path)
            loaded_data = service.load_embeddings(output_path)

            assert "embeddings" in loaded_data
            assert "metadata" in loaded_data
            assert len(loaded_data["embeddings"]) == 1
            assert len(loaded_data["embeddings"][0]) == 768

    def test_embeddings_roundtrip_consistency(self):
        """Test that embeddings saved and loaded maintain precision"""
        service = AraBERTService(use_dummy=True)

        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, "test_embeddings.json")

            original_embedding = service.embed_text("وآخر دعوانا أن الحمد لله رب العالمين")

            embeddings_data = {
                "embeddings": [original_embedding.tolist()],
                "metadata": {
                    "model_name": "aubmindlab/bert-base-arabertv2",
                    "vector_dimension": 768,
                    "normalization": "L2",
                    "count": 1
                }
            }

            service.save_embeddings(embeddings_data, output_path)
            loaded_data = service.load_embeddings(output_path)

            loaded_embedding = np.array(loaded_data["embeddings"][0])

            # Precision might be slightly reduced due to JSON serialization
            assert np.allclose(original_embedding, loaded_embedding, atol=1e-5), \
                "Loaded embedding should match saved embedding"


class TestEmbeddingStatistics:
    """Test embedding statistics and validation"""

    def test_embedding_statistics_method(self):
        """Test that we can compute statistics on embeddings"""
        service = AraBERTService(use_dummy=True)

        texts = ["أول نص", "نص ثاني", "ثالث"]
        embeddings = service.embed_batch(texts)

        stats = service.compute_statistics(embeddings)

        assert "mean_norm" in stats
        assert "std_norm" in stats
        assert "min_value" in stats
        assert "max_value" in stats

    def test_embeddings_are_normalized(self):
        """Test that batch embeddings are L2-normalized"""
        service = AraBERTService(use_dummy=True)

        texts = ["الآية الأولى", "الآية الثانية", "الآية الثالثة"]
        embeddings = service.embed_batch(texts)

        norms = np.linalg.norm(embeddings, axis=1)

        # All norms should be approximately 1.0
        assert np.allclose(norms, 1.0, atol=1e-6), \
            f"Expected all norms ~1.0, got norms: {norms}"


class TestDummyMode:
    """Test dummy/mock mode for testing without actual model"""

    def test_dummy_mode_flag(self):
        """Test that dummy mode can be enabled"""
        service = AraBERTService(use_dummy=True)
        assert service.use_dummy is True

    def test_dummy_embeddings_are_deterministic(self):
        """Test that dummy embeddings are deterministic (same input = same output)"""
        service = AraBERTService(use_dummy=True)
        text = "اختبار الوضع الوهمي"

        emb1 = service.embed_text(text)
        emb2 = service.embed_text(text)

        assert np.array_equal(emb1, emb2), "Dummy embeddings should be deterministic"

    def test_dummy_mode_useful_for_ci(self):
        """Test that dummy mode is fast enough for CI/testing"""
        import time
        service = AraBERTService(use_dummy=True)

        texts = [f"اختبار {i}" for i in range(100)]

        start = time.time()
        embeddings = service.embed_batch(texts)
        elapsed = time.time() - start

        # Dummy mode should be very fast (< 1 second for 100 texts)
        assert elapsed < 1.0, f"Dummy embedding took {elapsed:.2f}s, should be < 1s"
        assert len(embeddings) == 100


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
