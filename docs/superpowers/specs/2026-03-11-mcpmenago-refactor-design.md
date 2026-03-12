# mcpmenago Refactor Design
**Date:** 2026-03-11
**Scope:** `mcpmenago/mcpmenago/` — structural cleanup, no logic changes
**Tests:** 38 tests must remain green throughout

---

## Problem

Two structural issues in the current codebase:

1. **Duplicated path constants + config loader** — 5 path constants and `_load_config()` are copy-pasted verbatim in both `cli.py` and `server.py`. Any change to the filesystem layout requires two edits.

2. **Scattered book I/O** — loading `BookMeta`, `BookIndex`, and weights from disk is repeated inline across 5+ CLI commands and `LoadedBook.__init__`. Callers manually construct paths and call Pydantic `.model_validate_json()` directly, coupling them to the storage format.

---

## Decisions

| Decision | Choice | Rationale |
|---|---|---|
| Path building | `Path.joinpath()`, no `/` operator | Explicit, consistent with stdlib style |
| Path module | `paths.py` — module-level constants only | Stateless, importable anywhere, no class overhead |
| Book I/O | `BookStore` — static methods class | Centralises storage knowledge, no instantiation needed |
| Config loader | `load_settings(path)` in `models.py` | 3 lines, lives next to the model it loads |
| Rename | `McpMenagoConfig` → `Settings` | Less redundant, cleaner |
| `LoadedBook` | Stays in `server.py` | Server-specific: in-memory for MCP session lifetime |
| `settings.py` | Not created | YAGNI — config is just one model + one loader |

---

## New Files

### `mcpmenago/paths.py`
Five module-level constants. No class, no functions, no I/O.

```python
MCPMENAGO_ROOT = Path(__file__).parent.parent
LIBRARY        = MCPMENAGO_ROOT.joinpath("library")
CONFIG_PATH    = MCPMENAGO_ROOT.joinpath("mcpmenago.json")
PROJECT_ROOT   = MCPMENAGO_ROOT.parent
GITIGNORE      = PROJECT_ROOT.joinpath(".gitignore")
```

### `mcpmenago/store.py`
`BookStore` — static methods only. All book-level path construction and I/O lives here.

| Method | Returns | Replaces |
|---|---|---|
| `book_dir(name)` | `Path` | `LIBRARY / name` everywhere |
| `load_meta(name)` | `BookMeta` | `BookMeta.model_validate_json(...)` ×5 |
| `save_meta(name, meta)` | `None` | `(book_dir / "book.json").write_text(...)` ×3 |
| `load_index(name)` | `BookIndex` | `BookIndex.model_validate_json(...)` |
| `load_weights(name)` | `dict[str, float]` | `load_weights(book_dir / "weights.json")` |
| `list_books()` | `list[str]` | inline `LIBRARY.iterdir()` pattern ×2 |

`BookStore` imports from `paths` (for `LIBRARY`) and `models` (for Pydantic types). No circular imports.

---

## Changes to Existing Files

### `models.py`
- `McpMenagoConfig` → `Settings` *(already done)*
- Add `load_settings(path: Path) -> Settings` — replaces both `_load_config()` copies

### `cli.py`
- Remove: 5 path constants, `_load_config()`
- Add imports: `LIBRARY, CONFIG_PATH, PROJECT_ROOT, GITIGNORE` from `paths`; `BookStore` from `store`; `load_settings` from `models`
- Replace all inline path+load patterns with `BookStore` calls

### `server.py`
- Remove: 5 path constants, `_load_config()`
- Same import additions as `cli.py`
- `LoadedBook` and `_load_books()` stay, but `_load_books()` can use `BookStore.list_books()` internally

---

## What Does NOT Change

- File/module names (no filesystem reorganisation)
- All business logic in every file
- `index_builder.py` and `learn.py` — untouched
- `LoadedBook` class structure
- Test files — no test changes expected; all 38 must pass

---

## Test Coverage for New Code

`BookStore` and `load_settings` are new code and need tests:
- `test_store.py` — `load_meta`, `save_meta`, `load_index`, `load_weights`, `list_books` using `tmp_path` fixtures
- `test_models.py` — add `load_settings` happy path + missing file fallback

---

## Module Dependency Graph (after refactor)

```
paths.py        ← no deps
models.py       ← no deps (+ load_settings)
store.py        ← paths, models, learn (load_weights)
learn.py        ← models
index_builder.py← models
cli.py          ← paths, models, store, learn, index_builder
server.py       ← paths, models, store, learn
```

Clean layering. No circular dependencies.
