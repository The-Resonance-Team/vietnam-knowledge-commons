"""Validate records against the JSON Schemas in schemas/ (source of truth per ADR-0002)."""

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

import jsonschema
from referencing import Registry, Resource
from referencing.jsonschema import DRAFT202012

SCHEMAS_DIR = Path(__file__).resolve().parents[3] / "schemas"


@lru_cache
def load_schema(name: str) -> dict[str, Any]:
    schema: dict[str, Any] = json.loads((SCHEMAS_DIR / name).read_text(encoding="utf-8"))
    return schema


def _retrieve(uri: str) -> Resource[Any]:
    return Resource.from_contents(load_schema(uri), default_specification=DRAFT202012)


# `retrieve` is an attrs field alias; mypy's attrs support doesn't resolve it
# to a __init__ kwarg here even though it's the documented, working API.
_REGISTRY: Registry[Any] = Registry(retrieve=_retrieve)  # type: ignore[call-arg]


def validate_record(record: dict[str, Any], schema_name: str) -> None:
    """Raise jsonschema.ValidationError if record doesn't conform to schemas/<schema_name>."""
    schema = load_schema(schema_name)
    validator_cls = jsonschema.validators.validator_for(schema)
    validator_cls(schema, registry=_REGISTRY).validate(record)
