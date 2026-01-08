from __future__ import annotations

import base64
import colorsys
import io
from collections import Counter
from typing import Dict, List, Optional, Tuple

import numpy as np
from IPython.display import Image as IPyImage
from PIL import Image, ImageDraw, ImageFont
from rdkit.Chem import Mol, MolToSmiles, RemoveAllHs
from rdkit.Chem.Draw import MolsToGridImage, MolToImage
from rdkit.Chem.rdDepictor import Compute2DCoords

from src.utils.ui import Theme

RGBf = Tuple[float, float, float]  # 0..1 floats
RGBi = Tuple[int, int, int]  # 0..255 ints


class Renderer:
    """Stateful RDKit renderer configured with a persistent scientific theme."""

    def __init__(self, theme=Theme.Sea):
        self.theme = theme

    # === Single molecule ===
    def GetMoleculeImg(self, mol: Mol, size=(200, 200)) -> Image.Image:
        mol2d = Mol(mol)
        Compute2DCoords(mol2d)
        return MolToImage(mol2d, size=size, legend=MolToSmiles(mol2d))

    # === Molecule grid ===
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
        """
        Render a grid of molecules with optional highlight coloring and an optional compact legend strip.
        """
        # Theme colors
        bg_surface: RGBi = self.theme.Surface
        text_color: RGBi = self.theme.Text
        grid_color: RGBi = self.theme.GridLine

        # Align / sanitize inputs
        mols, highlightAtomLists, highlightAtomGroupsPerMol, matchesCountersPerMol = (
            self._align_inputs(
                mols=mols,
                highlightAtomLists=highlightAtomLists,
                highlightAtomGroupsPerMol=highlightAtomGroupsPerMol,
                matchesCountersPerMol=matchesCountersPerMol,
            )
        )

        # Precompute coords and legends
        for m in mols:
            Compute2DCoords(m)
        legends = self._build_legends(mols)

        # Build highlight atom colors + formula->color map (for legend)
        highlightAtomColors, formula_color = self._build_highlight_colors(
            highlightAtomLists=highlightAtomLists,
            highlightAtomGroupsPerMol=highlightAtomGroupsPerMol,
            dark_wins=True,
        )

        # Render via RDKit
        img = MolsToGridImage(
            mols,
            highlightAtomLists=highlightAtomLists,
            highlightAtomColors=highlightAtomColors,
            molsPerRow=mols_per_row,
            subImgSize=size,
            legends=legends,
        )

        # Convert to PIL
        img = ImageAdapter.to_pil(img).convert("RGB")

        # Replace RDKit near-white background with theme surface BEFORE overlays
        img = self._apply_theme_background(img, bg_surface)

        # Grid separators
        img = self._add_grid_lines(
            img, len(mols), mols_per_row, size, grid_color, sep_width
        )

        # Bottom label (your "Bonds matched..." line)
        if label:
            img = self._add_label(
                img, label, text_color, label_height, bg_color=self.theme.Background
            )

        # Legend (compact, centered, bold separators)
        if showLegend and formula_color:
            counts_by_formula = self._aggregate_counts(matchesCountersPerMol)
            img = self._add_color_legend_compact(
                img=img,
                formula_color=formula_color,
                counts_by_formula=counts_by_formula,
                text_color=text_color,
                bg_color=self.theme.Background,  # choose Surface if you want no dark strip
                center_lines=True,
                draw_separators=True,
            )

        return img

    # -------------------------
    # Input alignment / metadata
    # -------------------------

    def _align_inputs(
        self,
        mols: list[Mol],
        highlightAtomLists,
        highlightAtomGroupsPerMol,
        matchesCountersPerMol,
    ) -> tuple[
        list[Mol],
        Optional[list[list[int]]],
        Optional[list[dict[str, list[int]]]],
        Optional[list[Counter[str]]],
    ]:
        """
        Filters invalid molecules and keeps optional parallel lists aligned.
        """

        def mol_ok(m: Mol) -> bool:
            return (m is not None) and (m.GetNumAtoms() > 0)

        if highlightAtomLists is None:
            mols = [RemoveAllHs(m) for m in mols if mol_ok(m)]
            return mols, None, None, None

        # Normalize optional lists to correct length
        n = len(mols)
        if highlightAtomGroupsPerMol is None:
            highlightAtomGroupsPerMol = [None] * n
        if matchesCountersPerMol is None:
            matchesCountersPerMol = [None] * n

        items = list(
            zip(
                mols,
                highlightAtomLists,
                highlightAtomGroupsPerMol,
                matchesCountersPerMol,
            )
        )
        items = [(m, hl, hg, mc) for (m, hl, hg, mc) in items if mol_ok(m)]

        mols_out = [RemoveAllHs(m) for (m, _, _, _) in items]
        hls_out = [hl for (_, hl, _, _) in items]
        hgs_out = [hg for (_, _, hg, _) in items]
        mcs_out = [mc for (_, _, _, mc) in items]

        # If caller didn’t provide groups/counters, keep them as None
        if all(v is None for v in hgs_out):
            hgs_out = None
        if all(v is None for v in mcs_out):
            mcs_out = None

        return mols_out, hls_out, hgs_out, mcs_out

    def _build_legends(self, mols: list[Mol]) -> list[str]:
        out = []
        for m in mols:
            idx = m.GetProp("_MolIndex") if m.HasProp("_MolIndex") else "?"
            out.append(f"Mol {idx}: {MolToSmiles(m)}")
        return out

    def _aggregate_counts(
        self, matchesCountersPerMol: Optional[list[Counter[str]]]
    ) -> Optional[dict[str, int]]:
        if not matchesCountersPerMol:
            return None
        agg: Counter[str] = Counter()
        for c in matchesCountersPerMol:
            if c:
                agg.update(c)
        return dict(agg)

    # -------------------------
    # Highlight color generation
    # -------------------------

    @staticmethod
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

    @staticmethod
    def _luminance(rgb: RGBf) -> float:
        r, g, b = rgb
        return 0.2126 * r + 0.7152 * g + 0.0722 * b  # higher = brighter

    def _build_highlight_colors(
        self,
        highlightAtomLists: Optional[list[list[int]]],
        highlightAtomGroupsPerMol: Optional[list[dict[str, list[int]]]],
        dark_wins: bool = True,
    ) -> tuple[list[dict[int, RGBf]], dict[str, RGBf]]:
        """
        Returns:
          - highlightAtomColors (one dict per molecule mapping atom idx -> RGBf)
          - formula_color map (for legend)

        If no groups provided, colors are per-molecule (legacy behavior).
        If groups provided, colors are per-formula and overlaps resolve by luminance (dark wins by default).
        """
        if not highlightAtomLists:
            return [], {}

        # No groups => one color per molecule
        if not highlightAtomGroupsPerMol:
            palette = self._contrasting_palette(len(highlightAtomLists))
            colors_per_mol: list[dict[int, RGBf]] = []
            for i, atoms in enumerate(highlightAtomLists):
                col = palette[i] if i < len(palette) else (1.0, 0.0, 0.0)
                colors_per_mol.append({int(a): col for a in atoms})
            return colors_per_mol, {}

        # Groups => stable formula->color across all mols
        formulas: list[str] = []
        seen: set[str] = set()
        for groups in highlightAtomGroupsPerMol:
            if not groups:
                continue
            for f in groups.keys():  # insertion order respected
                if f not in seen:
                    seen.add(f)
                    formulas.append(f)

        palette = self._contrasting_palette(len(formulas))
        formula_color: dict[str, RGBf] = {f: palette[i] for i, f in enumerate(formulas)}

        colors_per_mol: list[dict[int, RGBf]] = []
        for mol_i, atoms_union in enumerate(highlightAtomLists):
            groups = (
                highlightAtomGroupsPerMol[mol_i]
                if mol_i < len(highlightAtomGroupsPerMol)
                else {}
            )
            atom_color_map: dict[int, RGBf] = {}

            # sort groups by luminance so desired priority is applied
            group_items = []
            for f, atoms in (groups or {}).items():
                col = formula_color.get(f, (1.0, 0.0, 0.0))
                group_items.append((self._luminance(col), atoms, col))

            # Apply bright first, dark last => dark overwrites
            # (If dark_wins=False, reverse this.)
            group_items.sort(key=lambda t: t[0], reverse=dark_wins)

            for _, atoms, col in group_items:
                for a in atoms:
                    atom_color_map[int(a)] = col

            # keep only atoms present in union highlight list (safety)
            allowed = set(atoms_union or [])
            atom_color_map = {a: c for a, c in atom_color_map.items() if a in allowed}

            colors_per_mol.append(atom_color_map)

        return colors_per_mol, formula_color

    # -------------------------
    # Image post-processing
    # -------------------------

    def _apply_theme_background(self, img: Image.Image, bg_color: RGBi) -> Image.Image:
        """
        Replace near-white areas in the RDKit image with themed background.
        Keep this BEFORE any overlays so you don't wipe text.
        """
        data = np.array(img.convert("RGB"))
        mask = (data > 230).all(axis=-1)
        data[mask] = bg_color
        return Image.fromarray(data)

    def _add_grid_lines(
        self,
        img: Image.Image,
        n_mols: int,
        mols_per_row: int,
        cell_size: tuple[int, int],
        sep_color: RGBi,
        sep_width: int,
    ) -> Image.Image:
        if n_mols <= 1:
            return img

        draw = ImageDraw.Draw(img)
        rows = (n_mols + mols_per_row - 1) // mols_per_row
        width, height = img.size

        # vertical separators
        for i in range(1, mols_per_row):
            x = i * cell_size[0]
            draw.line([(x, 0), (x, height)], fill=sep_color, width=sep_width)

        # horizontal separators
        for j in range(1, rows):
            y = j * cell_size[1]
            draw.line([(0, y), (width, y)], fill=sep_color, width=sep_width)

        return img

    def _add_label(
        self,
        img: Image.Image,
        label: str,
        text_color: RGBi,
        label_height: int,
        bg_color: RGBi,
    ) -> Image.Image:
        W, H = img.size
        out = Image.new("RGB", (W, H + label_height), bg_color)
        out.paste(img, (0, 0))

        draw = ImageDraw.Draw(out)
        font = ImageFont.load_default()

        bbox = draw.textbbox((0, 0), label, font=font)
        text_w = bbox[2] - bbox[0]
        text_h = bbox[3] - bbox[1]

        x = (W - text_w) // 2
        y = H + (label_height - text_h) // 2
        draw.text((x, y), label, fill=text_color, font=font)

        return out

    def _add_color_legend_compact(
        self,
        img: Image.Image,
        formula_color: dict[str, RGBf],
        counts_by_formula: Optional[dict[str, int]],
        text_color: RGBi,
        bg_color: RGBi,
        *,
        padding_x: int = 10,
        padding_y: int = 6,
        swatch: int = 10,
        gap: int = 6,
        item_gap: int = 14,
        line_gap: int = 4,
        separator_w: int = 1,  # bold bar width
        separator_gap: int = 22,  # space around bar
        center_lines: bool = True,
        draw_separators: bool = True,
    ) -> Image.Image:
        if not formula_color:
            return img

        font = ImageFont.load_default()
        W, H = img.size

        # Build items: (swatch_rgb_int, text)
        items: list[tuple[RGBi, str]] = []
        for formula, rgb in formula_color.items():
            if counts_by_formula is not None:
                txt = f"{formula}:{counts_by_formula.get(formula, 0)}"
            else:
                txt = formula
            sw_rgb = tuple(int(255 * v) for v in rgb)  # type: ignore[assignment]
            items.append((sw_rgb, txt))

        # Wrap items into lines based on width
        def item_width(text: str) -> int:
            return swatch + gap + int(font.getlength(text)) + item_gap

        lines: list[list[tuple[RGBi, str]]] = []
        cur: list[tuple[RGBi, str]] = []
        cur_w = 0

        for sw_rgb, txt in items:
            w = item_width(txt)
            # add separator width if not first element in the line
            extra = (
                (separator_gap * 2 + separator_w) if (draw_separators and cur) else 0
            )
            if cur and (padding_x + cur_w + extra + w > W - padding_x):
                lines.append(cur)
                cur = []
                cur_w = 0
                extra = 0
            cur.append((sw_rgb, txt))
            cur_w += extra + w

        if cur:
            lines.append(cur)

        # Compute legend height
        dummy = Image.new("RGB", (1, 1))
        draw_tmp = ImageDraw.Draw(dummy)
        text_h = draw_tmp.textbbox((0, 0), "Ag", font=font)[3]
        line_h = max(swatch, text_h)

        legend_h = (
            padding_y + len(lines) * line_h + (len(lines) - 1) * line_gap + padding_y
        )

        out = Image.new("RGB", (W, H + legend_h), bg_color)
        out.paste(img, (0, 0))
        draw = ImageDraw.Draw(out)

        y = H + padding_y
        for line in lines:
            # compute line width for centering
            lw = 0
            for i, (_, txt) in enumerate(line):
                lw += item_width(txt)
                if draw_separators and i < len(line) - 1:
                    lw += separator_gap * 2 + separator_w

            x = max(padding_x, (W - lw) // 2) if center_lines else padding_x

            for i, (sw_rgb, txt) in enumerate(line):
                # swatch
                y_s = y + (line_h - swatch) // 2
                draw.rectangle([x, y_s, x + swatch, y_s + swatch], fill=sw_rgb)

                # text
                draw.text((x + swatch + gap, y), txt, fill=text_color, font=font)

                x += item_width(txt)

                # separator between items
                if draw_separators and i < len(line) - 1:
                    x += separator_gap
                    draw.rectangle(
                        [x, y_s, x + separator_w, y_s + swatch], fill=(0, 0, 0)
                    )
                    x += separator_w + separator_gap

            y += line_h + line_gap

        return out


class ImageAdapter:
    """Converts image objects coming from RDKit into PIL.Image.Image."""

    @staticmethod
    def to_pil(img) -> Image.Image:
        if hasattr(img, "ToImage"):  # RDKit Draw.Image (Cairo)
            return img.ToImage()

        if isinstance(img, np.ndarray):  # Agg backend
            return Image.fromarray(img)

        if isinstance(img, IPyImage):  # Jupyter renderer (base64 PNG)
            data = img.data
            if isinstance(data, str):
                data = base64.b64decode(data)
            if not isinstance(data, (bytes, bytearray)):
                raise TypeError(f"Unsupported IPyImage data type: {type(data)}")
            return Image.open(io.BytesIO(data))

        if isinstance(img, Image.Image):
            return img

        raise TypeError(f"Unsupported image type: {type(img)}")
