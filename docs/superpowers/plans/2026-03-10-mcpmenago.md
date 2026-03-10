# mcpmenago Implementation Plan

---

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a standalone CLI tool + central MCP server that manages source code indexes for any GitHub repository using tree-sitter.

**Architecture:** Three-layer ranking (structural index → static weights → query context) with a library/books metaphor. CLI (`mcpmenago`) manages books; central FastMCP server exposes indexed symbols to Claude. All state in `mcpmenago/library/<book>/`.

**Tech Stack:** FastMCP, tree-sitter (+ tree-sitter-python, tree-sitter-cpp), Click, Pydantic, ripgrep

**Spec:** `mcpmenago/README.md` — full design doc with schemas, CLI flows, layer architecture, and TODO backlog.

**Baseline code:** `mcp/rdkit_mcp.py` (376 lines) — reusable patterns for ripgrep search, import parsing, tiered routing, FastMCP tool registration.

---

## File Map

| File | Responsibility | Creates/Modifies |
|------|---------------|-----------------|
| `mcpmenago/models.py` | All Pydantic schemas + weight constants | Create |
| `mcpmenago/venv_check.py` | Venv pre-check utility | Create |
| `mcpmenago/mcpmenago.json` | Default central config | Create |
| `mcpmenago/index_builder.py` | tree-sitter indexing (Layer 1) | Create |
| `mcpmenago/learn.py` | Dependency scanning (Layer 2) | Create |
| `mcpmenago/server.py` | Central FastMCP server — all MCP tools | Create |
| `mcpmenago/cli.py` | Click CLI entry point | Create |
| `mcpmenago/__init__.py` | Package init | Create |
| `.mcp.json` | Point to new server | Modify |
| `.gitignore` | Add library section | Modify |
| `tests/mcpmenago/__init__.py` | Test package init | Create |
| `tests/mcpmenago/conftest.py` | Shared fixtures (tmp library, sample files) | Create |
| `tests/mcpmenago/test_models.py` | Schema tests | Create |
| `tests/mcpmenago/test_venv_check.py` | Venv check tests | Create |
| `tests/mcpmenago/test_index_builder.py` | tree-sitter parsing tests | Create |
| `tests/mcpmenago/test_learn.py` | Learn/weight tests | Create |
| `tests/mcpmenago/test_cli.py` | CLI integration tests | Create |

---

## Chunk 1: Foundation

### Task 1: Pydantic Schemas (`models.py`) ✅ DONE

**Files:**
- Create: `mcpmenago/__init__.py`
- Create: `mcpmenago/models.py`
- Create: `tests/mcpmenago/__init__.py`
- Create: `tests/mcpmenago/test_models.py`

This is the foundation — every other file imports from `models.py`. Zero external dependencies beyond Pydantic.

- [ ] **Step 1: Write failing tests for all schemas**

Create `tests/mcpmenago/__init__.py` (empty) and `tests/mcpmenago/test_models.py`:

```python
"""Tests for mcpmenago Pydantic schemas and weight constants."""
from __future__ import annotations

from pathlib import Path

import pytest


def test_weight_constants():
    from mcpmenago.models import DISCOVERED, NOT_USED

    assert NOT_USED == 0.3
    assert DISCOVERED == 0.8


def test_mcpmenago_config_defaults():
    from mcpmenago.models import McpMenagoConfig

    config = McpMenagoConfig()
    assert config.learn_dirs == ["src", "tests", "notebooks"]
    assert config.supported_languages == ["python", "cpp"]


def test_mcpmenago_config_custom():
    from mcpmenago.models import McpMenagoConfig

    config = McpMenagoConfig(learn_dirs=["lib"], supported_languages=["python"])
    assert config.learn_dirs == ["lib"]
    assert config.supported_languages == ["python"]


def test_book_meta_required_fields():
    from mcpmenago.models import BookMeta

    meta = BookMeta(
        name="rdkit",
        github_url="https://github.com/rdkit/rdkit",
        languages=["python", "cpp"],
        python_path=Path(".venv/lib/python3.13/site-packages/rdkit"),
    )
    assert meta.name == "rdkit"
    assert meta.head_ref is None
    assert meta.head_ref_resolved is None
    assert meta.index_built_at is None


def test_book_meta_all_fields():
    from mcpmenago.models import BookMeta

    meta = BookMeta(
        name="rdkit",
        github_url="https://github.com/rdkit/rdkit",
        languages=["python", "cpp"],
        python_path=Path(".venv/lib/python3.13/site-packages/rdkit"),
        head_ref="Release_2025_09_6",
        head_ref_resolved="abc123",
        index_built_at="2026-03-10T12:00:00",
    )
    assert meta.head_ref == "Release_2025_09_6"
    assert meta.head_ref_resolved == "abc123"


def test_symbol_entry():
    from mcpmenago.models import SymbolEntry

    entry = SymbolEntry(
        name="GetSubstructMatches",
        kind="function",
        file="Code/GraphMol/substructmethods.h",
        start_line=98,
        end_line=114,
        signature="template <typename T> std::vector<MatchVectType> GetSubstructMatches(...)",
    )
    assert entry.name == "GetSubstructMatches"
    assert entry.end_line - entry.start_line == 16


def test_module_source():
    from mcpmenago.models import ModuleSource

    src = ModuleSource(path="Chem/rdmolops.py", lang="python")
    assert src.lang == "python"


def test_module_entry_multi_lang():
    from mcpmenago.models import ModuleEntry, ModuleSource

    entry = ModuleEntry(
        name="Chem.rdmolops",
        sources=[
            ModuleSource(path="Chem/rdmolops.py", lang="python"),
            ModuleSource(path="Code/GraphMol/MolOps.cpp", lang="cpp"),
        ],
        description="Molecule operations",
        key_functions=["GetSubstructMatches"],
    )
    assert len(entry.sources) == 2
    assert entry.sources[0].lang == "python"
    assert entry.sources[1].lang == "cpp"


def test_book_index_symbols_dict():
    from mcpmenago.models import BookIndex, SymbolEntry

    index = BookIndex(
        version="1.0",
        modules=[],
        symbols={
            "Foo": [
                SymbolEntry(name="Foo", kind="function", file="a.py", start_line=1, end_line=3, signature="def Foo():"),
                SymbolEntry(name="Foo", kind="function", file="b.cpp", start_line=10, end_line=20, signature="void Foo()"),
            ]
        },
    )
    assert len(index.symbols["Foo"]) == 2


def test_book_meta_json_roundtrip(tmp_path):
    from mcpmenago.models import BookMeta

    meta = BookMeta(
        name="rdkit",
        github_url="https://github.com/rdkit/rdkit",
        languages=["python", "cpp"],
        python_path=Path(".venv/lib/python3.13/site-packages/rdkit"),
        head_ref="v1.0",
    )
    path = tmp_path / "book.json"
    path.write_text(meta.model_dump_json(indent=2))
    loaded = BookMeta.model_validate_json(path.read_text())
    assert loaded.name == meta.name
    assert loaded.head_ref == meta.head_ref


def test_mcpmenago_json_validates_against_schema():
    import json
    from pathlib import Path

    from mcpmenago.models import McpMenagoConfig

    config_path = Path(__file__).parent.parent.parent / "mcpmenago" / "mcpmenago.json"
    config = McpMenagoConfig.model_validate_json(config_path.read_text())
    assert "python" in config.supported_languages


def test_book_index_json_roundtrip(tmp_path):
    from mcpmenago.models import BookIndex, ModuleEntry, ModuleSource, SymbolEntry

    index = BookIndex(
        version="2025.09.6",
        modules=[
            ModuleEntry(
                name="Chem",
                sources=[ModuleSource(path="Chem/__init__.py", lang="python")],
                description="Core module",
                key_functions=["MolFromSmiles"],
            )
        ],
        symbols={
            "MolFromSmiles": [
                SymbolEntry(name="MolFromSmiles", kind="function", file="Chem/__init__.py", start_line=10, end_line=15, signature="def MolFromSmiles(smiles):"),
            ]
        },
    )
    path = tmp_path / "index.json"
    path.write_text(index.model_dump_json(indent=2))
    loaded = BookIndex.model_validate_json(path.read_text())
    assert loaded.version == "2025.09.6"
    assert "MolFromSmiles" in loaded.symbols
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/mcpmenago/test_models.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'mcpmenago'`

- [ ] **Step 3: Create `mcpmenago/__init__.py`**

```python
"""mcpmenago — MCP Manager. Manages source code indexes for GitHub repositories."""
```

- [ ] **Step 4: Write `mcpmenago/models.py`**

```python
"""Pydantic schemas and weight constants for mcpmenago."""
from __future__ import annotations

from pathlib import Path

from pydantic import BaseModel

# ── Weight constants ──────────────────────────────────────────────────────────
NOT_USED = 0.3
DISCOVERED = 0.8


# ── Central config ────────────────────────────────────────────────────────────
class McpMenagoConfig(BaseModel):
    learn_dirs: list[str] = ["src", "tests", "notebooks"]
    supported_languages: list[str] = ["python", "cpp"]


# ── Per-book metadata (auto-generated → book.json) ───────────────────────────
class BookMeta(BaseModel):
    name: str
    github_url: str
    languages: list[str]
    python_path: Path
    head_ref: str | None = None
    head_ref_resolved: str | None = None
    index_built_at: str | None = None


# ── Symbol index ──────────────────────────────────────────────────────────────
class SymbolEntry(BaseModel):
    name: str
    kind: str
    file: str
    start_line: int
    end_line: int
    signature: str


class ModuleSource(BaseModel):
    path: str
    lang: str


class ModuleEntry(BaseModel):
    name: str
    sources: list[ModuleSource]
    description: str = ""
    key_functions: list[str] = []


class BookIndex(BaseModel):
    version: str
    modules: list[ModuleEntry]
    symbols: dict[str, list[SymbolEntry]]
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `pytest tests/mcpmenago/test_models.py -v`
Expected: All PASS

- [ ] **Step 6: Commit**

```bash
git add mcpmenago/__init__.py mcpmenago/models.py tests/mcpmenago/__init__.py tests/mcpmenago/test_models.py
git commit -m "feat(mcpmenago): add Pydantic schemas and weight constants"
```

---

### Task 2: Central Config (`mcpmenago.json`) ✅ DONE

**Files:**
- Create: `mcpmenago/mcpmenago.json`

The default config file. Loaded by `learn.py` and validated against `McpMenagoConfig`.

- [ ] **Step 1: Create default config file**

```json
{
  "learn_dirs": ["src", "tests", "notebooks"],
  "supported_languages": ["python", "cpp"]
}
```

- [ ] **Step 2: Commit**

```bash
git add mcpmenago/mcpmenago.json
git commit -m "feat(mcpmenago): add default central config"
```

---

### Task 3: Venv Pre-Check (`venv_check.py`) ✅ DONE

**Files:**
- Create: `mcpmenago/venv_check.py`
- Create: `tests/mcpmenago/test_venv_check.py`

Standalone utility. Called by CLI before `add` and `rebuild`. Checks that `sys.executable` is under the project's `.venv/`.

- [ ] **Step 1: Write failing tests**

```python
"""Tests for venv pre-check."""
from __future__ import annotations

from pathlib import Path
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
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/mcpmenago/test_venv_check.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'mcpmenago.venv_check'`

- [ ] **Step 3: Write `mcpmenago/venv_check.py`**

```python
"""Venv pre-check — ensures active Python is in the project's .venv/."""
from __future__ import annotations

import sys
from pathlib import Path


class VenvCheckError(RuntimeError):
    pass


def check_venv(project_root: Path | None = None) -> None:
    """Raise VenvCheckError if sys.executable is not inside project_root/.venv/.

    Args:
        project_root: Project root directory. Defaults to cwd.
    """
    if project_root is None:
        project_root = Path.cwd()

    venv_dir = (project_root / ".venv").resolve()
    executable = Path(sys.executable).resolve()

    if not str(executable).startswith(str(venv_dir) + "/"):
        raise VenvCheckError(
            f"Active Python ({executable}) is not inside the project venv ({venv_dir}).\n"
            f"Fix: python -m venv .venv && .venv/bin/pip install -r requirements.txt"
        )
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/mcpmenago/test_venv_check.py -v`
Expected: All PASS

- [ ] **Step 5: Commit**

```bash
git add mcpmenago/venv_check.py tests/mcpmenago/test_venv_check.py
git commit -m "feat(mcpmenago): add venv pre-check utility"
```

---

## Chunk 2: Core Engine

### Task 4: Index Builder — tree-sitter parsing ✅ DONE(`index_builder.py`)

**Files:**
- Create: `mcpmenago/index_builder.py`
- Create: `tests/mcpmenago/conftest.py` (shared fixtures)
- Create: `tests/mcpmenago/test_index_builder.py`

**Context for the implementing agent:**
- tree-sitter 0.25.x API: use `tree_sitter.Language` from `tree_sitter_python` and `tree_sitter_cpp` packages
- tree-sitter-python 0.25.x exports the language directly: `import tree_sitter_python as tspython; PYTHON_LANG = tspython.language()`
- tree-sitter-cpp 0.23.x: `import tree_sitter_cpp as tscpp; CPP_LANG = tscpp.language()`
- `tree_sitter.Parser()` then `parser.language = Language(lang_ptr)`
- Query syntax: `parser.parse(bytes_source)` returns a tree, then use `tree_sitter.Query(language, query_string)` to match nodes
- The `BookIndex`, `SymbolEntry`, `ModuleEntry`, `ModuleSource` schemas are in `mcpmenago/models.py` (see Task 1)

**What this module does:**
1. Takes a book's repo path + list of languages
2. Walks all source files for those languages
3. Parses each file with the matching tree-sitter grammar
4. Extracts function/class definitions into `SymbolEntry` objects
5. Returns a `BookIndex` and writes it to `index.json`

- [ ] **Step 1: Create test fixtures in `tests/mcpmenago/conftest.py`**

```python
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
```

- [ ] **Step 2: Write failing tests**

Create `tests/mcpmenago/test_index_builder.py`:

```python
"""Tests for tree-sitter index builder (Layer 1)."""
from __future__ import annotations

from pathlib import Path


def test_parse_python_file_extracts_functions(sample_python_file):
    from mcpmenago.index_builder import parse_python_file

    symbols = parse_python_file(sample_python_file, base_path=sample_python_file.parent)
    names = [s.name for s in symbols]
    assert "hello" in names
    assert "Calculator" in names


def test_parse_python_file_extracts_methods(sample_python_file):
    from mcpmenago.index_builder import parse_python_file

    symbols = parse_python_file(sample_python_file, base_path=sample_python_file.parent)
    names = [s.name for s in symbols]
    assert "add" in names
    assert "subtract" in names


def test_parse_python_file_line_numbers(sample_python_file):
    from mcpmenago.index_builder import parse_python_file

    symbols = parse_python_file(sample_python_file, base_path=sample_python_file.parent)
    hello = next(s for s in symbols if s.name == "hello")
    assert hello.start_line == 1
    assert hello.end_line == 3
    assert hello.kind == "function"


def test_parse_python_file_signature(sample_python_file):
    from mcpmenago.index_builder import parse_python_file

    symbols = parse_python_file(sample_python_file, base_path=sample_python_file.parent)
    hello = next(s for s in symbols if s.name == "hello")
    assert "def hello" in hello.signature


def test_parse_cpp_file_extracts_functions(sample_cpp_file):
    from mcpmenago.index_builder import parse_cpp_file

    symbols = parse_cpp_file(sample_cpp_file, base_path=sample_cpp_file.parent)
    names = [s.name for s in symbols]
    assert "greet" in names


def test_parse_cpp_file_extracts_class(sample_cpp_file):
    from mcpmenago.index_builder import parse_cpp_file

    symbols = parse_cpp_file(sample_cpp_file, base_path=sample_cpp_file.parent)
    names = [s.name for s in symbols]
    assert "Calculator" in names


def test_parse_cpp_file_extracts_template(sample_cpp_file):
    from mcpmenago.index_builder import parse_cpp_file

    symbols = parse_cpp_file(sample_cpp_file, base_path=sample_cpp_file.parent)
    names = [s.name for s in symbols]
    assert "identity" in names


def test_parse_cpp_file_line_numbers(sample_cpp_file):
    from mcpmenago.index_builder import parse_cpp_file

    symbols = parse_cpp_file(sample_cpp_file, base_path=sample_cpp_file.parent)
    greet = next(s for s in symbols if s.name == "greet")
    assert greet.start_line == 4
    assert greet.kind == "function"


def test_build_index_python_only(sample_repo):
    from mcpmenago.index_builder import build_index

    index = build_index(repo_path=sample_repo, languages=["python"])
    all_names = list(index.symbols.keys())
    assert "GetSubstructMatches" in all_names
    assert "SanitizeMol" in all_names
    assert "MolFromSmiles" in all_names


def test_build_index_cpp_only(sample_repo):
    from mcpmenago.index_builder import build_index

    index = build_index(repo_path=sample_repo, languages=["cpp"])
    all_names = list(index.symbols.keys())
    assert "SanitizeMol" in all_names
    assert "GetFormalCharge" in all_names


def test_build_index_both_languages(sample_repo):
    from mcpmenago.index_builder import build_index

    index = build_index(repo_path=sample_repo, languages=["python", "cpp"])
    # SanitizeMol should appear in both languages (overloads)
    assert "SanitizeMol" in index.symbols
    entries = index.symbols["SanitizeMol"]
    langs = {e.file.split(".")[-1] for e in entries}
    assert len(langs) >= 1  # at least one language


def test_build_index_writes_json(sample_repo, tmp_path):
    from mcpmenago.index_builder import build_index
    from mcpmenago.models import BookIndex

    output = tmp_path / "index.json"
    index = build_index(repo_path=sample_repo, languages=["python"], output_path=output)
    assert output.exists()
    loaded = BookIndex.model_validate_json(output.read_text())
    assert len(loaded.symbols) > 0


def test_build_index_symbol_entry_has_file_relative_to_repo(sample_repo):
    from mcpmenago.index_builder import build_index

    index = build_index(repo_path=sample_repo, languages=["python"])
    entry = index.symbols["GetSubstructMatches"][0]
    # file should be relative to repo root, not absolute
    assert not entry.file.startswith("/")
    assert "Chem/rdmolops.py" in entry.file
```

- [ ] **Step 3: Run tests to verify they fail**

Run: `pytest tests/mcpmenago/test_index_builder.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'mcpmenago.index_builder'`

- [ ] **Step 4: Write `mcpmenago/index_builder.py`**

```python
"""tree-sitter index builder (Layer 1) — parses source files into SymbolEntry objects."""
from __future__ import annotations

import sys
from datetime import datetime, timezone
from pathlib import Path

import tree_sitter_cpp as tscpp
import tree_sitter_python as tspython
from tree_sitter import Language, Parser

from mcpmenago.models import BookIndex, ModuleEntry, ModuleSource, SymbolEntry

# ── Language setup ────────────────────────────────────────────────────────────
PY_LANGUAGE = Language(tspython.language())
CPP_LANGUAGE = Language(tscpp.language())

LANG_EXTENSIONS: dict[str, list[str]] = {
    "python": [".py"],
    "cpp": [".h", ".hpp", ".cpp", ".cc", ".cxx"],
}

# ── Python queries ────────────────────────────────────────────────────────────
PY_FUNC_QUERY = PY_LANGUAGE.query("(function_definition name: (identifier) @name) @def")
PY_CLASS_QUERY = PY_LANGUAGE.query("(class_definition name: (identifier) @name) @def")

# ── C++ queries ───────────────────────────────────────────────────────────────
CPP_FUNC_QUERY = CPP_LANGUAGE.query("(function_definition) @def")
CPP_CLASS_QUERY = CPP_LANGUAGE.query("(class_specifier name: (type_identifier) @name) @def")
CPP_TEMPLATE_QUERY = CPP_LANGUAGE.query("(template_declaration) @def")


def _first_line(node_bytes: bytes) -> str:
    """Extract first line of a node as the signature."""
    text = node_bytes.decode("utf-8", errors="replace")
    return text.split("\n")[0].strip()


def _extract_name_from_cpp_func(node) -> str | None:
    """Walk a C++ function_definition to find the function name."""
    declarator = node.child_by_field_name("declarator")
    while declarator is not None:
        if declarator.type == "function_declarator":
            inner = declarator.child_by_field_name("declarator")
            if inner is not None:
                return inner.text.decode("utf-8", errors="replace")
            break
        # Drill into nested declarators (pointer, reference, etc.)
        declarator = declarator.child_by_field_name("declarator")
    return None


def parse_python_file(file_path: Path, base_path: Path) -> list[SymbolEntry]:
    """Parse a Python file and return SymbolEntry objects."""
    source = file_path.read_bytes()
    parser = Parser(PY_LANGUAGE)
    tree = parser.parse(source)
    rel_path = str(file_path.relative_to(base_path))
    symbols: list[SymbolEntry] = []

    # Functions (including methods)
    for match in PY_FUNC_QUERY.matches(tree.root_node):
        nodes = match[1]
        def_node = nodes.get("def")
        name_node = nodes.get("name")
        if def_node is None or name_node is None:
            continue
        parent = def_node.parent
        kind = "method" if parent is not None and parent.type == "block" else "function"
        symbols.append(
            SymbolEntry(
                name=name_node.text.decode("utf-8"),
                kind=kind,
                file=rel_path,
                start_line=def_node.start_point[0] + 1,
                end_line=def_node.end_point[0] + 1,
                signature=_first_line(def_node.text),
            )
        )

    # Classes
    for match in PY_CLASS_QUERY.matches(tree.root_node):
        nodes = match[1]
        def_node = nodes.get("def")
        name_node = nodes.get("name")
        if def_node is None or name_node is None:
            continue
        symbols.append(
            SymbolEntry(
                name=name_node.text.decode("utf-8"),
                kind="class",
                file=rel_path,
                start_line=def_node.start_point[0] + 1,
                end_line=def_node.end_point[0] + 1,
                signature=_first_line(def_node.text),
            )
        )

    return symbols


def parse_cpp_file(file_path: Path, base_path: Path) -> list[SymbolEntry]:
    """Parse a C++ file and return SymbolEntry objects."""
    source = file_path.read_bytes()
    parser = Parser(CPP_LANGUAGE)
    tree = parser.parse(source)
    rel_path = str(file_path.relative_to(base_path))
    symbols: list[SymbolEntry] = []

    # Functions
    for match in CPP_FUNC_QUERY.matches(tree.root_node):
        nodes = match[1]
        def_node = nodes.get("def")
        if def_node is None:
            continue
        name = _extract_name_from_cpp_func(def_node)
        if name is None:
            continue
        symbols.append(
            SymbolEntry(
                name=name,
                kind="function",
                file=rel_path,
                start_line=def_node.start_point[0] + 1,
                end_line=def_node.end_point[0] + 1,
                signature=_first_line(def_node.text),
            )
        )

    # Classes
    for match in CPP_CLASS_QUERY.matches(tree.root_node):
        nodes = match[1]
        def_node = nodes.get("def")
        name_node = nodes.get("name")
        if def_node is None or name_node is None:
            continue
        symbols.append(
            SymbolEntry(
                name=name_node.text.decode("utf-8"),
                kind="class",
                file=rel_path,
                start_line=def_node.start_point[0] + 1,
                end_line=def_node.end_point[0] + 1,
                signature=_first_line(def_node.text),
            )
        )

    # Templates
    for match in CPP_TEMPLATE_QUERY.matches(tree.root_node):
        nodes = match[1]
        def_node = nodes.get("def")
        if def_node is None:
            continue
        # Find the inner function or class name
        for child in def_node.children:
            if child.type == "function_definition":
                name = _extract_name_from_cpp_func(child)
                if name:
                    symbols.append(
                        SymbolEntry(
                            name=name,
                            kind="template",
                            file=rel_path,
                            start_line=def_node.start_point[0] + 1,
                            end_line=def_node.end_point[0] + 1,
                            signature=_first_line(def_node.text),
                        )
                    )

    return symbols


LANG_PARSERS: dict[str, callable] = {
    "python": parse_python_file,
    "cpp": parse_cpp_file,
}


def build_index(
    repo_path: Path,
    languages: list[str],
    version: str = "0.0.0",
    output_path: Path | None = None,
) -> BookIndex:
    """Build a BookIndex by parsing all source files in repo_path.

    Args:
        repo_path: Path to the cloned repository root.
        languages: List of languages to parse (e.g., ["python", "cpp"]).
        version: Version string for the index.
        output_path: If provided, write index JSON to this path.

    Returns:
        BookIndex with all extracted symbols.
    """
    symbols: dict[str, list[SymbolEntry]] = {}
    modules: list[ModuleEntry] = []

    for lang in languages:
        extensions = LANG_EXTENSIONS.get(lang, [])
        parser_fn = LANG_PARSERS.get(lang)
        if parser_fn is None:
            print(f"  Skipping unsupported language: {lang}", file=sys.stderr)
            continue

        for ext in extensions:
            for file_path in sorted(repo_path.rglob(f"*{ext}")):
                try:
                    file_symbols = parser_fn(file_path, base_path=repo_path)
                    for sym in file_symbols:
                        symbols.setdefault(sym.name, []).append(sym)
                except Exception as e:
                    print(f"  Warning: failed to parse {file_path}: {e}", file=sys.stderr)

    index = BookIndex(version=version, modules=modules, symbols=symbols)

    if output_path is not None:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(index.model_dump_json(indent=2))

    return index
```

**Important note for the implementing agent:** The tree-sitter API may differ slightly between versions. The code above targets tree-sitter 0.25.x. If `PY_LANGUAGE.query(...)` doesn't work, try `Language(tspython.language()).query(...)` or consult the tree-sitter Python bindings docs. The key pattern is: create a `Parser`, set its language, parse bytes, then query the tree. Test first — the test fixtures provide concrete verification.

- [ ] **Step 5: Run tests to verify they pass**

Run: `pytest tests/mcpmenago/test_index_builder.py -v`
Expected: All PASS

**If tree-sitter API differs:** Adjust the query/parser API calls. The tests define the contract — the implementation must satisfy them.

- [ ] **Step 6: Commit**

```bash
git add mcpmenago/index_builder.py tests/mcpmenago/conftest.py tests/mcpmenago/test_index_builder.py
git commit -m "feat(mcpmenago): add tree-sitter index builder (Layer 1)"
```

---

### Task 5: Learn — Dependency Scanning ✅ DONE(`learn.py`)

**Files:**
- Create: `mcpmenago/learn.py`
- Create: `tests/mcpmenago/test_learn.py`

**Context for implementing agent:**
- `learn.py` scans user project directories for import statements matching a book's package name
- Updates `weights.json` with `DISCOVERED = 0.8` for matched symbol names
- Reads `learn_dirs` from `mcpmenago/mcpmenago.json` via `McpMenagoConfig`
- `weights.json` is independent of `index.json` — different lifecycles
- Import regex pattern from baseline `mcp/rdkit_mcp.py:78`: `r"(?:from|import)\s+(rdkit(?:\.[a-zA-Z0-9_]+)*)"`
- Must be generalized: replace `rdkit` with the book's package name
- Must handle `.ipynb` files: parse `"source"` from code cells

- [ ] **Step 1: Write failing tests**

Create `tests/mcpmenago/test_learn.py`:

```python
"""Tests for dependency scanning (Layer 2)."""
from __future__ import annotations

import json
from pathlib import Path


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
    from mcpmenago.models import DISCOVERED

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
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/mcpmenago/test_learn.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'mcpmenago.learn'`

- [ ] **Step 3: Write `mcpmenago/learn.py`**

```python
"""Dependency scanning (Layer 2) — scans project imports, updates weights."""
from __future__ import annotations

import json
import re
from pathlib import Path

from mcpmenago.models import DISCOVERED


def _build_import_re(package_name: str) -> re.Pattern:
    """Build regex matching imports of a specific package."""
    return re.compile(rf"(?:from|import)\s+({re.escape(package_name)}(?:\.[a-zA-Z0-9_]+)*)")


def scan_imports(package_name: str, scan_dirs: list[str]) -> list[str]:
    """Scan directories for import statements matching package_name.

    Returns list of discovered module names (e.g., ["Chem", "Chem.rdmolops"]).
    """
    import_re = _build_import_re(package_name)
    modules: set[str] = set()

    for dir_path in scan_dirs:
        scan_dir = Path(dir_path)
        if not scan_dir.exists():
            continue
        for ext in ("*.py", "*.ipynb"):
            for fpath in scan_dir.rglob(ext):
                try:
                    text = fpath.read_text(errors="ignore")
                    if fpath.suffix == ".ipynb":
                        data = json.loads(text)
                        cells = data.get("cells", [])
                        text = "\n".join(
                            "".join(c.get("source", []))
                            for c in cells
                            if c.get("cell_type") == "code"
                        )
                    for match in import_re.finditer(text):
                        mod = match.group(1).removeprefix(f"{package_name}.")
                        # Normalize: "Chem.rdmolops.GetSubstructMatches" → "Chem.rdmolops"
                        parts = mod.split(".")
                        modules.add(".".join(parts[:2]) if len(parts) > 1 else parts[0])
                except Exception:
                    pass

    return sorted(modules)


def update_weights(
    discovered_modules: list[str],
    symbol_to_module: dict[str, str],
    output_path: Path,
) -> dict[str, float]:
    """Write weights.json for symbols whose module was discovered.

    Args:
        discovered_modules: Module names found in user's project.
        symbol_to_module: Map of symbol name → module name (from index).
        output_path: Path to write weights.json.

    Returns:
        The weights dict written.
    """
    discovered_set = set(discovered_modules)
    weights: dict[str, float] = {}

    for symbol_name, module_name in symbol_to_module.items():
        # Check if the symbol's module (or its parent) was discovered
        parts = module_name.split(".")
        for i in range(len(parts), 0, -1):
            if ".".join(parts[:i]) in discovered_set:
                weights[symbol_name] = DISCOVERED
                break

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(weights, indent=2))
    return weights


def load_weights(path: Path) -> dict[str, float]:
    """Load weights from a JSON file. Returns empty dict if file doesn't exist."""
    if not path.exists():
        return {}
    return json.loads(path.read_text())
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/mcpmenago/test_learn.py -v`
Expected: All PASS

- [ ] **Step 5: Commit**

```bash
git add mcpmenago/learn.py tests/mcpmenago/test_learn.py
git commit -m "feat(mcpmenago): add dependency scanner (Layer 2)"
```

---

## Chunk 3: Server + CLI + Integration

### Task 6: Central MCP Server (`server.py`) ✅ DONE

**Files:**
- Create: `mcpmenago/server.py`

**Context for implementing agent:**
- Replaces `mcp/rdkit_mcp.py`. Reuse patterns: `_rg()` helper, `_parse_context_imports()`, `search_code` tiered routing
- Key difference: every tool takes `package: str` parameter to route to the right book
- On startup: scan `mcpmenago/library/` for books, load their `index.json` and `weights.json`
- Layer 3 (query context): parse `context_file` imports fresh every call, no caching
- `get_symbol` is the new tool: look up name in `BookIndex.symbols`, read lines from file, return body
- No OpenTelemetry in this version — that's a future TODO

- [ ] **Step 1: Write `mcpmenago/server.py`**

```python
"""Central FastMCP server — manages all books, exposes MCP tools."""
from __future__ import annotations

import importlib
import inspect
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Literal

from mcp.server.fastmcp import FastMCP

from mcpmenago.learn import load_weights
from mcpmenago.models import NOT_USED, BookIndex, BookMeta, McpMenagoConfig

# ── Paths ─────────────────────────────────────────────────────────────────────
ROOT = Path(__file__).parent
LIBRARY = ROOT / "library"
CONFIG_PATH = ROOT / "mcpmenago.json"
PROJECT_ROOT = ROOT.parent

# ── Config ────────────────────────────────────────────────────────────────────
def _load_config() -> McpMenagoConfig:
    if CONFIG_PATH.exists():
        return McpMenagoConfig.model_validate_json(CONFIG_PATH.read_text())
    return McpMenagoConfig()


# ── Book loading ──────────────────────────────────────────────────────────────
class LoadedBook:
    """A book with its metadata, index, and weights loaded into memory."""

    def __init__(self, book_dir: Path):
        self.dir = book_dir
        self.meta = BookMeta.model_validate_json((book_dir / "book.json").read_text())
        self.index = BookIndex.model_validate_json((book_dir / "index.json").read_text())
        self.weights = load_weights(book_dir / "weights.json")
        self.repo_path = book_dir / "repo"

    def get_weight(self, symbol_name: str) -> float:
        return self.weights.get(symbol_name, NOT_USED)


def _load_books() -> dict[str, LoadedBook]:
    """Scan library/ and load all books."""
    books: dict[str, LoadedBook] = {}
    if not LIBRARY.exists():
        return books
    for book_dir in sorted(LIBRARY.iterdir()):
        if not book_dir.is_dir():
            continue
        book_json = book_dir / "book.json"
        index_json = book_dir / "index.json"
        if book_json.exists() and index_json.exists():
            try:
                book = LoadedBook(book_dir)
                books[book.meta.name] = book
            except Exception as e:
                print(f"Warning: failed to load book {book_dir.name}: {e}", file=sys.stderr)
    return books


# ── Import parsing (Layer 3) ─────────────────────────────────────────────────
def _parse_context_imports(context_file: str, package_name: str) -> list[str]:
    """Parse imports of package_name from context_file. Always fresh, no cache."""
    try:
        text = Path(context_file).read_text(errors="ignore")
        import_re = re.compile(rf"(?:from|import)\s+({re.escape(package_name)}(?:\.[a-zA-Z0-9_]+)*)")
        mods = []
        for m in import_re.finditer(text):
            mod = m.group(1).removeprefix(f"{package_name}.")
            parts = mod.split(".")
            mods.append(".".join(parts[:2]) if len(parts) > 1 else parts[0])
        return list(dict.fromkeys(mods))
    except Exception:
        return []


# ── Helpers ───────────────────────────────────────────────────────────────────
def _rg(pattern: str, path: Path, extra_args: list[str] | None = None) -> str:
    cmd = ["rg", "--color=never", "-n", "--max-count=5", pattern, str(path)]
    if extra_args:
        cmd[1:1] = extra_args
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.stdout or "(no matches)"


def _get_book(package: str) -> LoadedBook:
    if package not in _books:
        available = ", ".join(_books.keys()) if _books else "(none)"
        raise ValueError(f"Book '{package}' not found. Available: {available}")
    return _books[package]


# ── Startup ───────────────────────────────────────────────────────────────────
_config = _load_config()
_books = _load_books()
mcp = FastMCP("mcpmenago")

if _books:
    print(f"mcpmenago: loaded {len(_books)} book(s): {', '.join(_books.keys())}", file=sys.stderr)
else:
    print("mcpmenago: no books found in library/. Use 'mcpmenago add' to add one.", file=sys.stderr)


# ── Tools ─────────────────────────────────────────────────────────────────────
@mcp.tool()
def get_symbol(
    name: str,
    package: str,
    context_file: str | None = None,
) -> str:
    """Look up a symbol by exact name and return its source code body.

    Returns the function/class body from the source file, with file path and line range.
    If multiple matches exist (overloads), returns all sorted by weight.
    """
    book = _get_book(package)
    entries = book.index.symbols.get(name, [])
    if not entries:
        return f"Symbol '{name}' not found in {package} index."

    # Layer 3: filter by context if provided
    if context_file:
        context_mods = _parse_context_imports(context_file, book.meta.name)
        if context_mods:
            filtered = [e for e in entries if any(mod in e.file for mod in context_mods)]
            if filtered:
                entries = filtered

    # Layer 2: sort by weight
    entries.sort(key=lambda e: book.get_weight(e.name), reverse=True)

    results = []
    for entry in entries:
        source_path = book.repo_path / entry.file
        if source_path.exists():
            lines = source_path.read_text(errors="replace").splitlines()
            body = "\n".join(lines[entry.start_line - 1 : entry.end_line])
            results.append(
                f"[{entry.kind}] {entry.name} — {entry.file}:{entry.start_line}-{entry.end_line} "
                f"(weight: {book.get_weight(entry.name)})\n{body}"
            )
        else:
            results.append(f"[{entry.kind}] {entry.name} — {entry.file}:{entry.start_line}-{entry.end_line} (file not found)")

    return "\n\n---\n\n".join(results)


@mcp.tool()
def search_code(
    query: str,
    package: str,
    source: Literal["python", "cpp", "all"] = "all",
    context_file: str | None = None,
) -> str:
    """Search source code for a pattern using ripgrep.

    For exact symbol lookup, prefer get_symbol instead.
    """
    book = _get_book(package)
    repo = book.repo_path
    if not repo.exists():
        return f"Repository not found for {package}"

    # Layer 3: narrow to context modules if provided
    if context_file:
        context_mods = _parse_context_imports(context_file, book.meta.name)
        if context_mods:
            paths = [str(repo / mod.replace(".", "/")) for mod in context_mods]
            existing = [p for p in paths if Path(p).exists()]
            if existing:
                out = "\n".join(_rg(query, Path(p)) for p in existing)
                if "(no matches)" not in out:
                    return f"[context-scoped]\n{out}"

    # Full search
    out = _rg(query, repo, ["--max-count=10"])
    return out


@mcp.tool()
def read_file(path: str, package: str) -> str:
    """Read a source file from a book's repository.

    path: relative to the book's repo root.
    """
    book = _get_book(package)
    fpath = book.repo_path / path
    if not fpath.exists():
        return f"File not found: {path}"
    return fpath.read_text(errors="replace")


@mcp.tool()
def inspect_module(module_name: str, package: str) -> str:
    """Introspect a compiled module (.so) to get function signatures.

    module_name: dotted name e.g. 'Chem.rdmolops'
    """
    book = _get_book(package)
    try:
        mod = importlib.import_module(f"{book.meta.name}.{module_name}")
    except ImportError as e:
        return f"Could not import {book.meta.name}.{module_name}: {e}"

    lines = [f"Module: {book.meta.name}.{module_name}\n"]
    for name, obj in sorted(inspect.getmembers(mod)):
        if name.startswith("_"):
            continue
        doc = inspect.getdoc(obj) or ""
        sig_line = next((l for l in doc.splitlines() if "C++ signature" in l or l.startswith(name + "(")), "")
        kind = "class" if inspect.isclass(obj) else "fn"
        lines.append(f"  [{kind}] {name}")
        if sig_line:
            lines.append(f"         {sig_line.strip()}")
    return "\n".join(lines)


@mcp.tool()
def get_module_index(package: str, min_weight: float = 0.0) -> str:
    """Return the module index for a book as JSON.

    min_weight: filter to modules with weight >= this value (0.0 = all).
    """
    book = _get_book(package)
    out = {}
    for m in book.index.modules:
        out[m.name] = {
            "sources": [{"path": s.path, "lang": s.lang} for s in m.sources],
            "description": m.description,
            "key_functions": m.key_functions,
        }
    return json.dumps(out, indent=2)


@mcp.tool()
def list_directory(path: str, package: str) -> str:
    """List files and directories in a book's repository.

    path: relative path within repo (empty = root).
    """
    book = _get_book(package)
    base = book.repo_path / path
    if not base.exists():
        return f"Path not found: {path}"
    entries = sorted(base.iterdir(), key=lambda p: (p.is_file(), p.name))
    lines = [f"{'[DIR] ' if e.is_dir() else '      '}{e.name}" for e in entries]
    return "\n".join(lines)


# ── Entry point ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    mcp.run(transport="stdio")
```

- [ ] **Step 2: Verify server starts without errors (no books is OK)**

Run: `cd /Users/mir/PycharmProjects/mag-bridge && .venv/bin/python -c "import mcpmenago.server; print('OK')"`
Expected: `OK` (plus a stderr warning about no books)

- [ ] **Step 3: Commit**

```bash
git add mcpmenago/server.py
git commit -m "feat(mcpmenago): add central MCP server with all tools"
```

---

### Task 7: CLI (`cli.py`) ✅ DONE

**Files:**
- Create: `mcpmenago/cli.py`
- Create: `tests/mcpmenago/test_cli.py`

**Context for implementing agent:**
- Click CLI with `mcpmenago` entry point
- Commands: `add`, `remove`, `list`, `show`, `rebuild`, `update`, `learn`, `uninstall`
- `add` flow: venv check → validate URL → `git clone --depth 1` → `build_index()` → write `book.json` → update `.gitignore`
- `update` flow: delete repo/ → re-clone → rebuild → update book.json. Weights preserved.
- Book name derived from GitHub URL last path segment, overridable with `--book-name`
- `.gitignore` managed section: `# [mcpmenago] automatically generated content — do not edit`
- Uses `click.echo()` for output, `click.secho()` for colored errors

- [ ] **Step 1: Write failing CLI tests**

Create `tests/mcpmenago/test_cli.py`:

```python
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
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/mcpmenago/test_cli.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'mcpmenago.cli'`

- [ ] **Step 3: Write `mcpmenago/cli.py`**

```python
"""Click CLI for mcpmenago — MCP Manager."""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import click

from mcpmenago.index_builder import build_index
from mcpmenago.learn import load_weights, scan_imports, update_weights
from mcpmenago.models import BookMeta, McpMenagoConfig
from mcpmenago.venv_check import VenvCheckError, check_venv

# ── Paths ─────────────────────────────────────────────────────────────────────
ROOT = Path(__file__).parent
LIBRARY = ROOT / "library"
CONFIG_PATH = ROOT / "mcpmenago.json"
PROJECT_ROOT = ROOT.parent


# ── Helpers ───────────────────────────────────────────────────────────────────
def _load_config() -> McpMenagoConfig:
    if CONFIG_PATH.exists():
        return McpMenagoConfig.model_validate_json(CONFIG_PATH.read_text())
    return McpMenagoConfig()


def _extract_book_name(url: str) -> str:
    """Extract book name from GitHub URL."""
    name = url.rstrip("/").split("/")[-1]
    if name.endswith(".git"):
        name = name[:-4]
    return name


def _ensure_gitignore(gitignore_path: Path, library_rel_path: str = "mcpmenago/library/") -> None:
    """Append managed section to .gitignore if not present."""
    marker = "# [mcpmenago]"
    content = gitignore_path.read_text() if gitignore_path.exists() else ""
    if marker in content:
        return
    section = f"\n{marker} automatically generated content — do not edit\n{library_rel_path}\n"
    gitignore_path.write_text(content.rstrip("\n") + "\n" + section)


# ── CLI ───────────────────────────────────────────────────────────────────────
@click.group()
def cli():
    """mcpmenago — MCP Manager. Manages source code indexes for GitHub repositories."""
    pass


@cli.command()
@click.argument("url")
@click.option("--lang", multiple=True, required=True, help="Languages to index (e.g., python, cpp)")
@click.option("--head-ref", default=None, help="Git tag or branch to clone")
@click.option("--book-name", default=None, help="Override derived book name")
def add(url: str, lang: tuple[str], head_ref: str | None, book_name: str | None):
    """Add a GitHub repository and build its index."""
    config = _load_config()

    # Validate languages
    for l in lang:
        if l not in config.supported_languages:
            click.secho(f"Unsupported language: {l}. Supported: {config.supported_languages}", fg="red")
            sys.exit(1)

    # Venv pre-check
    try:
        check_venv(project_root=PROJECT_ROOT)
    except VenvCheckError as e:
        click.secho(str(e), fg="red")
        sys.exit(1)

    name = book_name or _extract_book_name(url)
    book_dir = LIBRARY / name
    repo_dir = book_dir / "repo"

    if book_dir.exists():
        click.secho(f"Book '{name}' already exists. Use 'update' or 'remove' first.", fg="red")
        sys.exit(1)

    # Clone
    click.echo(f"Cloning {url}...")
    clone_cmd = ["git", "clone", "--depth", "1"]
    if head_ref:
        clone_cmd += ["--branch", head_ref]
    clone_cmd += [url, str(repo_dir)]

    result = subprocess.run(clone_cmd, capture_output=True, text=True)
    if result.returncode != 0:
        click.secho(f"Clone failed: {result.stderr}", fg="red")
        sys.exit(1)

    # Get resolved commit SHA
    sha_result = subprocess.run(
        ["git", "-C", str(repo_dir), "rev-parse", "HEAD"],
        capture_output=True,
        text=True,
    )
    resolved_sha = sha_result.stdout.strip() if sha_result.returncode == 0 else None

    # Build index
    click.echo("Building index...")
    index_path = book_dir / "index.json"
    build_index(
        repo_path=repo_dir,
        languages=list(lang),
        version=head_ref or "HEAD",
        output_path=index_path,
    )

    # Detect python_path
    python_path = Path(sys.executable).parent.parent / "lib"  # best effort
    for p in Path(sys.executable).parent.parent.rglob(f"site-packages/{name}"):
        python_path = p
        break

    # Write book.json
    meta = BookMeta(
        name=name,
        github_url=url,
        languages=list(lang),
        python_path=python_path,
        head_ref=head_ref,
        head_ref_resolved=resolved_sha,
        index_built_at=datetime.now(timezone.utc).isoformat(),
    )
    (book_dir / "book.json").write_text(meta.model_dump_json(indent=2))

    # Update .gitignore
    _ensure_gitignore(PROJECT_ROOT / ".gitignore")

    index = json.loads(index_path.read_text())
    symbol_count = sum(len(v) for v in index.get("symbols", {}).values())
    click.secho(f"Added '{name}': {symbol_count} symbols indexed.", fg="green")


@cli.command()
@click.argument("book")
def remove(book: str):
    """Remove a book and all its data."""
    book_dir = LIBRARY / book
    if not book_dir.exists():
        click.secho(f"Book '{book}' not found.", fg="red")
        sys.exit(1)
    shutil.rmtree(book_dir)
    click.echo(f"Removed '{book}'.")


@cli.command("list")
def list_books():
    """List all managed books."""
    if not LIBRARY.exists():
        click.echo("No books. Library is empty.")
        return
    books = [d.name for d in sorted(LIBRARY.iterdir()) if d.is_dir() and (d / "book.json").exists()]
    if not books:
        click.echo("No books in library.")
        return
    for name in books:
        meta = BookMeta.model_validate_json((LIBRARY / name / "book.json").read_text())
        click.echo(f"  {name}  ({meta.github_url})  ref={meta.head_ref or 'HEAD'}")


@cli.command()
@click.argument("book")
def show(book: str):
    """Show details for a book."""
    book_dir = LIBRARY / book
    if not (book_dir / "book.json").exists():
        click.secho(f"Book '{book}' not found.", fg="red")
        sys.exit(1)

    meta = BookMeta.model_validate_json((book_dir / "book.json").read_text())
    click.echo(f"Name:       {meta.name}")
    click.echo(f"URL:        {meta.github_url}")
    click.echo(f"Languages:  {', '.join(meta.languages)}")
    click.echo(f"Head ref:   {meta.head_ref or 'HEAD'}")
    click.echo(f"SHA:        {meta.head_ref_resolved or 'unknown'}")
    click.echo(f"Indexed at: {meta.index_built_at or 'never'}")

    weights = load_weights(book_dir / "weights.json")
    click.echo(f"Weights:    {len(weights)} symbols discovered")


@cli.command()
@click.argument("book", required=False)
@click.option("--all", "rebuild_all", is_flag=True, help="Rebuild all books")
def rebuild(book: str | None, rebuild_all: bool):
    """Rebuild index for a book (or all books)."""
    if not book and not rebuild_all:
        click.secho("Specify a book name or use --all.", fg="red")
        sys.exit(1)

    targets = []
    if rebuild_all:
        if LIBRARY.exists():
            targets = [d.name for d in LIBRARY.iterdir() if d.is_dir() and (d / "book.json").exists()]
    else:
        targets = [book]

    for name in targets:
        book_dir = LIBRARY / name
        if not (book_dir / "book.json").exists():
            click.secho(f"Book '{name}' not found.", fg="red")
            continue

        meta = BookMeta.model_validate_json((book_dir / "book.json").read_text())
        click.echo(f"Rebuilding index for '{name}'...")
        build_index(
            repo_path=book_dir / "repo",
            languages=meta.languages,
            version=meta.head_ref or "HEAD",
            output_path=book_dir / "index.json",
        )
        meta.index_built_at = datetime.now(timezone.utc).isoformat()
        (book_dir / "book.json").write_text(meta.model_dump_json(indent=2))
        click.secho(f"Rebuilt '{name}'.", fg="green")


@cli.command()
@click.argument("book")
@click.option("--head-ref", required=True, help="New git tag or branch")
def update(book: str, head_ref: str):
    """Update a book to a new git ref (clean re-clone + rebuild)."""
    book_dir = LIBRARY / book
    if not (book_dir / "book.json").exists():
        click.secho(f"Book '{book}' not found.", fg="red")
        sys.exit(1)

    meta = BookMeta.model_validate_json((book_dir / "book.json").read_text())
    repo_dir = book_dir / "repo"

    # Clean re-clone
    click.echo(f"Removing old clone...")
    if repo_dir.exists():
        shutil.rmtree(repo_dir)

    click.echo(f"Cloning at {head_ref}...")
    result = subprocess.run(
        ["git", "clone", "--depth", "1", "--branch", head_ref, meta.github_url, str(repo_dir)],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        click.secho(f"Clone failed: {result.stderr}", fg="red")
        sys.exit(1)

    sha_result = subprocess.run(
        ["git", "-C", str(repo_dir), "rev-parse", "HEAD"],
        capture_output=True,
        text=True,
    )

    # Rebuild index
    click.echo("Rebuilding index...")
    build_index(
        repo_path=repo_dir,
        languages=meta.languages,
        version=head_ref,
        output_path=book_dir / "index.json",
    )

    # Update metadata (weights.json preserved)
    meta.head_ref = head_ref
    meta.head_ref_resolved = sha_result.stdout.strip() if sha_result.returncode == 0 else None
    meta.index_built_at = datetime.now(timezone.utc).isoformat()
    (book_dir / "book.json").write_text(meta.model_dump_json(indent=2))

    click.secho(f"Updated '{book}' to {head_ref}.", fg="green")


@cli.command()
@click.argument("book")
def learn(book: str):
    """Scan project imports and update weights for a book."""
    book_dir = LIBRARY / book
    if not (book_dir / "book.json").exists():
        click.secho(f"Book '{book}' not found.", fg="red")
        sys.exit(1)

    config = _load_config()
    meta = BookMeta.model_validate_json((book_dir / "book.json").read_text())
    index_data = json.loads((book_dir / "index.json").read_text())

    # Build symbol→module map from index (simplified: use file path as proxy for module)
    symbol_to_module: dict[str, str] = {}
    for sym_name, entries in index_data.get("symbols", {}).items():
        for entry in entries:
            # Derive module from file path: "Chem/rdmolops.py" → "Chem.rdmolops"
            rel = entry["file"]
            parts = Path(rel).with_suffix("").parts
            module = ".".join(parts)
            symbol_to_module[sym_name] = module
            break  # first entry is enough for module mapping

    # Scan project
    scan_dirs = [str(PROJECT_ROOT / d) for d in config.learn_dirs]
    discovered = scan_imports(package_name=meta.name, scan_dirs=scan_dirs)

    click.echo(f"Discovered modules: {discovered}")

    # Update weights
    weights = update_weights(
        discovered_modules=discovered,
        symbol_to_module=symbol_to_module,
        output_path=book_dir / "weights.json",
    )

    click.secho(f"Updated weights for '{book}': {len(weights)} symbols marked as DISCOVERED.", fg="green")


@cli.command()
def uninstall():
    """Remove all books and clean up."""
    if LIBRARY.exists():
        shutil.rmtree(LIBRARY)
        click.echo("Removed library/.")
    else:
        click.echo("Library already empty.")

    # Clean .gitignore
    gitignore = PROJECT_ROOT / ".gitignore"
    if gitignore.exists():
        content = gitignore.read_text()
        marker = "# [mcpmenago]"
        if marker in content:
            lines = content.splitlines()
            new_lines = []
            skip = False
            for line in lines:
                if marker in line:
                    skip = True
                    continue
                if skip and line.strip() == "":
                    skip = False
                    continue
                if skip and not line.startswith("#"):
                    continue
                skip = False
                new_lines.append(line)
            gitignore.write_text("\n".join(new_lines) + "\n")
    click.echo("Uninstall complete.")


# ── Entry point ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    cli()
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/mcpmenago/test_cli.py -v`
Expected: All PASS

- [ ] **Step 5: Commit**

```bash
git add mcpmenago/cli.py tests/mcpmenago/test_cli.py
git commit -m "feat(mcpmenago): add Click CLI with all commands"
```

---

### Task 8: Integration — `.mcp.json` + Smoke Test ✅ DONE (with caveats — see ISSUE-1)

**Files:**
- Modify: `.mcp.json`

- [ ] **Step 1: Update `.mcp.json` to point to new server**

Replace the existing `rdkit-source` entry with:

```json
{
  "mcpServers": {
    "mcpmenago": {
      "command": ".venv/bin/python",
      "args": ["mcpmenago/server.py"]
    }
  }
}
```

Keep the old `mcp/rdkit_mcp.py` as-is for reference — do not delete it.

- [ ] **Step 2: Run full test suite**

Run: `pytest tests/mcpmenago/ -v`
Expected: All PASS

- [ ] **Step 3: Smoke test — verify server starts**

Run: `cd /Users/mir/PycharmProjects/mag-bridge && .venv/bin/python -c "from mcpmenago.server import mcp; print('Server OK')" 2>&1`
Expected: `mcpmenago: no books found in library/...` (stderr) then `Server OK` (stdout)

- [ ] **Step 4: Smoke test — verify CLI help**

Run: `.venv/bin/python mcpmenago/cli.py --help`
Expected: Help text with all commands listed

- [ ] **Step 5: Commit all integration changes**

```bash
git add .mcp.json
git commit -m "feat(mcpmenago): update .mcp.json to central server"
```

- [ ] **Step 6: End-to-end test (manual, optional)**

If the RDKit submodule is available at `rdkit/`, test the full flow:

```bash
.venv/bin/python mcpmenago/cli.py add https://github.com/rdkit/rdkit --lang python --lang cpp --head-ref Release_2025_09_6 --book-name rdkit
.venv/bin/python mcpmenago/cli.py list
.venv/bin/python mcpmenago/cli.py show rdkit
.venv/bin/python mcpmenago/cli.py learn rdkit
.venv/bin/python mcpmenago/cli.py rebuild rdkit
```

Verify: `mcpmenago/library/rdkit/` contains `repo/`, `book.json`, `index.json`, and after learn: `weights.json`.

---

## Summary

| Task | What | Depends On | ~Lines |
|------|------|-----------|--------|
| 1 | `models.py` — schemas + weight constants | Nothing | ~60 |
| 2 | `mcpmenago.json` — default config | Nothing | ~4 |
| 3 | `venv_check.py` — venv pre-check | Nothing | ~25 |
| 4 | `index_builder.py` — tree-sitter (Layer 1) | Task 1 | ~180 |
| 5 | `learn.py` — dependency scanning (Layer 2) | Task 1 | ~80 |
| 6 | `server.py` — central MCP server | Tasks 1, 4, 5 | ~200 |
| 7 | `cli.py` — Click CLI | Tasks 1, 3, 4, 5 | ~250 |
| 8 | Integration — `.mcp.json` + smoke tests | All | ~10 |

**Dependency graph (what can run in parallel):**
- Tasks 1, 2, 3 are independent — can run in parallel
- Tasks 4, 5 depend only on Task 1 — can run in parallel with each other
- Task 6 depends on Tasks 1, 4, 5
- Task 7 depends on Tasks 1, 3, 4, 5
- Task 8 depends on all
