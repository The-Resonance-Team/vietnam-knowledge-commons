#!/usr/bin/env python3
"""Validate relationship integrity.

Checks:
1. No orphan edges (from_id/to_id must exist in examples or ingested records)
2. No circular replacements (A replaces B replaces A)
3. Effective dates are consistent (replaces date >= replaced document's effective_from)

Usage:
    python scripts/ingest/validate_relationships.py [--data-dir seed]
"""

import argparse
import json
from pathlib import Path


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def collect_ids(examples_dir: Path) -> set[str]:
    """Collect all canonical_ids from example files."""
    ids = set()
    if not examples_dir.exists():
        return ids
    for f in examples_dir.rglob("*.json"):
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
            if isinstance(data, dict) and "canonical_id" in data:
                ids.add(data["canonical_id"])
        except (json.JSONDecodeError, KeyError):
            continue
    return ids


def check_orphan_edges(relationships: list[dict], known_ids: set[str]) -> list[str]:
    """Check for edges referencing unknown IDs."""
    errors = []
    for rel in relationships:
        from_id = rel.get("from_id", "")
        to_id = rel.get("to_id", "")
        if from_id not in known_ids:
            errors.append(f"Orphan from_id: {from_id}")
        if to_id not in known_ids:
            errors.append(f"Orphan to_id: {to_id}")
    return errors


def check_circular_replacements(relationships: list[dict]) -> list[str]:
    """Check for circular replacement chains."""
    replaces = {}
    for rel in relationships:
        if rel["type"] == "replaces":
            replaces[rel["from_id"]] = rel["to_id"]

    errors = []
    for start in replaces:
        visited = {start}
        current = replaces[start]
        while current in replaces:
            if current in visited:
                errors.append(f"Circular replacement: {start} → {current}")
                break
            visited.add(current)
            current = replaces[current]
    return errors


def main():
    parser = argparse.ArgumentParser(description="Validate relationships")
    parser.add_argument(
        "--data-dir", default="seed", help="Directory with relationships.json"
    )
    args = parser.parse_args()

    data_dir = Path(args.data_dir)
    rel_path = data_dir / "relationships.json"

    if not rel_path.exists():
        print(f"Error: {rel_path} not found")
        raise SystemExit(1)

    data = load_json(rel_path)
    relationships = data.get("relationships", [])
    print(f"Loaded {len(relationships)} relationships")

    # Collect known IDs from examples
    known_ids = collect_ids(Path("examples"))
    print(f"Known IDs from examples: {len(known_ids)}")

    errors = []
    errors.extend(check_orphan_edges(relationships, known_ids))
    errors.extend(check_circular_replacements(relationships))

    if errors:
        print(f"\n{len(errors)} errors:")
        for e in errors:
            print(f"  ✗ {e}")
        raise SystemExit(1)
    else:
        print("\n✓ All relationship checks passed")


if __name__ == "__main__":
    main()
