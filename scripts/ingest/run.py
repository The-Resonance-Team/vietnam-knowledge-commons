#!/usr/bin/env python3
"""Orchestrate the vbpl.vn ingestion pipeline.

Runs all steps in sequence: sitemap → documents → build records.
Resumable: skips steps whose output already exists.

Usage:
    python scripts/ingest/run.py [--force] [--limit 50] [--output-dir scripts/ingest/output]
"""

import argparse
import subprocess
import sys
from pathlib import Path


def run_step(
    name: str, script: str, args: list[str], output_file: Path, force: bool
) -> bool:
    """Run a pipeline step, skip if output exists (unless force)."""
    if output_file.exists() and not force:
        print(f"✓ {name} — output exists, skipping")
        return True

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
        "--force", action="store_true", help="Re-run all steps even if output exists"
    )
    parser.add_argument(
        "--limit", type=int, default=50, help="Max documents to fetch (default: 50)"
    )
    parser.add_argument(
        "--output-dir", default="scripts/ingest/output", help="Output directory"
    )
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    steps = [
        ("Fetch sitemap", "fetch_sitemap.py", [], output_dir / "sitemap_index.json"),
        (
            "Fetch documents",
            "fetch_documents.py",
            ["--limit", str(args.limit)],
            output_dir / "source_records.json",
        ),
        ("Build records", "build_records.py", [], output_dir / "legal_documents.json"),
    ]

    for name, script, extra_args, output_file in steps:
        if not run_step(name, script, extra_args, output_file, args.force):
            print(f"\nPipeline stopped at: {name}")
            raise SystemExit(1)

    print(f"\n{'=' * 60}")
    print("  PIPELINE COMPLETE")
    print(f"{'=' * 60}")
    print(f"Output directory: {output_dir}")
    print("Files:")
    for f in sorted(output_dir.iterdir()):
        print(f"  {f.name} ({f.stat().st_size:,} bytes)")


if __name__ == "__main__":
    main()
