"""Seam: vnknowledge.search.fts5 build_index/search — SQLite FTS5 over
title+subject+body, diacritics-insensitive (unicode61 remove_diacritics=2)."""

from vnknowledge.search.fts5 import build_index, search

RECORDS = [
    {
        "canonical_id": "vnkc:legal-doc:100024",
        "title": "Thông tư 02/2016/TT-BCT của Bộ Công thương",
        "subject": "Thông tư số 02/2016/TT-BCT quy định về nguyên tắc điều hành hạn ngạch nhập"
        " khẩu muối",
        "body": "Bộ Công Thương ban hành Thông tư quy định về nguyên tắc điều hành nhập khẩu"
        " muối.",
    },
    {
        "canonical_id": "vnkc:legal-doc:100186",
        "title": "Nghị định 20/2016/NĐ-CP",
        "subject": "Nghị định số 20/2016/NĐ-CP Quy định Cơ sở dữ liệu quốc gia về xử lý vi phạm"
        " hành chính",
        "body": "Chính phủ quy định về cơ sở dữ liệu quốc gia về xử lý vi phạm hành chính.",
    },
]


def test_search_matches_diacritics_free_query():
    conn = build_index(RECORDS)

    results = search(conn, "thong tu")

    assert [r["canonical_id"] for r in results] == ["vnkc:legal-doc:100024"]


def test_search_matches_query_with_diacritics():
    conn = build_index(RECORDS)

    results = search(conn, "vi phạm hành chính")

    assert [r["canonical_id"] for r in results] == ["vnkc:legal-doc:100186"]


def test_search_respects_limit():
    conn = build_index(RECORDS)

    results = search(conn, "quy định", limit=1)

    assert len(results) == 1


def test_search_handles_special_characters_without_raising():
    conn = build_index(RECORDS)

    results = search(conn, 'muối" OR 1=1 --')

    assert isinstance(results, list)
