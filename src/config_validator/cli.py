"""Command-line interface for the configuration validator."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from .validator import ValidationError, apply_defaults, validate_config


def _read_document(path: Path, file_format: str) -> Any:
    selected_format = file_format
    if selected_format == 'auto':
        selected_format = 'yaml' if path.suffix.lower() in {'.yaml', '.yml'} else 'json'

    with path.open(encoding='utf-8') as file:
        if selected_format == 'json':
            return json.load(file)
        try:
            import yaml
        except ImportError as error:
            raise RuntimeError(
                'YAML support is optional. Install it with: '
                'python -m pip install -e ".[yaml]"'
            ) from error
        try:
            return yaml.safe_load(file)
        except yaml.YAMLError as error:
            raise ValueError(f'invalid YAML: {error}') from error


def _write_document(path: Path, value: Any, file_format: str) -> None:
    selected_format = file_format
    if selected_format == 'auto':
        selected_format = 'yaml' if path.suffix.lower() in {'.yaml', '.yml'} else 'json'

    if selected_format == 'json':
        path.write_text(json.dumps(value, indent=2) + chr(10), encoding='utf-8')
        return
    try:
        import yaml
    except ImportError as error:
        raise RuntimeError(
            'YAML support is optional. Install it with: '
            'python -m pip install -e ".[yaml]"'
        ) from error
    path.write_text(yaml.safe_dump(value, sort_keys=False), encoding='utf-8')


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog='config-validator',
        description='Validate a JSON or YAML configuration file against a schema.',
    )
    parser.add_argument('config', type=Path, help='configuration file to validate')
    parser.add_argument('--schema', type=Path, required=True, help='JSON schema file')
    parser.add_argument(
        '--format',
        choices=('auto', 'json', 'yaml'),
        default='auto',
        help='input format; auto detects .json, .yaml or .yml',
    )
    parser.add_argument(
        '--fix', action='store_true', help='write schema defaults for missing values'
    )
    parser.add_argument('--json', action='store_true', help='print machine-readable JSON output')
    return parser


def _print_errors(errors: list[ValidationError], as_json: bool) -> None:
    if as_json:
        print(json.dumps([error.as_dict() for error in errors], indent=2))
        return
    for error in errors:
        print(f'ERROR [{error.code}] {error.path}: {error.message}')
        if error.suggestion:
            print(f'  Suggestion: {error.suggestion}')


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        config = _read_document(args.config, args.format)
        schema = _read_document(args.schema, 'json')
        changes: list[str] = []
        if args.fix:
            config, changes = apply_defaults(config, schema)
            if changes:
                _write_document(args.config, config, args.format)
    except (FileNotFoundError, json.JSONDecodeError, RuntimeError, ValueError) as error:
        print(f'ERROR: {error}')
        return 2

    errors = validate_config(config, schema)
    if errors:
        _print_errors(errors, args.json)
        return 1

    result: dict[str, Any] = {'valid': True, 'file': str(args.config)}
    if changes:
        result['defaults_applied'] = changes
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f'VALID: {args.config}')
        if changes:
            print(f"FIXED: added {', '.join(changes)}")
    return 0
