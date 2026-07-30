#!/usr/bin/env python3
"""Assemble and write datasets/legal-corpus's full-text release artifact.

Reads raw payloads saved by sources/vbpl/fetch_documents.py, builds
LegalDocumentFulltext records (transform/legal_document_fulltext.py), and
writes them as sharded JSON files -- kept apart from the metadata-only
legal-corpus.json per DATA_POLICY.md's source-vs-derived separation, and
eligible to publish under ADR-0005's license posture. Sharded (not one file)
because full body text makes a single-file release exceed GitHub's 100MB
per-file limit; matches the metadata release's own prior 28-shard structure.

Usage:
    python -m vnknowledge.publish.legal_corpus_fulltext \\
        --corpus datasets/legal-corpus/releases/v0.1.0/legal-corpus.json \\
        --raw-dir data/raw/vbpl \\
        --output-dir datasets/legal-corpus/releases/v0.2.0/legal-corpus-fulltext
"""

import argparse
import json
from pathlib import Path
from typing import Any

from vnknowledge.transform.legal_document_fulltext import build_fulltext_record

SHARD_SIZE = 1000


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


def write_shards(
    records: list[dict[str, Any]], output_dir: Path, shard_size: int = SHARD_SIZE
) -> int:
    """Write `records` as shard-NNN.json files of at most `shard_size` records
    each. Returns the number of shards written."""
    output_dir.mkdir(parents=True, exist_ok=True)
    shard_count = 0
    for start in range(0, len(records), shard_size):
        shard = records[start : start + shard_size]
        shard_path = output_dir / f"shard-{shard_count:03d}.json"
        shard_path.write_text(json.dumps(shard, ensure_ascii=False, indent=2), encoding="utf-8")
        shard_count += 1
    return shard_count


def main() -> None:
    parser = argparse.ArgumentParser(description="Publish sharded legal-corpus-fulltext")
    parser.add_argument("--corpus", required=True, help="Path to legal-corpus.json")
    parser.add_argument("--raw-dir", default="data/raw/vbpl", help="fetch_documents.py output dir")
    parser.add_argument(
        "--output-dir", required=True, help="Directory to write shard-NNN.json into"
    )
    args = parser.parse_args()

    corpus = json.loads(Path(args.corpus).read_text(encoding="utf-8"))
    canonical_ids = {r["canonical_id"] for r in corpus}

    records = assemble_fulltext_records(Path(args.raw_dir), canonical_ids)

    shard_count = write_shards(records, Path(args.output_dir))
    print(f"Wrote {len(records)} record(s) across {shard_count} shard(s) to {args.output_dir}")


if __name__ == "__main__":
    main()
