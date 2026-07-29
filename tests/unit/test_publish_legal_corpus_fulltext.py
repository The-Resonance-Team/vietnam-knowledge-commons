"""Seam: vnknowledge.publish.legal_corpus_fulltext.assemble_fulltext_records —
gathers raw payloads into fulltext records, scoped to the current corpus."""

import json

from vnknowledge.publish.legal_corpus_fulltext import assemble_fulltext_records

RAW_WITH_BODY = {
    "canonical_id": "vnkc:legal-doc:100024",
    "official_url": "https://vbpl.vn/van-ban/chi-tiet/example--100024",
    "retrieved_at": "2026-07-29T00:00:00+00:00",
    "page_html": "<html></html>",
    "body_rsc": '0:["$@1",["x",null]]\n2:Te,<p>muối.</p>',
    "content_checksum": "sha256:" + "0" * 64,
}

RAW_NO_BODY = {**RAW_WITH_BODY, "canonical_id": "vnkc:legal-doc:999999", "body_rsc": "0:[]\n"}

RAW_NOT_IN_CORPUS = {**RAW_WITH_BODY, "canonical_id": "vnkc:legal-doc:not-in-corpus"}


def _write(raw_dir, name, raw):
    (raw_dir / name).write_text(json.dumps(raw, ensure_ascii=False), encoding="utf-8")


def test_includes_only_corpus_records_with_extractable_body(tmp_path):
    raw_dir = tmp_path / "raw"
    raw_dir.mkdir()
    _write(raw_dir, "100024.json", RAW_WITH_BODY)
    _write(raw_dir, "999999.json", RAW_NO_BODY)
    _write(raw_dir, "stray.json", RAW_NOT_IN_CORPUS)

    records = assemble_fulltext_records(
        raw_dir, canonical_ids={"vnkc:legal-doc:100024", "vnkc:legal-doc:999999"}
    )

    assert [r["canonical_id"] for r in records] == ["vnkc:legal-doc:100024"]


def test_empty_raw_dir_yields_no_records(tmp_path):
    raw_dir = tmp_path / "raw"
    raw_dir.mkdir()

    assert assemble_fulltext_records(raw_dir, canonical_ids=set()) == []
