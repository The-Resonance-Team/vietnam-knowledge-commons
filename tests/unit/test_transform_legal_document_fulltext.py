"""Seam: vnknowledge.transform.legal_document_fulltext.build_fulltext_record —
pure merge of a raw fetch payload into a schema-conformant fulltext record."""

from vnknowledge.transform.legal_document_fulltext import build_fulltext_record

RAW = {
    "canonical_id": "vnkc:legal-doc:100024",
    "official_url": "https://vbpl.vn/van-ban/chi-tiet/example--100024",
    "retrieved_at": "2026-07-29T00:00:00+00:00",
    "body_rsc": (
        '0:["$@1",["x",null]]\n'
        "2:T29,<p>Nội dung thông tư về muối.</p>"
        '1:{"id":"100024","title":"Thông tư số 02/2016/TT-BCT quy định về muối","docAbs":null}'
    ),
    "content_checksum": "sha256:" + "0" * 64,
}


def test_builds_valid_record_with_body_and_subject():
    record = build_fulltext_record(RAW)

    assert record is not None
    assert record["canonical_id"] == "vnkc:legal-doc:100024"
    assert "Nội dung thông tư về muối" in record["body"]
    assert record["subject"] == "Thông tư số 02/2016/TT-BCT quy định về muối"
    assert record["provenance"]["source_url"] == RAW["official_url"]
    assert record["provenance"]["content_checksum"] == RAW["content_checksum"]
    assert record["provenance"]["license_status"] == "verified-open"
    assert record["provenance"]["attribution"]


def test_returns_none_when_no_body_extractable():
    raw = {**RAW, "body_rsc": "0:[]\n"}

    assert build_fulltext_record(raw) is None


def test_omits_subject_when_not_extractable():
    raw = {**RAW, "body_rsc": '0:["$@1",["x",null]]\n2:T29,<p>Nội dung thông tư về muối.</p>'}

    record = build_fulltext_record(raw)

    assert record is not None
    assert "subject" not in record


def test_caller_can_override_source_id_and_license_status():
    raw = {**RAW, "canonical_id": "vnkc:legal-doc:other"}

    record = build_fulltext_record(
        raw, source_id="other-source", license_status="reference-only", attribution="Other Org"
    )

    assert record is not None
    assert record["provenance"]["source_id"] == "other-source"
    assert record["provenance"]["license_status"] == "reference-only"
    assert record["provenance"]["attribution"] == "Other Org"
