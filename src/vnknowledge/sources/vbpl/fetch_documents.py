#!/usr/bin/env python3
"""Fetch document pages from vbpl.vn and extract metadata.

Uses Scrapling's Fetcher for HTTP requests with:
- Browser impersonation (TLS fingerprint)
- Session management
- Polite rate limiting
- Concurrent requests (asyncio)

Read-only, polite: rate-limited, checksummed, provenance-tracked.
Input: document_urls.json (from fetch_sitemap.py)
Output: source_records.json (list of source-layer records)

Resume mode: skips URLs already in source_records.json. Run repeatedly
until all URLs are processed.

Usage:
    python scripts/ingest/fetch_documents.py [--limit 500] [--concurrency 5] [--output-dir scripts/ingest/output]
"""

import argparse
import asyncio
import hashlib
import json
import re
import time
from datetime import datetime, timezone
from pathlib import Path

from scrapling.fetchers import AsyncFetcher

RATE_LIMIT_DELAY = 1.5
MAX_PAGES = 500
DEFAULT_CONCURRENCY = 5


def extract_metadata(page, url: str) -> dict:
    """Extract document metadata from vbpl.vn HTML page using Scrapling parser."""
    record = {
        "source_url": url,
        "title": None,
        "document_number": None,
        "document_type": None,
        "issue_date": None,
        "effective_date": None,
        "status": "unknown",
        "retrieved_at": datetime.now(timezone.utc).isoformat(),
    }

    # Use Scrapling's CSS selectors
    title_el = page.css("title")
    if title_el:
        record["title"] = title_el[0].text.strip()

    h1_el = page.css("h1")
    if h1_el:
        record["title"] = h1_el[0].text.strip()

    # Extract document number
    body_text = page.text or ""
    doc_num_match = re.search(
        r"(\d{1,4}/\d{4}/[A-Z]{2,10}\d{0,2})", body_text, re.IGNORECASE
    )
    if doc_num_match:
        record["document_number"] = doc_num_match.group(1)

    # Extract dates
    date_patterns = [
        (r"ngày\s+(\d{1,2})\s+tháng\s+(\d{1,2})\s+năm\s+(\d{4})", "vi"),
        (r"(\d{1,2})/(\d{1,2})/(\d{4})", "slash"),
        (r"(\d{4})-(\d{2})-(\d{2})", "iso"),
    ]
    dates_found = []
    for pattern, fmt in date_patterns:
        for m in re.finditer(pattern, body_text):
            try:
                if fmt == "vi":
                    d, mo, y = int(m.group(1)), int(m.group(2)), int(m.group(3))
                elif fmt == "slash":
                    d, mo, y = int(m.group(1)), int(m.group(2)), int(m.group(3))
                else:
                    y, mo, d = int(m.group(1)), int(m.group(2)), int(m.group(3))
                dt = datetime(y, mo, d)
                dates_found.append(dt.strftime("%Y-%m-%d"))
            except ValueError:
                continue

    if dates_found:
        record["issue_date"] = dates_found[0]
        if len(dates_found) > 1:
            record["effective_date"] = dates_found[1]

    # Detect document type
    path = url.lower()
    title_lower = (record.get("title") or "").lower()
    if "luat" in path or "luật" in title_lower:
        record["document_type"] = "law"
    elif "nghi-dinh" in path or "nghị định" in title_lower:
        record["document_type"] = "decree"
    elif "quyet-dinh" in path or "quyết định" in title_lower:
        record["document_type"] = "decision"
    elif "thong-tu" in path or "thông tư" in title_lower:
        record["document_type"] = "circular"
    elif "nghi-quyet" in path or "nghị quyết" in title_lower:
        record["document_type"] = "resolution"

    return record


def load_existing(output_dir: Path) -> tuple[list[dict], set[str]]:
    """Load existing records and set of fetched URLs."""
    path = output_dir / "source_records.json"
    if not path.exists():
        return [], set()
    records = json.loads(path.read_text(encoding="utf-8"))
    urls = {r["source_url"] for r in records if "source_url" in r}
    return records, urls


async def fetch_document(
    fetcher: AsyncFetcher, url: str, semaphore: asyncio.Semaphore
) -> tuple[dict | None, dict | None]:
    """Fetch a single document page asynchronously."""
    async with semaphore:
        try:
            await asyncio.sleep(RATE_LIMIT_DELAY)
            page = await fetcher.get(url, stealthy_headers=True)
            record = extract_metadata(page, url)
            checksum = hashlib.sha256(page.text.encode("utf-8")).hexdigest()
            record["content_checksum"] = f"sha256:{checksum}"
            return record, None
        except Exception as e:
            return None, {"url": url, "error": str(e)}


async def main_async(args):
    """Async main loop with concurrency."""
    output_dir = Path(args.output_dir)
    doc_urls_path = output_dir / "document_urls.json"

    if not doc_urls_path.exists():
        print(f"Error: {doc_urls_path} not found. Run fetch_sitemap.py first.")
        raise SystemExit(1)

    all_urls = json.loads(doc_urls_path.read_text(encoding="utf-8"))
    existing_records, fetched_urls = load_existing(output_dir)

    # Filter to unfetched URLs
    remaining = [u for u in all_urls if u["url"] not in fetched_urls]
    to_fetch = remaining[: args.limit]

    print(f"Total URLs: {len(all_urls)}")
    print(f"Already fetched: {len(fetched_urls)}")
    print(f"Remaining: {len(remaining)}")
    print(f"This run: {len(to_fetch)} (concurrency: {args.concurrency})")

    if not to_fetch:
        print("\nNothing to fetch — all URLs processed.")
        return

    semaphore = asyncio.Semaphore(args.concurrency)
    fetcher = AsyncFetcher(impersonate="chrome")

    tasks = [fetch_document(fetcher, entry["url"], semaphore) for entry in to_fetch]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    new_records = []
    errors = []
    for i, result in enumerate(results):
        if isinstance(result, Exception):
            print(f"  [{i + 1}/{len(to_fetch)}] Exception: {result}")
            errors.append({"url": to_fetch[i]["url"], "error": str(result)})
        else:
            record, error = result
            if record:
                new_records.append(record)
                print(f"  [{i + 1}/{len(to_fetch)}] ✓ {to_fetch[i]['url']}")
            if error:
                errors.append(error)
                print(f"  [{i + 1}/{len(to_fetch)}] ✗ {error['url']}: {error['error']}")

    # Merge with existing records
    all_records = existing_records + new_records
    (output_dir / "source_records.json").write_text(
        json.dumps(all_records, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    if errors:
        (output_dir / "fetch_errors.json").write_text(
            json.dumps(errors, indent=2, ensure_ascii=False), encoding="utf-8"
        )

    print(f"\nFetched {len(new_records)} new documents, {len(errors)} errors")
    print(f"Total records now: {len(all_records)}")
    print(f"Remaining URLs: {len(remaining) - len(to_fetch)}")
    if remaining and len(to_fetch) < len(remaining):
        print("Run again to continue fetching.")


def main():
    parser = argparse.ArgumentParser(description="Fetch vbpl.vn documents")
    parser.add_argument(
        "--limit",
        type=int,
        default=MAX_PAGES,
        help=f"Max pages to fetch this run (default: {MAX_PAGES})",
    )
    parser.add_argument(
        "--concurrency",
        type=int,
        default=DEFAULT_CONCURRENCY,
        help=f"Concurrent requests (default: {DEFAULT_CONCURRENCY})",
    )
    parser.add_argument(
        "--output-dir", default="scripts/ingest/output", help="Output directory"
    )
    args = parser.parse_args()

    asyncio.run(main_async(args))


if __name__ == "__main__":
    main()
