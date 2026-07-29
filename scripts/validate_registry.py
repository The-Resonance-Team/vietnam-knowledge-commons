"""Validate registry YAML files against their schemas."""

import json
import sys
from pathlib import Path

import jsonschema
import yaml

ROOT = Path(__file__).resolve().parents[1]
SCHEMAS = ROOT / "schemas"
REGISTRY = ROOT / "registry"

errors: list[str] = []

for yaml_file in sorted(REGISTRY.glob("*.yaml")):
    rel = yaml_file.relative_to(ROOT)
    try:
        data = yaml.safe_load(yaml_file.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        errors.append(f"{rel}: invalid YAML — {exc}")
        continue

    schema_name = yaml_file.stem + ".schema.json"
    schema_path = SCHEMAS / schema_name
    if not schema_path.exists():
        continue  # no matching schema, skip

    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    try:
        jsonschema.validate(data, schema)
    except jsonschema.ValidationError as exc:
        errors.append(f"{rel}: {exc.message}")

if errors:
    print(f"FAILED — {len(errors)} registry validation error(s):")
    for e in errors:
        print(f"  ✗ {e}")
    sys.exit(1)

print(f"OK — all registry files valid against matching schemas.")
