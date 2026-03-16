"""
Retraction Tracker module for detecting retracted papers and flagging compromised sources.

This module provides:
- Checking if papers have been retracted
- Querying Retraction Watch API for retraction details
- Maintaining a cache of known retractions
- Batch checking of sources for retractions
"""

import json
import requests
from typing import Dict, List, Optional
from pathlib import Path
from datetime import datetime


class RetractionTracker:
    """Tracks retracted papers and flags compromised sources."""

    def __init__(self, cache_file: Optional[str] = None):
        """
        Initialize RetractionTracker with optional cache file.

        Args:
            cache_file: Optional path to retracted_papers.json cache
        """
        self.retraction_watch_url = "https://api.retractionwatch.com/papers"
        self.timeout = 10
        self.session = requests.Session()
        self.retraction_cache: Dict[str, Dict] = {}

        if cache_file and Path(cache_file).exists():
            self.load_retraction_cache(cache_file)

    def is_paper_retracted(self, doi: str) -> bool:
        """
        Check if a paper has been retracted.

        Args:
            doi: Digital Object Identifier

        Returns:
            bool: True if paper is retracted, False otherwise
        """
        # Check cache first
        if doi in self.retraction_cache:
            return True

        # Try to query Retraction Watch API
        try:
            url = f"{self.retraction_watch_url}?doi={doi}"
            response = self.session.get(url, timeout=self.timeout)

            if response.status_code == 200:
                data = response.json()
                if isinstance(data, dict) and data.get("data"):
                    # Paper found in Retraction Watch (it's retracted)
                    return True
            return False

        except Exception as e:
            # On error, fall back to cache only
            return doi in self.retraction_cache

    def get_retraction_details(self, doi: str) -> Dict:
        """
        Get detailed retraction information for a paper.

        Args:
            doi: Digital Object Identifier

        Returns:
            dict: {
                is_retracted: bool,
                reason: str,
                date_retracted: str (ISO format),
                replacement_doi: str or None
            }
        """
        # Check cache first
        if doi in self.retraction_cache:
            cached = self.retraction_cache[doi]
            return {
                "is_retracted": True,
                "reason": cached.get("reason"),
                "date_retracted": cached.get("date_retracted"),
                "replacement_doi": cached.get("replacement_doi"),
                "title": cached.get("title")
            }

        # Try to query API
        try:
            url = f"{self.retraction_watch_url}?doi={doi}"
            response = self.session.get(url, timeout=self.timeout)

            if response.status_code == 200:
                data = response.json()
                if isinstance(data, dict) and data.get("data"):
                    record = data["data"][0] if isinstance(data["data"], list) else data["data"]
                    return {
                        "is_retracted": True,
                        "reason": record.get("retraction_notice", record.get("reason")),
                        "date_retracted": record.get("date_retracted"),
                        "replacement_doi": record.get("replacement_doi"),
                        "title": record.get("title")
                    }

            return {"is_retracted": False, "reason": None, "date_retracted": None, "replacement_doi": None}

        except Exception as e:
            return {"is_retracted": False, "reason": None, "date_retracted": None, "replacement_doi": None}

    def check_all_sources_for_retractions(self, sources: List[Dict]) -> Dict:
        """
        Check all sources for retractions in batch.

        Args:
            sources: List of source dicts with at least 'doi' field

        Returns:
            dict: {
                total_checked: int,
                retracted_count: int,
                retracted_papers: [dict],
                retraction_percentage: float
            }
        """
        retracted_papers = []
        retracted_count = 0

        for source in sources:
            doi = source.get("doi")
            if not doi:
                continue

            if self.is_paper_retracted(doi):
                retracted_count += 1
                details = self.get_retraction_details(doi)
                retracted_papers.append({
                    "doi": doi,
                    "title": source.get("title"),
                    "reason": details.get("reason"),
                    "date_retracted": details.get("date_retracted"),
                    "replacement_doi": details.get("replacement_doi")
                })

        return {
            "total_checked": len(sources),
            "retracted_count": retracted_count,
            "retracted_papers": retracted_papers,
            "retraction_percentage": (retracted_count / len(sources) * 100) if sources else 0
        }

    def load_retraction_cache(self, cache_file: str) -> None:
        """
        Load retraction cache from JSON file.

        Args:
            cache_file: Path to retracted_papers.json file
        """
        try:
            cache_path = Path(cache_file)
            if cache_path.exists():
                with open(cache_path, 'r') as f:
                    self.retraction_cache = json.load(f)
        except Exception as e:
            self.retraction_cache = {}

    def save_retraction_cache(self, cache_file: str) -> None:
        """
        Save retraction cache to JSON file.

        Args:
            cache_file: Path to save retracted_papers.json
        """
        try:
            cache_path = Path(cache_file)
            cache_path.parent.mkdir(parents=True, exist_ok=True)
            with open(cache_path, 'w') as f:
                json.dump(self.retraction_cache, f, indent=2)
        except Exception as e:
            pass

    def add_to_cache(self, doi: str, title: str, reason: str, date_retracted: str, replacement_doi: Optional[str] = None) -> None:
        """
        Add a retraction record to the cache.

        Args:
            doi: Digital Object Identifier
            title: Paper title
            reason: Reason for retraction
            date_retracted: Date of retraction (ISO format)
            replacement_doi: DOI of replacement paper if available
        """
        self.retraction_cache[doi] = {
            "title": title,
            "reason": reason,
            "date_retracted": date_retracted,
            "replacement_doi": replacement_doi
        }

    def flag_papers_with_concerns(self, sources: List[Dict]) -> List[Dict]:
        """
        Flag papers that may have security/health concerns.

        Args:
            sources: List of source dicts

        Returns:
            list: Papers flagged for review with concern categories
        """
        concern_keywords = [
            "fraudulent", "fabricated", "falsified",
            "plagiarism", "self-plagiarism",
            "data manipulation", "image manipulation",
            "ethical violation", "undisclosed conflict",
            "safety concern", "health risk"
        ]

        flagged = []
        for source in sources:
            doi = source.get("doi")
            if not doi:
                continue

            details = self.get_retraction_details(doi)
            reason = details.get("reason", "").lower()

            for keyword in concern_keywords:
                if keyword in reason:
                    flagged.append({
                        "doi": doi,
                        "title": source.get("title"),
                        "concern": keyword,
                        "reason": details.get("reason"),
                        "severity": "high" if "fraud" in reason or "health" in reason else "medium"
                    })
                    break

        return flagged
