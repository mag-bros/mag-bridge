from __future__ import annotations

import colorsys
from dataclasses import dataclass
from typing import Tuple

RGBf = Tuple[float, float, float]  # 0..1 floats


@dataclass
class HighlightScheme:
    """Maps chemistry match data to per-atom and per-formula color assignments.

    Owns all palette math. Produces ready-to-use color dicts for the renderer.
    Bond color derivation is handled separately in Renderer (requires RDKit mol traversal).
    """

    atomColors: list[dict[int, RGBf]]  # per-mol: atom_idx → color
    formulaColor: dict[str, RGBf]  # formula → color (used by legend)

    @classmethod
    def fromGroups(
        cls,
        highlightAtomGroupsPerMol: list[dict[str, list[int]]],
        highlightAtomLists: list[list[int]],
    ) -> "HighlightScheme":
        """Main path: one stable color per formula, applied consistently across all molecules."""
        # Collect unique formulas in insertion order
        formulas: list[str] = []
        seen: set[str] = set()
        for groups in highlightAtomGroupsPerMol:
            if not groups:
                continue
            for f in groups:
                if f not in seen:
                    seen.add(f)
                    formulas.append(f)

        palette = _contrasting_palette(len(formulas))
        formula_color: dict[str, RGBf] = {f: palette[i] for i, f in enumerate(formulas)}

        atom_colors: list[dict[int, RGBf]] = []
        for mol_i, atoms_union in enumerate(highlightAtomLists):
            groups = highlightAtomGroupsPerMol[mol_i] if mol_i < len(highlightAtomGroupsPerMol) else {}

            # Collect every group color per atom — shared atoms get multiple entries
            per_atom: dict[int, list[RGBf]] = {}
            for f, atoms in (groups or {}).items():
                col = formula_color.get(f)
                if col is None:
                    continue
                for a in atoms:
                    per_atom.setdefault(int(a), []).append(col)

            # Blend colors for shared atoms (average RGB); single-group atoms keep their color
            atom_color_map: dict[int, RGBf] = {
                a: cols[0]
                if len(cols) == 1
                else (
                    sum(c[0] for c in cols) / len(cols),
                    sum(c[1] for c in cols) / len(cols),
                    sum(c[2] for c in cols) / len(cols),
                )
                for a, cols in per_atom.items()
            }

            # Keep only atoms present in the union highlight list
            allowed = set(atoms_union or [])
            atom_colors.append({a: c for a, c in atom_color_map.items() if a in allowed})

        return cls(atomColors=atom_colors, formulaColor=formula_color)

    @classmethod
    def fromAtomLists(cls, highlightAtomLists: list[list[int]]) -> "HighlightScheme":
        """Legacy fallback: one color per molecule, no formula grouping."""
        palette = _contrasting_palette(len(highlightAtomLists))
        atom_colors: list[dict[int, RGBf]] = []
        for i, atoms in enumerate(highlightAtomLists):
            col = palette[i] if i < len(palette) else (1.0, 0.0, 0.0)
            atom_colors.append({int(a): col for a in atoms})
        return cls(atomColors=atom_colors, formulaColor={})


# --- palette helpers (module-level, no state) ---


def _contrasting_palette(n: int, s: float = 0.80, v: float = 0.95) -> list[RGBf]:
    if n <= 0:
        return []
    step = 0.618033988749895  # golden ratio conjugate
    h = 0.0
    cols: list[RGBf] = []
    for _ in range(n):
        h = (h + step) % 1.0
        cols.append(colorsys.hsv_to_rgb(h, s, v))
    return cols
