from __future__ import annotations

import base64
import io
from collections import Counter
from dataclasses import dataclass
from typing import Optional, Tuple

import numpy as np
from IPython.display import Image as IPyImage
from PIL import Image, ImageDraw, ImageFont
from rdkit.Chem import Mol, MolToSmiles, RemoveAllHs
from rdkit.Chem.Draw import MolsToGridImage, MolToImage
from rdkit.Chem.rdDepictor import Compute2DCoords

from src.renderer.highlight import HighlightScheme, RGBf
from src.utils.ui import Theme, ThemeSettings

RGBi = Tuple[int, int, int]  # 0..255 ints

# Legend layout constants
_LEGEND_PADDING_X = 10
_LEGEND_PADDING_Y = 6
_LEGEND_SWATCH = 10
_LEGEND_GAP = 6
_LEGEND_ITEM_GAP = 14
_LEGEND_LINE_GAP = 4
_LEGEND_SEPARATOR_W = 1
_LEGEND_SEPARATOR_GAP = 22


@dataclass
class GridRenderConfig:
    """Layout parameters for GetMoleculesGridImg. Add new UI options here."""

    size: tuple[int, int] = (300, 300)
    molsPerRow: int = 4
    label: str | None = None
    showLegend: bool = False
    sepWidth: int = 2
    labelHeight: int = 28


class Renderer:
    """RDKit molecule renderer with theme support and formula-based highlight coloring."""

    def __init__(self, theme: ThemeSettings = Theme.Sea):
        self.theme = theme

    # === Public API ===

    def GetMoleculeImg(self, mol: Mol, size: tuple = (200, 200)) -> Image.Image:
        mol2d = Mol(mol)
        Compute2DCoords(mol2d)
        return MolToImage(mol2d, size=size, legend=MolToSmiles(mol2d))

    def GetMoleculesGridImg(
        self,
        mols: list[Mol],
        highlightAtomLists=None,
        highlightAtomGroupsPerMol=None,
        matchesCountersPerMol=None,
        size=(300, 300),
        mols_per_row=4,
        label: str | None = None,
        label_height=28,
        sep_width=2,
        showLegend: bool = False,
    ) -> Image.Image:
        """Render a grid of molecules with optional highlight coloring and legend."""
        config = GridRenderConfig(
            size=size,
            molsPerRow=mols_per_row,
            label=label,
            showLegend=showLegend,
            sepWidth=sep_width,
            labelHeight=label_height,
        )
        return self._render_grid(
            mols=mols,
            highlightAtomLists=highlightAtomLists,
            highlightAtomGroupsPerMol=highlightAtomGroupsPerMol,
            matchesCountersPerMol=matchesCountersPerMol,
            config=config,
        )

    # === Internal pipeline ===

    def _render_grid(
        self,
        mols: list[Mol],
        highlightAtomLists,
        highlightAtomGroupsPerMol,
        matchesCountersPerMol,
        config: GridRenderConfig,
    ) -> Image.Image:
        bg: RGBi = self.theme.Surface
        text_color: RGBi = self.theme.Text
        grid_color: RGBi = self.theme.GridLine

        mols, highlightAtomLists, highlightAtomGroupsPerMol, matchesCountersPerMol = self._align_inputs(
            mols, highlightAtomLists, highlightAtomGroupsPerMol, matchesCountersPerMol
        )

        for m in mols:
            Compute2DCoords(m)
        legends = [f"Mol {m.GetProp('_MolIndex') if m.HasProp('_MolIndex') else '?'}: {MolToSmiles(m)}" for m in mols]

        # Build highlight colors via HighlightScheme
        atom_colors: list[dict] = []
        bond_lists = None
        bond_colors = None
        formula_color: dict[str, RGBf] = {}

        if highlightAtomLists:
            if highlightAtomGroupsPerMol:
                scheme = HighlightScheme.fromGroups(highlightAtomGroupsPerMol, highlightAtomLists)
                atom_colors = scheme.atomColors
                formula_color = scheme.formulaColor
                if formula_color:
                    bond_lists, bond_colors = self._build_bond_colors(mols, highlightAtomGroupsPerMol, formula_color)
            else:
                scheme = HighlightScheme.fromAtomLists(highlightAtomLists)
                atom_colors = scheme.atomColors

        img = MolsToGridImage(
            mols,
            highlightAtomLists=highlightAtomLists,
            highlightAtomColors=atom_colors or None,
            highlightBondLists=bond_lists,
            highlightBondColors=bond_colors,
            molsPerRow=config.molsPerRow,
            subImgSize=config.size,
            legends=legends,
        )

        img = ImageAdapter.to_pil(img).convert("RGB")
        img = self._apply_theme_background(img, bg)
        img = self._add_grid_lines(img, len(mols), config.molsPerRow, config.size, grid_color, config.sepWidth)

        if config.label:
            img = self._add_label(img, config.label, text_color, config.labelHeight, bg_color=self.theme.Background)

        if config.showLegend and formula_color:
            counts = self._aggregate_counts(matchesCountersPerMol)
            img = self._add_legend(img, formula_color, counts, text_color, bg_color=self.theme.Background)

        return img

    # === Highlight — bond colors (requires RDKit mol traversal) ===

    @staticmethod
    def _build_bond_colors(
        mols: list[Mol],
        highlightAtomGroupsPerMol: list[dict[str, list[int]]],
        formula_color: dict[str, RGBf],
    ) -> tuple[list[list[int]], list[dict[int, RGBf]]]:
        """Derive bond highlight colors from atom groups. First-formula-wins per bond."""
        bond_lists: list[list[int]] = []
        bond_colors_out: list[dict[int, RGBf]] = []
        for mol, groups in zip(mols, highlightAtomGroupsPerMol):
            bond_color_map: dict[int, RGBf] = {}
            if not groups:
                bond_lists.append([])
                bond_colors_out.append({})
                continue
            for formula, atom_idxs in groups.items():
                col = formula_color.get(formula)
                if col is None:
                    continue
                aset = set(atom_idxs)
                for b in mol.GetBonds():
                    if b.GetBeginAtomIdx() in aset and b.GetEndAtomIdx() in aset:
                        bond_color_map.setdefault(b.GetIdx(), col)
            bond_lists.append(list(bond_color_map.keys()))
            bond_colors_out.append(bond_color_map)
        return bond_lists, bond_colors_out

    # === Input alignment ===

    @staticmethod
    def _align_inputs(
        mols: list[Mol],
        highlightAtomLists: Optional[list[list[int]]],
        highlightAtomGroupsPerMol: Optional[list[Optional[dict[str, list[int]]]]],
        matchesCountersPerMol: Optional[list[Optional[Counter[str]]]],
    ) -> tuple[
        list[Mol],
        Optional[list[list[int]]],
        Optional[list[dict[str, list[int]]]],
        Optional[list[Counter[str]]],
    ]:
        def mol_ok(m: Mol) -> bool:
            return m is not None and m.GetNumAtoms() > 0

        if highlightAtomLists is None:
            return [RemoveAllHs(m) for m in mols if mol_ok(m)], None, None, None

        n = len(mols)
        hgs: list[Optional[dict[str, list[int]]]] = highlightAtomGroupsPerMol if highlightAtomGroupsPerMol is not None else [None] * n
        mcs: list[Optional[Counter[str]]] = matchesCountersPerMol if matchesCountersPerMol is not None else [None] * n

        items = [(m, hl, hg, mc) for m, hl, hg, mc in zip(mols, highlightAtomLists, hgs, mcs) if mol_ok(m)]
        mols_out: list[Mol] = [RemoveAllHs(m) for m, *_ in items]
        hls_out: list[list[int]] = [hl for _, hl, _, _ in items]
        hgs_out: list[Optional[dict[str, list[int]]]] = [hg for _, _, hg, _ in items]
        mcs_out: list[Optional[Counter[str]]] = [mc for _, _, _, mc in items]

        filtered_hgs: Optional[list[dict[str, list[int]]]] = None if all(v is None for v in hgs_out) else [v for v in hgs_out if v is not None]
        filtered_mcs: Optional[list[Counter[str]]] = None if all(v is None for v in mcs_out) else [v for v in mcs_out if v is not None]
        return mols_out, hls_out, filtered_hgs, filtered_mcs

    @staticmethod
    def _aggregate_counts(matchesCountersPerMol: Optional[list[Counter[str]]]) -> Optional[dict[str, int]]:
        if not matchesCountersPerMol:
            return None
        agg: Counter[str] = Counter()
        for c in matchesCountersPerMol:
            if c:
                agg.update(c)
        return dict(agg)

    # === PIL post-processing ===

    @staticmethod
    def _apply_theme_background(img: Image.Image, bg_color: RGBi) -> Image.Image:
        data = np.array(img.convert("RGB"))
        data[(data > 230).all(axis=-1)] = bg_color
        return Image.fromarray(data)

    @staticmethod
    def _add_grid_lines(img: Image.Image, n_mols: int, mols_per_row: int, cell_size: tuple, sep_color: RGBi, sep_width: int) -> Image.Image:
        if n_mols <= 1:
            return img
        draw = ImageDraw.Draw(img)
        rows = (n_mols + mols_per_row - 1) // mols_per_row
        w, h = img.size
        for i in range(1, mols_per_row):
            x = i * cell_size[0]
            draw.line([(x, 0), (x, h)], fill=sep_color, width=sep_width)
        for j in range(1, rows):
            y = j * cell_size[1]
            draw.line([(0, y), (w, y)], fill=sep_color, width=sep_width)
        return img

    @staticmethod
    def _add_label(img: Image.Image, label: str, text_color: RGBi, label_height: int, bg_color: RGBi) -> Image.Image:
        W, H = img.size
        out = Image.new("RGB", (W, H + label_height), bg_color)
        out.paste(img, (0, 0))
        draw = ImageDraw.Draw(out)
        font = ImageFont.load_default()
        bbox = draw.textbbox((0, 0), label, font=font)
        x = (W - (bbox[2] - bbox[0])) // 2
        y = H + (label_height - (bbox[3] - bbox[1])) // 2
        draw.text((x, y), label, fill=text_color, font=font)
        return out

    @staticmethod
    def _add_legend(
        img: Image.Image,
        formula_color: dict[str, RGBf],
        counts_by_formula: Optional[dict[str, int]],
        text_color: RGBi,
        bg_color: RGBi,
    ) -> Image.Image:
        if not formula_color:
            return img

        font = ImageFont.load_default()
        W, H = img.size

        items: list[tuple[RGBi, str]] = []
        for formula, rgb in formula_color.items():
            txt = f"{formula}:{counts_by_formula.get(formula, 0)}" if counts_by_formula else formula
            items.append((tuple(int(255 * v) for v in rgb), txt))  # type: ignore[arg-type]

        def item_width(text: str) -> int:
            return _LEGEND_SWATCH + _LEGEND_GAP + int(font.getlength(text)) + _LEGEND_ITEM_GAP

        # Wrap items into lines
        lines: list[list[tuple]] = []
        cur: list[tuple] = []
        cur_w = 0
        for sw_rgb, txt in items:
            w = item_width(txt)
            extra = (_LEGEND_SEPARATOR_GAP * 2 + _LEGEND_SEPARATOR_W) if cur else 0
            if cur and (_LEGEND_PADDING_X + cur_w + extra + w > W - _LEGEND_PADDING_X):
                lines.append(cur)
                cur, cur_w, extra = [], 0, 0
            cur.append((sw_rgb, txt))
            cur_w += extra + w
        if cur:
            lines.append(cur)

        text_h = int(ImageDraw.Draw(Image.new("RGB", (1, 1))).textbbox((0, 0), "Ag", font=font)[3])
        line_h = max(_LEGEND_SWATCH, text_h)
        legend_h = _LEGEND_PADDING_Y + len(lines) * line_h + (len(lines) - 1) * _LEGEND_LINE_GAP + _LEGEND_PADDING_Y

        out = Image.new("RGB", (W, H + legend_h), bg_color)
        out.paste(img, (0, 0))
        draw = ImageDraw.Draw(out)

        y = H + _LEGEND_PADDING_Y
        for line in lines:
            lw = sum(item_width(txt) for _, txt in line) + (_LEGEND_SEPARATOR_GAP * 2 + _LEGEND_SEPARATOR_W) * (len(line) - 1)
            x = max(_LEGEND_PADDING_X, (W - lw) // 2)
            for i, (sw_rgb, txt) in enumerate(line):
                y_s = y + (line_h - _LEGEND_SWATCH) // 2
                draw.rectangle([x, y_s, x + _LEGEND_SWATCH, y_s + _LEGEND_SWATCH], fill=sw_rgb)
                draw.text((x + _LEGEND_SWATCH + _LEGEND_GAP, y), txt, fill=text_color, font=font)
                x += item_width(txt)
                if i < len(line) - 1:
                    x += _LEGEND_SEPARATOR_GAP
                    draw.rectangle([x, y_s, x + _LEGEND_SEPARATOR_W, y_s + _LEGEND_SWATCH], fill=(0, 0, 0))
                    x += _LEGEND_SEPARATOR_W + _LEGEND_SEPARATOR_GAP
            y += line_h + _LEGEND_LINE_GAP

        return out


class ImageAdapter:
    """Converts image objects from RDKit/numpy/IPython into PIL.Image.Image."""

    @staticmethod
    def to_pil(img) -> Image.Image:
        if hasattr(img, "ToImage"):
            return img.ToImage()
        if isinstance(img, np.ndarray):
            return Image.fromarray(img)
        if isinstance(img, IPyImage):
            data = img.data
            if isinstance(data, str):
                data = base64.b64decode(data)
            if not isinstance(data, (bytes, bytearray)):
                raise TypeError(f"Unsupported IPyImage data type: {type(data)}")
            return Image.open(io.BytesIO(data))
        if isinstance(img, Image.Image):
            return img
        raise TypeError(f"Unsupported image type: {type(img)}")
