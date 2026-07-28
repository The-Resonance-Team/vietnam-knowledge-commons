"""Viet Nam Knowledge Commons — Python SDK.

Two independent surfaces:
  - registry.py: thin adapter over the JSON Schemas in /schemas (the single
    source of truth, ADR-0002) and registry/sources.yaml. No network.
  - api.py: HTTP client for a running apps/api instance. Mirrors its REST
    routes; does not touch /schemas directly.
"""

from vnkc.api import DEFAULT_BASE_URL, VnkcApiError, VnkcClient
from vnkc.registry import (
    SCHEMA_KINDS,
    load_registry,
    summarize_registry,
    validate_record,
    validate_registry,
)

__all__ = [
    "DEFAULT_BASE_URL",
    "SCHEMA_KINDS",
    "VnkcApiError",
    "VnkcClient",
    "load_registry",
    "summarize_registry",
    "validate_record",
    "validate_registry",
]
