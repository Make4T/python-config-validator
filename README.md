# python-config-validator

A small, testable Python CLI for validating JSON configuration files against a focused JSON-schema-inspired format.

This is the first project in a portfolio roadmap from Python fundamentals toward SQL, TypeScript and full-stack engineering.

## What it does

- Validates required fields and nested object structure.
- Checks primitive types, numeric ranges and string lengths.
- Detects unknown properties.
- Prints readable terminal errors or machine-readable JSON.
- Includes valid/invalid examples, unit tests and GitHub Actions CI.

## Requirements

- Python 3.10+

## Run it

From the repository root:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
python -m config_validator configs/game.valid.json --schema schema/config.schema.json
python -m config_validator configs/game.invalid.json --schema schema/config.schema.json
```

The valid file exits with code `0`. The invalid file exits with code `1` and lists every detected problem.

For scripts and CI, use JSON output:

```powershell
python -m config_validator configs/game.invalid.json --schema schema/config.schema.json --json
```

After installation, the same command is available as:

```powershell
config-validator configs/game.valid.json --schema schema/config.schema.json
```

## Test and quality checks

```powershell
pytest
ruff check .
```

## Repository map

```text
src/config_validator/validator.py  validation engine
src/config_validator/cli.py        command-line interface
schema/config.schema.json           configuration rules
configs/                            valid and invalid examples
tests/                              automated tests
.github/workflows/ci.yml            lint + test on every push/PR
```

## Next improvements

- Add a `--fix` mode for safe defaults.
- Support schema error codes and suggestions.
- Add YAML input through an optional dependency.
- Package and publish the CLI to PyPI after the API stabilizes.
