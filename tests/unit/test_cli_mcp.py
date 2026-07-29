"""Seam: vnkc CLI `mcp serve` subcommand -- argument wiring dispatches to
vnknowledge.mcp.server.serve with the parsed paths."""

from pathlib import Path

from vnknowledge.cli import build_parser, dispatch


def test_mcp_serve_parses_default_paths():
    args = build_parser().parse_args(["mcp", "serve"])

    assert args.command == "mcp"
    assert args.mcp_command == "serve"


def test_mcp_serve_parses_custom_paths():
    args = build_parser().parse_args(["mcp", "serve", "--corpus", "a.json", "--fulltext", "b.json"])

    assert Path(args.corpus) == Path("a.json")
    assert Path(args.fulltext) == Path("b.json")


def test_dispatch_calls_serve_with_parsed_paths(monkeypatch):
    calls = []
    monkeypatch.setattr(
        "vnknowledge.mcp.server.serve",
        lambda corpus_path, fulltext_path: calls.append((corpus_path, fulltext_path)),
    )

    args = build_parser().parse_args(["mcp", "serve", "--corpus", "a.json", "--fulltext", "b.json"])
    dispatch(args)

    assert calls == [(Path("a.json"), Path("b.json"))]
