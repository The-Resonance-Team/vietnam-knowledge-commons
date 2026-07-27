#!/usr/bin/env python3
"""Orchestrate the vbpl.vn ingestion pipeline.

Runs all steps in sequence: sitemap → documents → build records.
Each step handles resume internally (skips already-processed data).

Usage:
    python scripts/ingest/run.py [--limit 500] [--output-dir scripts/ingest/output]
"""

import argparse
import subprocess
import sys
from pathlib import Path


def run_step(name: str, script: str, args: list[str]) -> bool:
    """Run a pipeline step."""
    print(f"\n{'=' * 60}")
    print(f"  STEP: {name}")
    print(f"{'=' * 60}")

    cmd = [sys.executable, f"scripts/ingest/{script}"] + args
    result = subprocess.run(cmd, cwd=Path(__file__).resolve().parents[2])

    if result.returncode != 0:
        print(f"✗ {name} failed (exit code {result.returncode})")
        return False

    print(f"✓ {name} complete")
    return True


def main():
    parser = argparse.ArgumentParser(description="Run vbpl.vn ingestion pipeline")
    parser.add_argument(
        "--limit",
        type=int,
        default=500,
        help="Max documents to fetch per run (default: 500)",
    )
    parser.add_argument(
        "--output-dir", default="scripts/ingest/output", help="Output directory"
    )
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    steps = [
        ("Fetch sitemap", "fetch_sitemap.py", []),
        (
            "Fetch documents",
            "fetch_documents.py",
            ["--limit", str(args.limit), "--output-dir", str(output_dir)],
        ),
        ("Build records", "build_records.py", ["--output-dir", str(output_dir)]),
    ]

    for name, script, extra_args in steps:
        if not run_step(name, script, extra_args):
            print(f"\nPipeline stopped at: {name}")
            raise SystemExit(1)

    # Final stats
    records_path = output_dir / "legal_documents.json"
    if records_path.exists():
        import json

        records = json.loads(records_path.read_text(encoding="utf-8"))
        print(f"\n{'=' * 60}")
        print(f"  PIPELINE COMPLETE — {len(records)} legal documents")
        print(f"{'=' * 60}")


if __name__ == "__main__":
    main()
