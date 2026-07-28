#!/usr/bin/env python3
"""Official Gazette scraper — PDFs from congbao.chinhphu.vn.

Scrapes PDF download URLs + metadata.
Output: .scratch/congbao/raw_pdfs.json

Usage:
    python scripts/scrapers/congbao_scraper.py --limit 500 --concurrency 5
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
OUTPUT_DIR = Path(".scratch/congbao")


def extract_pdf_metadata(page, url: str) -> dict:
    """Extract PDF metadata from congbao.chinhphu.vn page."""
    record = {
        "source_url": url,
        "title": None,
        "pdf_url": None,
        "document_ref": None,  # Reference to vbpl.vn doc
        "publication_date": None,
        "issue_number": None,
        "file_size_bytes": None,
        "retrieved_at": datetime.now(timezone.utc).isoformat(),
    }

    body_text = page.text or ""

    # Title
    h1_el = page.css("h1")
    if h1_el:
        record["title"] = h1_el[0].text.strip()

    # PDF URL
    pdf_link = page.css('a[href$=".pdf"]')
    if pdf_link:
        record["pdf_url"] = pdf_link[0].attrib.get("href")

    # Document reference (Số văn bản)
    ref_match = re.search(r"(\d{1,4}/\d{4}/[A-Z]{2,10}\d{0,2})", body_text, re.IGNORECASE)
    if ref_match:
        record["document_ref"] = ref_match.group(1)

    # Publication date
    date_match = re.search(r"ngày\s+(\d{1,2})\s+tháng\s+(\d{1,2})\s+năm\s+(\d{4})", body_text)
    if date_match:
        d, mo, y = int(date_match.group(1)), int(date_match.group(2)), int(date_match.group(3))
        try:
            dt = datetime(y, mo, d)
            record["publication_date"] = dt.strftime("%Y-%m-%d")
        except ValueError:
            pass

    # Issue number (Số Công báo)
    issue_match = re.search(r"[Cc]ông báo\s+số\s+([^\n]+)", body_text)
    if issue_match:
        record["issue_number"] = issue_match.group(1).strip()

    # File size
    size_match = re.search(r"(\d+(?:\.\d+)?)\s*(?:MB|KB)", body_text, re.IGNORECASE)
    if size_match:
        size_val = float(size_match.group(1))
        unit = size_match.group(2).upper()
        if unit == "MB":
            record["file_size_bytes"] = int(size_val * 1024 * 1024)
        elif unit == "KB":
            record["file_size_bytes"] = int(size_val * 1024)

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
            record = extract_pdf_metadata(page, url)
            return record, None
        except Exception as e:
            return None, {"url": url, "error": str(e)}


async def discover_urls(limit: int = 10000) -> list[str]:
    """Discover HTML page URLs from congbao.chinhphu.vn (skip PDF download links)."""
    urls = []

    try:
        page = await asyncio.to_thread(StealthyFetcher.fetch, "https://congbao.chinhphu.vn/", headless=True)
        if page.status == 200:
            links = page.css('a[href]')
            for link in links:
                href = link.attrib.get("href", "")
                if href:
                    # Skip PDF download links (trigger download instead of page load)
                    if "/download/stream" in href or href.endswith(".pdf"):
                        continue

                    # Keep HTML page URLs
                    if href.startswith("http"):
                        urls.append(href)
                    elif href.startswith("/"):
                        urls.append(f"https://congbao.chinhphu.vn{href}")

                    if len(urls) >= limit:
                        break
    except Exception as e:
        print(f"Error crawling homepage: {e}")

    return list(set(urls))[:limit]


async def main_async(args):
    """Async main loop."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    output_path = OUTPUT_DIR / "raw_pdfs.json"

    # Load existing
    existing = []
    fetched_urls = set()
    if output_path.exists():
        existing = json.loads(output_path.read_text(encoding="utf-8"))
        fetched_urls = {r["source_url"] for r in existing}

    # Discover URLs
    print("Discovering URLs from congbao.chinhphu.vn...")
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
    parser = argparse.ArgumentParser(description="Scrape congbao.chinhphu.vn")
    parser.add_argument("--limit", type=int, default=500)
    parser.add_argument("--concurrency", type=int, default=DEFAULT_CONCURRENCY)
    args = parser.parse_args()

    asyncio.run(main_async(args))


if __name__ == "__main__":
    main()
