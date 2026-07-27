"""Viet Nam Knowledge Commons — Python SDK.

Thin adapter over the JSON Schemas in /schemas, which are the single
source of truth. Mirrors the TypeScript @vnkc/sdk package.
"""

from vnkc.registry import (
    SCHEMA_KINDS,
    load_registry,
    summarize_registry,
    validate_record,
    validate_registry,
)

__all__ = [
    "SCHEMA_KINDS",
    "load_registry",
    "summarize_registry",
    "validate_record",
    "validate_registry",
]
