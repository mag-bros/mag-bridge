from __future__ import annotations

import base64
import colorsys
import io
import typing
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
        highlightAtomLists=None,  # TODO:: add better typing
        size=(300, 300),
        mols_per_row=4,
        label: str | None = None,
        label_height=28,
        sep_width=2,
    ) -> Image.Image:
        """Render a grid of molecules with legends, grid lines, and optional label."""

        # Theme colors
        bg_color = self.theme.Surface
        label_color = self.theme.Text
        sep_color = self.theme.GridLine

        # Prepare molecules safely
        mols = [RemoveAllHs(m) for m in mols if m.GetNumAtoms() > 0]
        for m in mols:
            Compute2DCoords(m)
        legends = [
            f"Mol {m.GetProp('_MolIndex')}: {MolToSmiles(m)}" if m else "" for m in mols
        ]

        # --- Render grid directly with themed background ---
        img = MolsToGridImage(
            mols,
            highlightAtomLists=highlightAtomLists,
            highlightAtomColors=self._build_highlight_colors_per_mol(
                highlightAtomLists
            ),
            molsPerRow=mols_per_row,
            subImgSize=size,
            legends=legends,
        )

        # --- Convert RDKit → PIL safely ---
        img = ImageAdapter.to_pil(img).convert("RGB")
        img = self._apply_theme_background(img, bg_color)

        # --- Optional grid + label overlay ---
        img = self._add_grid_lines(img, mols, mols_per_row, size, sep_color, sep_width)
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
    ) -> List[Dict[int, Tuple[float, float, float]]]:
        """
        Only input: highlightAtomLists (list-of-lists, one list per molecule).

        Returns:
        highlightAtomColors: list[dict[int, (r,g,b)]]
            - one dict per molecule
            - all atoms within a given molecule get the same color
            - colors are high-contrast across molecules

        Example:
        highlightAtomLists = [[0,1,2], [3,4], []]
        -> [
            {0:(...),1:(...),2:(...)},
            {3:(...),4:(...)},
            {}
            ]
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

        n = len(highlightAtomLists)
        palette = contrasting_palette(n)

        highlightAtomColors: List[Dict[int, Tuple[float, float, float]]] = []
        for i, atoms in enumerate(highlightAtomLists):
            color = palette[i] if i < len(palette) else (1.0, 0.0, 0.0)
            highlightAtomColors.append({a: color for a in atoms})

        return highlightAtomColors

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
