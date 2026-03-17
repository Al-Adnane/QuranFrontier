#!/usr/bin/env python3
"""
PHASE 1: Load real corpus data and generate embeddings
This script:
1. Loads merged corpus JSON
2. Generates real AraBERT embeddings (768-dim)
3. Saves embeddings for semantic search
4. Populates PostgreSQL with corpus data
"""

import json
import sys
import os
from pathlib import Path
from tqdm import tqdm

# Add quran-core to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.api.embeddings.arabert_service import AraBERTService

def load_corpus(corpus_path: str) -> dict:
    """Load merged corpus JSON"""
    print(f"📖 Loading corpus from {corpus_path}...")
    with open(corpus_path) as f:
        corpus = json.load(f)
    print(f"  ✓ Corpus loaded: {corpus['metadata']}")
    return corpus

def generate_embeddings(corpus: dict, output_dir: str = "embeddings") -> dict:
    """Generate real embeddings for all texts"""
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)

    print(f"\n🧠 Initializing AraBERT service (real mode)...")
    service = AraBERTService(dummy_mode=False)

    # Collect all texts for embedding
    embeddings_data = {
        "metadata": corpus["metadata"],
        "verses": [],
        "tafsirs": [],
        "hadiths": []
    }

    # Process verses
    print(f"\n📝 Processing {len(corpus['verses'])} verses...")
    for verse in tqdm(corpus["verses"], desc="Verses"):
        verse_text = verse.get("text", "")
        if verse_text:
            embedding = service.embed_text(verse_text)
            embeddings_data["verses"].append({
                "id": verse["id"],
                "surah": verse.get("surah"),
                "ayah": verse.get("ayah"),
                "text": verse_text,
                "embedding": embedding.tolist()  # Convert numpy to list for JSON
            })

    # Process tafsirs
    print(f"\n📚 Processing {len(corpus['tafsirs'])} tafsirs...")
    for tafsir in tqdm(corpus["tafsirs"][:100], desc="Tafsirs (first 100 for speed)"):
        tafsir_text = tafsir.get("text", "")
        if tafsir_text:
            embedding = service.embed_text(tafsir_text)
            embeddings_data["tafsirs"].append({
                "id": tafsir["id"],
                "verse_id": tafsir.get("verse_id"),
                "source": tafsir.get("source"),
                "text": tafsir_text[:500],  # Truncate for storage
                "embedding": embedding.tolist()
            })

    # Process hadiths
    print(f"\n📖 Processing {len(corpus['hadiths'])} hadiths...")
    for hadith in tqdm(corpus["hadiths"][:100], desc="Hadiths (first 100 for speed)"):
        hadith_text = hadith.get("text", "")
        if hadith_text:
            embedding = service.embed_text(hadith_text)
            embeddings_data["hadiths"].append({
                "id": hadith["id"],
                "chain": hadith.get("chain"),
                "grade": hadith.get("grade"),
                "text": hadith_text[:500],  # Truncate for storage
                "embedding": embedding.tolist()
            })

    # Save embeddings
    output_file = output_path / "corpus_embeddings.json"
    print(f"\n💾 Saving embeddings to {output_file}...")
    with open(output_file, "w") as f:
        json.dump(embeddings_data, f)

    print(f"✓ Embeddings saved: {len(embeddings_data['verses'])} verses, "
          f"{len(embeddings_data['tafsirs'])} tafsirs, {len(embeddings_data['hadiths'])} hadiths")

    return embeddings_data

def load_to_database(corpus: dict, embeddings: dict):
    """Load data into PostgreSQL"""
    import psycopg2
    from psycopg2.extras import execute_batch

    db_url = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/quran")
    print(f"\n🗄️  Connecting to database: {db_url}...")

    conn = psycopg2.connect(db_url)
    cur = conn.cursor()

    try:
        # Insert verses
        print(f"📝 Loading {len(embeddings['verses'])} verses to database...")
        verse_data = [
            (
                v["id"],
                v["surah"],
                v["ayah"],
                v["text"],
                json.dumps(v["embedding"])  # Store embedding as JSON
            )
            for v in embeddings["verses"]
        ]
        execute_batch(
            cur,
            "INSERT INTO verses (id, surah, ayah, text, embedding) VALUES (%s, %s, %s, %s, %s) ON CONFLICT DO NOTHING",
            verse_data,
            page_size=100
        )
        print(f"✓ Verses loaded")

        # Insert tafsirs
        print(f"📚 Loading {len(embeddings['tafsirs'])} tafsirs to database...")
        tafsir_data = [
            (
                t["id"],
                t["verse_id"],
                t["source"],
                t["text"],
                json.dumps(t["embedding"])
            )
            for t in embeddings["tafsirs"]
        ]
        execute_batch(
            cur,
            "INSERT INTO tafsirs (id, verse_id, source, text, embedding) VALUES (%s, %s, %s, %s, %s) ON CONFLICT DO NOTHING",
            tafsir_data,
            page_size=100
        )
        print(f"✓ Tafsirs loaded")

        # Insert hadiths
        print(f"📖 Loading {len(embeddings['hadiths'])} hadiths to database...")
        hadith_data = [
            (
                h["id"],
                h["chain"],
                h["grade"],
                h["text"],
                json.dumps(h["embedding"])
            )
            for h in embeddings["hadiths"]
        ]
        execute_batch(
            cur,
            "INSERT INTO hadiths (id, chain, grade, text, embedding) VALUES (%s, %s, %s, %s, %s) ON CONFLICT DO NOTHING",
            hadith_data,
            page_size=100
        )
        print(f"✓ Hadiths loaded")

        conn.commit()
        print(f"\n✓ All data loaded to database successfully")

    except Exception as e:
        conn.rollback()
        print(f"❌ Error loading data: {e}")
        raise
    finally:
        cur.close()
        conn.close()

def verify_embeddings(embeddings_file: str = "embeddings/corpus_embeddings.json"):
    """Verify embeddings were generated correctly"""
    print(f"\n✅ Verifying embeddings...")
    with open(embeddings_file) as f:
        data = json.load(f)

    # Check structure
    assert "verses" in data, "Missing verses"
    assert "tafsirs" in data, "Missing tafsirs"
    assert "hadiths" in data, "Missing hadiths"

    # Check embedding dimensions
    if data["verses"]:
        embedding_dim = len(data["verses"][0]["embedding"])
        assert embedding_dim == 768, f"Expected 768-dim embedding, got {embedding_dim}"
        print(f"  ✓ Verse embeddings: {len(data['verses'])} x {embedding_dim}")

    if data["tafsirs"]:
        embedding_dim = len(data["tafsirs"][0]["embedding"])
        assert embedding_dim == 768, f"Expected 768-dim embedding, got {embedding_dim}"
        print(f"  ✓ Tafsir embeddings: {len(data['tafsirs'])} x {embedding_dim}")

    if data["hadiths"]:
        embedding_dim = len(data["hadiths"][0]["embedding"])
        assert embedding_dim == 768, f"Expected 768-dim embedding, got {embedding_dim}"
        print(f"  ✓ Hadith embeddings: {len(data['hadiths'])} x {embedding_dim}")

    print(f"✓ Embeddings verified successfully!")

if __name__ == "__main__":
    try:
        # Load corpus
        corpus_path = "../corpus/merged_corpus.json"
        corpus = load_corpus(corpus_path)

        # Generate embeddings
        embeddings = generate_embeddings(corpus, output_dir="../embeddings")

        # Load to database (if DATABASE_URL is set)
        if os.getenv("DATABASE_URL"):
            load_to_database(corpus, embeddings)

        # Verify
        verify_embeddings("../embeddings/corpus_embeddings.json")

        print(f"\n🎉 PHASE 1 COMPLETE: Corpus loaded and embeddings generated!")
        sys.exit(0)

    except Exception as e:
        print(f"\n❌ PHASE 1 FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
