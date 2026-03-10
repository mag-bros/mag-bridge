# mcpmenago Standalone Portability

**Date:** 2026-03-10
**Status:** Approved
**Goal:** Make `mcpmenago/` a self-contained, copy-pasteable directory ready for extraction to its own repository.

## Context

mcpmenago is an MCP server + CLI that manages source code indexes for GitHub repositories. It currently lives inside the mag-bridge project but is designed to become a standalone plugin/marketplace package. The implementation drifted from this vision in several ways:

- Tests live in `tests/mcpmenago/` (mag-bridge's test tree) instead of inside the module
- Dependencies are incomplete — `pyproject.toml` declares `mcp`, `tree-sitter`, `pydantic` but is missing `click`, `tree-sitter-python`, `tree-sitter-cpp`
- `venv_check.py` enforces mag-bridge's venv, which contradicts standalone identity
- `.mcp.json` hardcodes `.venv/bin/python` instead of using the MCP ecosystem standard (`uv`)
- README contains duplicated Python source code from `models.py`
- `issues.md` contains agentic-generated issues that need human-level re-evaluation

## Decisions

| # | Decision | Rationale |
|---|----------|-----------|
| D1 | Transition to `uv run` for MCP server execution | MCP ecosystem standard. All official Anthropic servers use `uv`/`uvx`. Eliminates venv management. |
| D2 | Drop `venv_check.py` entirely | `uv` handles environment isolation. The concept of "check if we're in the right venv" no longer applies. |
| D3 | Declare deps in `pyproject.toml`, not requirements.txt | `uv run --project` reads `pyproject.toml` natively. requirements.txt is redundant for `uv`-based workflow. |
| D4 | Install both `tree-sitter-python` and `tree-sitter-cpp` as base deps | MVP simplicity. Future issue for interactive language detection / minimal install. |
| D5 | Tests live inside `mcpmenago/tests/` | Self-contained module. Copy-paste extraction. |
| D6 | `pyproject.toml` — minimal changes only | User's golden file. Only update `dependencies` and add `[project.optional-dependencies] dev`. No structural changes. |

## Plan

### Step 1: Update pyproject.toml dependencies

**What:** Complete the runtime deps and add dev deps. Minimal changes only.

**Replace the existing `dependencies` line** in `[project]` section (currently `dependencies = ["mcp", "tree-sitter", "pydantic"]`) with:
```toml
dependencies = [
    "mcp",
    "tree-sitter",
    "tree-sitter-python",
    "tree-sitter-cpp",
    "pydantic",
    "click",
]
```

**Add new section** (after `[tool.setuptools]`):
```toml
[project.optional-dependencies]
dev = ["pytest"]
```

**Add `testpaths`** to the existing `[tool.pytest.ini_options]` section:
```toml
testpaths = ["tests"]
```

**Do NOT change:** build-system, tool.setuptools, tool.ruff, tool.pyright, tool.yamllint, or any other existing section.

### Step 2: Drop venv_check.py

**What:** Remove the venv validation concept entirely.

**Delete:**
- `mcpmenago/venv_check.py`
- `tests/mcpmenago/test_venv_check.py`

**Update `cli.py`:**
- Remove `from mcpmenago.venv_check import VenvCheckError, check_venv` (line 17)
- Remove the try/except block in `add()` that calls `check_venv()` (lines 74-78)

### Step 3: Move tests into mcpmenago/

**What:** Move `tests/mcpmenago/` → `mcpmenago/tests/`

**Files to move:**
- `tests/mcpmenago/__init__.py` → `mcpmenago/tests/__init__.py`
- `tests/mcpmenago/conftest.py` → `mcpmenago/tests/conftest.py`
- `tests/mcpmenago/test_models.py` → `mcpmenago/tests/test_models.py`
- `tests/mcpmenago/test_index_builder.py` → `mcpmenago/tests/test_index_builder.py`
- `tests/mcpmenago/test_learn.py` → `mcpmenago/tests/test_learn.py`
- `tests/mcpmenago/test_cli.py` → `mcpmenago/tests/test_cli.py`

Note: `test_venv_check.py` was already deleted in Step 2.

**After move:** Delete the empty `tests/mcpmenago/` directory (and its `__pycache__/`).

**Verify:** Run `uv run --project ./mcpmenago --extra dev pytest -v` from project root. All tests pass (minus removed venv_check tests). The `testpaths = ["tests"]` in pyproject.toml is relative to the project root (`mcpmenago/`), so pytest discovers `mcpmenago/tests/` automatically.

### Step 4: Update .mcp.json

**What:** Switch from hardcoded venv Python to `uv run`.

**Change `.mcp.json` (project root) to:**
```json
{
  "mcpServers": {
    "mcpmenago": {
      "command": "uv",
      "args": ["run", "--project", "./mcpmenago", "python", "mcpmenago/server.py"]
    }
  }
}
```

**Verify:** `uv run --project ./mcpmenago python mcpmenago/server.py` starts the server without import errors (it will block on stdin — that's correct STDIO transport behavior). Kill with Ctrl+C after confirming no errors.

### Step 5: Clean up README

**Keep (these sections are valuable):**
- Title + one-line description
- Quick Start (update installation to use `uv`)
- CLI Commands table
- Filesystem Layout (update to show `tests/` inside mcpmenago)
- Three-Layer Ranking Architecture (full section — this is the core design doc)
- Design Principles
- Stack table
- Decisions Log (add new decisions D1-D6 from this spec)
- TODO section (future enhancements)

**Remove:**
- Schemas section (BookMeta, BookIndex, SymbolEntry, ModuleEntry, McpMenagoConfig Python code blocks) — these duplicate `models.py`
- Weight Constants Python code block — in `models.py`
- Venv Pre-Check section — concept removed
- Installation section referencing `pip install -e .`

**Update:**
- `.mcp.json` example to use `uv run`
- Installation to: `uv sync --project ./mcpmenago` (or just "dependencies managed by uv via pyproject.toml")
- Filesystem Layout to include `tests/` directory
- Decisions Log with D1-D6

**Verify:** README contains no Python code blocks duplicating `models.py`, no references to `venv_check`, and no `pip install -e .` instructions.

### Step 6: Rewrite issues.md

**What:** Re-evaluate all issues through the standalone plugin lens. Human-readable, concise.

**Drop:**
- ISSUE-9 (venv symlink) — fixed then removed entirely
- ISSUE-6 (_config loaded but unused) — merged into ISSUE-2

**Keep and simplify:**
- ISSUE-2 → "Config/path duplication across server.py and cli.py" — extract to `config.py`
- ISSUE-3 → "Import regex duplication between server.py and learn.py" — consolidate
- ISSUE-4 → "get_module_index returns empty — modules never populated" — decide: implement or remove tool
- ISSUE-5 → "search_code source parameter is ignored" — add glob filtering or remove parameter
- ISSUE-7 → "No server.py tests" — add integration tests
- ISSUE-8 → "Plan code blocks reference outdated tree-sitter API" — update plan docs or remove
- ISSUE-10 → "Silenced exceptions hide bugs" — add stderr logging

**Add new:**
- ISSUE-11 → "Tree-sitter language auto-detection" — MVP installs all grammars; future: detect from project, install minimal set, interactive CLI support
- ISSUE-12 → "inspect_module requires host Python packages" — tool does `importlib.import_module()` which needs the indexed package installed in the same Python. Decide: document limitation, defer, or redesign for standalone context.

**Format:** Each issue gets a title, one-line impact, and priority (Critical/Medium/Low). No multi-paragraph fix descriptions.

**Verify:** issues.md contains no ISSUE-6 or ISSUE-9. Each remaining issue has title, one-line impact, and priority label. New ISSUE-11 and ISSUE-12 are present.

### Final Verification

After all steps, run from project root:
```bash
uv run --project ./mcpmenago --extra dev pytest -v
```
All tests pass (minus removed venv_check tests). Test count should be original count minus venv_check test count.

Also verify:
- `mcpmenago/venv_check.py` does not exist
- `tests/mcpmenago/` directory does not exist
- `mcpmenago/tests/` directory contains conftest.py and all test files
- README contains no Python code blocks duplicating `models.py` and no references to `venv_check`
