"""Build LegalDocumentFulltext records (schemas/legal-document-fulltext.schema.json)
from raw vbpl.vn fetch payloads (see sources/vbpl/fetch_documents.py)."""

from typing import Any

from vnknowledge.sources.vbpl.parser import extract_body, extract_subject
from vnknowledge.validate.schemas import validate_record


def build_fulltext_record(
    raw: dict[str, Any],
    *,
    source_id: str = "moj-vbpl",
    license_status: str = "verified-open",
    attribution: str = "Bộ Tư pháp nước CHXHCN Việt Nam — vbpl.vn",
) -> dict[str, Any] | None:
    """`raw` is one payload as saved by fetch_documents.run.

    `license_status`/`attribution` default to moj-vbpl's per ADR-0005; a
    caller publishing a different source must pass its own -- each source's
    license_status is decided on its own facts (ADR-0003), never inherited.

    Returns None if no body could be extracted — an unparseable page isn't a
    schema violation, it's simply not ready to publish yet.
    """
    body = extract_body(raw["body_rsc"])
    if not body:
        return None

    record: dict[str, Any] = {
        "canonical_id": raw["canonical_id"],
        "body": body,
        "version": 1,
        "provenance": {
            "source_id": source_id,
            "source_url": raw["official_url"],
            "retrieved_at": raw["retrieved_at"],
            "retrieval_method": "html",
            "license_status": license_status,
            "attribution": attribution,
            "confidence": "unverified",
            "content_checksum": raw["content_checksum"],
        },
    }

    subject = extract_subject(raw["body_rsc"])
    if subject:
        record["subject"] = subject

    validate_record(record, "legal-document-fulltext.schema.json")
    return record
