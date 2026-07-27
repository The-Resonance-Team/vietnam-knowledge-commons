"""Registry and record validation against the VNKC JSON Schemas."""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any

import yaml
from jsonschema import Draft202012Validator
from referencing import Registry, Resource
from referencing.jsonschema import DRAFT202012

# ponytail: resolves /schemas relative to repo root — monorepo-local, same
# tradeoff as the TS SDK; bundling is a publish-time concern (ADR-0002).
REPO_ROOT = Path(__file__).resolve().parents[4]
SCHEMAS_DIR = REPO_ROOT / "schemas"

SCHEMA_KINDS = (
    "source",
    "source-registry",
    "legal-document",
    "administrative-procedure",
    "official-form",
    "organization",
    "jurisdiction",
    "relationship",
    "dataset-release",
    "provenance",
)


def _load_schemas() -> dict[str, dict[str, Any]]:
    return {
        p.name.removesuffix(".schema.json"): json.loads(p.read_text(encoding="utf-8"))
        for p in SCHEMAS_DIR.glob("*.schema.json")
    }


def _registry_store() -> Registry:
    resources = [
        (f"{kind}.schema.json", Resource(contents=schema, specification=DRAFT202012))
        for kind, schema in _load_schemas().items()
    ]
    return Registry().with_resources(resources)


def validate_record(kind: str, data: Any) -> list[str]:
    """Validate one record against schemas/<kind>.schema.json. Returns error strings."""
    schemas = _load_schemas()
    schema = schemas.get(kind)
    if schema is None:
        return [f"unknown schema kind: {kind}"]
    validator = Draft202012Validator(schema, registry=_registry_store())
    return [
        f"{'/'.join(map(str, e.absolute_path)) or '(root)'}: {e.message}"
        for e in validator.iter_errors(data)
    ]


def validate_registry(raw: Any) -> list[str]:
    """Schema validation plus cross-entry checks the schema cannot express."""
    errors = validate_record("source-registry", raw)
    if errors:
        return errors
    seen: Counter[str] = Counter()
    for i, source in enumerate(raw["sources"]):
        seen[source["id"]] += 1
        if seen[source["id"]] > 1:
            errors.append(f"sources[{i}]: duplicate id '{source['id']}'")
        if source["tier"] == "D" and source["license_status"] == "verified-open":
            errors.append(
                f"sources[{i}] ({source['id']}): Tier D discovery sources must not be "
                "marked verified-open — they are never ground truth"
            )
        if (
            source.get("robots_txt", {}).get("reviewed") is False
            and source["confidence"] == "verified"
        ):
            errors.append(
                f"sources[{i}] ({source['id']}): confidence 'verified' requires "
                "robots_txt.reviewed: true"
            )
    return errors


class _StringDatesLoader(yaml.SafeLoader):
    """SafeLoader minus timestamp implicit resolution.

    Registry dates (last_verified, generated) must stay strings — the JSON
    Schemas declare them format: date strings, and the TS yaml lib already
    leaves them alone. Without this, PyYAML turns 2026-07-27 into
    datetime.date and schema validation fails spuriously.
    """


for _key, _resolvers in list(_StringDatesLoader.yaml_implicit_resolvers.items()):
    _StringDatesLoader.yaml_implicit_resolvers[_key] = [
        (tag, regexp) for tag, regexp in _resolvers if tag != "tag:yaml.org,2002:timestamp"
    ]


def load_registry(path: str | Path) -> tuple[dict[str, Any], list[str]]:
    """Load registry/sources.yaml. Returns (registry, errors)."""
    raw = yaml.load(Path(path).read_text(encoding="utf-8"), Loader=_StringDatesLoader)
    return raw, validate_registry(raw)


def summarize_registry(registry: dict[str, Any]) -> dict[str, Any]:
    """Counts by tier, license status, and confidence — same shape as the TS SDK."""
    sources = registry["sources"]
    return {
        "total": len(sources),
        "by_tier": dict(Counter(s["tier"] for s in sources)),
        "by_license": dict(Counter(s["license_status"] for s in sources)),
        "by_confidence": dict(Counter(s["confidence"] for s in sources)),
        "tier_a": [s["id"] for s in sources if s["tier"] == "A"],
        "needs_review": [
            s["id"]
            for s in sources
            if s["license_status"] == "unknown" or s["confidence"] == "unverified"
        ],
    }
