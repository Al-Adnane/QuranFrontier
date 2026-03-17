#!/usr/bin/env python3
"""
Pre-Quranic Corpus Text Verification Script

This script helps verify the JSON text files in the corpus.
Run this to check for common issues.

Usage:
    python verify_corpus.py --path /path/to/pre-quranic

NOTE: This checks file structure only, NOT content accuracy.
Content accuracy requires scholarly verification.
"""

import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Any

# Required fields in each JSON file
REQUIRED_METADATA_FIELDS = [
    "collection",
    "tradition",
    "language",
    "date_range"
]

REQUIRED_ACCURACY_FIELDS = [
    "status",
    "warning"
]

def check_json_file(filepath: Path) -> Dict[str, Any]:
    """Check a single JSON file for common issues."""
    result = {
        "file": str(filepath),
        "valid_json": False,
        "has_metadata": False,
        "has_accuracy_notice": False,
        "has_texts": False,
        "errors": [],
        "warnings": []
    }
    
    # Check if file is valid JSON
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        result["valid_json"] = True
    except json.JSONDecodeError as e:
        result["errors"].append(f"Invalid JSON: {e}")
        return result
    except Exception as e:
        result["errors"].append(f"Cannot read file: {e}")
        return result
    
    # Check for metadata
    if "metadata" in data:
        result["has_metadata"] = True
        metadata = data["metadata"]
        
        # Check required metadata fields
        for field in REQUIRED_METADATA_FIELDS:
            if field not in metadata:
                result["warnings"].append(f"Missing metadata field: {field}")
        
        # Check for accuracy notice
        if "accuracy_notice" in metadata:
            result["has_accuracy_notice"] = True
            accuracy = metadata["accuracy_notice"]
            for field in REQUIRED_ACCURACY_FIELDS:
                if field not in accuracy:
                    result["warnings"].append(f"Missing accuracy field: {field}")
        else:
            result["warnings"].append("No accuracy_notice in metadata")
    else:
        result["warnings"].append("No metadata section")
    
    # Check for texts
    if "texts" in data:
        result["has_texts"] = True
        if len(data["texts"]) == 0:
            result["warnings"].append("Empty texts array")
    
    return result

def verify_corpus(corpus_path: Path) -> Dict[str, Any]:
    """Verify all JSON files in the corpus."""
    results = {
        "total_files": 0,
        "valid_files": 0,
        "files_with_errors": [],
        "files_with_warnings": [],
        "details": []
    }
    
    # Find all JSON files
    json_files = list(corpus_path.rglob("*.json"))
    results["total_files"] = len(json_files)
    
    for json_file in json_files:
        # Skip metadata files
        if "metadata" in str(json_file):
            continue
            
        result = check_json_file(json_file)
        results["details"].append(result)
        
        if result["valid_json"]:
            results["valid_files"] += 1
        
        if result["errors"]:
            results["files_with_errors"].append({
                "file": str(json_file),
                "errors": result["errors"]
            })
        
        if result["warnings"]:
            results["files_with_warnings"].append({
                "file": str(json_file),
                "warnings": result["warnings"]
            })
    
    return results

def print_report(results: Dict[str, Any]):
    """Print verification report."""
    print("=" * 60)
    print("PRE-QURANIC CORPUS VERIFICATION REPORT")
    print("=" * 60)
    print()
    print(f"Total JSON files checked: {results['total_files']}")
    print(f"Valid JSON files: {results['valid_files']}")
    print(f"Files with errors: {len(results['files_with_errors'])}")
    print(f"Files with warnings: {len(results['files_with_warnings'])}")
    print()
    
    if results["files_with_errors"]:
        print("FILES WITH ERRORS:")
        print("-" * 60)
        for item in results["files_with_errors"]:
            print(f"\n{item['file']}")
            for error in item["errors"]:
                print(f"  ❌ {error}")
        print()
    
    if results["files_with_warnings"]:
        print("FILES WITH WARNINGS:")
        print("-" * 60)
        for item in results["files_with_warnings"][:10]:  # Show first 10
            print(f"\n{item['file']}")
            for warning in item["warnings"]:
                print(f"  ⚠️ {warning}")
        if len(results["files_with_warnings"]) > 10:
            print(f"\n... and {len(results['files_with_warnings']) - 10} more files")
        print()
    
    print("=" * 60)
    print("NOTE: This script checks file structure only.")
    print("Content accuracy requires scholarly verification.")
    print("See VERIFICATION_STATUS.md for known issues.")
    print("=" * 60)

def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python verify_corpus.py <path_to_corpus>")
        print("Example: python verify_corpus.py /path/to/pre-quranic")
        sys.exit(1)
    
    corpus_path = Path(sys.argv[1])
    
    if not corpus_path.exists():
        print(f"Error: Path does not exist: {corpus_path}")
        sys.exit(1)
    
    results = verify_corpus(corpus_path)
    print_report(results)
    
    # Exit with error code if there are errors
    if results["files_with_errors"]:
        sys.exit(1)
    else:
        sys.exit(0)

if __name__ == "__main__":
    main()
