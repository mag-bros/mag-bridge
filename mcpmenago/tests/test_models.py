"""Tests for mcpmenago Pydantic schemas and weight constants."""

from __future__ import annotations

from pathlib import Path


def test_weight_constants():
    from mcpmenago.models import DISCOVERED, NOT_USED

    assert NOT_USED == 0.3
    assert DISCOVERED == 0.8


def test_mcpmenago_config_defaults():
    from mcpmenago.models import Settings

    config = Settings()
    assert config.learn_dirs == ["src", "tests", "notebooks"]
    assert config.supported_languages == ["python", "cpp"]


def test_mcpmenago_config_custom():
    from mcpmenago.models import Settings

    config = Settings(learn_dirs=["lib"], supported_languages=["python"])
    assert config.learn_dirs == ["lib"]
    assert config.supported_languages == ["python"]


def test_book_meta_required_fields():
    from mcpmenago.models import BookMeta

    meta = BookMeta(
        name="rdkit",
        github_url="https://github.com/rdkit/rdkit",
        languages=["python", "cpp"],
        python_path=Path(".venv/lib/python3.13/site-packages/rdkit"),
    )
    assert meta.name == "rdkit"
    assert meta.head_ref is None
    assert meta.head_ref_resolved is None
    assert meta.index_built_at is None


def test_book_meta_all_fields():
    from mcpmenago.models import BookMeta

    meta = BookMeta(
        name="rdkit",
        github_url="https://github.com/rdkit/rdkit",
        languages=["python", "cpp"],
        python_path=Path(".venv/lib/python3.13/site-packages/rdkit"),
        head_ref="Release_2025_09_6",
        head_ref_resolved="abc123",
        index_built_at="2026-03-10T12:00:00",
    )
    assert meta.head_ref == "Release_2025_09_6"
    assert meta.head_ref_resolved == "abc123"


def test_symbol_entry():
    from mcpmenago.models import SymbolEntry

    entry = SymbolEntry(
        name="GetSubstructMatches",
        kind="function",
        file="Code/GraphMol/substructmethods.h",
        start_line=98,
        end_line=114,
        signature="template <typename T> std::vector<MatchVectType> GetSubstructMatches(...)",
    )
    assert entry.name == "GetSubstructMatches"
    assert entry.end_line - entry.start_line == 16


def test_module_source():
    from mcpmenago.models import ModuleSource

    src = ModuleSource(path="Chem/rdmolops.py", lang="python")
    assert src.lang == "python"


def test_module_entry_multi_lang():
    from mcpmenago.models import ModuleEntry, ModuleSource

    entry = ModuleEntry(
        name="Chem.rdmolops",
        sources=[
            ModuleSource(path="Chem/rdmolops.py", lang="python"),
            ModuleSource(path="Code/GraphMol/MolOps.cpp", lang="cpp"),
        ],
        description="Molecule operations",
        key_functions=["GetSubstructMatches"],
    )
    assert len(entry.sources) == 2
    assert entry.sources[0].lang == "python"
    assert entry.sources[1].lang == "cpp"


def test_book_index_symbols_dict():
    from mcpmenago.models import BookIndex, SymbolEntry

    index = BookIndex(
        version="1.0",
        modules=[],
        symbols={
            "Foo": [
                SymbolEntry(name="Foo", kind="function", file="a.py", start_line=1, end_line=3, signature="def Foo():"),
                SymbolEntry(name="Foo", kind="function", file="b.cpp", start_line=10, end_line=20, signature="void Foo()"),
            ]
        },
    )
    assert len(index.symbols["Foo"]) == 2


def test_book_meta_json_roundtrip(tmp_path):
    from mcpmenago.models import BookMeta

    meta = BookMeta(
        name="rdkit",
        github_url="https://github.com/rdkit/rdkit",
        languages=["python", "cpp"],
        python_path=Path(".venv/lib/python3.13/site-packages/rdkit"),
        head_ref="v1.0",
    )
    path = tmp_path / "book.json"
    path.write_text(meta.model_dump_json(indent=2))
    loaded = BookMeta.model_validate_json(path.read_text())
    assert loaded.name == meta.name
    assert loaded.head_ref == meta.head_ref


def test_mcpmenago_json_validates_against_schema():
    from pathlib import Path

    from mcpmenago.models import Settings

    config_path = Path(__file__).parent.parent.parent / "mcpmenago" / "mcpmenago.json"
    config = Settings.model_validate_json(config_path.read_text())
    assert "python" in config.supported_languages


def test_book_index_json_roundtrip(tmp_path):
    from mcpmenago.models import BookIndex, ModuleEntry, ModuleSource, SymbolEntry

    index = BookIndex(
        version="2025.09.6",
        modules=[
            ModuleEntry(
                name="Chem",
                sources=[ModuleSource(path="Chem/__init__.py", lang="python")],
                description="Core module",
                key_functions=["MolFromSmiles"],
            )
        ],
        symbols={
            "MolFromSmiles": [
                SymbolEntry(
                    name="MolFromSmiles", kind="function", file="Chem/__init__.py", start_line=10, end_line=15, signature="def MolFromSmiles(smiles):"
                ),
            ]
        },
    )
    path = tmp_path / "index.json"
    path.write_text(index.model_dump_json(indent=2))
    loaded = BookIndex.model_validate_json(path.read_text())
    assert loaded.version == "2025.09.6"
    assert "MolFromSmiles" in loaded.symbols
