"""Shared test fixtures for mcpmenago tests."""

from __future__ import annotations

from pathlib import Path

import pytest


@pytest.fixture
def sample_python_file(tmp_path) -> Path:
    """Create a sample Python file with functions and classes."""
    code = tmp_path / "sample.py"
    code.write_text(
        '''\
def hello(name: str) -> str:
    """Greet someone."""
    return f"Hello, {name}"


class Calculator:
    """A simple calculator."""

    def add(self, a: int, b: int) -> int:
        return a + b

    def subtract(self, a: int, b: int) -> int:
        return a - b
'''
    )
    return code


@pytest.fixture
def sample_cpp_file(tmp_path) -> Path:
    """Create a sample C++ file with functions and classes."""
    code = tmp_path / "sample.h"
    code.write_text(
        """\
#include <vector>
#include <string>

std::string greet(const std::string& name) {
    return "Hello, " + name;
}

class Calculator {
public:
    int add(int a, int b) {
        return a + b;
    }

    int subtract(int a, int b) {
        return a - b;
    }
};

template <typename T>
T identity(T value) {
    return value;
}
"""
    )
    return code


@pytest.fixture
def sample_repo(tmp_path) -> Path:
    """Create a mock repo structure with Python and C++ files."""
    repo = tmp_path / "repo"

    # Python files
    py_dir = repo / "Chem"
    py_dir.mkdir(parents=True)
    (py_dir / "__init__.py").write_text("def MolFromSmiles(smiles): pass\n")
    (py_dir / "rdmolops.py").write_text(
        """\
def GetSubstructMatches(mol, pattern):
    pass

def SanitizeMol(mol):
    pass

class MolOps:
    def AddHs(self, mol):
        pass
"""
    )

    # C++ files
    cpp_dir = repo / "Code" / "GraphMol"
    cpp_dir.mkdir(parents=True)
    (cpp_dir / "MolOps.cpp").write_text(
        """\
#include "MolOps.h"

void SanitizeMol(RWMol& mol) {
    // implementation
}

int GetFormalCharge(const Atom& atom) {
    return atom.getFormalCharge();
}
"""
    )
    (cpp_dir / "MolOps.h").write_text(
        """\
#pragma once

void SanitizeMol(RWMol& mol);
int GetFormalCharge(const Atom& atom);
"""
    )

    return repo
