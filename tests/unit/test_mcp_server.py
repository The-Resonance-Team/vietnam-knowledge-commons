"""Seam: vnknowledge.mcp.server.build_server — joins corpus metadata with
fulltext records and registers a working search_legal_docs tool."""

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
    fulltext_path = tmp_path / "legal-corpus-fulltext.json"
    corpus_path.write_text(json.dumps(CORPUS, ensure_ascii=False), encoding="utf-8")
    fulltext_path.write_text(json.dumps(FULLTEXT, ensure_ascii=False), encoding="utf-8")
    return corpus_path, fulltext_path


def test_search_tool_joins_title_with_body_and_subject(tmp_path):
    corpus_path, fulltext_path = _write_release(tmp_path)

    server = build_server(corpus_path, fulltext_path)

    tools = asyncio.run(server.list_tools())
    assert any(t.name == "search_legal_docs" for t in tools)

    result = asyncio.run(server.call_tool("search_legal_docs", {"query": "nhập khẩu muối"}))
    payload = result.structured_content["result"]
    assert payload[0]["canonical_id"] == "vnkc:legal-doc:100024"
    assert payload[0]["title"] == "Thông tư 02/2016/TT-BCT của Bộ Công thương"


def test_build_server_with_no_fulltext_release_yet(tmp_path):
    corpus_path = tmp_path / "legal-corpus.json"
    corpus_path.write_text(json.dumps(CORPUS, ensure_ascii=False), encoding="utf-8")
    missing_fulltext_path = tmp_path / "legal-corpus-fulltext.json"

    server = build_server(corpus_path, missing_fulltext_path)

    result = asyncio.run(server.call_tool("search_legal_docs", {"query": "muối"}))
    assert result.structured_content["result"] == []
