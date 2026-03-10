"""Tests for mcpmenago CLI."""

from __future__ import annotations

from unittest.mock import patch

from click.testing import CliRunner


def test_cli_help():
    from mcpmenago.cli import cli

    runner = CliRunner()
    result = runner.invoke(cli, ["--help"])
    assert result.exit_code == 0
    assert "mcpmenago" in result.output.lower() or "MCP Manager" in result.output


def test_cli_list_empty(tmp_path):
    from mcpmenago.cli import cli

    runner = CliRunner()
    with patch("mcpmenago.cli.LIBRARY", tmp_path / "library"):
        result = runner.invoke(cli, ["list"])
        assert result.exit_code == 0
        assert "no books" in result.output.lower() or "empty" in result.output.lower()


def test_cli_remove_nonexistent(tmp_path):
    from mcpmenago.cli import cli

    runner = CliRunner()
    with patch("mcpmenago.cli.LIBRARY", tmp_path / "library"):
        result = runner.invoke(cli, ["remove", "nonexistent"])
        assert result.exit_code != 0 or "not found" in result.output.lower()


def test_extract_book_name_from_url():
    from mcpmenago.cli import _extract_book_name

    assert _extract_book_name("https://github.com/rdkit/rdkit") == "rdkit"
    assert _extract_book_name("https://github.com/rdkit/rdkit.git") == "rdkit"
    assert _extract_book_name("https://github.com/user/my-repo") == "my-repo"


def test_gitignore_management(tmp_path):
    from mcpmenago.cli import _ensure_gitignore

    gitignore = tmp_path / ".gitignore"
    _ensure_gitignore(gitignore, library_rel_path="mcpmenago/library/")

    content = gitignore.read_text()
    assert "# [mcpmenago]" in content
    assert "mcpmenago/library/" in content

    # Idempotent — running again doesn't duplicate
    _ensure_gitignore(gitignore, library_rel_path="mcpmenago/library/")
    content2 = gitignore.read_text()
    assert content2.count("[mcpmenago]") == 1
