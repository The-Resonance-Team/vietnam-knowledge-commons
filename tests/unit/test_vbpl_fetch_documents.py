"""Seam: vnknowledge.sources.vbpl.fetch_documents.run — rate-limiter timing,
resume/skip logic, and per-record failure isolation, against a mocked HTTP
transport (no real network calls)."""

import json

import httpx
import pytest

from vnknowledge.sources.vbpl.fetch_documents import RATE_LIMIT_DELAY, run

RECORD = {
    "canonical_id": "vnkc:legal-doc:100024",
    "official_url": "https://vbpl.vn/van-ban/chi-tiet/example--100024",
}
OTHER_RECORD = {
    "canonical_id": "vnkc:legal-doc:100186",
    "official_url": "https://vbpl.vn/van-ban/chi-tiet/example--100186",
}


def _client(handler):
    return httpx.Client(transport=httpx.MockTransport(handler))


def test_run_skips_records_already_fetched(tmp_path):
    out_dir = tmp_path / "raw"
    out_dir.mkdir()
    (out_dir / "100024.json").write_text("{}", encoding="utf-8")

    def handler(request: httpx.Request) -> httpx.Response:
        raise AssertionError(f"should not fetch an already-saved record: {request.url}")

    done = run([RECORD], out_dir, _client(handler), sleep=lambda _seconds: None)

    assert done == 0


def test_run_fetches_and_saves_new_record(tmp_path):
    out_dir = tmp_path / "raw"

    def handler(request: httpx.Request) -> httpx.Response:
        assert request.method == "POST"
        assert request.headers["next-action"]
        assert json.loads(request.content) == ["100024"]
        return httpx.Response(200, text='0:["$@1",["x",null]]\n2:T5,<p>x</p>')

    done = run([RECORD], out_dir, _client(handler), sleep=lambda _seconds: None)

    assert done == 1
    saved = json.loads((out_dir / "100024.json").read_text(encoding="utf-8"))
    assert saved["canonical_id"] == RECORD["canonical_id"]
    assert saved["content_checksum"].startswith("sha256:")
    assert "2:T5," in saved["body_rsc"]


def test_run_rate_limits_after_every_request(tmp_path):
    sleeps: list[float] = []

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, text="0:[]\n2:T5,<p>x</p>")

    run([RECORD], tmp_path / "raw", _client(handler), sleep=sleeps.append)

    assert sleeps == pytest.approx([RATE_LIMIT_DELAY])


def test_run_skips_a_permanently_failing_record_and_continues(tmp_path):
    out_dir = tmp_path / "raw"

    def handler(request: httpx.Request) -> httpx.Response:
        if "100024" in request.content.decode():
            return httpx.Response(500, text="server error")
        return httpx.Response(200, text='0:["$@1",["x",null]]\n2:T5,<p>x</p>')

    done = run(
        [RECORD, OTHER_RECORD],
        out_dir,
        _client(handler),
        sleep=lambda _seconds: None,
    )

    assert done == 1
    assert not (out_dir / "100024.json").exists()
    assert (out_dir / "100186.json").exists()
