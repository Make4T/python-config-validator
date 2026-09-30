"""A deliberately small JSON-schema-inspired validator.

The project uses a focused subset of JSON Schema so the implementation stays
easy to understand while still covering useful configuration checks.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class ValidationError:
    """One human-readable validation problem."""

    path: str
    message: str

    def as_dict(self) -> dict[str, str]:
        return {"path": self.path, "message": self.message}


def _type_matches(value: Any, expected: str) -> bool:
    checks = {
        "object": lambda item: isinstance(item, dict),
        "array": lambda item: isinstance(item, list),
        "string": lambda item: isinstance(item, str),
        "integer": lambda item: isinstance(item, int) and not isinstance(item, bool),
        "number": lambda item: isinstance(item, (int, float)) and not isinstance(item, bool),
        "boolean": lambda item: isinstance(item, bool),
        "null": lambda item: item is None,
    }
    return expected in checks and checks[expected](value)


def validate_config(value: Any, schema: dict[str, Any], path: str = "$") -> list[ValidationError]:
    """Validate *value* against the supported schema subset.

    Supported keywords are ``type``, ``required``, ``properties``,
    ``additionalProperties``, ``items``, ``enum``, ``minimum``, ``maximum``,
    ``minLength`` and ``minItems``.
    """

    errors: list[ValidationError] = []
    expected_type = schema.get("type")
    if expected_type and not _type_matches(value, expected_type):
        errors.append(ValidationError(path, f"expected type {expected_type}"))
        return errors

    if "enum" in schema and value not in schema["enum"]:
        errors.append(ValidationError(path, f"must be one of {schema['enum']}"))

    if isinstance(value, (int, float)) and not isinstance(value, bool):
        if "minimum" in schema and value < schema["minimum"]:
            errors.append(ValidationError(path, f"must be at least {schema['minimum']}"))
        if "maximum" in schema and value > schema["maximum"]:
            errors.append(ValidationError(path, f"must be at most {schema['maximum']}"))

    if isinstance(value, str) and "minLength" in schema and len(value) < schema["minLength"]:
        errors.append(
            ValidationError(path, f"must contain at least {schema['minLength']} characters")
        )

    if isinstance(value, list):
        if "minItems" in schema and len(value) < schema["minItems"]:
            errors.append(
                ValidationError(path, f"must contain at least {schema['minItems']} items")
            )
        item_schema = schema.get("items")
        if item_schema:
            for index, item in enumerate(value):
                errors.extend(validate_config(item, item_schema, f"{path}[{index}]"))

    if isinstance(value, dict):
        properties = schema.get("properties", {})
        for required_key in schema.get("required", []):
            if required_key not in value:
                errors.append(ValidationError(f"{path}.{required_key}", "is required"))

        if schema.get("additionalProperties") is False:
            for key in value:
                if key not in properties:
                    errors.append(ValidationError(f"{path}.{key}", "is not allowed"))

        for key, child_schema in properties.items():
            if key in value:
                errors.extend(validate_config(value[key], child_schema, f"{path}.{key}"))

    return errors
