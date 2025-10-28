from dataclasses import dataclass
from enum import Enum
from PIL import ImageColor


class Colors(Enum):
    """Centralized named color palette for consistent theming."""
    # === Core Spectrum ===
    RED         = "#E63946"
    CORAL       = "#FF7F50"
    SALMON      = "#FA8072"
    ORANGE      = "#FF9500"
    AMBER       = "#FFC107"
    GOLD        = "#FFD700"
    YELLOW      = "#FFFF00"
    LIME        = "#C6FF00"
    GREEN       = "#34C759"
    FOREST      = "#228B22"
    TEAL        = "#008080"
    CYAN        = "#00FFFF"
    SKY         = "#C4EEF3"
    BLUE        = "#007AFF"
    DEEP_BLUE   = "#1946A0"
    NAVY        = "#001F3F"
    INDIGO      = "#4B0082"
    PURPLE      = "#A020F0"
    MAGENTA     = "#FF00FF"
    VIOLET      = "#8A2BE2"
    PINK        = "#FF69B4"

    # === Neutral / Utility ===
    WHITE_SMOKE = "#F5F5F5"
    WHITE       = "#FFFFFF"
    LIGHT_GRAY  = "#D3D3D3"
    GRAY        = "#808080"
    DARK_GRAY   = "#2F2F2F"
    BLACK       = "#000000"
    SLATE       = "#708090"
    BROWN       = "#8B4513"
    OLIVE       = "#808000"

    # === Extended functional ===
    ERROR       = "#D32F2F"
    SUCCESS     = "#2E7D32"
    WARNING     = "#ED6C02"
    INFO        = "#0288D1"
    ACCENT_GOLD = "#C9A646"
    ACCENT_TEAL = "#00A6A6"
    ACCENT_PURPLE = "#6F42C1"

    def rgb(self) -> tuple[int, int, int]:
        """Convert HEX to RGB tuple."""
        return ImageColor.getrgb(self.value)

@dataclass(frozen=True)
class Theme:
    """Unified visual theme for charts, diagrams, and molecule renderers."""

    # Core background and surfaces
    Background: tuple[int, int, int]
    Surface: tuple[int, int, int]

    # Accent layers
    Primary: tuple[int, int, int]
    Secondary: tuple[int, int, int]
    Highlight: tuple[int, int, int]

    # Text and lines
    Text: tuple[int, int, int]
    SubtleText: tuple[int, int, int]
    GridLine: tuple[int, int, int]
    Border: tuple[int, int, int]

    def describe(self) -> dict[str, tuple[int, int, int]]:
        """Return dict of color attributes for presentation or export."""
        return {k: getattr(self, k) for k in self.__dataclass_fields__}
    
# === Theme presets optimized for molecule visibility ===

Theme.White = Theme(
    Background=Colors.WHITE.rgb(),              # Clean white base
    Surface=Colors.WHITE_SMOKE.rgb(),           # Soft off-white cards for molecules
    Primary=Colors.BLUE.rgb(),                  # Calm blue accents for titles / selections
    Secondary=Colors.DEEP_BLUE.rgb(),           # Darker blue shadows
    Highlight=Colors.CYAN.rgb(),                # Cool figure accents
    Text=Colors.BLACK.rgb(),                    # Default black text
    SubtleText=Colors.GRAY.rgb(),               # Muted labels and legends
    GridLine=Colors.LIGHT_GRAY.rgb(),           # Light card separators
    Border=Colors.GRAY.rgb(),                   # Soft edge outlines
)

Theme.LoFi = Theme(
    Background=Colors.BLACK.rgb(),              # Rich deep base
    Surface=Colors.SKY.rgb(),             # Raised surface under molecules
    Primary=Colors.PURPLE.rgb(),                # Signature magenta-purple tone
    Secondary=Colors.ACCENT_PURPLE.rgb(),       # Slightly darker version
    Highlight=Colors.MAGENTA.rgb(),             # Pink/magenta accents
    Text=Colors.WHITE_SMOKE.rgb(),              # High-contrast text
    SubtleText=Colors.SLATE.rgb(),              # Cool-gray subtext
    GridLine=Colors.ACCENT_PURPLE.rgb(),        # Thin purple separators
    Border=Colors.DARK_GRAY.rgb(),              # Minimal neutral frame
)

Theme.Sea = Theme(
    Background=Colors.NAVY.rgb(),               # Deep midnight base
    Surface=Colors.SKY.rgb(),                       # Slightly lighter blue-gray panels
    Primary=Colors.TEAL.rgb(),                  # Balanced teal
    Secondary=Colors.ACCENT_TEAL.rgb(),         # Stronger cyan-teal variant
    Highlight=Colors.CYAN.rgb(),                # Aqua focus accents
    Text=Colors.WHITE_SMOKE.rgb(),              # Clear high-contrast text
    SubtleText=Colors.LIGHT_GRAY.rgb(),         # Muted labels
    GridLine=Colors.ACCENT_TEAL.rgb(),                     # Medium teal grid separators
    Border=Colors.SLATE.rgb(),                  # Gentle card frame
)
