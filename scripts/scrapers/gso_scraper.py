#!/usr/bin/env python3
"""GSO scraper — administrative unit statistical codes.

Scrapes gso.gov.vn for GSO statistical codes + population + area.
Output: .scratch/gso/raw_codes.json

Usage:
    python scripts/scrapers/gso_scraper.py --limit 500 --concurrency 5
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
OUTPUT_DIR = Path(".scratch/gso")


def extract_unit_code(page, url: str) -> dict:
    """Extract administrative unit code from gso.gov.vn page."""
    record = {
        "source_url": url,
        "code": None,  # GSO statistical code
        "name": None,
        "name_en": None,
        "level": None,  # province, district, ward
        "parent_code": None,
        "population": None,
        "area_km2": None,
        "year": None,
        "retrieved_at": datetime.now(timezone.utc).isoformat(),
    }

    body_text = page.text or ""

    # GSO code (Mã thống kê)
    code_match = re.search(r"[Mm]ã\s+(?:thống kê|đơn vị)[:\s]+([A-Z0-9]+)", body_text)
    if code_match:
        record["code"] = code_match.group(1)

    # Unit name
    h1_el = page.css("h1")
    if h1_el:
        record["name"] = h1_el[0].text.strip()

    # English name
    name_en_el = page.css(".english-name, .name-en")
    if name_en_el:
        record["name_en"] = name_en_el[0].text.strip()

    # Level
    if "tỉnh" in body_text.lower() or "thành phố" in body_text.lower():
        record["level"] = "province"
    elif "quận" in body_text.lower() or "huyện" in body_text.lower():
        record["level"] = "district"
    elif "phường" in body_text.lower() or "xã" in body_text.lower():
        record["level"] = "ward"

    # Population
    pop_match = re.search(r"dân số[:\s]+([\d,]+)\s*(?:người|nhân)", body_text, re.IGNORECASE)
    if pop_match:
        record["population"] = int(pop_match.group(1).replace(",", ""))

    # Area
    area_match = re.search(r"diện tích[:\s]+([\d,.]+)\s*km²", body_text, re.IGNORECASE)
    if area_match:
        record["area_km2"] = float(area_match.group(1).replace(",", ""))

    # Year
    year_match = re.search(r"năm\s+(20\d{2})", body_text)
    if year_match:
        record["year"] = int(year_match.group(1))

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
            record = extract_unit_code(page, url)
            return record, None
        except Exception as e:
            return None, {"url": url, "error": str(e)}


async def main_async(args):
    """Async main loop."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    output_path = OUTPUT_DIR / "raw_codes.json"

    print("GSO scraper — gso.gov.vn")
    print("TODO: Implement URL discovery (statistical code pages)")
    print("Need: Crawl from https://gso.gov.vn/ or download Excel/CSV")
    return


def main():
    parser = argparse.ArgumentParser(description="Scrape gso.gov.vn")
    parser.add_argument("--limit", type=int, default=500)
    parser.add_argument("--concurrency", type=int, default=DEFAULT_CONCURRENCY)
    args = parser.parse_args()

    asyncio.run(main_async(args))


if __name__ == "__main__":
    main()
