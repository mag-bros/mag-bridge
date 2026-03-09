"""
RDKit MCP Server — grounded access to RDKit 2025.09.6 source for Claude.

Data sources:
  - Python: .venv/lib/python3.13/site-packages/rdkit/  (default)
  - C++ :   rdkit/                                       (explicit: source="cpp" or "all")

Tiered search (cheapest first, stops on match):
  Tier 1 — context_file imports  (~200 tokens)
  Tier 2 — index relevance       (~500 tokens)
  Tier 3 — full ripgrep          (~1000-3000 tokens)
"""

from __future__ import annotations

import inspect
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Literal

from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel

# ── Paths ──────────────────────────────────────────────────────────────────────
ROOT = Path(__file__).parent.parent
PYTHON_SRC = ROOT / ".venv/lib/python3.13/site-packages/rdkit"
CPP_SRC = ROOT / "rdkit"
INDEX_PATH = ROOT / "mcp/.module_index.json"
SRC_SCAN_DIRS = ["src", "tests", "notebooks"]

# ── OpenTelemetry (optional — silently no-ops if Phoenix not running) ──────────
from contextlib import nullcontext

try:
    from opentelemetry import trace
    from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor

    _provider = TracerProvider()
    _provider.add_span_processor(BatchSpanProcessor(OTLPSpanExporter(endpoint="localhost:4317", insecure=True)))
    trace.set_tracer_provider(_provider)
    tracer = trace.get_tracer("rdkit-mcp")
except Exception:
    tracer = None  # type: ignore[assignment]


def _span(name: str):
    """Context manager — no-op if tracer unavailable."""
    if tracer is not None:
        return tracer.start_as_current_span(name)
    return nullcontext()


# ── Pydantic index schema (MongoDB-ready) ─────────────────────────────────────
class ModuleEntry(BaseModel):
    name: str
    python_path: str
    cpp_path: str | None = None
    source_type: Literal["compiled", "python", "both"]
    description: str = ""
    key_functions: list[str] = []
    relevance: float = 0.3


class ModuleIndex(BaseModel):
    version: str
    modules: list[ModuleEntry]


ModuleIndex.model_rebuild()


# ── Index builder ─────────────────────────────────────────────────────────────
RDKIT_IMPORT_RE = re.compile(r"(?:from|import)\s+(rdkit(?:\.[a-zA-Z0-9_]+)*)")

# Manually curated relevance overrides — reflects MagBridge actual usage
_OVERRIDES: dict[str, dict] = {
    "Chem": {
        "relevance": 1.0,
        "description": "Core RDKit chemistry module — molecules, bonds, atoms",
        "key_functions": ["MolFromSmiles", "MolToSmiles", "MolFromSmarts", "MolToSmarts"],
    },
    "Chem.rdchem": {
        "relevance": 1.0,
        "description": "Core molecule/atom/bond object model (compiled)",
        "key_functions": ["Mol", "Atom", "Bond", "BondType", "GetSubstructMatches"],
    },
    "Chem.rdmolops": {
        "relevance": 0.9,
        "description": "Molecule operations: sanitize, add/remove Hs, substructure",
        "key_functions": ["GetSubstructMatches", "SanitizeMol", "AddHs", "RemoveAllHs"],
        "cpp_path": "Code/GraphMol/MolOps.cpp",
    },
    "Chem.Draw": {
        "relevance": 0.7,
        "description": "Molecule drawing/visualization",
        "key_functions": ["MolToImage", "MolsToGridImage"],
    },
    "Chem.rdDepictor": {
        "relevance": 0.6,
        "description": "2D coordinate generation for rendering",
        "key_functions": ["Compute2DCoords"],
    },
    "Chem.rdMolDescriptors": {
        "relevance": 0.5,
        "description": "Molecular descriptors and fingerprints",
        "key_functions": [],
    },
}


def _scan_project_imports() -> dict[str, int]:
    """Scan src/, tests/, notebooks/ for rdkit import frequency."""
    counts: dict[str, int] = {}
    for dir_name in SRC_SCAN_DIRS:
        scan_dir = ROOT / dir_name
        if not scan_dir.exists():
            continue
        for ext in ("*.py", "*.ipynb"):
            for fpath in scan_dir.rglob(ext):
                try:
                    text = fpath.read_text(errors="ignore")
                    if fpath.suffix == ".ipynb":
                        # extract source from code cells only
                        data = json.loads(text)
                        cells = data.get("cells", [])
                        text = "\n".join("".join(c.get("source", [])) for c in cells if c.get("cell_type") == "code")
                    for match in RDKIT_IMPORT_RE.finditer(text):
                        mod = match.group(1).removeprefix("rdkit.")
                        counts[mod] = counts.get(mod, 0) + 1
                except Exception:
                    pass
    return counts


def _build_index() -> ModuleIndex:
    print("Building RDKit module index...", file=sys.stderr)

    freq = _scan_project_imports()
    max_freq = max(freq.values(), default=1)
    print(f"  Scanned imports: {freq}", file=sys.stderr)

    entries: list[ModuleEntry] = []
    seen: set[str] = set()

    # Walk site-packages to enumerate all modules
    for fpath in sorted(PYTHON_SRC.rglob("*.py")):
        rel = fpath.relative_to(PYTHON_SRC)
        parts = list(rel.parts)
        if parts[-1] == "__init__.py":
            parts = parts[:-1]
        else:
            parts[-1] = parts[-1].removesuffix(".py")
        name = ".".join(parts) if parts else "Chem"
        if not name or name in seen:
            continue
        seen.add(name)
        source_type: Literal["compiled", "python", "both"] = "python"
        entries.append(ModuleEntry(name=name, python_path=str(rel), source_type=source_type))

    # Walk compiled .so modules
    for fpath in sorted(PYTHON_SRC.rglob("*.so")):
        rel = fpath.relative_to(PYTHON_SRC)
        base = re.sub(r"\.cpython.*", "", rel.name)
        parts = list(rel.parent.parts) + [base]
        name = ".".join(p for p in parts if p)
        if name in seen:
            # upgrade to "both"
            for e in entries:
                if e.name == name:
                    e.source_type = "both"
            continue
        seen.add(name)
        entries.append(ModuleEntry(name=name, python_path=str(rel), source_type="compiled"))

    # Apply frequency scores and overrides
    for e in entries:
        f = freq.get(e.name, 0)
        e.relevance = round(0.3 + 0.7 * (f / max_freq), 3) if f else 0.3
        override = _OVERRIDES.get(e.name, {})
        for k, v in override.items():
            setattr(e, k, v)

    # Sort by relevance descending
    entries.sort(key=lambda x: x.relevance, reverse=True)

    index = ModuleIndex(version="2025.09.6", modules=entries)
    INDEX_PATH.parent.mkdir(parents=True, exist_ok=True)
    INDEX_PATH.write_text(index.model_dump_json(indent=2))
    print(f"  Index built: {len(entries)} modules, {sum(1 for e in entries if e.relevance >= 0.8)} high-relevance", file=sys.stderr)
    return index


def _load_index() -> ModuleIndex:
    if INDEX_PATH.exists():
        return ModuleIndex.model_validate_json(INDEX_PATH.read_text())
    return _build_index()


# ── Startup ───────────────────────────────────────────────────────────────────
_index = _load_index()
mcp = FastMCP("rdkit-source")


# ── Helpers ───────────────────────────────────────────────────────────────────
def _rg(pattern: str, path: Path, extra_args: list[str] | None = None) -> str:
    cmd = ["rg", "--color=never", "-n", "--max-count=5", pattern, str(path)]
    if extra_args:
        cmd[1:1] = extra_args
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.stdout or "(no matches)"


def _parse_context_imports(context_file: str) -> list[str]:
    """Return list of rdkit module names imported by context_file."""
    try:
        text = Path(context_file).read_text(errors="ignore")
        mods = []
        for m in RDKIT_IMPORT_RE.finditer(text):
            mod = m.group(1).removeprefix("rdkit.")
            # normalise: 'Chem.rdmolops.GetSubstructMatches' → 'Chem.rdmolops'
            parts = mod.split(".")
            mods.append(".".join(parts[:2]) if len(parts) > 1 else parts[0])
        return list(dict.fromkeys(mods))  # deduplicate, preserve order
    except Exception:
        return []


# ── Tools ─────────────────────────────────────────────────────────────────────
@mcp.tool()
def list_directory(path: str = "") -> str:
    """List files and directories in the RDKit Python source tree.
    path: relative path within site-packages/rdkit/ (empty = root)
    Use this first to understand structure before reading files.
    """
    base = PYTHON_SRC / path
    if not base.exists():
        return f"Path not found: {base}"
    entries = sorted(base.iterdir(), key=lambda p: (p.is_file(), p.name))
    lines = [f"{'[DIR] ' if e.is_dir() else '      '}{e.name}" for e in entries]
    return "\n".join(lines)


@mcp.tool()
def search_code(
    query: str,
    source: Literal["python", "cpp", "all"] = "python",
    context_file: str | None = None,
) -> str:
    """Search RDKit source code for a pattern using ripgrep.

    Routing (cheapest first, stops on match):
      Tier 1: search only modules imported by context_file (if provided)
      Tier 2: search top-relevance modules from index
      Tier 3: full search across entire source

    source: 'python' (default), 'cpp', or 'all'
    context_file: absolute path to the file you are currently editing
    """
    tier = 0
    result = "(no matches)"

    with _span("search_code"):
        # Tier 1 — context imports
        if context_file:
            mods = _parse_context_imports(context_file)
            if mods:
                paths = [str(PYTHON_SRC / m.replace(".", "/")) for m in mods]
                existing = [p for p in paths if Path(p).exists()]
                if existing:
                    tier = 1
                    out = "\n".join(_rg(query, Path(p)) for p in existing)
                    if "(no matches)" not in out:
                        result = f"[Tier 1 — context]\n{out}"

        # Tier 2 — top index modules
        if tier == 0 or result == "(no matches)":
            top = [e for e in _index.modules if e.relevance >= 0.7][:5]
            paths = [str(PYTHON_SRC / e.python_path) for e in top]
            existing = [p for p in paths if Path(p).exists()]
            if existing:
                tier = 2
                out = "\n".join(_rg(query, Path(p)) for p in existing)
                if "(no matches)" not in out:
                    result = f"[Tier 2 — index]\n{out}"

        # Tier 3 — full search
        if result == "(no matches)":
            tier = 3
            search_roots = []
            if source in ("python", "all"):
                search_roots.append(PYTHON_SRC)
            if source in ("cpp", "all") and CPP_SRC.exists():
                search_roots.append(CPP_SRC)
            out = "\n".join(_rg(query, p, ["--max-count=10"]) for p in search_roots)
            result = f"[Tier 3 — full]\n{out}" if out.strip() else "(no matches)"

        return result


@mcp.tool()
def read_file(path: str, source: Literal["python", "cpp"] = "python") -> str:
    """Read a source file from the RDKit codebase.

    source='python': path relative to site-packages/rdkit/
    source='cpp':    path relative to rdkit/ submodule root
    """
    base = PYTHON_SRC if source == "python" else CPP_SRC
    fpath = base / path
    if not fpath.exists():
        return f"File not found: {fpath}"
    with _span("read_file"):
        return fpath.read_text(errors="replace")


@mcp.tool()
def inspect_module(module_name: str) -> str:
    """Introspect a compiled RDKit module (.so) to get C++ function signatures.

    module_name: dotted name e.g. 'Chem.rdmolops', 'Chem.rdchem'
    Returns: list of members with C++ signatures extracted from docstrings.
    """
    with _span("inspect_module"):
        try:
            import importlib

            mod = importlib.import_module(f"rdkit.{module_name}")
        except ImportError as e:
            return f"Could not import rdkit.{module_name}: {e}"

        lines = [f"Module: rdkit.{module_name}\n"]
        for name, obj in sorted(inspect.getmembers(mod)):
            if name.startswith("_"):
                continue
            doc = inspect.getdoc(obj) or ""
            # Extract C++ signature line if present
            sig_line = next((l for l in doc.splitlines() if "C++ signature" in l or l.startswith(name + "(")), "")
            kind = "class" if inspect.isclass(obj) else "fn"
            lines.append(f"  [{kind}] {name}")
            if sig_line:
                lines.append(f"         {sig_line.strip()}")
        return "\n".join(lines)


@mcp.tool()
def get_module_index(min_relevance: float = 0.0) -> str:
    """Return the RDKit module index as a compact JSON map.

    min_relevance: filter to modules with relevance >= this value (0.0 = all)
    Use this first to understand which modules are most relevant to MagBridge.
    High relevance (>=0.8) = heavily used in project.
    """
    with _span("get_module_index"):
        modules = [m for m in _index.modules if m.relevance >= min_relevance]
        out = {
            m.name: {
                "relevance": m.relevance,
                "type": m.source_type,
                "path": m.python_path,
                "cpp": m.cpp_path,
                "desc": m.description,
                "key_fns": m.key_functions,
            }
            for m in modules
        }
        return json.dumps(out, indent=2)


# ── Entry point ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    mcp.run(transport="stdio")
