"""AraBERT Embedding Service - Phase 3 Implementation

Generates 768-dimensional embeddings for Quranic text using AraBERT model.
Supports both real embeddings (using transformers library) and dummy embeddings (for testing).
"""
import numpy as np
import json
import hashlib
from typing import List, Dict, Any, Optional, Union
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class AraBERTService:
    """Service for generating AraBERT embeddings"""

    def __init__(
        self,
        model_name: str = "aubmindlab/bert-base-arabertv2",
        use_dummy: bool = False,
        device: str = "cpu"
    ):
        """Initialize AraBERT service

        Args:
            model_name: HuggingFace model ID for AraBERT
            use_dummy: Use dummy embeddings for testing (fast, deterministic)
            device: PyTorch device ("cpu" or "cuda")
        """
        self.model_name = model_name
        self.use_dummy = use_dummy
        self.device = device
        self.embedding_dim = 768

        if not use_dummy:
            # Load real model and tokenizer
            try:
                from transformers import AutoModel, AutoTokenizer
                import torch

                logger.info(f"Loading AraBERT model: {model_name}")
                self.model = AutoModel.from_pretrained(model_name).to(device)
                self.tokenizer = AutoTokenizer.from_pretrained(model_name)
                self.torch = torch
                logger.info("AraBERT model loaded successfully")
            except ImportError:
                raise ImportError("transformers and torch are required. Install with: pip install transformers torch")
        else:
            # Dummy mode for testing
            self.model = None
            self.tokenizer = None
            self.torch = None
            logger.info("Using dummy embeddings mode (for testing)")

    def embed_text(self, text: str) -> np.ndarray:
        """Generate embedding for a single text

        Args:
            text: Arabic text to embed

        Returns:
            768-dimensional L2-normalized numpy array
        """
        if self.use_dummy:
            return self._embed_text_dummy(text)
        else:
            return self._embed_text_real(text)

    def _embed_text_dummy(self, text: str) -> np.ndarray:
        """Generate dummy embedding (deterministic based on text hash)

        This is useful for testing without loading the actual model.
        """
        # Generate deterministic embedding based on text
        text_hash = hashlib.sha256(text.encode('utf-8')).digest()

        # Create 768-dimensional vector from hash
        np.random.seed(int.from_bytes(text_hash[:4], byteorder='big') % (2**31))
        embedding = np.random.randn(self.embedding_dim).astype(np.float32)

        # L2 normalize
        embedding = embedding / np.linalg.norm(embedding)

        return embedding

    def _embed_text_real(self, text: str) -> np.ndarray:
        """Generate real embedding using AraBERT model"""
        if self.model is None or self.tokenizer is None:
            raise RuntimeError("Model not loaded. Use use_dummy=False during initialization")

        # Tokenize
        tokens = self.tokenizer(
            text,
            return_tensors="pt",
            padding=True,
            truncation=True,
            max_length=512
        ).to(self.device)

        # Get embeddings
        with self.torch.no_grad():
            outputs = self.model(**tokens)

        # Use [CLS] token embedding (first token)
        embedding = outputs.last_hidden_state[:, 0, :].cpu().numpy()[0].astype(np.float32)

        # L2 normalize
        embedding = embedding / np.linalg.norm(embedding)

        return embedding

    def embed_batch(
        self,
        texts: List[str],
        batch_size: int = 32,
        show_progress: bool = False
    ) -> np.ndarray:
        """Generate embeddings for multiple texts

        Args:
            texts: List of Arabic texts
            batch_size: Batch size for processing
            show_progress: Show progress bar (requires tqdm)

        Returns:
            (N, 768) numpy array of embeddings
        """
        embeddings = []

        if show_progress:
            try:
                from tqdm import tqdm
                iterator = tqdm(range(0, len(texts), batch_size), desc="Embedding texts")
            except ImportError:
                show_progress = False
                iterator = range(0, len(texts), batch_size)
        else:
            iterator = range(0, len(texts), batch_size)

        for i in iterator:
            batch_texts = texts[i:i + batch_size]

            if self.use_dummy:
                batch_embeddings = np.array(
                    [self._embed_text_dummy(text) for text in batch_texts]
                )
            else:
                batch_embeddings = self._embed_batch_real(batch_texts)

            embeddings.append(batch_embeddings)

        return np.vstack(embeddings)

    def _embed_batch_real(self, texts: List[str]) -> np.ndarray:
        """Generate real embeddings for a batch"""
        if self.model is None or self.tokenizer is None:
            raise RuntimeError("Model not loaded")

        # Tokenize batch
        tokens = self.tokenizer(
            texts,
            return_tensors="pt",
            padding=True,
            truncation=True,
            max_length=512
        ).to(self.device)

        # Get embeddings
        with self.torch.no_grad():
            outputs = self.model(**tokens)

        # Use [CLS] token embedding for each text
        embeddings = outputs.last_hidden_state[:, 0, :].cpu().numpy().astype(np.float32)

        # L2 normalize each embedding
        norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
        embeddings = embeddings / (norms + 1e-8)  # Add small epsilon to avoid division by zero

        return embeddings

    def compute_statistics(self, embeddings: np.ndarray) -> Dict[str, float]:
        """Compute statistics on embeddings

        Args:
            embeddings: (N, 768) array of embeddings

        Returns:
            Dictionary with statistics
        """
        norms = np.linalg.norm(embeddings, axis=1)

        return {
            "count": len(embeddings),
            "mean_norm": float(np.mean(norms)),
            "std_norm": float(np.std(norms)),
            "min_norm": float(np.min(norms)),
            "max_norm": float(np.max(norms)),
            "min_value": float(np.min(embeddings)),
            "max_value": float(np.max(embeddings)),
            "dimension": embeddings.shape[1]
        }

    def save_embeddings(
        self,
        embeddings_data: Dict[str, Any],
        output_path: Union[str, Path]
    ) -> None:
        """Save embeddings to JSON file

        Args:
            embeddings_data: Dictionary with 'embeddings' and 'metadata' keys
            output_path: Output file path
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(embeddings_data, f, ensure_ascii=False, indent=2)

        logger.info(f"Saved embeddings to {output_path}")

    @staticmethod
    def load_embeddings(input_path: Union[str, Path]) -> Dict[str, Any]:
        """Load embeddings from JSON file

        Args:
            input_path: Input file path

        Returns:
            Dictionary with embeddings and metadata
        """
        with open(input_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        logger.info(f"Loaded embeddings from {input_path}")
        return data

    def generate_corpus_embeddings(
        self,
        corpus_data: Dict[str, List[Dict]],
        output_dir: Union[str, Path] = "./embeddings"
    ) -> Dict[str, str]:
        """Generate embeddings for entire corpus

        Args:
            corpus_data: Dictionary with 'verses', 'tafsirs', 'hadiths' keys
            output_dir: Output directory for embedding files

        Returns:
            Dictionary mapping corpus type to output file path
        """
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        output_files = {}

        # Process verses
        if 'verses' in corpus_data:
            logger.info(f"Embedding {len(corpus_data['verses'])} verses...")
            verses_text = [v.get('text_arabic', '') for v in corpus_data['verses']]
            verses_embeddings = self.embed_batch(verses_text, show_progress=True)

            verses_output = {
                "embeddings": verses_embeddings.tolist(),
                "metadata": {
                    "model_name": self.model_name,
                    "vector_dimension": self.embedding_dim,
                    "normalization": "L2",
                    "count": len(verses_embeddings),
                    "corpus_type": "verses"
                },
                "statistics": self.compute_statistics(verses_embeddings)
            }

            verses_path = output_dir / "vectors_quran.json"
            self.save_embeddings(verses_output, verses_path)
            output_files['verses'] = str(verses_path)

        # Process tafsirs
        if 'tafsirs' in corpus_data:
            logger.info(f"Embedding {len(corpus_data['tafsirs'])} tafsirs...")
            tafsirs_text = [t.get('text', '') for t in corpus_data['tafsirs']]
            tafsirs_embeddings = self.embed_batch(tafsirs_text, show_progress=True)

            tafsirs_output = {
                "embeddings": tafsirs_embeddings.tolist(),
                "metadata": {
                    "model_name": self.model_name,
                    "vector_dimension": self.embedding_dim,
                    "normalization": "L2",
                    "count": len(tafsirs_embeddings),
                    "corpus_type": "tafsirs"
                },
                "statistics": self.compute_statistics(tafsirs_embeddings)
            }

            tafsirs_path = output_dir / "vectors_tafsir.json"
            self.save_embeddings(tafsirs_output, tafsirs_path)
            output_files['tafsirs'] = str(tafsirs_path)

        # Process hadiths
        if 'hadiths' in corpus_data:
            logger.info(f"Embedding {len(corpus_data['hadiths'])} hadiths...")
            hadiths_text = [h.get('text', '') for h in corpus_data['hadiths']]
            hadiths_embeddings = self.embed_batch(hadiths_text, show_progress=True)

            hadiths_output = {
                "embeddings": hadiths_embeddings.tolist(),
                "metadata": {
                    "model_name": self.model_name,
                    "vector_dimension": self.embedding_dim,
                    "normalization": "L2",
                    "count": len(hadiths_embeddings),
                    "corpus_type": "hadiths"
                },
                "statistics": self.compute_statistics(hadiths_embeddings)
            }

            hadiths_path = output_dir / "vectors_hadith.json"
            self.save_embeddings(hadiths_output, hadiths_path)
            output_files['hadiths'] = str(hadiths_path)

        logger.info(f"All embeddings generated. Output files: {output_files}")
        return output_files
