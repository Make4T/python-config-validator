"""Command-line interface for the configuration validator."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from .validator import ValidationError, validate_config


def _read_json(path: Path) -> Any:
    with path.open(encoding="utf-8") as file:
        return json.load(file)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="config-validator",
        description="Validate a JSON configuration file against a JSON schema.",
    )
    parser.add_argument("config", type=Path, help="JSON configuration file to validate")
    parser.add_argument("--schema", type=Path, required=True, help="JSON schema file")
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON output")
    return parser


def _print_errors(errors: list[ValidationError], as_json: bool) -> None:
    if as_json:
        print(json.dumps([error.as_dict() for error in errors], indent=2))
        return
    for error in errors:
        print(f"ERROR {error.path}: {error.message}")


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        config = _read_json(args.config)
        schema = _read_json(args.schema)
    except FileNotFoundError as error:
        print(f"ERROR: file not found: {error.filename}")
        return 2
    except json.JSONDecodeError as error:
        print(
            f"ERROR: invalid JSON in {error.doc[:30]!r}: "
            f"line {error.lineno}, column {error.colno}"
        )
        return 2

    errors = validate_config(config, schema)
    if errors:
        _print_errors(errors, args.json)
        return 1

    if args.json:
        print(json.dumps({"valid": True, "file": str(args.config)}))
    else:
        print(f"VALID: {args.config}")
    return 0
