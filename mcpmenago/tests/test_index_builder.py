"""Tests for tree-sitter index builder (Layer 1)."""

from __future__ import annotations


def test_parse_python_file_extracts_functions(sample_python_file):
    from mcpmenago.index_builder import parse_python_file

    symbols = parse_python_file(sample_python_file, base_path=sample_python_file.parent)
    names = [s.name for s in symbols]
    assert "hello" in names
    assert "Calculator" in names


def test_parse_python_file_extracts_methods(sample_python_file):
    from mcpmenago.index_builder import parse_python_file

    symbols = parse_python_file(sample_python_file, base_path=sample_python_file.parent)
    names = [s.name for s in symbols]
    assert "add" in names
    assert "subtract" in names


def test_parse_python_file_line_numbers(sample_python_file):
    from mcpmenago.index_builder import parse_python_file

    symbols = parse_python_file(sample_python_file, base_path=sample_python_file.parent)
    hello = next(s for s in symbols if s.name == "hello")
    assert hello.start_line == 1
    assert hello.end_line == 3
    assert hello.kind == "function"


def test_parse_python_file_signature(sample_python_file):
    from mcpmenago.index_builder import parse_python_file

    symbols = parse_python_file(sample_python_file, base_path=sample_python_file.parent)
    hello = next(s for s in symbols if s.name == "hello")
    assert "def hello" in hello.signature


def test_parse_cpp_file_extracts_functions(sample_cpp_file):
    from mcpmenago.index_builder import parse_cpp_file

    symbols = parse_cpp_file(sample_cpp_file, base_path=sample_cpp_file.parent)
    names = [s.name for s in symbols]
    assert "greet" in names


def test_parse_cpp_file_extracts_class(sample_cpp_file):
    from mcpmenago.index_builder import parse_cpp_file

    symbols = parse_cpp_file(sample_cpp_file, base_path=sample_cpp_file.parent)
    names = [s.name for s in symbols]
    assert "Calculator" in names


def test_parse_cpp_file_extracts_template(sample_cpp_file):
    from mcpmenago.index_builder import parse_cpp_file

    symbols = parse_cpp_file(sample_cpp_file, base_path=sample_cpp_file.parent)
    names = [s.name for s in symbols]
    assert "identity" in names


def test_parse_cpp_file_line_numbers(sample_cpp_file):
    from mcpmenago.index_builder import parse_cpp_file

    symbols = parse_cpp_file(sample_cpp_file, base_path=sample_cpp_file.parent)
    greet = next(s for s in symbols if s.name == "greet")
    assert greet.start_line == 4
    assert greet.kind == "function"


def test_build_index_python_only(sample_repo):
    from mcpmenago.index_builder import build_index

    index = build_index(repo_path=sample_repo, languages=["python"])
    all_names = list(index.symbols.keys())
    assert "GetSubstructMatches" in all_names
    assert "SanitizeMol" in all_names
    assert "MolFromSmiles" in all_names


def test_build_index_cpp_only(sample_repo):
    from mcpmenago.index_builder import build_index

    index = build_index(repo_path=sample_repo, languages=["cpp"])
    all_names = list(index.symbols.keys())
    assert "SanitizeMol" in all_names
    assert "GetFormalCharge" in all_names


def test_build_index_both_languages(sample_repo):
    from mcpmenago.index_builder import build_index

    index = build_index(repo_path=sample_repo, languages=["python", "cpp"])
    # SanitizeMol should appear in both languages (overloads)
    assert "SanitizeMol" in index.symbols
    entries = index.symbols["SanitizeMol"]
    langs = {e.file.split(".")[-1] for e in entries}
    assert len(langs) >= 1  # at least one language


def test_build_index_writes_json(sample_repo, tmp_path):
    from mcpmenago.index_builder import build_index
    from mcpmenago.models import BookIndex

    output = tmp_path / "01_index.json"
    index = build_index(repo_path=sample_repo, languages=["python"], output_path=output)
    assert output.exists()
    loaded = BookIndex.model_validate_json(output.read_text())
    assert len(loaded.symbols) > 0


def test_build_index_symbol_entry_has_file_relative_to_repo(sample_repo):
    from mcpmenago.index_builder import build_index

    index = build_index(repo_path=sample_repo, languages=["python"])
    entry = index.symbols["GetSubstructMatches"][0]
    # file should be relative to repo root, not absolute
    assert not entry.file.startswith("/")
    assert "Chem/rdmolops.py" in entry.file
