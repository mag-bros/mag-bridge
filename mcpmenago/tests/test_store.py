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

    _make_book_dir(tmp_path, "rdkit")
    library = tmp_path.joinpath("library")
    meta = BookStore.load_meta("rdkit", library)
    assert isinstance(meta, BookMeta)
    assert meta.name == "rdkit"
    assert meta.head_ref == "v1.0"


def test_load_meta_raises_when_missing(tmp_path):
    from mcpmenago.store import BookStore

    library = tmp_path.joinpath("library")
    library.mkdir()
    library.joinpath("rdkit").mkdir()
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
    tmp_path.joinpath("library", "orphan").mkdir()
    library = tmp_path.joinpath("library")
    books = BookStore.list_books(library)
    assert books == ["rdkit"]


def test_list_books_returns_empty_when_library_missing(tmp_path):
    from mcpmenago.store import BookStore

    library = tmp_path.joinpath("library")
    books = BookStore.list_books(library)
    assert books == []
