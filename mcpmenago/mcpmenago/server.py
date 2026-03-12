"""Central FastMCP server — manages all books, exposes MCP tools."""

from __future__ import annotations

# Bootstrap: allow running as `python mcpmenago/server.py` (script) or via .mcp.json
# sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import importlib
import inspect
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Literal

from mcp.server.fastmcp import FastMCP

from mcpmenago.models import NOT_USED, BookIndex, BookMeta, load_settings
from mcpmenago.paths import CONFIG_PATH, LIBRARY
from mcpmenago.store import BookStore


# ── Book loading ──────────────────────────────────────────────────────────────
class LoadedBook:
    """A book with its metadata, index, and weights loaded into memory."""

    def __init__(self, book_dir: Path):
        self.dir = book_dir
        self.meta = BookMeta.model_validate_json(book_dir.joinpath("book.json").read_text())
        self.index = BookIndex.model_validate_json(book_dir.joinpath("01_index.json").read_text())
        self.weights = BookStore.load_weights(book_dir.name, book_dir.parent)
        self.repo_path = book_dir.joinpath("repo")

    def get_weight(self, symbol_name: str) -> float:
        return self.weights.get(symbol_name, NOT_USED)


def _load_books() -> dict[str, LoadedBook]:
    """Scan library/ and load all books."""
    books: dict[str, LoadedBook] = {}
    for name in BookStore.list_books(LIBRARY):
        book_dir = BookStore.book_dir(name, LIBRARY)
        if not book_dir.joinpath("01_index.json").exists():
            continue
        try:
            book = LoadedBook(book_dir)
            books[book.meta.name] = book
        except Exception as e:
            print(f"Warning: failed to load book {name}: {e}", file=sys.stderr)
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
_config = load_settings(CONFIG_PATH)
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
                f"[{entry.kind}] {entry.name} — {entry.file}:{entry.start_line}-{entry.end_line} (weight: {book.get_weight(entry.name)})\n{body}"
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
