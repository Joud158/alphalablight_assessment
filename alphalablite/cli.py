from __future__ import annotations
import argparse
import math
import sys
from .exceptions import AlphaLabLiteError
from .service import AlphaLabLiteService

def _format_float(value: float) -> str:
    if isinstance(value, float) and math.isnan(value):
        return "nan"
    return repr(value)

def _format_series(series: list[float]) -> str:
    return "[" + ", ".join(_format_float(value) for value in series) + "]"

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="AlphaLabLite CLI tool")
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser(
        "execute",
        help="Read entire stdin as input script",
    )
    view_parser = subparsers.add_parser(
        "view",
        help="View items by ID",
    )
    view_parser.add_argument("--id", required=True, dest="script_id")
    view_parser.add_argument("items", nargs="+")
    return parser

def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    service = AlphaLabLiteService()
    try:
        if args.command == "execute":
            script = sys.stdin.read()
            script_id = service.execute(script)
            print(f"Script successfully executed: {script_id}")
            return 0
        if args.command == "view":
            result = service.view(args.script_id, args.items)
            for name, series in result.items():
                print(f"{name}:")
                print(_format_series(series))
            return 0
        parser.error("Unknown command")
        return 2
    except AlphaLabLiteError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

if __name__ == "__main__":
    raise SystemExit(main())