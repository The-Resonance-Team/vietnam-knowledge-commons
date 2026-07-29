"""Seam: vnknowledge.validate.schemas.validate_record against
legal-document-fulltext.schema.json (canonical shape + provenance $ref resolution)."""

import jsonschema
import pytest

from vnknowledge.validate.schemas import validate_record

VALID_RECORD = {
    "canonical_id": "vnkc:legal-doc:100024",
    "body": "BỘ CÔNG THƯƠNG ...",
    "version": 1,
    "provenance": {
        "source_id": "moj-vbpl",
        "source_url": "https://vbpl.vn/van-ban/chi-tiet/example--100024",
        "retrieved_at": "2026-07-29T00:00:00+00:00",
        "retrieval_method": "html",
        "license_status": "verified-open",
        "confidence": "unverified",
        "content_checksum": "sha256:" + "0" * 64,
    },
}


def test_valid_fulltext_record_passes():
    validate_record(VALID_RECORD, "legal-document-fulltext.schema.json")


def test_record_without_body_is_rejected():
    record = {k: v for k, v in VALID_RECORD.items() if k != "body"}
    with pytest.raises(jsonschema.ValidationError):
        validate_record(record, "legal-document-fulltext.schema.json")


def test_unknown_additional_field_is_rejected():
    record = {**VALID_RECORD, "summary": "not allowed"}
    with pytest.raises(jsonschema.ValidationError):
        validate_record(record, "legal-document-fulltext.schema.json")
