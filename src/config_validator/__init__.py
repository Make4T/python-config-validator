"""JSON configuration validation package."""

from .validator import ValidationError, validate_config

__all__ = ["ValidationError", "validate_config"]
