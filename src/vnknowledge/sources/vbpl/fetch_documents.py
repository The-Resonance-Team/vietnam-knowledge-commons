#!/usr/bin/env python3
"""Fetch raw body/subject payloads for vbpl.vn legal documents.

vbpl.vn's detail pages are client-rendered: a plain GET only returns SSR
`<head>` metadata (title, SEO description, dates) — the document body is
fetched by the page's own JS via a second request. So each record costs two
sequential HTTP requests:

    GET  <official_url>                        -> page_html (subject source)
    POST <official_url>  (next-action header)   -> body_rsc  (body source)

See parser.py for why the POST looks the way it does, and for turning these
raw payloads into body/subject text.

Read-only, polite: one request in flight at a time (scraping-plan.md: no
parallel requests to a single domain), rate-limited, checksummed,
provenance-tracked. Resume mode: skips canonical_ids already saved under
--output-dir, so this can be run repeatedly until all records are fetched.

Usage:
    python -m vnknowledge.sources.vbpl.fetch_documents \\
        --corpus datasets/legal-corpus/releases/v0.1.0/legal-corpus.json \\
        --output-dir data/raw/vbpl [--limit 500]
"""

import argparse
import json
import time
from collections.abc import Callable, Iterable
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import httpx

from vnknowledge.common.checksums import sha256_hex
from vnknowledge.sources.vbpl.parser import BODY_ACTION_ID

RATE_LIMIT_DELAY = 1.5
RETRY_DELAYS = (1, 2, 4)
USER_AGENT = (
    "Mozilla/5.0 (compatible; VNKC-research/0.1; "
    "+https://github.com/The-Resonance-Team/vietnam-knowledge-commons)"
)


def doc_id_from_canonical_id(canonical_id: str) -> str:
    return canonical_id.removeprefix("vnkc:legal-doc:")


def _request_with_retries(
    client: httpx.Client, method: str, url: str, **kwargs: Any
) -> httpx.Response:
    delays: Iterable[float] = (0.0, *RETRY_DELAYS)
    last_error: httpx.HTTPError | None = None
    for delay in delays:
        if delay:
            time.sleep(delay)
        try:
            response = client.request(method, url, **kwargs)
            response.raise_for_status()
            return response
        except httpx.HTTPError as error:
            last_error = error
    assert last_error is not None
    raise last_error


def fetch_raw(
    client: httpx.Client, record: dict[str, Any], sleep: Callable[[float], None]
) -> dict[str, Any]:
    """Two sequential requests (GET page, POST body) for one corpus record."""
    url = record["official_url"]
    doc_id = doc_id_from_canonical_id(record["canonical_id"])

    get_response = _request_with_retries(client, "GET", url)
    sleep(RATE_LIMIT_DELAY)

    post_response = _request_with_retries(
        client,
        "POST",
        url,
        headers={
            "next-action": BODY_ACTION_ID,
            "accept": "text/x-component",
            "content-type": "text/plain;charset=UTF-8",
            "origin": "https://vbpl.vn",
            "referer": url,
        },
        content=json.dumps([doc_id]),
    )
    sleep(RATE_LIMIT_DELAY)

    return {
        "canonical_id": record["canonical_id"],
        "official_url": url,
        "retrieved_at": datetime.now(UTC).isoformat(),
        "page_html": get_response.text,
        "body_rsc": post_response.text,
        "content_checksum": sha256_hex(post_response.content),
    }


def run(
    records: list[dict[str, Any]],
    output_dir: Path,
    client: httpx.Client,
    *,
    sleep: Callable[[float], None] = time.sleep,
    limit: int | None = None,
) -> int:
    """Fetch `records` not already saved under `output_dir`. Returns count fetched."""
    output_dir.mkdir(parents=True, exist_ok=True)
    fetched = 0
    for record in records:
        if limit is not None and fetched >= limit:
            break
        doc_id = doc_id_from_canonical_id(record["canonical_id"])
        out_path = output_dir / f"{doc_id}.json"
        if out_path.exists():
            continue
        raw = fetch_raw(client, record, sleep)
        out_path.write_text(json.dumps(raw, ensure_ascii=False, indent=2), encoding="utf-8")
        fetched += 1
    return fetched


def main() -> None:
    parser = argparse.ArgumentParser(description="Fetch vbpl.vn document body/subject payloads")
    parser.add_argument("--corpus", required=True, help="Path to legal-corpus.json")
    parser.add_argument(
        "--output-dir", default="data/raw/vbpl", help="Raw payload output directory"
    )
    parser.add_argument("--limit", type=int, default=None, help="Max records to fetch this run")
    args = parser.parse_args()

    records = json.loads(Path(args.corpus).read_text(encoding="utf-8"))
    with httpx.Client(timeout=30, headers={"User-Agent": USER_AGENT}) as client:
        fetched = run(records, Path(args.output_dir), client, limit=args.limit)

    print(f"Fetched {fetched} new record(s) into {args.output_dir}")


if __name__ == "__main__":
    main()
