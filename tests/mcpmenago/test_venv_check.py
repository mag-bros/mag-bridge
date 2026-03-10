"""Tests for venv pre-check."""

from __future__ import annotations

from unittest.mock import patch


def test_check_venv_passes_when_in_venv(tmp_path):
    from mcpmenago.venv_check import check_venv

    venv_python = tmp_path / ".venv" / "bin" / "python"
    venv_python.parent.mkdir(parents=True)
    venv_python.touch()

    with patch("mcpmenago.venv_check.sys") as mock_sys:
        mock_sys.executable = str(venv_python)
        # Should not raise
        check_venv(project_root=tmp_path)


def test_check_venv_fails_when_global(tmp_path):
    import pytest
    from mcpmenago.venv_check import VenvCheckError, check_venv

    with patch("mcpmenago.venv_check.sys") as mock_sys:
        mock_sys.executable = "/usr/bin/python3"
        with pytest.raises(VenvCheckError, match="not inside"):
            check_venv(project_root=tmp_path)


def test_check_venv_error_message_includes_fix(tmp_path):
    import pytest
    from mcpmenago.venv_check import VenvCheckError, check_venv

    with patch("mcpmenago.venv_check.sys") as mock_sys:
        mock_sys.executable = "/usr/bin/python3"
        with pytest.raises(VenvCheckError, match="python -m venv .venv"):
            check_venv(project_root=tmp_path)
