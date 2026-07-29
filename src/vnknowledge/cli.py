"""vnkc CLI — entry point for Vietnam Knowledge Commons tools."""

import argparse
import sys


def main():
    parser = argparse.ArgumentParser(
        prog="vnkc",
        description="Vietnam Knowledge Commons CLI",
    )
    sub = parser.add_subparsers(dest="command")

    sub.add_parser("validate-sources", help="Validate registry/sources.yaml")
    sub.add_parser("validate-record", help="Validate records against schemas")
    sub.add_parser("report-sources", help="Report on source health")

    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        sys.exit(1)

    print(f"vnkc: {args.command} — not yet implemented")
    sys.exit(0)


if __name__ == "__main__":
    main()
