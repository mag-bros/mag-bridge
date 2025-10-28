from PIL import Image, ImageDraw, ImageFont
import numpy as np
from rdkit.Chem import Mol, MolToSmiles
from rdkit.Chem.Draw import MolToImage, MolsToGridImage
from rdkit.Chem.rdDepictor import Compute2DCoords

from src.utils.image_bridge import ImageBridge
from src.utils.ui import Theme


class Renderer:
    """Stateful RDKit renderer configured with a persistent scientific theme."""

    def __init__(self, theme: Theme = None):
        """Initialize renderer with a given Theme (defaults to Theme.White)."""
        self.theme = theme or Theme.White

    # === Single molecule ===
    def GetMoleculeImg(self, mol: Mol, size=(200, 200)) -> Image:
        """Return a 2D depiction of a single molecule with SMILES legend."""
        mol2d = Mol(mol)
        Compute2DCoords(mol2d)
        return MolToImage(mol2d, size=size, legend=MolToSmiles(mol2d))

    # === Molecule grid ===
    def GetMoleculesGridImg(
        self,
        mols: list[Mol],
        size=(122, 122),
        mols_per_row=4,
        label: str | None = None,
        label_height=28,
        sep_width=2,
    ) -> Image:
        """Render a grid of molecules with legends, grid lines, and optional label."""

        # Theme colors
        bg_color = self.theme.Surface
        label_color = self.theme.Text
        sep_color = self.theme.GridLine

        # Prepare molecules safely
        mols = [Mol(m) for m in mols if m is not None]
        mols = [m for m in mols if m.GetNumAtoms() > 0]
        for m in mols:
            Compute2DCoords(m)
        legends = [MolToSmiles(m) if m else "" for m in mols]

        # --- Render grid directly with themed background ---
        img = MolsToGridImage(
            mols,
            molsPerRow=mols_per_row,
            subImgSize=size,
            legends=legends,
        )

        # --- Convert RDKit → PIL safely ---
        img = ImageBridge.to_pil(img).convert("RGB")
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
            draw.line([(i * size[0], 0), (i * size[0], height)], fill=sep_color, width=sep_width)
        for j in range(1, rows):
            draw.line([(0, j * size[1]), (width, j * size[1])], fill=sep_color, width=sep_width)
        return img

    # === Helper: Add label annotation below grid ===
    def _add_label(self, img, label, label_color, label_height):
        """Draw label below image with subtle extra spacing for readability."""
        width, height = img.size
        annotated = Image.new("RGB", (width, height + label_height), self.theme.Background)
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


    def _apply_theme_background(self, img: Image.Image, bg_color: tuple[int, int, int]) -> Image.Image:
        """Replace near-white areas in RDKit image with themed background."""
        img = img.convert("RGB")
        data = np.array(img)
        mask = (data > 230).all(axis=-1)           # all channels near white
        data[mask] = bg_color
        return Image.fromarray(data)
