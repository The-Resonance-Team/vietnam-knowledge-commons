"""Tests for the vnkc Python SDK — through the public interface only."""

import json
from pathlib import Path

import pytest

from vnkc import load_registry, summarize_registry, validate_record

REPO_ROOT = Path(__file__).resolve().parents[3]
REGISTRY = REPO_ROOT / "registry" / "sources.yaml"
EXAMPLES = REPO_ROOT / "examples"


def test_committed_registry_is_valid():
    registry, errors = load_registry(REGISTRY)
    assert errors == []
    assert len(registry["sources"]) >= 30


def test_summary_counts():
    registry, _ = load_registry(REGISTRY)
    summary = summarize_registry(registry)
    assert summary["total"] == len(registry["sources"])
    assert len(summary["tier_a"]) >= 3
    assert summary["by_license"].get("prohibited", 0) == 0


@pytest.mark.parametrize("example", sorted(EXAMPLES.glob("*/*.json")))
def test_committed_examples_validate(example: Path):
    kind = example.parent.name
    data = json.loads(example.read_text(encoding="utf-8"))
    assert validate_record(kind, data) == []


def test_rejects_source_with_uncontrolled_license_status():
    errors = validate_record(
        "source",
        {
            "id": "bad-source",
            "name_vi": "Nguồn xấu",
            "publisher": "X",
            "authority": "X",
            "url": "https://example.vn",
            "tier": "A",
            "domains": ["law"],
            "jurisdiction": "national",
            "access_method": "html",
            "license_status": "public-domain-bro",
            "pii_risk": "none",
            "stability": "high",
            "last_verified": "2026-07-27",
            "confidence": "verified",
        },
    )
    assert any("license_status" in e for e in errors)
