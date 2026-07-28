#!/usr/bin/env python3
"""Thuvienphapluat.vn scraper — legal docs + files.

Async concurrent fetcher with resume support.
Output: .scratch/thuvienphapluat/raw_docs.json

Usage:
    python scripts/scrapers/thuvienphapluat_scraper.py --limit 500 --concurrency 5
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
OUTPUT_DIR = Path(".scratch/thuvienphapluat")


def extract_metadata(page, url: str) -> dict:
    """Extract document metadata from thuvienphapluat.vn page."""
    record = {
        "source_url": url,
        "title": None,
        "document_number": None,
        "document_type": None,
        "issue_date": None,
        "effective_date": None,
        "issuing_body": None,
        "pdf_url": None,
        "related_docs": [],
        "keywords": [],
        "retrieved_at": datetime.now(timezone.utc).isoformat(),
    }

    body_text = page.text or ""

    # Title
    h1_el = page.css("h1")
    if h1_el:
        record["title"] = h1_el[0].text.strip()

    # Document number
    doc_num_match = re.search(r"(\d{1,4}/\d{4}/[A-Z]{2,10}\d{0,2})", body_text, re.IGNORECASE)
    if doc_num_match:
        record["document_number"] = doc_num_match.group(1)

    # Dates
    date_patterns = [
        (r"ngày\s+(\d{1,2})\s+tháng\s+(\d{1,2})\s+năm\s+(\d{4})", "vi"),
        (r"(\d{1,2})/(\d{1,2})/(\d{4})", "slash"),
    ]
    dates_found = []
    for pattern, fmt in date_patterns:
        for m in re.finditer(pattern, body_text):
            try:
                d, mo, y = int(m.group(1)), int(m.group(2)), int(m.group(3))
                dt = datetime(y, mo, d)
                dates_found.append(dt.strftime("%Y-%m-%d"))
            except ValueError:
                continue

    if dates_found:
        record["issue_date"] = dates_found[0]
        if len(dates_found) > 1:
            record["effective_date"] = dates_found[1]

    # Document type
    title_lower = (record.get("title") or "").lower()
    if "luật" in title_lower:
        record["document_type"] = "law"
    elif "nghị định" in title_lower:
        record["document_type"] = "decree"
    elif "quyết định" in title_lower:
        record["document_type"] = "decision"
    elif "thông tư" in title_lower:
        record["document_type"] = "circular"
    elif "nghị quyết" in title_lower:
        record["document_type"] = "resolution"

    # PDF link
    pdf_link = page.css('a[href$=".pdf"]')
    if pdf_link:
        record["pdf_url"] = pdf_link[0].attrib.get("href")

    # Keywords (tags)
    tag_els = page.css(".tag, .keyword")
    record["keywords"] = [el.text.strip() for el in tag_els if el.text]

    # Checksum
    checksum = hashlib.sha256(body_text.encode("utf-8")).hexdigest()
    record["content_checksum"] = f"sha256:{checksum}"

    return record


async def fetch_document(fetcher: AsyncFetcher, url: str, semaphore: asyncio.Semaphore):
    """Fetch a single document."""
    async with semaphore:
        try:
            await asyncio.sleep(RATE_LIMIT_DELAY)
            page = await fetcher.get(url, stealthy_headers=True)
            record = extract_metadata(page, url)
            return record, None
        except Exception as e:
            return None, {"url": url, "error": str(e)}


async def discover_urls(fetcher: AsyncFetcher, limit: int = 5000) -> list[str]:
    """Discover document URLs from thuvienphapluat.vn homepage + categories."""
    urls = []

    # Crawl from homepage and category pages
    base_url = "https://thuvienphapluat.vn"
    pages_to_crawl = [
        "",  # Homepage
        "/van-ban/Phap-luat",
        "/van-ban/Hanh-chinh",
        "/van-ban/Dau-tu",
        "/van-ban/Dat-dai",
        "/van-ban/Thue",
    ]

    for path in pages_to_crawl:
        if len(urls) >= limit:
            break

        index_url = f"{base_url}{path}"
        try:
            page = await fetcher.get(index_url, stealthy_headers=True)
            if page.status != 200:
                continue

            # Find all van-ban links
            links = page.css('a[href*="/van-ban/"]')
            for link in links:
                href = link.attrib.get("href", "")
                if href and ".aspx" in href and "/van-ban/" in href:
                    if href.startswith("http"):
                        urls.append(href)
                    elif href.startswith("/"):
                        urls.append(f"{base_url}{href}")

                    if len(urls) >= limit:
                        break
        except Exception as e:
            print(f"Error crawling {index_url}: {e}")
            continue

    # Deduplicate
    urls = list(set(urls))
    return urls[:limit]


async def main_async(args):
    """Async main loop."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    output_path = OUTPUT_DIR / "raw_docs.json"

    # Load existing
    existing = []
    fetched_urls = set()
    if output_path.exists():
        existing = json.loads(output_path.read_text(encoding="utf-8"))
        fetched_urls = {r["source_url"] for r in existing}

    # Discover URLs
    fetcher = AsyncFetcher(impersonate="chrome")
    print("Discovering URLs from thuvienphapluat.vn...")
    all_urls = await discover_urls(fetcher, limit=args.limit * 2)
    print(f"Found {len(all_urls)} URLs")

    # Filter to unfetched
    to_fetch = [u for u in all_urls if u not in fetched_urls][: args.limit]
    print(f"Already fetched: {len(fetched_urls)}, this run: {len(to_fetch)}")

    if not to_fetch:
        print("Nothing to fetch")
        return

    # Fetch concurrently
    semaphore = asyncio.Semaphore(args.concurrency)
    tasks = [fetch_document(fetcher, url, semaphore) for url in to_fetch]
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
    parser = argparse.ArgumentParser(description="Scrape thuvienphapluat.vn")
    parser.add_argument("--limit", type=int, default=500)
    parser.add_argument("--concurrency", type=int, default=DEFAULT_CONCURRENCY)
    args = parser.parse_args()

    asyncio.run(main_async(args))


if __name__ == "__main__":
    main()
