"""vnkc CLI — entry point for Vietnam Knowledge Commons tools."""

import argparse
import sys
from pathlib import Path

# Mirrors vnknowledge.mcp.server.DEFAULT_CORPUS/DEFAULT_FULLTEXT as string
# literals, rather than importing them, so `vnkc <anything else>` doesn't pay
# the cost of importing the mcp package (build_parser() runs on every
# invocation, so a module-level or in-function import there isn't lazy).
_DEFAULT_CORPUS = "datasets/legal-corpus/releases/v0.1.0/legal-corpus.json"
_DEFAULT_FULLTEXT = "datasets/legal-corpus/releases/v0.2.0/legal-corpus-fulltext.json"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="vnkc",
        description="Vietnam Knowledge Commons CLI",
    )
    sub = parser.add_subparsers(dest="command")

    sub.add_parser("validate-sources", help="Validate registry/sources.yaml")
    sub.add_parser("validate-record", help="Validate records against schemas")
    sub.add_parser("report-sources", help="Report on source health")

    mcp_parser = sub.add_parser("mcp", help="MCP server commands")
    mcp_sub = mcp_parser.add_subparsers(dest="mcp_command")
    serve_parser = mcp_sub.add_parser(
        "serve", help="Run the legal-doc search MCP server over stdio"
    )
    serve_parser.add_argument("--corpus", default=_DEFAULT_CORPUS, help="Path to legal-corpus.json")
    serve_parser.add_argument(
        "--fulltext", default=_DEFAULT_FULLTEXT, help="Path to legal-corpus-fulltext.json"
    )

    return parser


def dispatch(args: argparse.Namespace) -> None:
    if args.command == "mcp" and args.mcp_command == "serve":
        from vnknowledge.mcp.server import serve

        serve(Path(args.corpus), Path(args.fulltext))
        return

    print(f"vnkc: {args.command} — not yet implemented")


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        sys.exit(1)

    dispatch(args)
    sys.exit(0)


if __name__ == "__main__":
    main()
