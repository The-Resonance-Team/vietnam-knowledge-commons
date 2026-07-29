#!/usr/bin/env python3
"""Assemble and write datasets/legal-corpus's full-text release artifact.

Reads raw payloads saved by sources/vbpl/fetch_documents.py, builds
LegalDocumentFulltext records (transform/legal_document_fulltext.py), and
writes them to a separate legal-corpus-fulltext.json — kept apart from the
metadata-only legal-corpus.json per DATA_POLICY.md's source-vs-derived
separation, and eligible to publish under ADR-0005's license posture.

Usage:
    python -m vnknowledge.publish.legal_corpus_fulltext \\
        --corpus datasets/legal-corpus/releases/v0.1.0/legal-corpus.json \\
        --raw-dir data/raw/vbpl \\
        --output datasets/legal-corpus/releases/v0.2.0/legal-corpus-fulltext.json
"""

import argparse
import json
from pathlib import Path
from typing import Any

from vnknowledge.transform.legal_document_fulltext import build_fulltext_record


def assemble_fulltext_records(raw_dir: Path, canonical_ids: set[str]) -> list[dict[str, Any]]:
    """Build fulltext records from raw payloads in `raw_dir` whose canonical_id
    belongs to the current corpus. Payloads with no extractable body are
    skipped -- not every fetched page has parsed cleanly yet."""
    records = []
    for path in sorted(raw_dir.glob("*.json")):
        raw = json.loads(path.read_text(encoding="utf-8"))
        if raw["canonical_id"] not in canonical_ids:
            continue
        record = build_fulltext_record(raw)
        if record is not None:
            records.append(record)
    return records


def main() -> None:
    parser = argparse.ArgumentParser(description="Publish legal-corpus-fulltext.json")
    parser.add_argument("--corpus", required=True, help="Path to legal-corpus.json")
    parser.add_argument("--raw-dir", default="data/raw/vbpl", help="fetch_documents.py output dir")
    parser.add_argument("--output", required=True, help="Path to write legal-corpus-fulltext.json")
    args = parser.parse_args()

    corpus = json.loads(Path(args.corpus).read_text(encoding="utf-8"))
    canonical_ids = {r["canonical_id"] for r in corpus}

    records = assemble_fulltext_records(Path(args.raw_dir), canonical_ids)

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(records, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {len(records)} fulltext record(s) to {output_path}")


if __name__ == "__main__":
    main()
