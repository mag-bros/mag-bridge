## Project Status (2026-03-10)

**Overall:** Chunks 1-3 implemented. 41/41 tests pass. All source files exist. **Not production-ready** — critical issues below must be resolved before first real use.

### Critical Issues

**ISSUE-2: `_load_config()` duplicated + `_config` unused in server**
- `_load_config()` is copy-pasted identically in both `server.py:25` and `cli.py:26`.
- `server.py:98` stores `_config = _load_config()` at module level but **never reads it** — no tool uses `_config.learn_dirs` or `_config.supported_languages`.
- The same path constants (`ROOT`, `LIBRARY`, `CONFIG_PATH`, `PROJECT_ROOT`) are duplicated across both files.
- **Fix:** Extract shared constants + `_load_config()` into a `mcpmenago/config.py` module. Both `server.py` and `cli.py` import from it.

### Medium Issues

**ISSUE-3: Import regex duplicated between `server.py` and `learn.py`**
- `server.py:70` inlines `re.compile(rf"(?:from|import)\s+...")` — the exact same regex that `learn.py:11` `_build_import_re()` already encapsulates.
- `server.py._parse_context_imports()` and `learn.py.scan_imports()` share 80% logic (regex build, module normalization, `.ipynb` handling in `learn.py` only).
- **Fix:** `server.py` should call `learn._build_import_re()` or better yet, extract a shared `parse_imports_from_text(text, package_name)` function in `learn.py`.

**ISSUE-4: `build_index()` never populates `modules` — `get_module_index` is dead**
- `index_builder.py:200` initializes `modules: list[ModuleEntry] = []` but never appends to it.
- The `BookIndex.modules` field is always empty after indexing.
- `server.py:get_module_index` tool iterates `book.index.modules` — will always return `{}`.
- **Impact:** The `get_module_index` MCP tool is functionally useless. Any Claude agent calling it gets nothing.
- **Fix:** Either populate `modules` during `build_index()` (group symbols by file → derive module entries), or mark `get_module_index` as not-yet-implemented in the tool description.

**ISSUE-5: `search_code` `source` parameter is ignored**
- `server.py:156` accepts `source: Literal["python", "cpp", "all"]` but the function body never reads it.
- ripgrep runs against the entire repo regardless of `source` value.
- **Impact:** Misleading to Claude — it thinks it can filter by language but actually can't.
- **Fix:** Add `--glob` args to `_rg()` based on `source` (e.g., `--glob '*.py'` for python).

### Low Issues / Observations

**ISSUE-6: `server.py` `_config` loaded but unused**
- Beyond duplication (ISSUE-2), the server never uses config at all. Neither `learn_dirs` nor `supported_languages` are consulted by any server tool. This is by design (server is read-only, `learn` is CLI-only) but the dead load adds confusion.

**ISSUE-7: No `server.py` tests**
- `test_cli.py` has 5 tests. `server.py` has 0. The server is the primary MCP interface — it should have tests for `LoadedBook`, `_get_book` (error path), `_parse_context_imports`, and at least one tool integration test.

**ISSUE-8: Plan's tree-sitter API drift was handled but not documented**
- Plan specified `PY_LANGUAGE.query(...)` and `match[1]` dict access.
- Actual implementation uses `Query(PY_LANGUAGE, ...)` and `QueryCursor(...).matches()` returning `(_, nodes)` tuples with list values (`nodes.get("def", [])`).
- The implementing agent adapted correctly, but the plan's code blocks are now misleading for future reference.

**ISSUE-9: `venv_check.py` path separator is Unix-only**
- `venv_check.py:24` checks `str(executable).startswith(str(venv_dir) + "/")` — hardcoded `/`. Won't work on Windows.
- Per CLAUDE.md this is a localhost app. If Windows support matters, use `Path.is_relative_to()` (Python 3.9+).
- Another venv issue: ```➜ python -m mcpmenago.cli add https://github.com/rdkit/rdkit --lang python
Active Python (/opt/homebrew/Cellar/python@3.13/3.13.2/Frameworks/Python.framework/Versions/3.13/bin/python3.13) is not inside the project venv (/Users/mir/PycharmProjects/mag-bridge/.venv).
Fix: python -m venv .venv && .venv/bin/pip install -r requirements.txt```

**ISSUE-10: Silenced exceptions in `learn.py` and `server.py`**
- `learn.py:45` bare `except Exception: pass` swallows all parse errors (corrupt notebooks, encoding issues).
- `server.py:77` same pattern for `_parse_context_imports`.
- At minimum, log to stderr so debugging isn't blind.
