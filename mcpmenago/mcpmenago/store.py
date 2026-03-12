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
