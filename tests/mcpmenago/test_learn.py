"""Tests for dependency scanning (Layer 2)."""

from __future__ import annotations

import json


def test_scan_imports_finds_direct_import(tmp_path):
    from mcpmenago.learn import scan_imports

    src = tmp_path / "src"
    src.mkdir()
    (src / "main.py").write_text("from rdkit.Chem import MolFromSmiles\nimport rdkit.Chem.rdmolops\n")
    result = scan_imports(package_name="rdkit", scan_dirs=[str(src)])
    assert "Chem" in result
    assert "Chem.rdmolops" in result


def test_scan_imports_ignores_unrelated(tmp_path):
    from mcpmenago.learn import scan_imports

    src = tmp_path / "src"
    src.mkdir()
    (src / "main.py").write_text("import numpy\nfrom pathlib import Path\n")
    result = scan_imports(package_name="rdkit", scan_dirs=[str(src)])
    assert len(result) == 0


def test_scan_imports_handles_notebook(tmp_path):
    from mcpmenago.learn import scan_imports

    nb_dir = tmp_path / "notebooks"
    nb_dir.mkdir()
    notebook = {
        "cells": [
            {"cell_type": "code", "source": ["from rdkit.Chem import Draw\n"]},
            {"cell_type": "markdown", "source": ["# Not code"]},
        ]
    }
    (nb_dir / "test.ipynb").write_text(json.dumps(notebook))
    result = scan_imports(package_name="rdkit", scan_dirs=[str(nb_dir)])
    assert "Chem" in result or "Chem.Draw" in result


def test_scan_imports_works_for_non_rdkit_package(tmp_path):
    from mcpmenago.learn import scan_imports

    src = tmp_path / "src"
    src.mkdir()
    (src / "app.py").write_text("import flet\nfrom flet import Page, Text\n")
    result = scan_imports(package_name="flet", scan_dirs=[str(src)])
    assert len(result) > 0


def test_update_weights_writes_file(tmp_path):
    from mcpmenago.learn import update_weights
    from mcpmenago.models import DISCOVERED

    symbols_in_index = ["GetSubstructMatches", "SanitizeMol", "AddHs", "MolFromSmiles"]
    discovered_modules = ["Chem.rdmolops", "Chem"]
    # Simulate: GetSubstructMatches and SanitizeMol are in Chem.rdmolops
    symbol_to_module = {
        "GetSubstructMatches": "Chem.rdmolops",
        "SanitizeMol": "Chem.rdmolops",
        "AddHs": "Chem.rdmolops",
        "MolFromSmiles": "Chem",
    }

    weights_path = tmp_path / "weights.json"
    update_weights(
        discovered_modules=discovered_modules,
        symbol_to_module=symbol_to_module,
        output_path=weights_path,
    )

    assert weights_path.exists()
    weights = json.loads(weights_path.read_text())
    assert weights["GetSubstructMatches"] == DISCOVERED
    assert weights["SanitizeMol"] == DISCOVERED


def test_update_weights_only_includes_discovered(tmp_path):
    from mcpmenago.learn import update_weights

    symbol_to_module = {
        "GetSubstructMatches": "Chem.rdmolops",
        "UnusedFunction": "DataStructs",
    }

    weights_path = tmp_path / "weights.json"
    update_weights(
        discovered_modules=["Chem.rdmolops"],  # Only rdmolops discovered
        symbol_to_module=symbol_to_module,
        output_path=weights_path,
    )

    weights = json.loads(weights_path.read_text())
    assert "GetSubstructMatches" in weights
    assert "UnusedFunction" not in weights


def test_load_weights_returns_empty_for_missing_file(tmp_path):
    from mcpmenago.learn import load_weights

    result = load_weights(tmp_path / "nonexistent.json")
    assert result == {}


def test_load_weights_reads_existing(tmp_path):
    from mcpmenago.learn import load_weights
    from mcpmenago.models import DISCOVERED

    path = tmp_path / "weights.json"
    path.write_text(json.dumps({"Foo": DISCOVERED}))
    result = load_weights(path)
    assert result["Foo"] == DISCOVERED
