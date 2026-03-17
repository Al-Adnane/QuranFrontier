#!/usr/bin/env python3
"""
BLOCKER 1: Discover real peer-reviewed sources for 20 priority scientific concepts.

Replaces synthetic sequential DOIs (10.1038/s00XXX) with real papers discovered
via Semantic Scholar and CrossRef APIs.

Usage:
    python quran/corpus_extraction/scripts/discover_real_sources.py

Output:
    quran/corpus_extraction/sources/concept_sources_real.json

Rate limits respected:
    - Semantic Scholar: ~1 req/sec (no auth key)
    - CrossRef: ~1 req/sec
    - Total estimated runtime: 5-8 minutes for 20 concepts
"""

import json
import re
import sys
import time
import signal
from datetime import datetime
from pathlib import Path

import requests

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

SCRIPT_DIR = Path(__file__).parent
BASE_DIR = SCRIPT_DIR.parent
OUTPUT_FILE = BASE_DIR / "sources" / "concept_sources_real.json"
CONCEPTS_FILE = BASE_DIR / "ontology" / "scientific_concepts.json"

# ---------------------------------------------------------------------------
# Priority concept queries (concept_id -> (concept_name, search_query, quran_ref))
# ---------------------------------------------------------------------------

PRIORITY_QUERIES = [
    ("embryology",            "Embryonic Development",        "human embryonic development stages morphology",                "Q23:12-14 embryonic stages"),
    ("expanding_universe",    "Expansion of Universe",        "cosmic expansion Hubble constant dark energy accelerating",    "Q51:47 expanding universe"),
    ("mountain_isostasy",     "Mountain Roots / Isostasy",    "mountain roots isostasy crustal structure lithosphere",        "Q78:7 mountains as pegs"),
    ("water_cycle",           "Hydrological Cycle",           "hydrological cycle precipitation evaporation transpiration",  "Q39:21 water cycle"),
    ("oceanography_halocline","Ocean Halocline / Barrier",    "halocline salinity barrier ocean mixing thermohaline",        "Q55:19-20 two seas barrier"),
    ("honey_antimicrobial",   "Honey Antimicrobial",          "honey antimicrobial antibacterial hydrogen peroxide wound",   "Q16:69 honey healing"),
    ("iron_meteorite",        "Iron Meteorite Origin",        "iron meteorite extraterrestrial origin siderophile element",  "Q57:25 iron sent down"),
    ("bee_communication",     "Bee Dance Communication",      "bee dance communication waggle foraging Karl von Frisch",     "Q16:68-69 bee revelation"),
    ("atmospheric_layers",    "Atmospheric Pressure Layers",  "atmospheric pressure altitude troposphere stratosphere mesosphere","Q6:125 chest tightening altitude"),
    ("solar_motion",          "Solar Motion in Galaxy",       "solar apex galactic motion milky way velocity",               "Q36:38 sun swimming orbit"),
    ("genetics_reproduction", "Genetic Recombination",        "genetic recombination sexual reproduction meiosis crossover",  "Q53:45-46 male female pairs"),
    ("plant_photosynthesis",  "Plant Photosynthesis",         "plant photosynthesis chlorophyll light reaction carbon fixation","Q6:95 grain splitting plant"),
    ("groundwater",           "Groundwater Aquifer",          "groundwater aquifer recharge springs karst hydrogeology",     "Q15:22 water stored earth"),
    ("deep_ocean_darkness",   "Deep Ocean Aphotic Zone",      "deep ocean aphotic zone bioluminescence darkness mesopelagic","Q24:40 deep sea darkness"),
    ("skin_pain_receptors",   "Skin Pain Nociceptors",        "skin nociceptors pain receptors nerve endings C-fiber burn",  "Q4:56 skin regrown pain"),
    ("sleep_neuroscience",    "Sleep Neuroscience",           "sleep REM NREM brain waves slow wave sleep memory consolidation","Q39:42 soul taken sleep"),
    ("frontal_lobe",          "Prefrontal Cortex Function",   "prefrontal cortex decision making inhibition executive function","Q96:15-16 forelock lying"),
    ("tectonic_plates",       "Tectonic Plate Movement",      "tectonic plate movement earthquake subduction geology",       "Q21:31 mountains stability"),
    ("nitrogen_cycle",        "Nitrogen Cycle Fixation",      "nitrogen fixation soil bacteria rhizobium agriculture cycle", "Q50:9 blessed water plant"),
    ("mathematics_fractions", "Islamic Inheritance Math",     "fraction algebra inheritance division mathematical partition", "Q4:11-12 inheritance fractions"),
]

# ---------------------------------------------------------------------------
# Simple rate limiter
# ---------------------------------------------------------------------------

class RateLimiter:
    def __init__(self, min_interval: float = 1.1):
        self.min_interval = min_interval
        self._last = 0.0

    def wait(self):
        elapsed = time.time() - self._last
        if elapsed < self.min_interval:
            time.sleep(self.min_interval - elapsed)
        self._last = time.time()


SS_LIMITER = RateLimiter(2.5)
CF_LIMITER = RateLimiter(1.5)

# ---------------------------------------------------------------------------
# Semantic Scholar search
# ---------------------------------------------------------------------------

SS_SESSION = requests.Session()
SS_SESSION.headers.update({"User-Agent": "QuranFrontier/1.0 (research; mailto:research@quranfrontier.org)"})


def search_semantic_scholar(query: str, limit: int = 5, retries: int = 4) -> list:
    """Search Semantic Scholar Graph API. Returns list of paper dicts."""
    url = "https://api.semanticscholar.org/graph/v1/paper/search"
    params = {
        "query": query,
        "limit": limit,
        "fields": "title,authors,year,externalIds,citationCount,journal,abstract",
    }
    backoff = 8.0
    for attempt in range(retries):
        SS_LIMITER.wait()
        try:
            resp = SS_SESSION.get(url, params=params, timeout=15)
            if resp.status_code == 200:
                return resp.json().get("data", [])
            elif resp.status_code == 429:
                retry_after = int(resp.headers.get("Retry-After", backoff))
                wait_time = max(backoff, retry_after)
                print(f"  [SS] Rate limited (attempt {attempt+1}/{retries}) — sleeping {wait_time:.0f}s")
                time.sleep(wait_time)
                backoff *= 2
            else:
                print(f"  [SS] HTTP {resp.status_code} for query: {query[:50]}")
                return []
        except Exception as e:
            print(f"  [SS] Error: {e}")
            if attempt < retries - 1:
                time.sleep(backoff)
                backoff *= 2
            else:
                return []
    return []


def parse_ss_paper(item: dict) -> dict | None:
    """Parse a Semantic Scholar paper item into our schema."""
    doi = None
    ext = item.get("externalIds") or {}
    doi = ext.get("DOI") or ext.get("doi")

    title = item.get("title", "").strip()
    if not title:
        return None

    year = item.get("year")
    citation_count = item.get("citationCount") or 0

    # Authors
    authors = [a.get("name", "") for a in (item.get("authors") or []) if a.get("name")]

    # Journal
    journal_obj = item.get("journal") or {}
    journal = journal_obj.get("name", "") if isinstance(journal_obj, dict) else str(journal_obj)
    if not journal:
        journal = item.get("venue", "")

    return {
        "doi": doi,
        "title": title,
        "authors": authors[:5],
        "journal": journal or "Unknown",
        "year": year,
        "citation_count": citation_count,
        "source_api": "semantic_scholar",
    }


# ---------------------------------------------------------------------------
# CrossRef validation
# ---------------------------------------------------------------------------

CF_SESSION = requests.Session()
CF_SESSION.headers.update({"User-Agent": "QuranFrontier/1.0 (research; mailto:research@quranfrontier.org)"})


def validate_doi_crossref(doi: str) -> dict:
    """Validate a DOI via CrossRef and return enriched metadata."""
    url = f"https://api.crossref.org/works/{doi}"
    CF_LIMITER.wait()
    try:
        resp = CF_SESSION.get(url, timeout=10)
        if resp.status_code == 200:
            return resp.json().get("message", {})
        elif resp.status_code == 404:
            return {}
        elif resp.status_code == 429:
            print("  [CF] Rate limited — sleeping 5s")
            time.sleep(5)
            return {}
    except Exception as e:
        print(f"  [CF] Error for {doi}: {e}")
    return {}


def extract_crossref_metadata(msg: dict) -> dict:
    """Extract key fields from a CrossRef message object."""
    title_list = msg.get("title", [])
    title = title_list[0] if title_list else ""

    # Year
    year = None
    for date_key in ("published-online", "published-print", "issued"):
        dp = msg.get(date_key, {}).get("date-parts", [[]])
        if dp and dp[0]:
            try:
                year = int(dp[0][0])
                break
            except (ValueError, TypeError):
                pass

    # Journal
    ct = msg.get("container-title", [])
    journal = ct[0] if ct else ""

    # Authors
    authors = []
    for a in msg.get("author", []):
        name = f"{a.get('given', '')} {a.get('family', '')}".strip()
        if name:
            authors.append(name)

    return {"title": title, "year": year, "journal": journal, "authors": authors[:5]}


# ---------------------------------------------------------------------------
# Quality scoring (mirrors SourceQualityScorer logic, standalone)
# ---------------------------------------------------------------------------

TOP_TIER = {"nature", "science", "cell", "pnas", "lancet", "jama", "bmj",
            "new england journal of medicine", "nejm"}
HIGH_TIER = {"nature physics", "nature chemistry", "nature astronomy",
             "nature medicine", "elife", "plos biology", "plos medicine",
             "science translational medicine"}
PREPRINTS = {"arxiv", "biorxiv", "medrxiv", "chemrxiv"}


def score_quality(journal: str, year: int | None, citation_count: int, peer_reviewed: bool = True) -> float:
    """Compute a quality score [0,1] from journal, year, citations, peer_review."""
    score = 0.0
    j = (journal or "").lower().strip()

    # Journal impact (0-0.3)
    if any(p in j for p in PREPRINTS):
        score += 0.0
    elif any(t in j for t in TOP_TIER):
        score += 0.3
    elif any(h in j for h in HIGH_TIER):
        score += 0.2
    else:
        score += 0.08

    # Recency (0-0.2)
    if year:
        age = 2026 - year
        if age <= 2:
            score += 0.2
        elif age <= 5:
            score += 0.15
        elif age <= 10:
            score += 0.12
        else:
            score += 0.1
    else:
        score += 0.1

    # Citations (0-0.3)
    c = citation_count or 0
    if c >= 100:
        score += 0.3
    elif c >= 50:
        score += 0.25
    elif c >= 10:
        score += 0.2
    elif c >= 1:
        score += 0.1

    # Peer review (0-0.2)
    if peer_reviewed and not any(p in j for p in PREPRINTS):
        score += 0.2

    return round(min(1.0, max(0.0, score)), 3)


# ---------------------------------------------------------------------------
# DOI format check
# ---------------------------------------------------------------------------

VALID_DOI_RE = re.compile(r"^10\.\d{4,}/[^\s]+$")
SYNTHETIC_DOI_RE = re.compile(r"^10\.1038/s0\d{4}$")


def is_real_doi(doi: str | None) -> bool:
    if not doi:
        return False
    if SYNTHETIC_DOI_RE.match(doi):
        return False
    return bool(VALID_DOI_RE.match(doi))


# ---------------------------------------------------------------------------
# Main discovery function
# ---------------------------------------------------------------------------

def discover_for_concept(concept_id: str, concept_name: str, query: str, quran_ref: str) -> dict:
    """Discover real sources for one concept. Returns a concept entry dict."""
    print(f"\n[{concept_id}] Searching: {query[:60]}")
    sources = []
    seen_dois = set()

    # Step 1: Search Semantic Scholar
    raw_papers = search_semantic_scholar(query, limit=5)
    print(f"  SS returned {len(raw_papers)} papers")

    for item in raw_papers:
        parsed = parse_ss_paper(item)
        if not parsed:
            continue

        doi = parsed.get("doi")

        # Skip if no real DOI
        if not is_real_doi(doi):
            # Still keep paper without DOI if it has a good title
            if not doi and parsed.get("title"):
                quality = score_quality(
                    parsed["journal"], parsed["year"], parsed["citation_count"], peer_reviewed=True
                )
                sources.append({
                    "doi": None,
                    "title": parsed["title"],
                    "authors": parsed["authors"],
                    "journal": parsed["journal"],
                    "year": parsed["year"],
                    "citation_count": parsed["citation_count"],
                    "quality_score": quality,
                    "relevance_to_quran": quran_ref,
                    "source_api": "semantic_scholar",
                    "validated": False,
                })
            continue

        if doi in seen_dois:
            continue
        seen_dois.add(doi)

        # Step 2: Validate via CrossRef
        cf_msg = validate_doi_crossref(doi)
        validated = bool(cf_msg)

        if cf_msg:
            cf_meta = extract_crossref_metadata(cf_msg)
            # Prefer CrossRef metadata (more authoritative)
            final_title = cf_meta["title"] or parsed["title"]
            final_journal = cf_meta["journal"] or parsed["journal"]
            final_year = cf_meta["year"] or parsed["year"]
            final_authors = cf_meta["authors"] or parsed["authors"]
        else:
            final_title = parsed["title"]
            final_journal = parsed["journal"]
            final_year = parsed["year"]
            final_authors = parsed["authors"]

        quality = score_quality(final_journal, final_year, parsed["citation_count"], peer_reviewed=True)

        sources.append({
            "doi": doi,
            "title": final_title,
            "authors": final_authors,
            "journal": final_journal,
            "year": final_year,
            "citation_count": parsed["citation_count"],
            "quality_score": quality,
            "relevance_to_quran": quran_ref,
            "source_api": "semantic_scholar",
            "validated": validated,
        })

        print(f"    + {doi[:50]:50s}  citations={parsed['citation_count']:5d}  q={quality}")

    return {
        "concept_id": concept_id,
        "concept_name": concept_name,
        "sources": sources,
    }


# ---------------------------------------------------------------------------
# Graceful interrupt: save partial results
# ---------------------------------------------------------------------------

_partial_results = []
_interrupted = False


def _handle_sigint(signum, frame):
    global _interrupted
    print("\n\n[!] Interrupted by user — saving partial results...")
    _interrupted = True


signal.signal(signal.SIGINT, _handle_sigint)

# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def main():
    global _partial_results, _interrupted

    print("=" * 70)
    print("BLOCKER 1: Real Source Discovery")
    print(f"Output: {OUTPUT_FILE}")
    print(f"Concepts to process: {len(PRIORITY_QUERIES)}")
    print("=" * 70)

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    start_time = time.time()

    # Load any existing partial results to resume
    already_done = {}
    if OUTPUT_FILE.exists():
        try:
            with open(OUTPUT_FILE) as f:
                prev = json.load(f)
            for entry in prev.get("concepts", []):
                if entry.get("sources"):  # only keep concepts that have sources
                    already_done[entry["concept_id"]] = entry
            if already_done:
                print(f"Resuming: {len(already_done)} concepts already have sources, will skip them")
        except Exception:
            pass

    results = list(already_done.values())

    for i, (concept_id, concept_name, query, quran_ref) in enumerate(PRIORITY_QUERIES):
        if _interrupted:
            break

        # Skip if already successfully discovered
        if concept_id in already_done:
            print(f"\n[{i+1}/{len(PRIORITY_QUERIES)}] Skipping {concept_id} (already has {len(already_done[concept_id]['sources'])} sources)")
            continue

        elapsed = time.time() - start_time
        print(f"\n[{i+1}/{len(PRIORITY_QUERIES)}] elapsed={elapsed:.0f}s")

        entry = discover_for_concept(concept_id, concept_name, query, quran_ref)
        results.append(entry)
        _partial_results = results  # keep reference for signal handler

        source_count = len(entry["sources"])
        validated_count = sum(1 for s in entry["sources"] if s.get("validated"))
        print(f"  -> {source_count} sources ({validated_count} CrossRef-validated)")

        # Save partial results every 5 concepts
        if (i + 1) % 5 == 0 or _interrupted:
            _save_results(results)
            print(f"  [saved partial results: {len(results)} concepts]")

    # Final save
    _save_results(results)

    total_sources = sum(len(e["sources"]) for e in results)
    validated_total = sum(
        sum(1 for s in e["sources"] if s.get("validated"))
        for e in results
    )
    concepts_with_sources = sum(1 for e in results if len(e["sources"]) > 0)

    elapsed = time.time() - start_time
    print("\n" + "=" * 70)
    print("DISCOVERY COMPLETE")
    print(f"  Concepts processed:      {len(results)}")
    print(f"  Concepts with sources:   {concepts_with_sources}")
    print(f"  Total sources:           {total_sources}")
    print(f"  CrossRef-validated DOIs: {validated_total}")
    print(f"  Elapsed time:            {elapsed:.1f}s")
    print(f"  Output file:             {OUTPUT_FILE}")
    print("=" * 70)

    if _interrupted:
        print("\n[!] Partial run completed (interrupted). Re-run to complete remaining concepts.")
        sys.exit(1)


def _save_results(results: list):
    """Write results to the output JSON file."""
    output = {
        "metadata": {
            "generated": datetime.utcnow().isoformat() + "Z",
            "discovery_date": datetime.utcnow().isoformat() + "Z",
            "version": "1.0",
            "description": "Real peer-reviewed sources for priority Quranic scientific concepts",
            "apis_used": ["semantic_scholar", "crossref"],
            "total_concepts": len(results),
            "total_sources": sum(len(e["sources"]) for e in results),
            "validated_dois": sum(
                sum(1 for s in e["sources"] if s.get("validated"))
                for e in results
            ),
            "blocker": "BLOCKER_1",
        },
        "concepts": results,
    }
    with open(OUTPUT_FILE, "w") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    main()
