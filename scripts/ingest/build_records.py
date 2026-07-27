#!/usr/bin/env python3
"""Build source-layer records from fetched vbpl.vn documents.

Reads source_records.json, deduplicates, generates canonical_ids,
and outputs final records conforming to the legal-document schema.

Usage:
    python scripts/ingest/build_records.py [--output-dir scripts/ingest/output]
"""

import argparse
import json
import re
from pathlib import Path


def generate_canonical_id(record: dict) -> str:
    """Generate a stable canonical_id from document metadata."""
    doc_num = record.get("document_number")
    if doc_num:
        # Normalize: "45/2024/QH15" → "45-2024-QH15"
        slug = re.sub(r"[^a-z0-9]+", "-", doc_num.lower()).strip("-")
        return f"vnkc:legal-doc:{slug}"

    # Fallback: use URL path
    url = record.get("source_url", "")
    path = url.rstrip("/").split("/")[-1] if url else "unknown"
    slug = re.sub(r"[^a-z0-9]+", "-", path.lower()).strip("-")
    return f"vnkc:legal-doc:{slug}"


def build_record(record: dict) -> dict:
    """Transform a source record into a legal-document record."""
    canonical_id = generate_canonical_id(record)

    return {
        "canonical_id": canonical_id,
        "document_number": record.get("document_number"),
        "title": record.get("title"),
        "title_en": None,
        "document_type": record.get("document_type", "unknown"),
        "issuing_authority": None,
        "jurisdiction": "national",
        "issue_date": record.get("issue_date"),
        "publication_date": None,
        "effective_from": record.get("effective_date"),
        "effective_to": None,
        "status": record.get("status", "unknown"),
        "language": "vi",
        "official_url": record.get("source_url"),
        "attachment_urls": [],
        "retrieved_at": record.get("retrieved_at"),
        "version": 1,
        "legal_basis": [],
        "related_documents": [],
        "amends": [],
        "amended_by": [],
        "replaces": [],
        "replaced_by": [],
        "repeals": [],
        "repealed_by": [],
        "guides": [],
        "validity_confidence": "unverified",
        "provenance": {
            "source_id": "moj-vbpl",
            "source_url": record.get("source_url"),
            "retrieved_at": record.get("retrieved_at"),
            "retrieval_method": "html",
            "content_checksum": record.get("content_checksum"),
            "license_status": "reference-only",
            "attribution": "Bộ Tư pháp nước CHXHCN Việt Nam — vbpl.vn",
            "confidence": "unverified",
            "notes": "Phase 0 automated ingestion. Metadata extracted from HTML; requires human verification.",
        },
    }


def deduplicate(records: list[dict]) -> list[dict]:
    """Deduplicate by canonical_id, keeping first occurrence."""
    seen = set()
    unique = []
    for r in records:
        cid = r["canonical_id"]
        if cid not in seen:
            seen.add(cid)
            unique.append(r)
    return unique


def main():
    parser = argparse.ArgumentParser(description="Build source-layer records")
    parser.add_argument(
        "--output-dir", default="scripts/ingest/output", help="Output directory"
    )
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    source_path = output_dir / "source_records.json"

    if not source_path.exists():
        print(f"Error: {source_path} not found. Run fetch_documents.py first.")
        raise SystemExit(1)

    source_records = json.loads(source_path.read_text(encoding="utf-8"))
    print(f"Loaded {len(source_records)} source records")

    # Build legal-document records
    records = [build_record(r) for r in source_records]

    # Deduplicate
    records = deduplicate(records)
    print(f"After dedup: {len(records)} unique records")

    # Save
    (output_dir / "legal_documents.json").write_text(
        json.dumps(records, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print(f"Output: {output_dir}/legal_documents.json")

    # Summary
    types = {}
    for r in records:
        t = r["document_type"]
        types[t] = types.get(t, 0) + 1
    print("\nDocument types:")
    for t, count in sorted(types.items()):
        print(f"  {t}: {count}")


if __name__ == "__main__":
    main()
