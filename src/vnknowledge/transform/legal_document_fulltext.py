"""Build LegalDocumentFulltext records (schemas/legal-document-fulltext.schema.json)
from raw vbpl.vn fetch payloads (see sources/vbpl/fetch_documents.py)."""

from typing import Any

from vnknowledge.sources.vbpl.parser import extract_body, extract_subject
from vnknowledge.validate.schemas import validate_record


def build_fulltext_record(
    raw: dict[str, Any], *, source_id: str = "moj-vbpl"
) -> dict[str, Any] | None:
    """`raw` is one payload as saved by fetch_documents.run.

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
            "license_status": "verified-open",
            "confidence": "unverified",
            "content_checksum": raw["content_checksum"],
        },
    }

    subject = extract_subject(raw["page_html"])
    if subject:
        record["subject"] = subject

    validate_record(record, "legal-document-fulltext.schema.json")
    return record
