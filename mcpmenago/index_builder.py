"""tree-sitter index builder (Layer 1) — parses source files into SymbolEntry objects."""
from __future__ import annotations

import sys
from collections.abc import Callable
from pathlib import Path

import tree_sitter_cpp as tscpp
import tree_sitter_python as tspython
from tree_sitter import Language, Parser, Query, QueryCursor

from mcpmenago.models import BookIndex, ModuleEntry, ModuleSource, SymbolEntry

# ── Language setup ────────────────────────────────────────────────────────────
PY_LANGUAGE = Language(tspython.language())
CPP_LANGUAGE = Language(tscpp.language())

LANG_EXTENSIONS: dict[str, list[str]] = {
    "python": [".py"],
    "cpp": [".h", ".hpp", ".cpp", ".cc", ".cxx"],
}

# ── Python queries ────────────────────────────────────────────────────────────
PY_FUNC_QUERY = Query(PY_LANGUAGE, "(function_definition name: (identifier) @name) @def")
PY_CLASS_QUERY = Query(PY_LANGUAGE, "(class_definition name: (identifier) @name) @def")

# ── C++ queries ───────────────────────────────────────────────────────────────
CPP_FUNC_QUERY = Query(CPP_LANGUAGE, "(function_definition) @def")
CPP_CLASS_QUERY = Query(CPP_LANGUAGE, "(class_specifier name: (type_identifier) @name) @def")
CPP_TEMPLATE_QUERY = Query(CPP_LANGUAGE, "(template_declaration) @def")


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
    for _, nodes in QueryCursor(PY_FUNC_QUERY).matches(tree.root_node):
        def_nodes = nodes.get("def", [])
        name_nodes = nodes.get("name", [])
        if not def_nodes or not name_nodes:
            continue
        def_node = def_nodes[0]
        name_node = name_nodes[0]
        parent = def_node.parent
        kind = "method" if parent is not None and parent.type == "block" else "function"
        symbols.append(
            SymbolEntry(
                name=(name_node.text or b"").decode("utf-8"),
                kind=kind,
                file=rel_path,
                start_line=def_node.start_point[0] + 1,
                end_line=def_node.end_point[0] + 1,
                signature=_first_line(def_node.text or b""),
            )
        )

    # Classes
    for _, nodes in QueryCursor(PY_CLASS_QUERY).matches(tree.root_node):
        def_nodes = nodes.get("def", [])
        name_nodes = nodes.get("name", [])
        if not def_nodes or not name_nodes:
            continue
        def_node = def_nodes[0]
        name_node = name_nodes[0]
        symbols.append(
            SymbolEntry(
                name=(name_node.text or b"").decode("utf-8"),
                kind="class",
                file=rel_path,
                start_line=def_node.start_point[0] + 1,
                end_line=def_node.end_point[0] + 1,
                signature=_first_line(def_node.text or b""),
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
    for _, nodes in QueryCursor(CPP_FUNC_QUERY).matches(tree.root_node):
        def_nodes = nodes.get("def", [])
        if not def_nodes:
            continue
        def_node = def_nodes[0]
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
                signature=_first_line(def_node.text or b""),
            )
        )

    # Classes
    for _, nodes in QueryCursor(CPP_CLASS_QUERY).matches(tree.root_node):
        def_nodes = nodes.get("def", [])
        name_nodes = nodes.get("name", [])
        if not def_nodes or not name_nodes:
            continue
        def_node = def_nodes[0]
        name_node = name_nodes[0]
        symbols.append(
            SymbolEntry(
                name=(name_node.text or b"").decode("utf-8"),
                kind="class",
                file=rel_path,
                start_line=def_node.start_point[0] + 1,
                end_line=def_node.end_point[0] + 1,
                signature=_first_line(def_node.text or b""),
            )
        )

    # Templates
    for _, nodes in QueryCursor(CPP_TEMPLATE_QUERY).matches(tree.root_node):
        def_nodes = nodes.get("def", [])
        if not def_nodes:
            continue
        def_node = def_nodes[0]
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
                            signature=_first_line(def_node.text or b""),
                        )
                    )

    return symbols


LANG_PARSERS: dict[str, Callable[..., list[SymbolEntry]]] = {
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
