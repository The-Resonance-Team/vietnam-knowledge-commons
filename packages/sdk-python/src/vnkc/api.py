"""Client for the VNKC API (apps/api) — a thin wrapper over its REST routes.

Distinct from registry.py: that module reads /schemas and registry/sources.yaml
directly off disk, with no server involved. This module calls a *running*
apps/api instance over HTTP. Endpoint shapes here must track
apps/api/src/**/*.controller.ts; there is no generated client, so a route
change there means an update here.
"""

from __future__ import annotations

import json
from typing import Any

import httpx

DEFAULT_BASE_URL = "http://localhost:3100/v1"


class VnkcApiError(RuntimeError):
    """Raised when the API responds with an error status or an MCP call fails."""


class VnkcClient:
    """Sync client for the VNKC API.

    Example:
        with VnkcClient() as client:
            page = client.list_legal_docs(limit=20)
            doc = client.get_legal_doc(page[0]["id"])
    """

    def __init__(
        self,
        base_url: str = DEFAULT_BASE_URL,
        *,
        timeout: float = 30.0,
        transport: httpx.BaseTransport | None = None,
    ) -> None:
        # transport is test-only: injects an httpx.MockTransport so
        # tests/test_api.py doesn't need a running apps/api instance.
        self._http = httpx.Client(base_url=base_url, timeout=timeout, transport=transport)

    def __enter__(self) -> VnkcClient:
        return self

    def __exit__(self, *exc: object) -> None:
        self.close()

    def close(self) -> None:
        self._http.close()

    def _get(self, path: str, **params: Any) -> Any:
        params = {k: v for k, v in params.items() if v is not None}
        resp = self._http.get(path, params=params)
        resp.raise_for_status()
        return resp.json()

    # ---- Legal documents ---------------------------------------------

    def list_legal_docs(self, limit: int = 100, offset: int = 0) -> list[dict[str, Any]]:
        """GET /legal-docs — most recent issue_date first."""
        return self._get("/legal-docs", limit=limit, offset=offset)

    def search_legal_docs(self, query: str, limit: int = 50) -> list[dict[str, Any]]:
        """GET /legal-docs/search — SQL LIKE over title/document_number/full_text.

        Not full-text search: this corpus has no document body (ADR-0004), and
        `title` is a citation, not a subject — see CONTEXT.md. Matches are
        limited to what's literally in the citation or number.
        """
        return self._get("/legal-docs/search", q=query, limit=limit)

    def get_legal_doc(self, doc_id: str) -> dict[str, Any]:
        """GET /legal-docs/:id. `doc_id` is the DB row id (uuid), not canonical_id."""
        return self._get(f"/legal-docs/{doc_id}")

    # ---- Administrative units ------------------------------------------

    def list_admin_units(self, limit: int = 100, offset: int = 0) -> list[dict[str, Any]]:
        """GET /admin-units."""
        return self._get("/admin-units", limit=limit, offset=offset)

    def current_admin_units(self) -> list[dict[str, Any]]:
        """GET /admin-units/current — units with valid_to null or in the future."""
        return self._get("/admin-units/current")

    def get_admin_unit(self, unit_id: str) -> dict[str, Any]:
        """GET /admin-units/:id."""
        return self._get(f"/admin-units/{unit_id}")

    def get_admin_unit_by_code(self, code: str) -> dict[str, Any]:
        """GET /admin-units/code/:code — GSO statistical code."""
        return self._get(f"/admin-units/code/{code}")

    # ---- MCP -------------------------------------------------------------

    def list_mcp_tools(self) -> list[dict[str, Any]]:
        """GET /mcp/tools."""
        return self._get("/mcp/tools")["tools"]

    def call_mcp_tool(self, name: str, arguments: dict[str, Any] | None = None) -> Any:
        """POST /mcp/call. The route replies over SSE regardless of client,
        so this parses the single `data:` event out of the stream body.
        """
        resp = self._http.post("/mcp/call", json={"name": name, "arguments": arguments or {}})
        resp.raise_for_status()
        event = _parse_sse_data(resp.text)
        if event.get("type") == "error":
            raise VnkcApiError(f"MCP tool {name!r} failed: {event.get('message')}")
        return event.get("data")


def _parse_sse_data(body: str) -> dict[str, Any]:
    for line in body.splitlines():
        if line.startswith("data:"):
            return json.loads(line[len("data:") :].strip())
    raise VnkcApiError(f"no SSE data event in response: {body!r}")


def demo() -> None:
    """Self-check against a real base URL; skips cleanly if nothing is listening.

    Run the API first: `cd apps/api && pnpm dev`.
    """
    try:
        probe = httpx.get(f"{DEFAULT_BASE_URL}/mcp/tools", timeout=2.0)
    except httpx.ConnectError:
        print("demo: skipped (no API listening at", DEFAULT_BASE_URL, ")")
        return
    assert probe.status_code == 200

    with VnkcClient() as client:
        tools = client.list_mcp_tools()
        assert isinstance(tools, list) and tools
        docs = client.list_legal_docs(limit=5)
        assert isinstance(docs, list)
        if docs:
            fetched = client.get_legal_doc(docs[0]["id"])
            assert fetched["id"] == docs[0]["id"]
    print("demo: ok")


if __name__ == "__main__":
    demo()
