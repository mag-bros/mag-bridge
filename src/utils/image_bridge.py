import io
import numpy as np
from PIL import Image
from IPython.display import Image as IPyImage

class ImageBridge:
    """Converts image objects coming from RDKit (numpy, IPython.Image, RDKit Draw.Image) into PIL.Image.Image."""

    @staticmethod
    def to_pil(img) -> Image.Image:
        """Return a Pillow image from any supported RDKit/Jupyter image type."""
        if hasattr(img, "ToImage"):                 # RDKit Draw.Image (Cairo)
            return img.ToImage()
        elif isinstance(img, np.ndarray):           # Agg backend
            return Image.fromarray(img)
        elif isinstance(img, IPyImage):             # Jupyter renderer (base64 PNG)
            return Image.open(io.BytesIO(img.data))
        elif isinstance(img, Image.Image):          # Already PIL
            return img
        else:
            raise TypeError(f"Unsupported image type: {type(img)}")
