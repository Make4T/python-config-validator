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

### Safe defaults

The schema can provide safe defaults for missing properties. `--fix` writes only
those missing defaults and never overwrites existing values or removes unknown
properties:

```powershell
python -m config_validator configs/game.missing.json --schema schema/config.schema.json --fix
```

The command validates the result again after writing it. Invalid values that are
already present still require a manual correction.

For scripts and CI, use JSON output:

```powershell
python -m config_validator configs/game.invalid.json --schema schema/config.schema.json --json
```

JSON diagnostics include a stable `code`, `path`, `message` and, when useful, a
`suggestion` field. These are suitable for editor integrations or CI reports.

### YAML (optional)

Install the optional dependency only when YAML is needed:

```powershell
python -m pip install -e ".[yaml]"
python -m config_validator configs/game.yaml --schema schema/config.schema.json
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
.github/workflows/publish.yml       builds/publishes tagged releases to PyPI
```

## Release to PyPI

The package build is available locally with:

```powershell
python -m pip install -e ".[dev]"
python -m build
```

The publish workflow runs when a GitHub Release is published. Before the first
release, configure a PyPI Trusted Publisher for this repository and workflow.
Do not put a PyPI token in the repository.
