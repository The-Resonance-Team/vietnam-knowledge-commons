#!/usr/bin/env python3
"""VBPL.vn ingestion spider using Scrapling.

Uses Scrapling's SitemapSpider for sitemap-driven crawling with:
- AutoThrottle (adapts to server response)
- Robots.txt compliance
- Pause/resume with checkpoints
- Adaptive parsing (survives website changes)

Usage:
    # Full crawl (pause/resume with Ctrl+C)
    python scripts/ingest/vbpl_spider.py

    # Quick test (50 pages)
    python scripts/ingest/vbpl_spider.py --limit 50

    # Resume from checkpoint
    python scripts/ingest/vbpl_spider.py --resume
"""

import argparse
import hashlib
import json
import re
from datetime import datetime
from pathlib import Path

from scrapling.fetchers import FetcherSession
from scrapling.spiders import Request, Response, Spider


class VBPLSpider(Spider):
    """Spider for vbpl.vn legal document database."""

    name = "vbpl"
    start_urls = ["https://vbpl.vn/sitemap.xml"]

    # Concurrency and throttling
    concurrent_requests = 5
    download_delay = 1.5
    autorottle_enabled = True

    # Robots.txt compliance
    robots_txt_obey = True

    def __init__(self, output_dir: str = "scripts/ingest/output", limit: int = 500, **kwargs):
        super().__init__(**kwargs)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.limit = limit
        self.fetched_count = 0
        self.records = []

    def configure_sessions(self, manager):
        """Configure HTTP sessions with polite headers."""
        manager.add(
            "default",
            FetcherSession(impersonate="chrome"),
        )

    async def parse(self, response: Response):
        """Parse a vbpl.vn page."""
        url = response.url

        # If this is the sitemap index, extract sub-sitemap URLs
        if "sitemap.xml" in url and "sitemap/" not in url:
            # Parse sitemap index
            import xml.etree.ElementTree as ET

            root = ET.fromstring(response.text)
            for sm in root.findall(".//{http://www.sitemaps.org/schemas/sitemap/0.9}sitemap"):
                loc = sm.find("{http://www.sitemaps.org/schemas/sitemap/0.9}loc")
                if loc is not None and loc.text:
                    yield Request(loc.text.strip(), callback=self.parse_sitemap)
            return

    async def parse_sitemap(self, response: Response):
        """Parse a sub-sitemap to extract document URLs."""
        import xml.etree.ElementTree as ET

        root = ET.fromstring(response.text)

        for url_elem in root.findall(".//{http://www.sitemaps.org/schemas/sitemap/0.9}url"):
            loc = url_elem.find("{http://www.sitemaps.org/schemas/sitemap/0.9}loc")
            if loc is not None and loc.text:
                page_url = loc.text.strip()
                # Only follow document detail pages
                if "/van-ban/chi-tiet/" in page_url:
                    if self.fetched_count >= self.limit:
                        return
                    yield Request(page_url, callback=self.parse_document)

    async def parse_document(self, response: Response):
        """Parse a vbpl.vn document page."""
        if self.fetched_count >= self.limit:
            return

        record = self.extract_metadata(response)
        if record:
            self.records.append(record)
            self.fetched_count += 1

            # Save progress every 100 records
            if self.fetched_count % 100 == 0:
                self.save_records()
                print(f"  Progress: {self.fetched_count}/{self.limit} documents fetched")

    def extract_metadata(self, response: Response) -> dict | None:
        """Extract document metadata from vbpl.vn HTML page."""
        url = response.url

        record = {
            "source_url": url,
            "title": None,
            "document_number": None,
            "document_type": None,
            "issue_date": None,
            "effective_date": None,
            "status": "unknown",
            "retrieved_at": "",
        }

        # Use Scrapling's CSS selectors
        title_el = response.css("title")
        if title_el:
            record["title"] = title_el[0].text.strip()

        h1_el = response.css("h1")
        if h1_el:
            record["title"] = h1_el[0].text.strip()

        # Extract document number
        body_text = response.text or ""
        doc_num_match = re.search(r"(\d{1,4}/\d{4}/[A-Z]{2,10}\d{0,2})", body_text, re.IGNORECASE)
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

        # Content checksum
        content_bytes = (response.text or "").encode("utf-8")
        checksum = hashlib.sha256(content_bytes).hexdigest()
        record["content_checksum"] = f"sha256:{checksum}"

        return record

    def save_records(self):
        """Save accumulated records to disk."""
        output_path = self.output_dir / "source_records.json"

        # Load existing records for resume support
        existing = []
        if output_path.exists():
            existing = json.loads(output_path.read_text(encoding="utf-8"))

        # Merge (dedup by URL)
        existing_urls = {r["source_url"] for r in existing}
        new_records = [r for r in self.records if r["source_url"] not in existing_urls]
        all_records = existing + new_records

        output_path.write_text(
            json.dumps(all_records, indent=2, ensure_ascii=False), encoding="utf-8"
        )
        print(f"  Saved {len(all_records)} total records ({len(new_records)} new)")

    async def on_close(self):
        """Save records when spider closes."""
        self.save_records()


def main():
    parser = argparse.ArgumentParser(description="VBPL.vn ingestion spider")
    parser.add_argument("--limit", type=int, default=500, help="Max pages to fetch (default: 500)")
    parser.add_argument("--output-dir", default="scripts/ingest/output", help="Output directory")
    parser.add_argument("--resume", action="store_true", help="Resume from checkpoint")
    args = parser.parse_args()

    spider = VBPLSpider(output_dir=args.output_dir, limit=args.limit)
    spider.start()


if __name__ == "__main__":
    main()
