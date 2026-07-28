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

from scrapling.fetchers import AsyncFetcher

RATE_LIMIT_DELAY = 1.5
DEFAULT_CONCURRENCY = 5
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


async def fetch_page(fetcher: AsyncFetcher, url: str, semaphore: asyncio.Semaphore):
    """Fetch a single page."""
    async with semaphore:
        try:
            await asyncio.sleep(RATE_LIMIT_DELAY)
            page = await fetcher.get(url, stealthy_headers=True)
            record = extract_pdf_metadata(page, url)
            return record, None
        except Exception as e:
            return None, {"url": url, "error": str(e)}


async def main_async(args):
    """Async main loop."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    output_path = OUTPUT_DIR / "raw_pdfs.json"

    print("Official Gazette scraper — congbao.chinhphu.vn")
    print("TODO: Implement URL discovery (PDF pages)")
    print("Need: Crawl from https://congbao.chinhphu.vn/ or sitemap")
    print("Note: May need DynamicFetcher for PDF viewer JS")
    return


def main():
    parser = argparse.ArgumentParser(description="Scrape congbao.chinhphu.vn")
    parser.add_argument("--limit", type=int, default=500)
    parser.add_argument("--concurrency", type=int, default=DEFAULT_CONCURRENCY)
    args = parser.parse_args()

    asyncio.run(main_async(args))


if __name__ == "__main__":
    main()
