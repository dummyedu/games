from __future__ import annotations

import argparse
from pathlib import Path
from typing import Sequence

from world_engine.validation import validate_world


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="world-engine")
    subparsers = parser.add_subparsers(dest="command", required=True)

    validate = subparsers.add_parser("validate", help="validate a world directory")
    validate.add_argument("world_root", type=Path)

    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "validate":
        result = validate_world(args.world_root)
        if result.ok:
            print(f"valid: {args.world_root}")
            for warning in result.warnings:
                print(f"warning: {warning}")
            return 0
        for error in result.errors:
            print(f"error: {error}")
        return 1

    parser.error(f"unsupported command: {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
