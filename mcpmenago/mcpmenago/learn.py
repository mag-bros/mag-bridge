"""Dependency scanning (Layer 2) — scans project imports, updates weights."""
from __future__ import annotations

import json
import re
from pathlib import Path

from mcpmenago.models import DISCOVERED


def _build_import_re(package_name: str) -> re.Pattern[str]:
    """Build regex matching imports of a specific package."""
    return re.compile(rf"(?:from|import)\s+({re.escape(package_name)}(?:\.[a-zA-Z0-9_]+)*)")


def scan_imports(package_name: str, scan_dirs: list[str]) -> list[str]:
    """Scan directories for import statements matching package_name.

    Returns list of discovered module names (e.g., ["Chem", "Chem.rdmolops"]).
    """
    import_re = _build_import_re(package_name)
    modules: set[str] = set()

    for dir_path in scan_dirs:
        scan_dir = Path(dir_path)
        if not scan_dir.exists():
            continue
        for ext in ("*.py", "*.ipynb"):
            for fpath in scan_dir.rglob(ext):
                try:
                    text = fpath.read_text(errors="ignore")
                    if fpath.suffix == ".ipynb":
                        data = json.loads(text)
                        cells = data.get("cells", [])
                        text = "\n".join(
                            "".join(c.get("source", []))
                            for c in cells
                            if c.get("cell_type") == "code"
                        )
                    for match in import_re.finditer(text):
                        mod = match.group(1).removeprefix(f"{package_name}.")
                        # Normalize: "Chem.rdmolops.GetSubstructMatches" → "Chem.rdmolops"
                        parts = mod.split(".")
                        modules.add(".".join(parts[:2]) if len(parts) > 1 else parts[0])
                except Exception:
                    pass

    return sorted(modules)


def update_weights(
    discovered_modules: list[str],
    symbol_to_module: dict[str, str],
    output_path: Path,
) -> dict[str, float]:
    """Write weights.json for symbols whose module was discovered.

    Args:
        discovered_modules: Module names found in user's project.
        symbol_to_module: Map of symbol name → module name (from index).
        output_path: Path to write weights.json.

    Returns:
        The weights dict written.
    """
    discovered_set = set(discovered_modules)
    weights: dict[str, float] = {}

    for symbol_name, module_name in symbol_to_module.items():
        # Check if the symbol's module (or its parent) was discovered
        parts = module_name.split(".")
        for i in range(len(parts), 0, -1):
            if ".".join(parts[:i]) in discovered_set:
                weights[symbol_name] = DISCOVERED
                break

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(weights, indent=2))
    return weights


def load_weights(path: Path) -> dict[str, float]:
    """Load weights from a JSON file. Returns empty dict if file doesn't exist."""
    if not path.exists():
        return {}
    return json.loads(path.read_text())
