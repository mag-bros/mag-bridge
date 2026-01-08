from __future__ import annotations

import base64
import colorsys
import io
import typing
from collections import Counter
from collections.abc import Iterable
from typing import Dict, List, Tuple

import numpy as np
from IPython.display import Image as IPyImage
from PIL import Image, ImageDraw, ImageFont
from rdkit.Chem import Mol, MolToSmiles, RemoveAllHs
from rdkit.Chem.Draw import MolsToGridImage, MolToImage
from rdkit.Chem.rdDepictor import Compute2DCoords

from src.utils.ui import Theme


class Renderer:
    """Stateful RDKit renderer configured with a persistent scientific theme."""

    def __init__(self, theme=Theme.Sea):
        """Initialize renderer with a given Theme (defaults to Theme.White)."""
        self.theme = theme

    # === Single molecule ===
    def GetMoleculeImg(self, mol: Mol, size=(200, 200)) -> Image.Image:
        """Return a 2D depiction of a single molecule with SMILES legend."""
        mol2d = Mol(mol)
        Compute2DCoords(mol2d)
        return MolToImage(mol2d, size=size, legend=MolToSmiles(mol2d))

    # === Molecule grid ===
    def GetMoleculesGridImg(
        self,
        mols: list[Mol],
        highlightAtomLists=None,
        highlightAtomGroupsPerMol=None,  # already added earlier in your flow
        matchesCountersPerMol=None,
        size=(300, 300),
        mols_per_row=4,
        label: str | None = None,
        label_height=28,
        sep_width=2,
        showLegend: bool = False,
    ) -> Image.Image:
        """Render a grid of molecules with legends, grid lines, and optional label."""

        # Theme colors
        bg_color = self.theme.Surface
        label_color = self.theme.Text
        sep_color = self.theme.GridLine

        # Prepare molecules safely
        # Prepare molecules safely (keep highlight lists aligned if provided)
        if highlightAtomLists is not None:
            items = list(
                zip(
                    mols,
                    highlightAtomLists,
                    highlightAtomGroupsPerMol or [None] * len(mols),
                )
            )
            items = [
                (m, hl, hg)
                for (m, hl, hg) in items
                if m is not None and m.GetNumAtoms() > 0
            ]
            mols = [RemoveAllHs(m) for (m, _, _) in items]
            highlightAtomLists = [hl for (_, hl, _) in items]
            if highlightAtomGroupsPerMol is not None:
                highlightAtomGroupsPerMol = [hg for (_, _, hg) in items]
        else:
            mols = [
                RemoveAllHs(m) for m in mols if m is not None and m.GetNumAtoms() > 0
            ]

        for m in mols:
            Compute2DCoords(m)

        legends = [
            f"Mol {m.GetProp('_MolIndex')}: {MolToSmiles(m)}" if m else "" for m in mols
        ]

        # --- Render grid directly with themed background ---
        # compute highlight colors + formula->color mapping (only if groups provided)
        formula_color = {}
        if highlightAtomGroupsPerMol is not None:
            highlightAtomColors, formula_color = (
                self._build_highlight_colors_and_formula_map(
                    highlightAtomLists,
                    highlightAtomGroupsPerMol,
                )
            )
        else:
            highlightAtomColors = self._build_highlight_colors_per_mol(
                highlightAtomLists
            )

        img = MolsToGridImage(
            mols,
            highlightAtomLists=highlightAtomLists,
            highlightAtomColors=highlightAtomColors,
            molsPerRow=mols_per_row,
            subImgSize=size,
            legends=legends,
        )

        # --- Convert RDKit → PIL safely ---
        img = ImageAdapter.to_pil(img).convert("RGB")
        img = self._apply_theme_background(img, bg_color)

        # --- Optional grid + label overlay ---
        img = self._add_grid_lines(img, mols, mols_per_row, size, sep_color, sep_width)

        # Aggregate counts across mols for legend (optional)
        counts_by_formula = None
        if matchesCountersPerMol:
            agg = Counter()
            for c in matchesCountersPerMol:
                if c:
                    agg.update(c)
            counts_by_formula = dict(agg)

        if showLegend and formula_color:
            img = self._add_color_legend(
                img,
                formula_color=formula_color,
                counts_by_formula=counts_by_formula,
                label_color=label_color,
                bg_color=self.theme.Background,
            )

        if label:
            img = self._add_label(img, label, label_color, label_height)

        return img

    # === Helper: Draw grid separators ===
    def _add_grid_lines(self, img, mols, mols_per_row, size, sep_color, sep_width):
        draw = ImageDraw.Draw(img)
        rows = (len(mols) + mols_per_row - 1) // mols_per_row
        width, height = img.size

        for i in range(1, mols_per_row):
            draw.line(
                [(i * size[0], 0), (i * size[0], height)],
                fill=sep_color,
                width=sep_width,
            )
        for j in range(1, rows):
            draw.line(
                [(0, j * size[1]), (width, j * size[1])],
                fill=sep_color,
                width=sep_width,
            )
        return img

    def hsv_palette(self, n: int, s: float = 0.75, v: float = 0.95):
        n = max(1, n)
        for i in range(n):
            h = (i / n) % 1.0
            yield colorsys.hsv_to_rgb(h, s, v)  # (r,g,b) floats 0..1

    def _build_highlight_colors_per_mol(
        self,
        highlightAtomLists: List[List[int]],
        highlightAtomGroupsPerMol: List[Dict[str, List[int]]] | None = None,
    ) -> List[Dict[int, Tuple[float, float, float]]]:
        """
        Base behavior (no groups):
            - one color per molecule (your existing behavior)

        Group behavior (when highlightAtomGroupsPerMol is provided):
            - assigns a distinct color per formula (bond-type group) within each molecule
            - returns per-molecule dict: atom_idx -> (r,g,b)
            - overlap policy: later groups overwrite earlier groups (deterministic)
        """

        def contrasting_palette(n: int) -> List[Tuple[float, float, float]]:
            if n <= 0:
                return []
            s, v = 0.80, 0.95
            step = 0.618033988749895  # golden ratio conjugate
            h = 0.0
            cols: List[Tuple[float, float, float]] = []
            for _ in range(n):
                h = (h + step) % 1.0
                cols.append(colorsys.hsv_to_rgb(h, s, v))
            return cols

        # === Group mode: multiple colors within a molecule ===
        if highlightAtomGroupsPerMol is not None:
            # stable global mapping: formula -> color (same formula = same color across all mols)
            formulas_in_order: List[str] = []
            seen: set[str] = set()
            for groups in highlightAtomGroupsPerMol:
                if not groups:
                    continue
                for formula in groups.keys():  # relies on insertion order (Py3.7+)
                    if formula not in seen:
                        seen.add(formula)
                        formulas_in_order.append(formula)

            palette = contrasting_palette(len(formulas_in_order))
            formula_color: Dict[str, Tuple[float, float, float]] = {
                f: palette[i] for i, f in enumerate(formulas_in_order)
            }

            out: List[Dict[int, Tuple[float, float, float]]] = []
            for mol_i, atoms_union in enumerate(highlightAtomLists):
                groups = (
                    highlightAtomGroupsPerMol[mol_i]
                    if mol_i < len(highlightAtomGroupsPerMol)
                    else {}
                )

                atom_color_map: Dict[int, Tuple[float, float, float]] = {}

                # assign by group (overlap policy: later overwrites earlier)
                for formula, atoms in (groups or {}).items():
                    col = formula_color.get(formula, (1.0, 0.0, 0.0))
                    for a in atoms:
                        atom_color_map[int(a)] = col

                # safety: only keep atoms that are actually highlighted
                allowed = set(atoms_union or [])
                atom_color_map = {
                    a: c for a, c in atom_color_map.items() if a in allowed
                }

                out.append(atom_color_map)

            return out

        # === Base mode: one color per molecule (your existing behavior) ===
        n = len(highlightAtomLists)
        palette = contrasting_palette(n)

        highlightAtomColors: List[Dict[int, Tuple[float, float, float]]] = []
        for i, atoms in enumerate(highlightAtomLists):
            color = palette[i] if i < len(palette) else (1.0, 0.0, 0.0)
            highlightAtomColors.append({a: color for a in atoms})

        return highlightAtomColors

    def _build_highlight_colors_and_formula_map(
        self,
        highlightAtomLists: List[List[int]],
        highlightAtomGroupsPerMol: List[Dict[str, List[int]]],
    ) -> tuple[
        List[Dict[int, Tuple[float, float, float]]],
        Dict[str, Tuple[float, float, float]],
    ]:
        def contrasting_palette(n: int) -> List[Tuple[float, float, float]]:
            if n <= 0:
                return []
            s, v = 0.80, 0.95
            step = 0.618033988749895
            h = 0.0
            cols: List[Tuple[float, float, float]] = []
            for _ in range(n):
                h = (h + step) % 1.0
                cols.append(colorsys.hsv_to_rgb(h, s, v))
            return cols

        # stable formula order: first occurrence in groups dict order
        formulas: List[str] = []
        seen: set[str] = set()
        for groups in highlightAtomGroupsPerMol:
            if not groups:
                continue
            for formula in groups.keys():
                if formula not in seen:
                    seen.add(formula)
                    formulas.append(formula)

        palette = contrasting_palette(len(formulas))
        formula_color: Dict[str, Tuple[float, float, float]] = {
            f: palette[i] for i, f in enumerate(formulas)
        }

        colors_per_mol: List[Dict[int, Tuple[float, float, float]]] = []
        for mol_i, atoms_union in enumerate(highlightAtomLists):
            groups = (
                highlightAtomGroupsPerMol[mol_i]
                if mol_i < len(highlightAtomGroupsPerMol)
                else {}
            )
            atom_color_map: Dict[int, Tuple[float, float, float]] = {}

            # overlap policy: later formula overwrites earlier
            for formula, atoms in (groups or {}).items():
                col = formula_color.get(formula, (1.0, 0.0, 0.0))
                for a in atoms:
                    atom_color_map[int(a)] = col

            # safety: only keep atoms actually highlighted
            allowed = set(atoms_union or [])
            atom_color_map = {a: c for a, c in atom_color_map.items() if a in allowed}
            colors_per_mol.append(atom_color_map)

        return colors_per_mol, formula_color

    def _add_color_legend(
        self,
        img: Image.Image,
        formula_color: Dict[str, Tuple[float, float, float]],
        counts_by_formula: Dict[str, int] | None,
        label_color: tuple[int, int, int],
        bg_color: tuple[int, int, int],
        padding: int = 10,
        swatch: int = 12,
        gap: int = 8,
        line_gap: int = 4,
        max_cols: int = 3,
    ) -> Image.Image:
        if not formula_color:
            return img

        font = ImageFont.load_default()

        items = []
        for formula, rgb in formula_color.items():
            if counts_by_formula is not None:
                items.append((rgb, f"{formula}: {counts_by_formula.get(formula, 0)}"))
            else:
                items.append((rgb, formula))

        def text_w(t: str) -> int:
            return int(font.getlength(t))

        item_w = swatch + gap + max(text_w(t) for _, t in items)
        col_w = item_w + padding
        cols = min(max_cols, max(1, img.size[0] // max(1, col_w)))
        rows = (len(items) + cols - 1) // cols

        line_h = max(swatch, font.getbbox("Ag")[3])
        legend_h = padding + rows * (line_h + line_gap) + padding - line_gap

        width, height = img.size
        out = Image.new("RGB", (width, height + legend_h), bg_color)
        out.paste(img, (0, 0))
        draw = ImageDraw.Draw(out)

        x0 = padding
        y0 = height + padding

        for idx, (rgb, text) in enumerate(items):
            r = idx // cols
            c = idx % cols
            x = x0 + c * col_w
            y = y0 + r * (line_h + line_gap)

            swatch_rgb = tuple(int(255 * v) for v in rgb)
            y_s = y + (line_h - swatch) // 2
            draw.rectangle([x, y_s, x + swatch, y_s + swatch], fill=swatch_rgb)

            draw.text((x + swatch + gap, y), text, fill=label_color, font=font)

        return out

    # === Helper: Add label annotation below grid ===
    def _add_label(self, img, label, label_color, label_height):
        """Draw label below image with subtle extra spacing for readability."""
        width, height = img.size
        annotated = Image.new(
            "RGB", (width, height + label_height), self.theme.Background
        )
        annotated.paste(img, (0, 0))

        draw_anno = ImageDraw.Draw(annotated)
        font = ImageFont.load_default()

        # subtle spacing between letters
        spacing = 1

        text_w = sum(font.getlength(ch) + spacing for ch in label) - spacing
        text_x = (width - text_w) // 2
        text_y = height + (label_height - font.getbbox(label)[3]) // 2

        for ch in label:
            draw_anno.text((text_x, text_y), ch, fill=label_color, font=font)
            text_x += font.getlength(ch) + spacing

        return annotated

    def _apply_theme_background(
        self, img: Image.Image, bg_color: tuple[int, int, int]
    ) -> Image.Image:
        """Replace near-white areas in RDKit image with themed background."""
        img = img.convert("RGB")
        data = np.array(img)
        mask = (data > 230).all(axis=-1)  # all channels near white
        data[mask] = bg_color
        return Image.fromarray(data)


class ImageAdapter:
    """Converts image objects coming from RDKit (numpy, IPython.Image, RDKit Draw.Image) into PIL.Image.Image."""

    @staticmethod
    def to_pil(img) -> Image.Image:
        """Return a Pillow image from any supported RDKit/Jupyter image type."""
        if hasattr(img, "ToImage"):  # RDKit Draw.Image (Cairo)
            return img.ToImage()

        elif isinstance(img, np.ndarray):  # Agg backend
            return Image.fromarray(img)

        elif isinstance(img, IPyImage):  # Jupyter renderer (base64 PNG)
            data = img.data
            if isinstance(data, str):
                data = base64.b64decode(data)
            if not isinstance(data, (bytes, bytearray)):
                raise TypeError(f"Unsupported IPyImage data type: {type(data)}")
            return Image.open(io.BytesIO(data))

        elif isinstance(img, Image.Image):  # Already PIL
            return img

        else:
            raise TypeError(f"Unsupported image type: {type(img)}")
