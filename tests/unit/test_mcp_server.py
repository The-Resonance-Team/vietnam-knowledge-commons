"""Seam: vnknowledge.mcp.server.build_server — joins corpus metadata with
sharded fulltext records and registers a working search_legal_docs tool."""

import asyncio
import json
from pathlib import Path

from vnknowledge.mcp.server import build_server

CORPUS = [
    {
        "canonical_id": "vnkc:legal-doc:100024",
        "title": "Thông tư 02/2016/TT-BCT của Bộ Công thương",
    },
]
FULLTEXT = [
    {
        "canonical_id": "vnkc:legal-doc:100024",
        "body": "Bộ Công Thương ban hành Thông tư quy định về nguyên tắc điều hành nhập khẩu muối.",
        "subject": "Thông tư số 02/2016/TT-BCT quy định về nguyên tắc điều hành nhập khẩu muối",
        "version": 1,
        "provenance": {},
    },
]


def _write_release(tmp_path: Path) -> tuple[Path, Path]:
    corpus_path = tmp_path / "legal-corpus.json"
    fulltext_dir = tmp_path / "legal-corpus-fulltext"
    fulltext_dir.mkdir()
    corpus_path.write_text(json.dumps(CORPUS, ensure_ascii=False), encoding="utf-8")
    (fulltext_dir / "shard-000.json").write_text(
        json.dumps(FULLTEXT, ensure_ascii=False), encoding="utf-8"
    )
    return corpus_path, fulltext_dir


def test_search_tool_joins_title_with_body_and_subject(tmp_path):
    corpus_path, fulltext_dir = _write_release(tmp_path)

    server = build_server(corpus_path, fulltext_dir)

    tools = asyncio.run(server.list_tools())
    assert any(t.name == "search_legal_docs" for t in tools)

    result = asyncio.run(server.call_tool("search_legal_docs", {"query": "nhập khẩu muối"}))
    payload = result.structured_content["result"]
    assert payload[0]["canonical_id"] == "vnkc:legal-doc:100024"
    assert payload[0]["title"] == "Thông tư 02/2016/TT-BCT của Bộ Công thương"


def test_build_server_with_no_fulltext_release_yet(tmp_path):
    corpus_path = tmp_path / "legal-corpus.json"
    corpus_path.write_text(json.dumps(CORPUS, ensure_ascii=False), encoding="utf-8")
    missing_fulltext_dir = tmp_path / "legal-corpus-fulltext"

    server = build_server(corpus_path, missing_fulltext_dir)

    result = asyncio.run(server.call_tool("search_legal_docs", {"query": "muối"}))
    assert result.structured_content["result"] == []


def test_load_records_reads_across_multiple_shards(tmp_path):
    corpus = [
        {"canonical_id": "vnkc:legal-doc:a", "title": "A"},
        {"canonical_id": "vnkc:legal-doc:b", "title": "B"},
    ]
    corpus_path = tmp_path / "legal-corpus.json"
    corpus_path.write_text(json.dumps(corpus, ensure_ascii=False), encoding="utf-8")
    fulltext_dir = tmp_path / "legal-corpus-fulltext"
    fulltext_dir.mkdir()
    (fulltext_dir / "shard-000.json").write_text(
        json.dumps(
            [
                {
                    "canonical_id": "vnkc:legal-doc:a",
                    "body": "text a",
                    "version": 1,
                    "provenance": {},
                }
            ],
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    (fulltext_dir / "shard-001.json").write_text(
        json.dumps(
            [
                {
                    "canonical_id": "vnkc:legal-doc:b",
                    "body": "text b",
                    "version": 1,
                    "provenance": {},
                }
            ],
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    server = build_server(corpus_path, fulltext_dir)

    result = asyncio.run(server.call_tool("search_legal_docs", {"query": "text"}))
    ids = {r["canonical_id"] for r in result.structured_content["result"]}
    assert ids == {"vnkc:legal-doc:a", "vnkc:legal-doc:b"}


def test_search_matches_document_number_and_falls_back_to_subject_slug(tmp_path):
    corpus = [
        {
            "canonical_id": "vnkc:legal-doc:100024",
            "title": "Thông tư 02/2016/TT-BCT của Bộ Công thương",
            "document_number": "02/2016/TT-BCT",
            "issuing_authority_code": "TT-BCT",
            "subject_slug": "thong-tu-so-02-2016-tt-bct-quy-dinh-ve-muoi",
        }
    ]
    fulltext = [
        {
            "canonical_id": "vnkc:legal-doc:100024",
            "body": "Nội dung thông tư về muối.",
            "version": 1,
            "provenance": {},
        }
    ]
    corpus_path = tmp_path / "legal-corpus.json"
    fulltext_dir = tmp_path / "legal-corpus-fulltext"
    fulltext_dir.mkdir()
    corpus_path.write_text(json.dumps(corpus, ensure_ascii=False), encoding="utf-8")
    (fulltext_dir / "shard-000.json").write_text(
        json.dumps(fulltext, ensure_ascii=False), encoding="utf-8"
    )

    server = build_server(corpus_path, fulltext_dir)

    result = asyncio.run(server.call_tool("search_legal_docs", {"query": "02/2016/TT-BCT"}))
    payload = result.structured_content["result"]
    assert payload[0]["canonical_id"] == "vnkc:legal-doc:100024"
    assert payload[0]["subject"] == "thong-tu-so-02-2016-tt-bct-quy-dinh-ve-muoi"
