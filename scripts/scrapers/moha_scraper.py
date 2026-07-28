#!/usr/bin/env python3
"""MOH scraper — administrative units (merger decrees).

Scrapes moha.gov.vn for post-2025 administrative unit mergers.
Output: .scratch/moha/raw_units.json

Usage:
    python scripts/scrapers/moha_scraper.py --limit 500 --concurrency 5
"""

import argparse
import asyncio
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path

from scrapling.fetchers import AsyncFetcher

RATE_LIMIT_DELAY = 1.5
DEFAULT_CONCURRENCY = 5
OUTPUT_DIR = Path(".scratch/moha")


def extract_unit_metadata(page, url: str) -> dict:
    """Extract administrative unit metadata from moha.gov.vn page."""
    record = {
        "source_url": url,
        "unit_name": None,
        "unit_level": None,  # province, district, ward
        "parent_unit": None,
        "merger_decision": None,
        "effective_date": None,
        "predecessors": [],
        "successors": [],
        "population": None,
        "area_km2": None,
        "retrieved_at": datetime.now(timezone.utc).isoformat(),
    }

    body_text = page.text or ""

    # Unit name
    h1_el = page.css("h1")
    if h1_el:
        record["unit_name"] = h1_el[0].text.strip()

    # Detect level
    if "tỉnh" in body_text.lower() or "thành phố" in body_text.lower():
        record["unit_level"] = "province"
    elif "quận" in body_text.lower() or "huyện" in body_text.lower():
        record["unit_level"] = "district"
    elif "phường" in body_text.lower() or "xã" in body_text.lower():
        record["unit_level"] = "ward"

    # Merger decision (nghị quyết)
    merger_match = re.search(r"[Nn]ghị quyết\s+số\s+([^\n]+)", body_text)
    if merger_match:
        record["merger_decision"] = merger_match.group(1).strip()

    # Effective date
    date_match = re.search(r"ngày\s+(\d{1,2})\s+tháng\s+(\d{1,2})\s+năm\s+(\d{4})", body_text)
    if date_match:
        d, mo, y = int(date_match.group(1)), int(date_match.group(2)), int(date_match.group(3))
        try:
            dt = datetime(y, mo, d)
            record["effective_date"] = dt.strftime("%Y-%m-%d")
        except ValueError:
            pass

    # Population + area (if in table)
    pop_match = re.search(r"dân số[:\s]+([\d,]+)", body_text, re.IGNORECASE)
    if pop_match:
        record["population"] = int(pop_match.group(1).replace(",", ""))

    area_match = re.search(r"diện tích[:\s]+([\d,.]+)\s*km²", body_text, re.IGNORECASE)
    if area_match:
        record["area_km2"] = float(area_match.group(1).replace(",", ""))

    # Checksum
    checksum = hashlib.sha256(body_text.encode("utf-8")).hexdigest()
    record["content_checksum"] = f"sha256:{checksum}"

    return record


async def fetch_page(fetcher: AsyncFetcher, url: str, semaphore: asyncio.Semaphore):
    """Fetch a single page."""
    async with semaphore:
        try:
            await asyncio.sleep(RATE_LIMIT_DELAY)
            page = await fetcher.get(url, stealthy_headers=True)
            record = extract_unit_metadata(page, url)
            return record, None
        except Exception as e:
            return None, {"url": url, "error": str(e)}


async def main_async(args):
    """Async main loop."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    output_path = OUTPUT_DIR / "raw_units.json"

    print("MOH scraper — moha.gov.vn")
    print("TODO: Implement URL discovery (merger decree pages)")
    print("Need: Crawl from https://moha.gov.vn/van-ban/ or search API")
    return


def main():
    parser = argparse.ArgumentParser(description="Scrape moha.gov.vn")
    parser.add_argument("--limit", type=int, default=500)
    parser.add_argument("--concurrency", type=int, default=DEFAULT_CONCURRENCY)
    args = parser.parse_args()

    asyncio.run(main_async(args))


if __name__ == "__main__":
    main()
