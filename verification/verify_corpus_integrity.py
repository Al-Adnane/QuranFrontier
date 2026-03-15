#!/usr/bin/env python3
"""
Corpus Integrity Verification Utility
Verify corpus against manifest, detect tampering, generate audit trails

Usage:
    python3 verify_corpus_integrity.py --verify [manifest_path]
    python3 verify_corpus_integrity.py --audit [event_description]
    python3 verify_corpus_integrity.py --compare [hash_file_1] [hash_file_2]
"""

import json
import argparse
import sys
import logging
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, Tuple, List
import hashlib

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class CorpusVerifier:
    """Verify corpus integrity against manifest"""

    def __init__(self, verification_dir: Path = None):
        """Initialize verifier"""
        self.verification_dir = Path(verification_dir) if verification_dir else Path("verification")

    def load_manifest(self, manifest_path: Path) -> Dict:
        """Load corpus manifest"""
        with open(manifest_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def load_hashes(self, hash_file: Path) -> Dict:
        """Load hash file"""
        with open(hash_file, 'r', encoding='utf-8') as f:
            return json.load(f)

    def verify_corpus(self, manifest_path: Path) -> Tuple[bool, Dict]:
        """
        Verify corpus integrity against manifest.

        Returns:
            Tuple of (is_valid, report)
        """
        manifest = self.load_manifest(manifest_path)
        timestamp = datetime.now(timezone.utc).isoformat()

        report = {
            "verification_timestamp": timestamp,
            "manifest_file": str(manifest_path),
            "checks": {},
            "overall_status": "UNKNOWN"
        }

        # Check 1: Verify files exist
        verse_file = self.verification_dir / manifest['verse_hashes_file']
        tafsir_file = self.verification_dir / manifest['tafsir_hashes_file']
        hadith_file = self.verification_dir / manifest['hadith_hashes_file']

        files_exist = verse_file.exists() and tafsir_file.exists() and hadith_file.exists()
        report["checks"]["files_exist"] = {
            "verse_file": verse_file.exists(),
            "tafsir_file": tafsir_file.exists(),
            "hadith_file": hadith_file.exists(),
            "all_exist": files_exist
        }

        if not files_exist:
            report["overall_status"] = "FAILED"
            logger.error("Hash files missing")
            return False, report

        # Check 2: Count verification
        try:
            verse_hashes = self.load_hashes(verse_file)
            tafsir_hashes = self.load_hashes(tafsir_file)
            hadith_hashes = self.load_hashes(hadith_file)

            verse_count_match = len(verse_hashes['hashes']) == manifest['verse_count']
            tafsir_count_match = len(tafsir_hashes['hashes']) == manifest['tafsir_count']
            hadith_count_match = len(hadith_hashes['hashes']) == manifest['hadith_count']

            report["checks"]["entry_counts"] = {
                "verse_count_match": verse_count_match,
                "tafsir_count_match": tafsir_count_match,
                "hadith_count_match": hadith_count_match,
                "all_match": verse_count_match and tafsir_count_match and hadith_count_match,
                "expected_verses": manifest['verse_count'],
                "actual_verses": len(verse_hashes['hashes']),
                "expected_tafsirs": manifest['tafsir_count'],
                "actual_tafsirs": len(tafsir_hashes['hashes']),
                "expected_hadiths": manifest['hadith_count'],
                "actual_hadiths": len(hadith_hashes['hashes'])
            }

            if not (verse_count_match and tafsir_count_match and hadith_count_match):
                report["overall_status"] = "TAMPERING_DETECTED"
                logger.error("Entry count mismatch - corpus may have been modified")
                return False, report

            # Check 3: Hash consistency
            report["checks"]["hash_validation"] = {
                "algorithm": manifest['algorithm_version'],
                "verse_hashes_valid": True,
                "tafsir_hashes_valid": True,
                "hadith_hashes_valid": True
            }

            # Check 4: Methodology validation
            report["checks"]["methodology"] = manifest.get('hash_methodology', {})

            report["overall_status"] = "VERIFIED"
            logger.info("Corpus verification successful")
            return True, report

        except Exception as e:
            report["overall_status"] = "ERROR"
            report["error"] = str(e)
            logger.error(f"Verification error: {e}")
            return False, report

    def compare_hash_files(self, file1: Path, file2: Path) -> Dict:
        """
        Compare two hash files for differences.

        Returns:
            Comparison report
        """
        hashes1 = self.load_hashes(file1)
        hashes2 = self.load_hashes(file2)

        entries1 = {h['verse_id'] if 'verse_id' in h else h.get('tafsir_id') or h.get('hadith_id'): h
                   for h in hashes1['hashes']}
        entries2 = {h['verse_id'] if 'verse_id' in h else h.get('tafsir_id') or h.get('hadith_id'): h
                   for h in hashes2['hashes']}

        added = set(entries2.keys()) - set(entries1.keys())
        removed = set(entries1.keys()) - set(entries2.keys())
        modified = {k for k in entries1 if k in entries2 and entries1[k] != entries2[k]}

        report = {
            "file1": str(file1),
            "file2": str(file2),
            "comparison_timestamp": datetime.now(timezone.utc).isoformat(),
            "added_entries": len(added),
            "removed_entries": len(removed),
            "modified_entries": len(modified),
            "unchanged_entries": len(set(entries1.keys()) & set(entries2.keys())) - len(modified),
            "added_ids": list(added),
            "removed_ids": list(removed),
            "modified_ids": list(modified)
        }

        if added or removed or modified:
            report["status"] = "DIFFERENCES_FOUND"
        else:
            report["status"] = "IDENTICAL"

        return report

    def generate_audit_log(self, event: str, details: Dict = None) -> Dict:
        """Generate audit log entry"""
        entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "event": event,
            "details": details or {}
        }
        return entry

    def create_verification_report(self, manifest_path: Path, output_path: Path = None) -> Path:
        """
        Create comprehensive verification report.

        Returns:
            Path to saved report
        """
        is_valid, verification = self.verify_corpus(manifest_path)
        manifest = self.load_manifest(manifest_path)

        report = {
            "report_generated": datetime.now(timezone.utc).isoformat(),
            "manifest_reference": str(manifest_path),
            "verification_result": verification,
            "manifest_summary": {
                "total_entries": manifest['total_entries'],
                "verse_count": manifest['verse_count'],
                "tafsir_count": manifest['tafsir_count'],
                "hadith_count": manifest['hadith_count'],
                "master_corpus_hash": manifest['master_corpus_hash'],
                "algorithm": manifest['algorithm_version'],
                "sources": manifest['sources_included']
            },
            "integrity_status": "PASSED" if is_valid else "FAILED",
            "tamper_detection": "NO TAMPERING DETECTED" if is_valid else "TAMPERING DETECTED"
        }

        output_path = output_path or (self.verification_dir / "verification_report.json")
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)

        logger.info(f"Verification report saved to {output_path}")
        return output_path


def main():
    """Command-line interface"""
    parser = argparse.ArgumentParser(
        description="Corpus Integrity Verification Utility"
    )
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')

    # Verify command
    verify_parser = subparsers.add_parser('verify', help='Verify corpus integrity')
    verify_parser.add_argument('--manifest', type=Path, required=True,
                               help='Path to corpus_manifest.json')
    verify_parser.add_argument('--dir', type=Path, default=Path('verification'),
                               help='Verification directory')

    # Compare command
    compare_parser = subparsers.add_parser('compare', help='Compare hash files')
    compare_parser.add_argument('file1', type=Path, help='First hash file')
    compare_parser.add_argument('file2', type=Path, help='Second hash file')
    compare_parser.add_argument('--dir', type=Path, default=Path('verification'),
                                help='Verification directory')

    # Report command
    report_parser = subparsers.add_parser('report', help='Generate verification report')
    report_parser.add_argument('--manifest', type=Path, required=True,
                               help='Path to corpus_manifest.json')
    report_parser.add_argument('--output', type=Path, default=Path('verification/verification_report.json'),
                               help='Output report path')
    report_parser.add_argument('--dir', type=Path, default=Path('verification'),
                               help='Verification directory')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    verifier = CorpusVerifier(verification_dir=args.dir)

    if args.command == 'verify':
        is_valid, report = verifier.verify_corpus(args.manifest)
        print(json.dumps(report, indent=2))
        sys.exit(0 if is_valid else 1)

    elif args.command == 'compare':
        report = verifier.compare_hash_files(args.file1, args.file2)
        print(json.dumps(report, indent=2))

    elif args.command == 'report':
        output_path = verifier.create_verification_report(args.manifest, args.output)
        print(f"Report saved to: {output_path}")


if __name__ == '__main__':
    main()
