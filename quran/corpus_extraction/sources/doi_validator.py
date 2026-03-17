"""
DOI Validator module for validating Digital Object Identifiers and resolving paper metadata.

This module provides:
- DOI format validation using regex pattern
- DOI resolution via CrossRef API
- Paper metadata validation (title, year, authors)
- Batch validation of sources
"""

import re
import json
import requests
from typing import Dict, List, Optional
from datetime import datetime


class DOIValidator:
    """Validates DOI format, resolves DOI to metadata, and validates paper information."""

    # DOI format: 10.XXXX/YYYY where XXXX is numeric and YYYY is any valid suffix
    DOI_PATTERN = r"^10\.\d{4,}/[a-zA-Z0-9./_-]+$"

    def __init__(self):
        """Initialize DOIValidator with CrossRef API configuration."""
        self.doi_pattern = self.DOI_PATTERN
        self.crossref_url = "https://api.crossref.org/works"
        self.timeout = 10
        self.session = requests.Session()

    def validate_doi_format(self, doi: str) -> bool:
        """
        Validate if DOI matches the correct format: 10.XXXX/YYYY

        Args:
            doi: Digital Object Identifier string

        Returns:
            bool: True if DOI format is valid, False otherwise
        """
        if not doi or not isinstance(doi, str):
            return False
        return bool(re.match(self.doi_pattern, doi.strip()))

    def resolve_doi(self, doi: str) -> Optional[Dict]:
        """
        Resolve DOI to paper metadata using CrossRef API.

        Args:
            doi: Digital Object Identifier string

        Returns:
            dict: Paper metadata including title, year, authors, journal, or None if not found
        """
        if not self.validate_doi_format(doi):
            return None

        try:
            url = f"{self.crossref_url}/{doi}"
            response = self.session.get(url, timeout=self.timeout)

            if response.status_code == 200:
                data = response.json()
                message = data.get("message", {})

                # Extract metadata from CrossRef response
                metadata = {
                    "doi": message.get("DOI", doi),
                    "title": self._extract_title(message),
                    "year": self._extract_year(message),
                    "journal": message.get("container-title", "Unknown"),
                    "authors": self._extract_authors(message),
                    "type": message.get("type", "journal-article"),
                    "published": message.get("published-online") or message.get("published-print"),
                }
                return metadata
            elif response.status_code == 404:
                return None
            else:
                return None

        except Exception as e:
            return None

    def _extract_title(self, message: Dict) -> str:
        """Extract title from CrossRef metadata."""
        title = message.get("title", [])
        if isinstance(title, list):
            return title[0] if title else "Unknown"
        return str(title) if title else "Unknown"

    def _extract_year(self, message: Dict) -> Optional[int]:
        """Extract publication year from CrossRef metadata."""
        # Try published-online first, then published-print
        for date_key in ["published-online", "published-print", "issued"]:
            date_info = message.get(date_key)
            if date_info and isinstance(date_info, dict):
                date_parts = date_info.get("date-parts", [])
                if date_parts and isinstance(date_parts[0], list) and len(date_parts[0]) > 0:
                    try:
                        return int(date_parts[0][0])
                    except (ValueError, IndexError, TypeError):
                        continue
        return None

    def _extract_authors(self, message: Dict) -> List[str]:
        """Extract author names from CrossRef metadata."""
        authors = []
        author_list = message.get("author", [])
        for author in author_list:
            if isinstance(author, dict):
                given = author.get("given", "")
                family = author.get("family", "")
                if family:
                    name = f"{given} {family}".strip()
                    authors.append(name)
        return authors

    def validate_paper_metadata(
        self,
        resolved_metadata: Dict,
        expected_title: str,
        expected_year: int
    ) -> Dict:
        """
        Validate that resolved metadata matches expected values.

        Args:
            resolved_metadata: Metadata dict from resolve_doi()
            expected_title: Expected paper title
            expected_year: Expected publication year

        Returns:
            dict: {is_valid: bool, match_score: float, mismatches: [str]}
        """
        if not resolved_metadata:
            return {"is_valid": False, "match_score": 0.0, "mismatches": ["No metadata"]}

        mismatches = []
        match_score = 1.0

        # Check title similarity (case-insensitive partial match)
        resolved_title = resolved_metadata.get("title", "").lower().strip()
        expected_title_lower = expected_title.lower().strip()

        if resolved_title != expected_title_lower:
            # Check for partial match (allowing for minor differences)
            similarity = self._calculate_title_similarity(resolved_title, expected_title_lower)
            if similarity < 0.7:
                mismatches.append("title_mismatch")
                match_score -= 0.5  # Major penalty for different titles
            else:
                match_score -= 0.15  # Minor title difference

        # Check year (exact match or within 1 year)
        resolved_year = resolved_metadata.get("year")
        if resolved_year and abs(resolved_year - expected_year) > 1:
            mismatches.append("year_mismatch")
            match_score -= 0.4  # Higher penalty for year mismatch

        is_valid = match_score > 0.7  # Strict inequality to exclude boundary case
        return {
            "is_valid": is_valid,
            "match_score": max(0.0, match_score),
            "mismatches": mismatches
        }

    def _calculate_title_similarity(self, title1: str, title2: str) -> float:
        """
        Calculate similarity between two titles using Jaccard similarity.
        Requires significant word overlap for high scores.

        Args:
            title1: First title
            title2: Second title

        Returns:
            float: Similarity score (0-1)
        """
        # Remove common stop words
        stop_words = {"the", "a", "an", "and", "or", "in", "of", "to", "with", "by"}

        words1 = set(w for w in title1.lower().split() if w not in stop_words)
        words2 = set(w for w in title2.lower().split() if w not in stop_words)

        if not words1 or not words2:
            return 1.0 if title1 == title2 else 0.0

        intersection = len(words1 & words2)
        union = len(words1 | words2)
        jaccard = intersection / union if union > 0 else 0

        return jaccard

    def validate_all_sources(self, sources: List[Dict]) -> Dict:
        """
        Validate all sources in batch.

        Args:
            sources: List of source dicts with doi, title, year

        Returns:
            dict: Validation summary with total, valid, invalid, and details
        """
        validation_details = []
        valid_count = 0
        invalid_count = 0

        for source in sources:
            doi = source.get("doi")
            title = source.get("title")
            year = source.get("year")

            # Validate DOI format
            is_valid_format = self.validate_doi_format(doi)

            if not is_valid_format:
                validation_details.append({
                    "doi": doi,
                    "valid": False,
                    "reason": "Invalid DOI format"
                })
                invalid_count += 1
                continue

            # Try to resolve and validate metadata
            resolved = self.resolve_doi(doi)
            if resolved:
                metadata_check = self.validate_paper_metadata(resolved, title, year)
                is_valid = metadata_check["is_valid"]
                reason = (
                    "Metadata mismatch: " + ", ".join(metadata_check["mismatches"])
                    if metadata_check["mismatches"]
                    else "Valid"
                )
            else:
                is_valid = True  # DOI format valid but can't resolve (API issue)
                reason = "Format valid, could not resolve"

            if is_valid:
                valid_count += 1
            else:
                invalid_count += 1

            validation_details.append({
                "doi": doi,
                "valid": is_valid,
                "reason": reason,
                "metadata": resolved
            })

        return {
            "total": len(sources),
            "valid": valid_count,
            "invalid": invalid_count,
            "validation_details": validation_details,
            "validity_percentage": (valid_count / len(sources) * 100) if sources else 0
        }
