#!/usr/bin/env python3
"""
Phase 2 Normalization Service
Handles Unicode NFC normalization and SHA-256 hashing of Quranic verses
"""

import json
import hashlib
import unicodedata
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any


class NormalizationService:
    """Service for normalizing Quranic text and generating hashes"""

    def __init__(self, corpus_path: str, output_dir: str = None):
        """Initialize the normalization service"""
        self.corpus_path = Path(corpus_path)
        self.output_dir = Path(output_dir) if output_dir else self.corpus_path.parent
        self.corpus_data = None
        self.normalized_data = {}
        self.stats = {
            'total_verses_processed': 0,
            'total_verses_normalized': 0,
            'errors': []
        }

    def load_corpus(self) -> Dict[str, Any]:
        """Load the merged corpus"""
        print(f"Loading corpus from {self.corpus_path}...")
        with open(self.corpus_path, 'r', encoding='utf-8') as f:
            self.corpus_data = json.load(f)
        print(f"Loaded {len(self.corpus_data.get('verses', []))} verses")
        return self.corpus_data

    def normalize_text_nfc(self, text: str) -> str:
        """Normalize text to NFC form"""
        if not text:
            return text
        return unicodedata.normalize('NFC', text)

    def generate_verse_hash(self, verse: Dict[str, Any]) -> str:
        """Generate SHA-256 hash for a verse based on core fields"""
        # Create hashable data from core fields
        hashable_data = {
            'verse_id': verse.get('verse_id'),
            'surah_number': verse.get('surah_number'),
            'ayah_number': verse.get('ayah_number'),
            'text_ar': verse.get('text_ar'),
            'text_en': verse.get('text_en')
        }

        # Serialize to JSON with consistent ordering
        json_str = json.dumps(hashable_data, ensure_ascii=False, sort_keys=True)

        # Generate SHA-256 hash
        hash_obj = hashlib.sha256(json_str.encode('utf-8'))
        return hash_obj.hexdigest()

    def normalize_verse(self, verse: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize a single verse"""
        normalized_verse = verse.copy()

        # Normalize all Arabic text to NFC
        if 'text_ar' in normalized_verse:
            normalized_verse['text_ar'] = self.normalize_text_nfc(normalized_verse['text_ar'])

        if 'surah_name_ar' in normalized_verse:
            normalized_verse['surah_name_ar'] = self.normalize_text_nfc(normalized_verse['surah_name_ar'])

        # Generate SHA-256 hash
        normalized_verse['hash'] = self.generate_verse_hash(normalized_verse)

        return normalized_verse

    def process_quran(self) -> List[Dict[str, Any]]:
        """Process and normalize all Quranic verses"""
        print("\nNormalizing Quranic verses...")
        verses = self.corpus_data.get('verses', [])
        self.stats['total_verses_processed'] = len(verses)

        normalized_verses = []
        for i, verse in enumerate(verses):
            try:
                normalized_verse = self.normalize_verse(verse)
                normalized_verses.append(normalized_verse)
                self.stats['total_verses_normalized'] += 1

                if (i + 1) % 1000 == 0:
                    print(f"  Processed {i + 1}/{len(verses)} verses...")
            except Exception as e:
                error_msg = f"Error normalizing verse {verse.get('verse_id')}: {str(e)}"
                self.stats['errors'].append(error_msg)
                print(f"  Warning: {error_msg}")

        print(f"Normalized {self.stats['total_verses_normalized']} verses")
        return normalized_verses

    def generate_searchable_version(self, verses: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate searchable version with diacritics removed"""
        print("\nGenerating searchable version (diacritics removed)...")
        searchable_verses = []

        # Arabic diacritical marks
        arabic_diacritics = [
            '\u064B',  # FATHATAN
            '\u064C',  # DAMMATAN
            '\u064D',  # KASRATAN
            '\u064E',  # FATHA
            '\u064F',  # DAMMA
            '\u0650',  # KASRA
            '\u0651',  # SHADDA
            '\u0652',  # SUKUN
            '\u0653',  # MADDAH
            '\u0654',  # HAMZA ABOVE
            '\u0655',  # HAMZA BELOW
            '\u0656',  # SUBSCRIPT ALEF
            '\u0657',  # INVERTED DAMMA
            '\u0658',  # MARK NOON GHUNNA
            '\u0670',  # SUPERSCRIPT ALEF
        ]

        for verse in verses:
            searchable_verse = verse.copy()

            # Remove diacritics from Arabic text for indexing
            if 'text_ar' in searchable_verse:
                text = searchable_verse['text_ar']
                for diacritic in arabic_diacritics:
                    text = text.replace(diacritic, '')
                searchable_verse['text_ar_searchable'] = text

            searchable_verses.append(searchable_verse)

        return searchable_verses

    def save_normalized_quran(self, normalized_verses: List[Dict[str, Any]]) -> Path:
        """Save normalized Quran to file"""
        output_path = self.output_dir / "normalized_quran.json"

        output_data = {
            'metadata': {
                'normalization_id': f"norm_{datetime.now().isoformat()}",
                'created_at': datetime.now().isoformat(),
                'normalization_form': 'NFC',
                'hash_algorithm': 'SHA-256',
                'total_verses': len(normalized_verses)
            },
            'verses': normalized_verses
        }

        print(f"\nSaving normalized Quran to {output_path}...")
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)

        print(f"Saved {len(normalized_verses)} verses to {output_path}")
        return output_path

    def save_searchable_quran(self, searchable_verses: List[Dict[str, Any]]) -> Path:
        """Save searchable (diacritics-removed) Quran to file"""
        output_path = self.output_dir / "normalized_quran_searchable.json"

        output_data = {
            'metadata': {
                'normalization_id': f"norm_searchable_{datetime.now().isoformat()}",
                'created_at': datetime.now().isoformat(),
                'normalization_form': 'NFC (diacritics removed)',
                'hash_algorithm': 'SHA-256',
                'total_verses': len(searchable_verses),
                'note': 'This version has diacritics removed for text indexing'
            },
            'verses': searchable_verses
        }

        print(f"Saving searchable Quran to {output_path}...")
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)

        print(f"Saved {len(searchable_verses)} searchable verses")
        return output_path

    def save_tafsir(self) -> Path:
        """Save normalized Tafsir collection"""
        output_path = self.output_dir / "normalized_tafsir.json"

        tafsirs = self.corpus_data.get('tafsirs', [])

        # Normalize tafsir text
        normalized_tafsirs = []
        for tafsir in tafsirs:
            norm_tafsir = tafsir.copy()

            # Normalize Arabic fields
            if 'text_ar' in norm_tafsir:
                norm_tafsir['text_ar'] = self.normalize_text_nfc(norm_tafsir['text_ar'])

            normalized_tafsirs.append(norm_tafsir)

        output_data = {
            'metadata': {
                'created_at': datetime.now().isoformat(),
                'normalization_form': 'NFC',
                'total_tafsirs': len(normalized_tafsirs)
            },
            'tafsirs': normalized_tafsirs
        }

        print(f"\nSaving normalized Tafsir to {output_path}...")
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)

        print(f"Saved {len(normalized_tafsirs)} tafsirs")
        return output_path

    def save_hadith(self) -> Path:
        """Save normalized Hadith collection"""
        output_path = self.output_dir / "normalized_hadith.json"

        hadiths = self.corpus_data.get('hadiths', [])

        # Normalize hadith text
        normalized_hadiths = []
        for hadith in hadiths:
            norm_hadith = hadith.copy()

            # Normalize Arabic fields
            if 'text_ar' in norm_hadith:
                norm_hadith['text_ar'] = self.normalize_text_nfc(norm_hadith['text_ar'])

            normalized_hadiths.append(norm_hadith)

        output_data = {
            'metadata': {
                'created_at': datetime.now().isoformat(),
                'normalization_form': 'NFC',
                'total_hadiths': len(normalized_hadiths)
            },
            'hadiths': normalized_hadiths
        }

        print(f"Saving normalized Hadith to {output_path}...")
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)

        print(f"Saved {len(normalized_hadiths)} hadiths")
        return output_path

    def generate_report(self, output_files: Dict[str, Path]) -> Path:
        """Generate normalization report"""
        report_path = self.output_dir / "normalization_report.json"

        report = {
            'normalization_id': f"norm_{datetime.now().isoformat()}",
            'timestamp': datetime.now().isoformat(),
            'total_verses_processed': self.stats['total_verses_processed'],
            'total_verses_normalized': self.stats['total_verses_normalized'],
            'unicode_normalization_form': 'NFC (Canonical Composition)',
            'hash_algorithm': 'SHA-256',
            'output_files': {
                key: str(path) for key, path in output_files.items()
            },
            'validation_stats': {
                'verses_with_hash': self.stats['total_verses_normalized'],
                'verses_in_nfc': self.stats['total_verses_normalized'],
                'errors': len(self.stats['errors'])
            },
            'errors': self.stats['errors'] if self.stats['errors'] else []
        }

        print(f"\nSaving normalization report to {report_path}...")
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)

        return report_path

    def run(self):
        """Execute the complete normalization process"""
        print("=" * 60)
        print("PHASE 2 NORMALIZATION - Unicode NFC & SHA-256 Hashing")
        print("=" * 60)

        # Load corpus
        self.load_corpus()

        # Normalize Quran
        normalized_verses = self.process_quran()

        # Generate searchable version
        searchable_verses = self.generate_searchable_version(normalized_verses)

        # Save outputs
        output_files = {}
        output_files['normalized_quran'] = self.save_normalized_quran(normalized_verses)
        output_files['normalized_quran_searchable'] = self.save_searchable_quran(searchable_verses)
        output_files['normalized_tafsir'] = self.save_tafsir()
        output_files['normalized_hadith'] = self.save_hadith()

        # Generate report
        report_path = self.generate_report(output_files)
        output_files['normalization_report'] = report_path

        print("\n" + "=" * 60)
        print("NORMALIZATION COMPLETE")
        print("=" * 60)
        print(f"\nProcessed: {self.stats['total_verses_processed']} verses")
        print(f"Normalized: {self.stats['total_verses_normalized']} verses")
        print(f"Errors: {len(self.stats['errors'])}")

        return output_files


def main():
    """Main entry point"""
    corpus_path = "/Users/mac/Desktop/QuranFrontier/corpus/merged_corpus.json"
    output_dir = "/Users/mac/Desktop/QuranFrontier/corpus"

    service = NormalizationService(corpus_path, output_dir)
    service.run()


if __name__ == "__main__":
    main()
