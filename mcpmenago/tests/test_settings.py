"""Tests for load_settings() — runtime config loader."""

from __future__ import annotations

from mcpmenago.models import Settings


def test_load_settings_returns_defaults_when_file_missing(tmp_path):
    from mcpmenago.models import load_settings

    path = tmp_path / "mcpmenago.json"
    result = load_settings(path)
    assert isinstance(result, Settings)
    assert result.learn_dirs == ["src", "tests", "notebooks"]


def test_load_settings_reads_file_when_present(tmp_path):
    from mcpmenago.models import load_settings

    path = tmp_path / "mcpmenago.json"
    custom = Settings(learn_dirs=["lib"], supported_languages=["python"])
    path.write_text(custom.model_dump_json())

    result = load_settings(path)
    assert result.learn_dirs == ["lib"]
    assert result.supported_languages == ["python"]
