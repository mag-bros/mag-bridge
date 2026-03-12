"""Pydantic schemas and weight constants for mcpmenago."""

from __future__ import annotations

from pathlib import Path

from pydantic import BaseModel

# ── Weight constants ──────────────────────────────────────────────────────────
NOT_USED = 0.3
DISCOVERED = 0.8


# ── Central config ────────────────────────────────────────────────────────────
class Settings(BaseModel):
    learn_dirs: list[str] = ["src", "tests", "notebooks"]
    supported_languages: list[str] = ["python", "cpp"]


def load_settings(path: Path) -> Settings:
    if path.exists():
        return Settings.model_validate_json(path.read_text())
    return Settings()


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
