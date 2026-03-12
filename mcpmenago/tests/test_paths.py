"""Tests for mcpmenago.paths — global path constants."""

from __future__ import annotations

from pathlib import Path


def test_mcpmenago_root_is_directory():
    from mcpmenago.paths import MCPMENAGO_ROOT

    assert MCPMENAGO_ROOT.is_dir()


def test_mcpmenago_root_contains_pyproject():
    from mcpmenago.paths import MCPMENAGO_ROOT

    assert MCPMENAGO_ROOT.joinpath("pyproject.toml").exists()


def test_library_is_under_mcpmenago_root():
    from mcpmenago.paths import LIBRARY, MCPMENAGO_ROOT

    assert LIBRARY == MCPMENAGO_ROOT.joinpath("library")


def test_config_path_points_to_json():
    from mcpmenago.paths import CONFIG_PATH, MCPMENAGO_ROOT

    assert CONFIG_PATH == MCPMENAGO_ROOT.joinpath("mcpmenago.json")
    assert CONFIG_PATH.suffix == ".json"


def test_project_root_is_parent_of_mcpmenago_root():
    from mcpmenago.paths import MCPMENAGO_ROOT, PROJECT_ROOT

    assert PROJECT_ROOT == MCPMENAGO_ROOT.parent


def test_gitignore_is_under_project_root():
    from mcpmenago.paths import GITIGNORE, PROJECT_ROOT

    assert GITIGNORE == PROJECT_ROOT.joinpath(".gitignore")


def test_all_constants_are_path_objects():
    from mcpmenago.paths import CONFIG_PATH, GITIGNORE, LIBRARY, MCPMENAGO_ROOT, PROJECT_ROOT

    for p in [MCPMENAGO_ROOT, LIBRARY, CONFIG_PATH, PROJECT_ROOT, GITIGNORE]:
        assert isinstance(p, Path)
