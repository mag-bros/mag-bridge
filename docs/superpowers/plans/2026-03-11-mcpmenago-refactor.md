# mcpmenago Refactor Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Eliminate duplicated path constants and scattered book I/O by introducing `paths.py` and `store.py`, while keeping all 38 tests green throughout.

**Architecture:** `paths.py` exposes 5 module-level `Path` constants (no class, no I/O). `store.py` provides a `BookStore` class with static methods that own all book-level file access. `models.py` gains a `load_settings()` function. `cli.py` and `server.py` lose their duplicated path blocks and inline I/O patterns.

**Tech Stack:** Python 3.12+, pathlib, pydantic, pytest, uv

---

## Test command (run from `mcpmenago/` directory)

```bash
cd mcpmenago && uv run pytest -v
```

---

## Chunk 1: Foundation — `paths.py` and `load_settings()`

### Task 1: Create `paths.py`

**Files:**
- Create: `mcpmenago/mcpmenago/paths.py`
- Create: `mcpmenago/tests/test_paths.py`

- [ ] **Step 1: Write the failing tests**

Create `mcpmenago/tests/test_paths.py`:

```python
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
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
cd mcpmenago && uv run pytest tests/test_paths.py -v
```

Expected: `ImportError: cannot import name 'MCPMENAGO_ROOT' from 'mcpmenago.paths'` (module doesn't exist yet)

- [ ] **Step 3: Create `mcpmenago/mcpmenago/paths.py`**

```python
"""Global path constants for mcpmenago.

All paths are anchored to this file's location so they resolve correctly
regardless of the working directory from which mcpmenago is invoked.
"""

from __future__ import annotations

from pathlib import Path

# mcpmenago/mcpmenago/ → mcpmenago/
MCPMENAGO_ROOT = Path(__file__).parent.parent

# mcpmenago/library/
LIBRARY = MCPMENAGO_ROOT.joinpath("library")

# mcpmenago/mcpmenago.json
CONFIG_PATH = MCPMENAGO_ROOT.joinpath("mcpmenago.json")

# host project root (mag-bridge/)
PROJECT_ROOT = MCPMENAGO_ROOT.parent

# host project .gitignore
GITIGNORE = PROJECT_ROOT.joinpath(".gitignore")
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
cd mcpmenago && uv run pytest tests/test_paths.py -v
```

Expected: 7 passed

- [ ] **Step 5: Run full suite to confirm nothing broken**

```bash
cd mcpmenago && uv run pytest -v
```

Expected: 38 passed (no regressions)

- [ ] **Step 6: Commit**

```bash
git add mcpmenago/mcpmenago/paths.py mcpmenago/tests/test_paths.py
git commit -m "feat(mcpmenago): add paths.py with centralized global path constants"
```

---

### Task 2: Add `load_settings()` to `models.py`

**Files:**
- Modify: `mcpmenago/mcpmenago/models.py`
- Modify: `mcpmenago/tests/test_models.py`

- [ ] **Step 1: Write the failing tests**

Append to `mcpmenago/tests/test_models.py`:

```python
def test_load_settings_returns_defaults_when_file_missing(tmp_path):
    from mcpmenago.models import Settings, load_settings

    path = tmp_path / "mcpmenago.json"
    # file does not exist
    result = load_settings(path)
    assert isinstance(result, Settings)
    assert result.learn_dirs == ["src", "tests", "notebooks"]


def test_load_settings_reads_file_when_present(tmp_path):
    from mcpmenago.models import Settings, load_settings

    path = tmp_path / "mcpmenago.json"
    custom = Settings(learn_dirs=["lib"], supported_languages=["python"])
    path.write_text(custom.model_dump_json())

    result = load_settings(path)
    assert result.learn_dirs == ["lib"]
    assert result.supported_languages == ["python"]
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
cd mcpmenago && uv run pytest tests/test_models.py::test_load_settings_returns_defaults_when_file_missing tests/test_models.py::test_load_settings_reads_file_when_present -v
```

Expected: `ImportError: cannot import name 'load_settings'`

- [ ] **Step 3: Add `load_settings()` to `models.py`**

Add after the `Settings` class in `mcpmenago/mcpmenago/models.py`:

```python
def load_settings(path: Path) -> Settings:
    if path.exists():
        return Settings.model_validate_json(path.read_text())
    return Settings()
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
cd mcpmenago && uv run pytest tests/test_models.py -v
```

Expected: all model tests pass (including 2 new ones)

- [ ] **Step 5: Run full suite**

```bash
cd mcpmenago && uv run pytest -v
```

Expected: 40 passed

- [ ] **Step 6: Commit**

```bash
git add mcpmenago/mcpmenago/models.py mcpmenago/tests/test_models.py
git commit -m "feat(mcpmenago): add load_settings() to models.py, replacing duplicated _load_config()"
```

---

## Chunk 2: `BookStore` — centralised book I/O

### Task 3: Create `store.py` with `BookStore`

**Files:**
- Create: `mcpmenago/mcpmenago/store.py`
- Create: `mcpmenago/tests/test_store.py`

- [ ] **Step 1: Write the failing tests**

Create `mcpmenago/tests/test_store.py`:

```python
"""Tests for mcpmenago.store.BookStore."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from mcpmenago.models import BookIndex, BookMeta, ModuleEntry, ModuleSource, SymbolEntry


def _make_book_dir(tmp_path: Path, name: str = "rdkit") -> Path:
    """Create a minimal valid book directory under tmp_path/library/<name>/."""
    book_dir = tmp_path.joinpath("library", name)
    book_dir.mkdir(parents=True)

    meta = BookMeta(
        name=name,
        github_url="https://github.com/rdkit/rdkit",
        languages=["python"],
        python_path=Path(".venv/lib/python3.13/site-packages/rdkit"),
        head_ref="v1.0",
    )
    book_dir.joinpath("book.json").write_text(meta.model_dump_json(indent=2))

    index = BookIndex(
        version="1.0",
        modules=[
            ModuleEntry(
                name="Chem",
                sources=[ModuleSource(path="Chem/__init__.py", lang="python")],
            )
        ],
        symbols={
            "MolFromSmiles": [
                SymbolEntry(
                    name="MolFromSmiles",
                    kind="function",
                    file="Chem/__init__.py",
                    start_line=1,
                    end_line=5,
                    signature="def MolFromSmiles(smiles: str):",
                )
            ]
        },
    )
    book_dir.joinpath("index.json").write_text(index.model_dump_json(indent=2))

    weights = {"MolFromSmiles": 0.8}
    book_dir.joinpath("weights.json").write_text(json.dumps(weights))

    return book_dir


def test_book_dir_returns_path(tmp_path):
    from mcpmenago.store import BookStore

    library = tmp_path.joinpath("library")
    library.mkdir()
    result = BookStore.book_dir("rdkit", library)
    assert result == library.joinpath("rdkit")
    assert isinstance(result, Path)


def test_load_meta_returns_book_meta(tmp_path):
    from mcpmenago.store import BookStore

    book_dir = _make_book_dir(tmp_path, "rdkit")
    library = tmp_path.joinpath("library")
    meta = BookStore.load_meta("rdkit", library)
    assert isinstance(meta, BookMeta)
    assert meta.name == "rdkit"
    assert meta.head_ref == "v1.0"


def test_load_meta_raises_when_missing(tmp_path):
    from mcpmenago.store import BookStore

    library = tmp_path.joinpath("library")
    library.mkdir()
    (library / "rdkit").mkdir()
    with pytest.raises(FileNotFoundError):
        BookStore.load_meta("rdkit", library)


def test_save_meta_writes_book_json(tmp_path):
    from mcpmenago.store import BookStore

    _make_book_dir(tmp_path, "rdkit")
    library = tmp_path.joinpath("library")
    meta = BookStore.load_meta("rdkit", library)
    meta.head_ref = "v2.0"
    BookStore.save_meta("rdkit", meta, library)

    reloaded = BookStore.load_meta("rdkit", library)
    assert reloaded.head_ref == "v2.0"


def test_load_index_returns_book_index(tmp_path):
    from mcpmenago.store import BookStore

    _make_book_dir(tmp_path, "rdkit")
    library = tmp_path.joinpath("library")
    index = BookStore.load_index("rdkit", library)
    assert isinstance(index, BookIndex)
    assert "MolFromSmiles" in index.symbols


def test_load_weights_returns_dict(tmp_path):
    from mcpmenago.store import BookStore

    _make_book_dir(tmp_path, "rdkit")
    library = tmp_path.joinpath("library")
    weights = BookStore.load_weights("rdkit", library)
    assert isinstance(weights, dict)
    assert weights["MolFromSmiles"] == 0.8


def test_load_weights_returns_empty_dict_when_missing(tmp_path):
    from mcpmenago.store import BookStore

    book_dir = _make_book_dir(tmp_path, "rdkit")
    book_dir.joinpath("weights.json").unlink()
    library = tmp_path.joinpath("library")
    weights = BookStore.load_weights("rdkit", library)
    assert weights == {}


def test_list_books_returns_names(tmp_path):
    from mcpmenago.store import BookStore

    _make_book_dir(tmp_path, "rdkit")
    _make_book_dir(tmp_path, "numpy")
    library = tmp_path.joinpath("library")
    books = BookStore.list_books(library)
    assert set(books) == {"rdkit", "numpy"}


def test_list_books_excludes_dirs_without_book_json(tmp_path):
    from mcpmenago.store import BookStore

    _make_book_dir(tmp_path, "rdkit")
    # stray dir with no book.json
    tmp_path.joinpath("library", "orphan").mkdir()
    library = tmp_path.joinpath("library")
    books = BookStore.list_books(library)
    assert books == ["rdkit"]


def test_list_books_returns_empty_when_library_missing(tmp_path):
    from mcpmenago.store import BookStore

    library = tmp_path.joinpath("library")
    # library dir does not exist
    books = BookStore.list_books(library)
    assert books == []
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
cd mcpmenago && uv run pytest tests/test_store.py -v
```

Expected: `ModuleNotFoundError: No module named 'mcpmenago.store'`

- [ ] **Step 3: Create `mcpmenago/mcpmenago/store.py`**

```python
"""BookStore — centralised book I/O for mcpmenago.

All knowledge of how book data is laid out on disk lives here.
Callers receive Pydantic model instances, not raw paths or file contents.
"""

from __future__ import annotations

import json
from pathlib import Path

from mcpmenago.models import BookIndex, BookMeta


class BookStore:
    """Static accessor for book data stored under a library directory.

    Every method accepts an explicit `library` path so callers can inject
    a temporary directory during tests without touching global state.
    When used in production, pass `paths.LIBRARY`.
    """

    @staticmethod
    def book_dir(name: str, library: Path) -> Path:
        """Return the directory for a named book."""
        return library.joinpath(name)

    @staticmethod
    def load_meta(name: str, library: Path) -> BookMeta:
        """Load and return BookMeta from book.json.

        Raises FileNotFoundError if book.json is absent.
        """
        path = library.joinpath(name, "book.json")
        if not path.exists():
            raise FileNotFoundError(f"book.json not found for '{name}': {path}")
        return BookMeta.model_validate_json(path.read_text())

    @staticmethod
    def save_meta(name: str, meta: BookMeta, library: Path) -> None:
        """Persist BookMeta to book.json (overwrites existing)."""
        path = library.joinpath(name, "book.json")
        path.write_text(meta.model_dump_json(indent=2))

    @staticmethod
    def load_index(name: str, library: Path) -> BookIndex:
        """Load and return BookIndex from index.json."""
        path = library.joinpath(name, "index.json")
        return BookIndex.model_validate_json(path.read_text())

    @staticmethod
    def load_weights(name: str, library: Path) -> dict[str, float]:
        """Load weights from weights.json. Returns empty dict if file absent."""
        path = library.joinpath(name, "weights.json")
        if not path.exists():
            return {}
        return json.loads(path.read_text())

    @staticmethod
    def list_books(library: Path) -> list[str]:
        """Return sorted list of book names present in library.

        A directory counts as a book only if it contains book.json.
        Returns empty list if library does not exist.
        """
        if not library.exists():
            return []
        return sorted(
            d.name
            for d in library.iterdir()
            if d.is_dir() and d.joinpath("book.json").exists()
        )
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
cd mcpmenago && uv run pytest tests/test_store.py -v
```

Expected: 10 passed

- [ ] **Step 5: Run full suite**

```bash
cd mcpmenago && uv run pytest -v
```

Expected: 50 passed (no regressions)

- [ ] **Step 6: Commit**

```bash
git add mcpmenago/mcpmenago/store.py mcpmenago/tests/test_store.py
git commit -m "feat(mcpmenago): add store.py with BookStore — centralised book I/O"
```

---

## Chunk 3: Wire up callers — `cli.py` and `server.py`

### Task 4: Refactor `cli.py`

**Files:**
- Modify: `mcpmenago/mcpmenago/cli.py`

No new tests needed — existing `test_cli.py` covers all CLI behaviour. The refactor is mechanical substitution only.

- [ ] **Step 1: Run existing CLI tests as baseline**

```bash
cd mcpmenago && uv run pytest tests/test_cli.py -v
```

Record: all CLI tests pass before touching anything.

- [ ] **Step 2: Replace path block and `_load_config()` in `cli.py`**

Remove lines 18–30 (the `# ── Paths` block and `_load_config` function):

```python
# ── Paths ─────────────────────────────────────────────────────────────────────
ROOT = Path(__file__).parent  # mcpmenago/mcpmenago/
MCPMENAGO_ROOT = ROOT.parent  # mcpmenago/ (project root)
LIBRARY = MCPMENAGO_ROOT / "library"
CONFIG_PATH = MCPMENAGO_ROOT / "mcpmenago.json"
PROJECT_ROOT = MCPMENAGO_ROOT.parent  # host project root (mag-bridge/)


# ── Helpers ───────────────────────────────────────────────────────────────────
def _load_config() -> Settings:
    if CONFIG_PATH.exists():
        return Settings.model_validate_json(CONFIG_PATH.read_text())
    return Settings()
```

Replace the imports block at the top of `cli.py` with:

```python
from mcpmenago.index_builder import build_index
from mcpmenago.learn import load_weights, scan_imports, update_weights
from mcpmenago.models import BookMeta, Settings, load_settings
from mcpmenago.paths import CONFIG_PATH, GITIGNORE, LIBRARY, PROJECT_ROOT
from mcpmenago.store import BookStore
```

- [ ] **Step 3: Replace all `_load_config()` calls with `load_settings(CONFIG_PATH)`**

Two occurrences in `cli.py`:
- `add` command (line ~65): `config = _load_config()` → `config = load_settings(CONFIG_PATH)`
- `learn` command (line ~282): `config = _load_config()` → `config = load_settings(CONFIG_PATH)`

- [ ] **Step 4: Replace inline `LIBRARY / name` path construction with `BookStore.book_dir()`**

Find all occurrences of `LIBRARY / name` or `book_dir = LIBRARY / book` and replace:

```python
# Before:
book_dir = LIBRARY / name
# After:
book_dir = BookStore.book_dir(name, LIBRARY)
```

```python
# Before (remove command):
book_dir = LIBRARY / book
# After:
book_dir = BookStore.book_dir(book, LIBRARY)
```

- [ ] **Step 5: Replace inline `(book_dir / "book.json").write_text(...)` with `BookStore.save_meta()`**

Three occurrences (in `add`, `rebuild`, `update`):

```python
# Before:
(book_dir / "book.json").write_text(meta.model_dump_json(indent=2))
# After:
BookStore.save_meta(name, meta, LIBRARY)
```

Note: `update` command uses variable `book` (not `name`) — use the correct variable.

- [ ] **Step 6: Replace inline `BookMeta.model_validate_json(...)` with `BookStore.load_meta()`**

Five occurrences (in `list_books`, `show`, `rebuild`, `update`, `learn`):

```python
# Before:
meta = BookMeta.model_validate_json((book_dir / "book.json").read_text())
# After:
meta = BookStore.load_meta(name, LIBRARY)   # use correct name variable per command
```

- [ ] **Step 7: Replace inline `LIBRARY.iterdir()` pattern with `BookStore.list_books()`**

Two occurrences (`list_books` command, `rebuild --all` target):

```python
# Before (list_books):
books = [d.name for d in sorted(LIBRARY.iterdir()) if d.is_dir() and (d / "book.json").exists()]
# After:
books = BookStore.list_books(LIBRARY)

# Before (rebuild --all):
targets = [d.name for d in LIBRARY.iterdir() if d.is_dir() and (d / "book.json").exists()]
# After:
targets = BookStore.list_books(LIBRARY)
```

- [ ] **Step 8: Replace `PROJECT_ROOT / ".gitignore"` with `GITIGNORE`**

In `add` command:
```python
# Before:
_ensure_gitignore(PROJECT_ROOT / ".gitignore")
# After:
_ensure_gitignore(GITIGNORE)
```

In `uninstall` command:
```python
# Before:
gitignore = PROJECT_ROOT / ".gitignore"
# After:
gitignore = GITIGNORE
```

- [ ] **Step 9: Remove unused `Path` import if no longer needed**

Check if `from pathlib import Path` is still used directly in `cli.py` (it is — in `add` for `python_path` and `Path(rel)`). Keep it.

- [ ] **Step 10: Run CLI tests**

```bash
cd mcpmenago && uv run pytest tests/test_cli.py -v
```

Expected: same count as Step 1, all passing.

- [ ] **Step 11: Run full suite**

```bash
cd mcpmenago && uv run pytest -v
```

Expected: all tests pass.

- [ ] **Step 12: Commit**

```bash
git add mcpmenago/mcpmenago/cli.py
git commit -m "refactor(mcpmenago): cli.py — remove duplicated paths, use paths.py + BookStore"
```

---

### Task 5: Refactor `server.py`

**Files:**
- Modify: `mcpmenago/mcpmenago/server.py`

- [ ] **Step 1: Replace path block and `_load_config()` in `server.py`**

Remove lines 21–33 (the `# ── Paths` and `# ── Config` blocks):

```python
# ── Paths ─────────────────────────────────────────────────────────────────────
ROOT = Path(__file__).parent  # mcpmenago/mcpmenago/
MCPMENAGO_ROOT = ROOT.parent  # mcpmenago/ (project root)
LIBRARY = MCPMENAGO_ROOT / "library"
CONFIG_PATH = MCPMENAGO_ROOT / "mcpmenago.json"
PROJECT_ROOT = MCPMENAGO_ROOT.parent  # host project root (mag-bridge/)


# ── Config ────────────────────────────────────────────────────────────────────
def _load_config() -> Settings:
    if CONFIG_PATH.exists():
        return Settings.model_validate_json(CONFIG_PATH.read_text())
    return Settings()
```

Update the imports block:

```python
from mcpmenago.learn import load_weights
from mcpmenago.models import NOT_USED, BookIndex, BookMeta, Settings, load_settings
from mcpmenago.paths import CONFIG_PATH, LIBRARY
from mcpmenago.store import BookStore
```

- [ ] **Step 2: Replace `_load_config()` at startup**

```python
# Before (line ~103):
_config = _load_config()
# After:
_config = load_settings(CONFIG_PATH)
```

- [ ] **Step 3: Replace `LIBRARY.iterdir()` in `_load_books()` with `BookStore.list_books()`**

```python
# Before:
def _load_books() -> dict[str, LoadedBook]:
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

# After:
def _load_books() -> dict[str, LoadedBook]:
    books: dict[str, LoadedBook] = {}
    for name in BookStore.list_books(LIBRARY):
        book_dir = BookStore.book_dir(name, LIBRARY)
        try:
            book = LoadedBook(book_dir)
            books[book.meta.name] = book
        except Exception as e:
            print(f"Warning: failed to load book {name}: {e}", file=sys.stderr)
    return books
```

Note: `LoadedBook.__init__` reads `book.json` and `index.json` itself — leave it unchanged.

- [ ] **Step 4: Remove unused `Path` import if no longer needed**

`Path` is still used in `_parse_context_imports` (`Path(context_file)`) and `read_file` (`fpath = book.repo_path / path`). Keep it.

- [ ] **Step 5: Run full suite**

```bash
cd mcpmenago && uv run pytest -v
```

Expected: all tests pass.

- [ ] **Step 6: Commit**

```bash
git add mcpmenago/mcpmenago/server.py
git commit -m "refactor(mcpmenago): server.py — remove duplicated paths, use paths.py + BookStore"
```

---

## Final verification

- [ ] **Run complete test suite one final time**

```bash
cd mcpmenago && uv run pytest -v
```

Expected: all tests pass with zero failures.

- [ ] **Verify no stale imports remain**

```bash
cd mcpmenago && grep -n "_load_config\|MCPMENAGO_ROOT\s*=\|LIBRARY\s*=\|CONFIG_PATH\s*=\|PROJECT_ROOT\s*=\|ROOT\s*=" mcpmenago/cli.py mcpmenago/server.py
```

Expected: no output (all duplicated definitions gone).
