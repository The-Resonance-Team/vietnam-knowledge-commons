"""MCP server exposing legal-document full-text search to AI agents.

Wired into the CLI as `vnkc mcp serve` -- a subcommand of the vnknowledge SDK,
not a standalone service (no new deployable unit; ADR-0001 keeps this a
monorepo until a split trigger fires). Builds a SQLite FTS5 index from the
published legal-corpus + legal-corpus-fulltext release artifacts and exposes
one tool, search_legal_docs, over stdio.
"""

import json
from pathlib import Path
from typing import Any

from mcp.server.mcpserver import MCPServer

from vnknowledge.search.fts5 import build_index
from vnknowledge.search.fts5 import search as fts5_search

DEFAULT_CORPUS = Path("datasets/legal-corpus/releases/v0.1.0/legal-corpus.json")
DEFAULT_FULLTEXT = Path("datasets/legal-corpus/releases/v0.2.0/legal-corpus-fulltext.json")


def load_records(corpus_path: Path, fulltext_path: Path) -> list[dict[str, Any]]:
    """Join metadata (title) with fulltext (subject, body) records by canonical_id.

    Only documents that have a fulltext record are indexed -- title-only
    metadata isn't useful for full-text search.
    """
    corpus = {r["canonical_id"]: r for r in json.loads(corpus_path.read_text(encoding="utf-8"))}
    fulltext = (
        json.loads(fulltext_path.read_text(encoding="utf-8")) if fulltext_path.exists() else []
    )

    records = []
    for record in fulltext:
        meta = corpus.get(record["canonical_id"], {})
        records.append(
            {
                "canonical_id": record["canonical_id"],
                "title": meta.get("title", ""),
                "subject": record.get("subject") or meta.get("subject_slug", ""),
                "body": record["body"],
                "document_number": meta.get("document_number", ""),
                "issuing_authority_code": meta.get("issuing_authority_code", ""),
            }
        )
    return records


def build_server(
    corpus_path: Path = DEFAULT_CORPUS, fulltext_path: Path = DEFAULT_FULLTEXT
) -> MCPServer:
    server = MCPServer(name="vnkc", title="Vietnam Knowledge Commons legal document search")
    index = build_index(load_records(corpus_path, fulltext_path))

    @server.tool()
    def search_legal_docs(query: str, limit: int = 10) -> list[dict[str, Any]]:
        """Search Vietnamese legal documents by title, subject, and body text."""
        return fts5_search(index, query, limit)

    return server


def serve(corpus_path: Path = DEFAULT_CORPUS, fulltext_path: Path = DEFAULT_FULLTEXT) -> None:
    build_server(corpus_path, fulltext_path).run()
