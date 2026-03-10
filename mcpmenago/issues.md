# mcpmenago Issues

## Critical

**ISSUE-2: Config and path constants duplicated across server.py and cli.py**
`ROOT`, `MCPMENAGO_ROOT`, `LIBRARY`, `CONFIG_PATH`, `PROJECT_ROOT`, `_load_config()` are copy-pasted in both files. Extract to `mcpmenago/config.py`.
Priority: Critical

---

## Medium

**ISSUE-3: Import regex duplicated between server.py and learn.py**
`server._parse_context_imports()` reimplements the same logic already in `learn.scan_imports()`. Consolidate into a shared function in `learn.py`.
Priority: Medium

**ISSUE-4: `get_module_index` tool always returns empty**
`build_index()` never populates `BookIndex.modules`. The tool always returns `{}`. Either populate modules during indexing (group symbols by file path), or remove the tool.
Priority: Medium

**ISSUE-5: `search_code` `source` parameter is silently ignored**
Ripgrep always searches the full repo regardless of `source="python"` or `source="cpp"`. Misleads Claude. Fix: pass `--glob '*.py'` / `--glob '*.{h,cpp}'` based on source value.
Priority: Medium

**ISSUE-7: No server.py tests**
Server is the primary MCP interface with zero test coverage. Add tests for `LoadedBook`, `_get_book` error path, `_parse_context_imports`, and at least one tool (e.g. `get_symbol` with a fixture book).
Priority: Medium

**ISSUE-10: Silenced exceptions hide bugs**
`learn.py` and `server._parse_context_imports()` use bare `except Exception: pass`. Log to stderr at minimum.
Priority: Medium

**ISSUE-13: Drop site-packages support in favor of fully managed shallow clones**
`BookMeta.python_path` stores a path to the host's site-packages, and `inspect_module` calls `importlib.import_module()` against it. This couples the server to the host's installed packages — inconsistent with the standalone clone-based philosophy. Proposal: remove `python_path` from `BookMeta`, remove `inspect_module` tool. All source access goes through the shallow clone in `library/<book>/repo/`. This simplifies the model, eliminates host env coupling, and aligns with the standalone plugin target.
Priority: Medium

---

## Low

**ISSUE-8: Outdated tree-sitter API in plan documents**
Planning docs reference old `PY_LANGUAGE.query(...)` API. Implementation uses `Query(PY_LANGUAGE, ...)` + `QueryCursor(...).matches()`. Update or remove plan docs.
Priority: Low

**ISSUE-11: tree-sitter language auto-detection**
MVP always installs both grammars. Future: detect language needs from project, install minimal set, prompt via interactive CLI wizard.
Priority: Low

**ISSUE-12: Versioning — setuptools_scm blocked until extraction**
`setuptools_scm` cannot detect a version for `mcpmenago/` because it is a subdirectory of `mag-bridge` with no own git tags. Current workaround: `SETUPTOOLS_SCM_PRETEND_VERSION=0.1.0`. Permanent fix: extract to own repo with own tags, then setuptools_scm works natively.
Priority: Very Low
