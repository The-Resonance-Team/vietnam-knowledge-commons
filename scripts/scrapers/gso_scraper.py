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

from scrapling.fetchers import StealthyFetcher

RATE_LIMIT_DELAY = 2.0
DEFAULT_CONCURRENCY = 2
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


async def fetch_page(url: str, semaphore: asyncio.Semaphore):
    """Fetch a single page with StealthyFetcher (sync, run in thread)."""
    async with semaphore:
        try:
            await asyncio.sleep(RATE_LIMIT_DELAY)
            page = await asyncio.to_thread(StealthyFetcher.fetch, url, headless=True)
            record = extract_unit_code(page, url)
            return record, None
        except Exception as e:
            return None, {"url": url, "error": str(e)}


async def discover_urls(limit: int = 2000) -> list[str]:
    """Discover administrative unit code URLs from nso.gov.vn (redirected from gso.gov.vn)."""
    urls = []

    # Use nso.gov.vn (redirect target from gso.gov.vn)
    base_url = "https://www.nso.gov.vn"

    try:
        page = await asyncio.to_thread(StealthyFetcher.fetch, f"{base_url}/", headless=True)
        if page.status == 200:
            links = page.css('a[href]')
            for link in links:
                href = link.attrib.get("href", "")
                if href and any(kw in href for kw in ["/tinh-", "/huyen-", "/xa-", "don-vi", "thong-ke"]):
                    if href.startswith("http"):
                        urls.append(href)
                    elif href.startswith("/"):
                        urls.append(f"{base_url}{href}")

                    if len(urls) >= limit:
                        break
    except Exception as e:
        print(f"Error crawling homepage: {e}")

    return list(set(urls))[:limit]


async def main_async(args):
    """Async main loop."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    output_path = OUTPUT_DIR / "raw_codes.json"

    # Load existing
    existing = []
    fetched_urls = set()
    if output_path.exists():
        existing = json.loads(output_path.read_text(encoding="utf-8"))
        fetched_urls = {r["source_url"] for r in existing}

    # Discover URLs
    print("Discovering URLs from nso.gov.vn...")
    all_urls = await discover_urls(limit=args.limit * 2)
    print(f"Found {len(all_urls)} URLs")

    # Filter to unfetched
    to_fetch = [u for u in all_urls if u not in fetched_urls][: args.limit]
    print(f"Already fetched: {len(fetched_urls)}, this run: {len(to_fetch)}")

    if not to_fetch:
        print("Nothing to fetch")
        return

    # Fetch concurrently
    semaphore = asyncio.Semaphore(args.concurrency)
    tasks = [fetch_page(url, semaphore) for url in to_fetch]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    new_records = []
    errors = []
    for i, result in enumerate(results):
        if isinstance(result, Exception):
            errors.append({"url": to_fetch[i], "error": str(result)})
        else:
            record, error = result
            if record:
                new_records.append(record)
            if error:
                errors.append(error)

    # Merge and save
    all_records = existing + new_records
    output_path.write_text(json.dumps(all_records, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"✓ Saved {len(all_records)} records ({len(new_records)} new, {len(errors)} errors)")


def main():
    parser = argparse.ArgumentParser(description="Scrape gso.gov.vn")
    parser.add_argument("--limit", type=int, default=500)
    parser.add_argument("--concurrency", type=int, default=DEFAULT_CONCURRENCY)
    args = parser.parse_args()

    asyncio.run(main_async(args))


if __name__ == "__main__":
    main()
