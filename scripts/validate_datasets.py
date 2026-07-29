"""Validate all JSON datasets against their schemas."""

import json
import sys
from pathlib import Path

import jsonschema

ROOT = Path(__file__).resolve().parents[1]
SCHEMAS = ROOT / "schemas"
DATASETS = ROOT / "datasets"

errors: list[str] = []

for json_file in sorted(DATASETS.rglob("*.json")):
    rel = json_file.relative_to(ROOT)
    try:
        data = json.loads(json_file.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        errors.append(f"{rel}: invalid JSON — {exc}")
        continue

    # Try to match by filename to a schema
    schema_name = json_file.stem + ".schema.json"
    schema_path = SCHEMAS / schema_name
    if not schema_path.exists():
        # Check if parent dir name matches a schema
        schema_name = json_file.parent.name + ".schema.json"
        schema_path = SCHEMAS / schema_name
    if not schema_path.exists():
        continue  # no matching schema, skip

    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    try:
        jsonschema.validate(data, schema)
    except jsonschema.ValidationError as exc:
        errors.append(f"{rel}: {exc.message}")

if errors:
    print(f"FAILED — {len(errors)} dataset validation error(s):")
    for e in errors:
        print(f"  ✗ {e}")
    sys.exit(1)

print("OK — all datasets valid against matching schemas.")
