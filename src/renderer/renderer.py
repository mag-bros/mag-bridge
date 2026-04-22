from __future__ import annotations

import base64
import io
from collections import Counter
from dataclasses import dataclass
from typing import Optional, Tuple

import matplotlib.patches as mpatches
import numpy as np
from IPython.display import Image as IPyImage
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.figure import Figure
from PIL import Image
from rdkit.Chem import Mol, MolToSmiles, RemoveAllHs
from rdkit.Chem.Draw import MolsToGridImage, MolToImage, rdMolDraw2D
from rdkit.Chem.rdDepictor import Compute2DCoords

from src.renderer.highlight import HighlightScheme, RGBf
from src.utils.ui import Theme, ThemeSettings

RGBi = Tuple[int, int, int]  # 0..255 ints

_DPI = 100


@dataclass
class GridRenderConfig:
    """Layout parameters for GetMoleculesGridImg. Add new UI options here."""

    size: tuple[int, int] = (300, 300)
    molsPerRow: int = 4
    label: str | None = None
    showLegend: bool = False
    showAtomIndexes: bool = False
    highlightAlpha: float = 0.6
    sepWidth: int = 2
    labelHeight: int = 28  # kept for API compatibility


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
        showAtomIndexes: bool = False,
        highlightAlpha: float = 0.6,
    ) -> Image.Image:
        """Render a grid of molecules with optional highlight coloring and legend."""
        config = GridRenderConfig(
            size=size,
            molsPerRow=mols_per_row,
            label=label,
            showLegend=showLegend,
            showAtomIndexes=showAtomIndexes,
            highlightAlpha=highlightAlpha,
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
        mols, highlightAtomLists, highlightAtomGroupsPerMol, matchesCountersPerMol = self._align_inputs(
            mols, highlightAtomLists, highlightAtomGroupsPerMol, matchesCountersPerMol
        )

        for m in mols:
            Compute2DCoords(m)
        legends = [f"Mol {m.GetProp('_MolIndex') if m.HasProp('_MolIndex') else '?'}: {MolToSmiles(m)}" for m in mols]

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

        a = config.highlightAlpha
        if atom_colors:
            atom_colors = [{idx: (*rgb, a) for idx, rgb in ac.items()} for ac in atom_colors]
        if bond_colors:
            bond_colors = [{idx: (*rgb, a) for idx, rgb in bc.items()} for bc in bond_colors]

        draw_opts = rdMolDraw2D.MolDrawOptions()
        draw_opts.addAtomIndices = config.showAtomIndexes

        rdkit_img = MolsToGridImage(
            mols,
            highlightAtomLists=highlightAtomLists,
            highlightAtomColors=atom_colors or None,
            highlightBondLists=bond_lists,
            highlightBondColors=bond_colors,
            molsPerRow=config.molsPerRow,
            subImgSize=config.size,
            legends=legends,
            drawOptions=draw_opts,
        )

        mol_img = ImageAdapter.to_pil(rdkit_img).convert("RGB")
        return self._compose_figure(mol_img, len(mols), config, formula_color, matchesCountersPerMol)

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

    # === matplotlib figure composition ===

    def _compose_figure(
        self,
        mol_img: Image.Image,
        n_mols: int,
        config: GridRenderConfig,
        formula_color: dict[str, RGBf],
        matchesCountersPerMol: Optional[list[Counter[str]]],
    ) -> Image.Image:
        def _norm(rgb: RGBi) -> tuple[float, float, float]:
            return (rgb[0] / 255, rgb[1] / 255, rgb[2] / 255)

        bg_norm = _norm(self.theme.Background)
        text_norm = _norm(self.theme.Text)
        grid_norm = _norm(self.theme.GridLine)

        # Replace near-white molecule cell backgrounds with theme Surface color
        data = np.array(mol_img)
        data[(data > 230).all(axis=-1)] = self.theme.Surface

        W, H = mol_img.size
        fig = Figure(figsize=(W / _DPI, H / _DPI), dpi=_DPI, facecolor=bg_norm)
        FigureCanvasAgg(fig)

        ax = fig.add_axes((0.0, 0.0, 1.0, 1.0))
        ax.imshow(data, aspect="auto", interpolation="nearest")
        ax.axis("off")

        # Grid lines at cell boundaries (data coordinates match pixel positions in imshow)
        if n_mols > 1:
            n_rows = (n_mols + config.molsPerRow - 1) // config.molsPerRow
            for col in range(1, config.molsPerRow):
                ax.axvline(config.size[0] * col - 0.5, color=grid_norm, linewidth=config.sepWidth)
            for row in range(1, n_rows):
                ax.axhline(config.size[1] * row - 0.5, color=grid_norm, linewidth=config.sepWidth)

        # Label below axes (axes coordinates: y < 0 is below)
        if config.label:
            ax.text(0.5, -0.02, config.label, ha="center", va="top", color=text_norm, fontsize=10, transform=ax.transAxes)

        # Legend below label (or directly below axes when no label)
        if config.showLegend and formula_color:
            counts = self._aggregate_counts(matchesCountersPerMol)
            patches = [mpatches.Patch(color=rgb_f, label=f"{f}:{(counts or {}).get(f, 0)}" if counts else f) for f, rgb_f in formula_color.items()]
            y_anchor = -0.08 if config.label else -0.02
            ax.legend(
                handles=patches,
                loc="upper center",
                bbox_to_anchor=(0.5, y_anchor),
                ncols=len(patches),
                frameon=True,
                facecolor=bg_norm,
                edgecolor=grid_norm,
                labelcolor=text_norm,
            )

        buf = io.BytesIO()
        fig.savefig(buf, format="png", dpi=_DPI, bbox_inches="tight", facecolor=bg_norm)
        buf.seek(0)
        # Round-trip through numpy: strips matplotlib PNG metadata (DPI stored as tuple)
        # that breaks RDKit's IPython display hook, and normalizes to RGB mode.
        return Image.fromarray(np.array(Image.open(buf).convert("RGB")))


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
