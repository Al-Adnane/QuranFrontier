#!/usr/bin/env python3
"""
Convert Pre-Quranic Corpus JSON to CSV format.

Usage:
    python convert_to_csv.py --input /path/to/pre-quranic --output /path/to/output

This creates CSV files for easier analysis in spreadsheet software.
"""

import json
import csv
import os
from pathlib import Path
from typing import List, Dict, Any

def extract_texts_from_json(filepath: Path) -> List[Dict[str, Any]]:
    """Extract all texts from a JSON file."""
    texts = []
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print(f"Error reading {filepath}: {e}")
        return texts
    
    metadata = data.get("metadata", {})
    tradition = metadata.get("tradition", "Unknown")
    language = metadata.get("language", "Unknown")
    
    # Extract texts based on structure
    if "texts" in data:
        for text in data["texts"]:
            text_data = {
                "tradition": tradition,
                "language": language,
                "text_id": text.get("text_id", ""),
                "text_name": text.get("text_name_en", ""),
                "content": str(text.get("verses", text.get("passages", []))),
                "file": str(filepath)
            }
            texts.append(text_data)
    
    return texts

def convert_corpus_to_csv(corpus_path: Path, output_path: Path):
    """Convert all JSON files to CSV."""
    all_texts = []
    
    # Find all JSON files (excluding metadata)
    json_files = list(corpus_path.rglob("*.json"))
    
    for json_file in json_files:
        if "metadata" in str(json_file):
            continue
        
        texts = extract_texts_from_json(json_file)
        all_texts.extend(texts)
    
    # Write to CSV
    if all_texts:
        output_file = output_path / "pre_quranic_texts.csv"
        
        with open(output_file, 'w', encoding='utf-8', newline='') as f:
            fieldnames = ["tradition", "language", "text_id", "text_name", "content", "file"]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            
            writer.writeheader()
            for text in all_texts:
                writer.writerow(text)
        
        print(f"✓ Created: {output_file}")
        print(f"  Total texts: {len(all_texts)}")
    else:
        print("No texts found to convert")

def main():
    import sys
    
    if len(sys.argv) < 3:
        print("Usage: python convert_to_csv.py <input_path> <output_path>")
        sys.exit(1)
    
    corpus_path = Path(sys.argv[1])
    output_path = Path(sys.argv[2])
    
    if not corpus_path.exists():
        print(f"Error: Input path does not exist: {corpus_path}")
        sys.exit(1)
    
    output_path.mkdir(parents=True, exist_ok=True)
    
    convert_corpus_to_csv(corpus_path, output_path)

if __name__ == "__main__":
    main()
