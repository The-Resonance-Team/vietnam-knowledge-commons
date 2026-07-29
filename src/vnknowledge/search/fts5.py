"""SQLite FTS5 full-text search over legal documents (title + subject + body).

Vietnamese-aware via the unicode61 tokenizer with remove_diacritics=2, so a
diacritics-free query ("thong tu") matches diacritic text ("Thông tư").
No external service: ships inside the release artifact.
"""

import sqlite3
from pathlib import Path
from typing import Any


def build_index(
    records: list[dict[str, Any]], db_path: str | Path = ":memory:"
) -> sqlite3.Connection:
    """records: {canonical_id, title, subject, body} dicts (subject/body optional).

    ponytail: check_same_thread=False because the MCP server calls tools from a
    worker thread different from the one that builds the index at startup;
    calls are effectively serial here, so this is a single shared connection,
    not a pool. If concurrent MCP requests start overlapping, switch to a
    connection per request (the db is on-disk-shaped already: pass a real
    db_path instead of ":memory:") or add a lock around search().
    """
    conn = sqlite3.connect(db_path, check_same_thread=False)
    conn.execute(
        "CREATE VIRTUAL TABLE IF NOT EXISTS legal_docs USING fts5("
        "canonical_id UNINDEXED, title, subject, body, "
        "tokenize = 'unicode61 remove_diacritics 2')"
    )
    conn.executemany(
        "INSERT INTO legal_docs (canonical_id, title, subject, body) VALUES (?, ?, ?, ?)",
        [
            (r["canonical_id"], r.get("title", ""), r.get("subject", ""), r.get("body", ""))
            for r in records
        ],
    )
    conn.commit()
    return conn


def _as_phrase_query(query: str) -> str:
    """Treat `query` as a literal phrase, not FTS5 boolean-query syntax --
    user-supplied search text shouldn't have to be valid FTS5 syntax."""
    return '"' + query.replace('"', '""') + '"'


def search(conn: sqlite3.Connection, query: str, limit: int = 10) -> list[dict[str, Any]]:
    """FTS5 phrase search over title/subject/body, ranked by bm25."""
    cursor = conn.execute(
        "SELECT canonical_id, title, subject, "
        "snippet(legal_docs, 3, '[', ']', '...', 10) AS body_snippet "
        "FROM legal_docs WHERE legal_docs MATCH ? ORDER BY bm25(legal_docs) LIMIT ?",
        (_as_phrase_query(query), limit),
    )
    columns = [d[0] for d in cursor.description]
    return [dict(zip(columns, row, strict=True)) for row in cursor.fetchall()]
