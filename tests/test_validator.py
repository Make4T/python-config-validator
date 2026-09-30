import json
from pathlib import Path

from config_validator.validator import validate_config

ROOT = Path(__file__).parents[1]
SCHEMA = json.loads((ROOT / "schema/config.schema.json").read_text(encoding="utf-8"))


def test_valid_config_has_no_errors() -> None:
    config = json.loads((ROOT / "configs/game.valid.json").read_text(encoding="utf-8"))
    assert validate_config(config, SCHEMA) == []


def test_invalid_config_reports_all_problems() -> None:
    config = json.loads((ROOT / "configs/game.invalid.json").read_text(encoding="utf-8"))
    errors = validate_config(config, SCHEMA)
    paths = {error.path for error in errors}
    assert "$.project_name" in paths
    assert "$.audio.master_volume" in paths
    assert "$.audio.subtitles" in paths
    assert "$.controls.interact" in paths
    assert "$.debug_mode" in paths


def test_nested_values_are_checked() -> None:
    config = {
        "project_name": "Demo",
        "version": "1.0",
        "audio": {"master_volume": 0.0, "subtitles": False},
        "controls": {"move_forward": "W", "interact": "E"},
    }
    assert validate_config(config, SCHEMA) == []


def test_boolean_is_not_accepted_as_number() -> None:
    config = {
        "project_name": "Demo",
        "version": "1.0",
        "audio": {"master_volume": True, "subtitles": False},
        "controls": {"move_forward": "W", "interact": "E"},
    }
    errors = validate_config(config, SCHEMA)
    assert any(error.path == "$.audio.master_volume" for error in errors)
