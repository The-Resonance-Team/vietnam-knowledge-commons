"""Tests for vnkc.api — through the public interface, against a mock transport.

No live apps/api instance required: httpx.MockTransport stands in for the
server so route/query construction and SSE parsing are checked deterministically.
"""

import httpx
import pytest

from vnkc import VnkcApiError, VnkcClient

BASE = "http://test/v1"


def _client(handler) -> VnkcClient:
    return VnkcClient(base_url=BASE, transport=httpx.MockTransport(handler))


def test_list_legal_docs_builds_query_and_drops_none():
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/v1/legal-docs"
        assert dict(request.url.params) == {"limit": "5", "offset": "0"}
        return httpx.Response(200, json=[{"id": "1", "title": "Thông tư 1/2026/TT-BYT"}])

    with _client(handler) as c:
        docs = c.list_legal_docs(limit=5)
        assert docs[0]["id"] == "1"


def test_search_legal_docs_passes_query_string():
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/v1/legal-docs/search"
        assert request.url.params["q"] == "y tế"
        return httpx.Response(200, json=[])

    with _client(handler) as c:
        assert c.search_legal_docs("y tế") == []


def test_get_legal_doc_by_id():
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/v1/legal-docs/abc-123"
        return httpx.Response(200, json={"id": "abc-123"})

    with _client(handler) as c:
        assert c.get_legal_doc("abc-123")["id"] == "abc-123"


def test_current_admin_units_and_by_code():
    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/v1/admin-units/current":
            return httpx.Response(200, json=[{"code": "01"}])
        if request.url.path == "/v1/admin-units/code/01":
            return httpx.Response(200, json={"code": "01"})
        raise AssertionError(request.url.path)

    with _client(handler) as c:
        assert c.current_admin_units() == [{"code": "01"}]
        assert c.get_admin_unit_by_code("01")["code"] == "01"


def test_http_error_status_raises():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(500, json={"message": "boom"})

    with _client(handler) as c, pytest.raises(httpx.HTTPStatusError):
        c.list_legal_docs()


def test_mcp_call_parses_sse_result_event():
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/v1/mcp/call"
        assert httpx.Request("POST", "x").method == "POST"
        body = request.read()
        assert b"search_legal_docs" in body
        sse = 'data: {"type": "result", "data": [{"id": "1"}]}\n\n'
        return httpx.Response(200, text=sse, headers={"content-type": "text/event-stream"})

    with _client(handler) as c:
        result = c.call_mcp_tool("search_legal_docs", {"query": "luật"})
        assert result == [{"id": "1"}]


def test_mcp_call_raises_on_sse_error_event():
    def handler(request: httpx.Request) -> httpx.Response:
        sse = 'data: {"type": "error", "message": "Unknown tool: nope"}\n\n'
        return httpx.Response(200, text=sse, headers={"content-type": "text/event-stream"})

    with _client(handler) as c, pytest.raises(VnkcApiError, match="Unknown tool"):
        c.call_mcp_tool("nope")
