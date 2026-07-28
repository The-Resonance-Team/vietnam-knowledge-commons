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

from scrapling.fetchers import StealthyFetcher

RATE_LIMIT_DELAY = 2.0  # Slower for stealth
DEFAULT_CONCURRENCY = 2  # Lower concurrency
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


async def fetch_page(url: str, semaphore: asyncio.Semaphore):
    """Fetch a single page with StealthyFetcher (sync, run in thread)."""
    async with semaphore:
        try:
            await asyncio.sleep(RATE_LIMIT_DELAY)
            page = await asyncio.to_thread(StealthyFetcher.fetch, url, headless=True)
            record = extract_unit_metadata(page, url)
            return record, None
        except Exception as e:
            return None, {"url": url, "error": str(e)}


async def discover_urls(limit: int = 2000) -> list[str]:
    """Discover administrative unit URLs from moha.gov.vn."""
    urls = []

    # Crawl from homepage with network_idle + wait (JS-rendered SPA)
    try:
        page = await asyncio.to_thread(
            StealthyFetcher.fetch,
            "https://moha.gov.vn/",
            headless=True,
            network_idle=True,
            wait=5
        )
        if page.status == 200:
            # Find all /tin-tuc/ links (news articles about admin units)
            links = page.css('a[href]')
            for link in links:
                href = link.attrib.get("href", "")
                text = link.text.strip() if link.text else ""

                # Filter for tin-tuc or admin unit keywords
                if href and ("/tin-tuc/" in href or "/nghi-quyet" in href or
                           any(kw in text.lower() for kw in ["đơn vị hành chính", "sáp nhập", "tỉnh", "huyện", "xã", "ward", "district", "province"])):
                    if href.startswith("http"):
                        urls.append(href)
                    elif href.startswith("/"):
                        urls.append(f"https://moha.gov.vn{href}")

                    if len(urls) >= limit:
                        break
    except Exception as e:
        print(f"Error crawling homepage: {e}")

    # Also try /tin-tuc/ section with network_idle
    if len(urls) < limit:
        try:
            page = await asyncio.to_thread(
                StealthyFetcher.fetch,
                "https://moha.gov.vn/tin-tuc/",
                headless=True,
                network_idle=True,
                wait=5
            )
            if page.status == 200:
                links = page.css('a[href]')
                for link in links:
                    href = link.attrib.get("href", "")
                    if href and "/tin-tuc/" in href:
                        if href.startswith("http"):
                            urls.append(href)
                        elif href.startswith("/"):
                            urls.append(f"https://moha.gov.vn{href}")

                        if len(urls) >= limit:
                            break
        except Exception:
            pass

    return list(set(urls))[:limit]


async def main_async(args):
    """Async main loop."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    output_path = OUTPUT_DIR / "raw_units.json"

    # Load existing
    existing = []
    fetched_urls = set()
    if output_path.exists():
        existing = json.loads(output_path.read_text(encoding="utf-8"))
        fetched_urls = {r["source_url"] for r in existing}

    # Discover URLs
    print("Discovering URLs from moha.gov.vn...")
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
    parser = argparse.ArgumentParser(description="Scrape moha.gov.vn")
    parser.add_argument("--limit", type=int, default=500)
    parser.add_argument("--concurrency", type=int, default=DEFAULT_CONCURRENCY)
    args = parser.parse_args()

    asyncio.run(main_async(args))


if __name__ == "__main__":
    main()
