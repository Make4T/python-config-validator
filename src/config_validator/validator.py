"""A small JSON-schema-inspired validator with actionable diagnostics."""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class ValidationError:
    """One machine-readable and human-readable validation problem."""

    path: str
    code: str
    message: str
    suggestion: str = ""

    def as_dict(self) -> dict[str, str]:
        result = {"path": self.path, "code": self.code, "message": self.message}
        if self.suggestion:
            result["suggestion"] = self.suggestion
        return result


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
    """Validate *value* against the supported schema subset."""

    errors: list[ValidationError] = []
    expected_type = schema.get("type")
    if expected_type and not _type_matches(value, expected_type):
        errors.append(
            ValidationError(
                path,
                "type_mismatch",
                f"expected type {expected_type}",
                f"Change this value to a JSON {expected_type}.",
            )
        )
        return errors

    if "enum" in schema and value not in schema["enum"]:
        errors.append(
            ValidationError(
                path,
                "invalid_choice",
                f"must be one of {schema['enum']}",
                "Choose one of the allowed values.",
            )
        )

    if isinstance(value, (int, float)) and not isinstance(value, bool):
        if "minimum" in schema and value < schema["minimum"]:
            errors.append(
                ValidationError(
                    path,
                    "below_minimum",
                    f"must be at least {schema['minimum']}",
                    f"Increase the value to {schema['minimum']} or higher.",
                )
            )
        if "maximum" in schema and value > schema["maximum"]:
            errors.append(
                ValidationError(
                    path,
                    "above_maximum",
                    f"must be at most {schema['maximum']}",
                    f"Lower the value to {schema['maximum']} or less.",
                )
            )

    if isinstance(value, str) and "minLength" in schema and len(value) < schema["minLength"]:
        errors.append(
            ValidationError(
                path,
                "too_short",
                f"must contain at least {schema['minLength']} characters",
                "Enter a longer value.",
            )
        )

    if isinstance(value, list):
        if "minItems" in schema and len(value) < schema["minItems"]:
            errors.append(
                ValidationError(
                    path,
                    "too_few_items",
                    f"must contain at least {schema['minItems']} items",
                    "Add the required number of items.",
                )
            )
        item_schema = schema.get("items")
        if item_schema:
            for index, item in enumerate(value):
                errors.extend(validate_config(item, item_schema, f"{path}[{index}]"))

    if isinstance(value, dict):
        properties = schema.get("properties", {})
        for required_key in schema.get("required", []):
            if required_key not in value:
                errors.append(
                    ValidationError(
                        f"{path}.{required_key}",
                        "required",
                        "is required",
                        "Add this property or run --fix if a schema default exists.",
                    )
                )

        if schema.get("additionalProperties") is False:
            for key in value:
                if key not in properties:
                    errors.append(
                        ValidationError(
                            f"{path}.{key}",
                            "unknown_property",
                            "is not allowed",
                            "Remove this property or add it to the schema.",
                        )
                    )

        for key, child_schema in properties.items():
            if key in value:
                errors.extend(validate_config(value[key], child_schema, f"{path}.{key}"))

    return errors


def apply_defaults(
    value: Any, schema: dict[str, Any], path: str = "$"
) -> tuple[Any, list[str]]:
    """Return a copy with only schema-provided defaults filled in."""

    if not isinstance(value, dict) or schema.get("type") != "object":
        return deepcopy(value), []

    result = deepcopy(value)
    changes: list[str] = []
    for key, child_schema in schema.get("properties", {}).items():
        child_path = f"{path}.{key}"
        if key not in result and "default" in child_schema:
            result[key] = deepcopy(child_schema["default"])
            changes.append(child_path)
        elif key in result:
            result[key], nested_changes = apply_defaults(result[key], child_schema, child_path)
            changes.extend(nested_changes)
    return result, changes
