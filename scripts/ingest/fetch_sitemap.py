#!/usr/bin/env python3
"""Fetch vbpl.vn sitemap index and discover document URLs.

Read-only, polite: respects robots.txt, rate-limited to 1 req/sec.
Output: sitemap_index.json (list of sitemap URLs) + sitemap_urls.json (all document URLs).

Usage:
    python scripts/ingest/fetch_sitemap.py [--output-dir scripts/ingest/output]
"""

import argparse
import json
import time
import xml.etree.ElementTree as ET
from pathlib import Path
from urllib.parse import urlparse

import httpx

SITEMAP_INDEX_URL = "https://vbpl.vn/sitemap.xml"
USER_AGENT = (
    "VNKC/0.1 (+https://github.com/The-Resonance-Team/vietnam-knowledge-commons)"
)
RATE_LIMIT_DELAY = 1.0  # seconds between requests
REQUEST_TIMEOUT = 30.0


def fetch_url(url: str, client: httpx.Client) -> str:
    """Fetch URL with rate limiting and polite headers."""
    time.sleep(RATE_LIMIT_DELAY)
    resp = client.get(url, follow_redirects=True)
    resp.raise_for_status()
    return resp.text


def parse_sitemap_index(xml_text: str) -> list[dict]:
    """Parse sitemap index XML, return list of {url, lastmod}."""
    root = ET.fromstring(xml_text)
    sitemaps = []
    for sm in root.findall(".//{http://www.sitemaps.org/schemas/sitemap/0.9}sitemap"):
        loc = sm.find("{http://www.sitemaps.org/schemas/sitemap/0.9}loc")
        lastmod = sm.find("{http://www.sitemaps.org/schemas/sitemap/0.9}lastmod")
        if loc is not None and loc.text:
            sitemaps.append(
                {
                    "url": loc.text.strip(),
                    "lastmod": lastmod.text.strip() if lastmod is not None else None,
                }
            )
    return sitemaps


def parse_sitemap_urls(xml_text: str) -> list[dict]:
    """Parse a sitemap XML, return list of {url, lastmod, changefreq, priority}."""
    root = ET.fromstring(xml_text)
    urls = []
    for url_elem in root.findall(".//{http://www.sitemaps.org/schemas/sitemap/0.9}url"):
        loc = url_elem.find("{http://www.sitemaps.org/schemas/sitemap/0.9}loc")
        lastmod = url_elem.find("{http://www.sitemaps.org/schemas/sitemap/0.9}lastmod")
        changefreq = url_elem.find(
            "{http://www.sitemaps.org/schemas/sitemap/0.9}changefreq"
        )
        priority = url_elem.find(
            "{http://www.sitemaps.org/schemas/sitemap/0.9}priority"
        )
        if loc is not None and loc.text:
            urls.append(
                {
                    "url": loc.text.strip(),
                    "lastmod": lastmod.text.strip() if lastmod is not None else None,
                    "changefreq": changefreq.text.strip()
                    if changefreq is not None
                    else None,
                    "priority": float(priority.text) if priority is not None else None,
                }
            )
    return urls


def filter_document_urls(urls: list[dict]) -> list[dict]:
    """Filter to likely legal document URLs (skip assets, images, etc.)."""
    doc_urls = []
    for entry in urls:
        parsed = urlparse(entry["url"])
        path = parsed.path.lower()
        # Keep only HTML-like paths that look like document pages
        if any(path.endswith(ext) for ext in [".xml", ".png", ".jpg", ".css", ".js"]):
            continue
        if "/assets/" in path or "/images/" in path or "/static/" in path:
            continue
        # Keep if it looks like a document path
        if "/van-ban/" in path or "/luat/" in path or "/nghi-dinh/" in path:
            doc_urls.append(entry)
        elif "/chi-tiet/" in path or "/detail/" in path:
            doc_urls.append(entry)
        elif parsed.netloc == "vbpl.vn" and len(path.split("/")) > 2:
            doc_urls.append(entry)
    return doc_urls


def main():
    parser = argparse.ArgumentParser(description="Fetch vbpl.vn sitemap")
    parser.add_argument(
        "--output-dir",
        default="scripts/ingest/output",
        help="Output directory (default: scripts/ingest/output)",
    )
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    headers = {"User-Agent": USER_AGENT}

    with httpx.Client(timeout=REQUEST_TIMEOUT, headers=headers) as client:
        print(f"Fetching sitemap index: {SITEMAP_INDEX_URL}")
        index_xml = fetch_url(SITEMAP_INDEX_URL, client)
        sitemaps = parse_sitemap_index(index_xml)
        print(f"Found {len(sitemaps)} sitemaps")

        # Save sitemap index
        (output_dir / "sitemap_index.json").write_text(
            json.dumps(sitemaps, indent=2, ensure_ascii=False), encoding="utf-8"
        )

        # Fetch each sitemap and collect document URLs
        all_urls = []
        for i, sm in enumerate(sitemaps):
            print(f"  [{i + 1}/{len(sitemaps)}] {sm['url']}")
            try:
                xml = fetch_url(sm["url"], client)
                urls = parse_sitemap_urls(xml)
                all_urls.extend(urls)
                print(f"    → {len(urls)} URLs")
            except Exception as e:
                print(f"    ✗ Error: {e}")

        # Filter to document URLs
        doc_urls = filter_document_urls(all_urls)
        print(f"\nTotal URLs: {len(all_urls)}, document URLs: {len(doc_urls)}")

        # Save all URLs and filtered document URLs
        (output_dir / "sitemap_urls.json").write_text(
            json.dumps(all_urls, indent=2, ensure_ascii=False), encoding="utf-8"
        )
        (output_dir / "document_urls.json").write_text(
            json.dumps(doc_urls, indent=2, ensure_ascii=False), encoding="utf-8"
        )

        print(f"\nOutput saved to {output_dir}/")
        print(f"  sitemap_index.json  — {len(sitemaps)} sitemaps")
        print(f"  sitemap_urls.json   — {len(all_urls)} total URLs")
        print(f"  document_urls.json  — {len(doc_urls)} document URLs")


if __name__ == "__main__":
    main()
