#!/usr/bin/env python3
"""Fetch document pages from vbpl.vn and extract metadata.

Read-only, polite: rate-limited, checksummed, provenance-tracked.
Input: document_urls.json (from fetch_sitemap.py)
Output: source_records.json (list of source-layer records)

Resume mode: skips URLs already in source_records.json. Run repeatedly
until all URLs are processed.

Usage:
    python scripts/ingest/fetch_documents.py [--limit 500] [--output-dir scripts/ingest/output]
"""

import argparse
import hashlib
import json
import re
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

import httpx

USER_AGENT = (
    "VNKC/0.1 (+https://github.com/The-Resonance-Team/vietnam-knowledge-commons)"
)
RATE_LIMIT_DELAY = 1.5
REQUEST_TIMEOUT = 30.0
MAX_PAGES = 500


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def extract_metadata(html: str, url: str) -> dict:
    """Extract document metadata from vbpl.vn HTML page."""
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

    title_match = re.search(r"<title[^>]*>([^<]+)</title>", html, re.IGNORECASE)
    if title_match:
        record["title"] = title_match.group(1).strip()

    h1_match = re.search(r"<h1[^>]*>([^<]+)</h1>", html, re.IGNORECASE)
    if h1_match:
        record["title"] = h1_match.group(1).strip()

    doc_num_match = re.search(
        r"(\d{1,4}/\d{4}/[A-Z]{2,10}\d{0,2})", html, re.IGNORECASE
    )
    if doc_num_match:
        record["document_number"] = doc_num_match.group(1)

    date_patterns = [
        (r"ngày\s+(\d{1,2})\s+tháng\s+(\d{1,2})\s+năm\s+(\d{4})", "vi"),
        (r"(\d{1,2})/(\d{1,2})/(\d{4})", "slash"),
        (r"(\d{4})-(\d{2})-(\d{2})", "iso"),
    ]
    dates_found = []
    for pattern, fmt in date_patterns:
        for m in re.finditer(pattern, html):
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

    path = urlparse(url).path.lower()
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


def main():
    parser = argparse.ArgumentParser(description="Fetch vbpl.vn documents")
    parser.add_argument(
        "--limit",
        type=int,
        default=MAX_PAGES,
        help=f"Max pages to fetch this run (default: {MAX_PAGES})",
    )
    parser.add_argument(
        "--output-dir", default="scripts/ingest/output", help="Output directory"
    )
    args = parser.parse_args()

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
    print(f"This run: {len(to_fetch)}")

    if not to_fetch:
        print("\nNothing to fetch — all URLs processed.")
        return

    headers = {"User-Agent": USER_AGENT}
    new_records = []
    errors = []

    with httpx.Client(
        timeout=REQUEST_TIMEOUT, headers=headers, follow_redirects=True
    ) as client:
        for i, entry in enumerate(to_fetch):
            url = entry["url"]
            print(f"  [{i + 1}/{len(to_fetch)}] {url}")
            try:
                time.sleep(RATE_LIMIT_DELAY)
                resp = client.get(url)
                resp.raise_for_status()
                html = resp.text
                checksum = sha256_hex(resp.content)

                record = extract_metadata(html, url)
                record["content_checksum"] = f"sha256:{checksum}"
                record["status_code"] = resp.status_code
                new_records.append(record)

            except Exception as e:
                print(f"    Error: {e}")
                errors.append({"url": url, "error": str(e)})

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


if __name__ == "__main__":
    main()
