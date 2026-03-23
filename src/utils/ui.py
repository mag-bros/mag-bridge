from dataclasses import dataclass
from enum import Enum

from PIL import ImageColor


class Colors(Enum):
    """Centralized named color palette for consistent theming."""

    # === Core Spectrum ===
    RED = "#E63946"
    CORAL = "#FF7F50"
    SALMON = "#FA8072"
    ORANGE = "#FF9500"
    AMBER = "#FFC107"
    GOLD = "#FFD700"
    YELLOW = "#FFFF00"
    LIME = "#C6FF00"
    GREEN = "#34C759"
    FOREST = "#228B22"
    TEAL = "#008080"
    CYAN = "#00FFFF"
    SKY = "#E6FCFF"
    LOFI_SKY = "#EFF5FF"
    BLUE = "#007AFF"
    DEEP_BLUE = "#1946A0"
    NAVY = "#001F3F"
    INDIGO = "#4B0082"
    PURPLE = "#A020F0"
    MAGENTA = "#FF00FF"
    VIOLET = "#8A2BE2"
    PINK = "#FF69B4"

    # === Neutral / Utility ===
    WHITE_SMOKE = "#F5F5F5"
    WHITE = "#FFFFFF"
    LIGHT_GRAY = "#D3D3D3"
    GRAY = "#808080"
    DARK_GRAY = "#2F2F2F"
    BLACK = "#000000"
    SLATE = "#708090"
    BROWN = "#8B4513"
    OLIVE = "#808000"
    DARK_PURPLE = "#380458"
    LOFI_DARK = "#3D1A78"  # rich mid-dark purple — clearly visible, vibrant

    # === Extended functional ===
    ERROR = "#D32F2F"
    SUCCESS = "#2E7D32"
    WARNING = "#ED6C02"
    INFO = "#0288D1"
    ACCENT_GOLD = "#C9A646"
    ACCENT_TEAL = "#00A6A6"
    ACCENT_PURPLE = "#6F42C1"

    def rgb(self) -> tuple[int, int, int] | tuple[int, int, int, int]:
        """Convert HEX to RGB tuple."""
        return ImageColor.getrgb(self.value)


from dataclasses import dataclass
from typing import Dict, Tuple


@dataclass(frozen=True)
class ThemeSettings:
    """Unified visual theme for charts, diagrams, and molecule renderers."""

    # Core background and surfaces
    Background: Tuple[int, int, int]
    Surface: Tuple[int, int, int]

    # Accent layers
    Primary: Tuple[int, int, int]
    Secondary: Tuple[int, int, int]
    Highlight: Tuple[int, int, int]

    # Text and lines
    Text: Tuple[int, int, int]
    SubtleText: Tuple[int, int, int]
    GridLine: Tuple[int, int, int]
    Border: Tuple[int, int, int]

    def describe(self) -> Dict[str, Tuple[int, int, int]]:
        """Return dict of color attributes for presentation or export."""
        return {field: getattr(self, field) for field in self.__dataclass_fields__}


# === Theme presets optimized for molecule visibility ===
class Theme:
    """Factory namespace for predefined visual themes."""

    White = ThemeSettings(
        Background=Colors.WHITE.rgb(),  # Clean white base
        Surface=Colors.WHITE_SMOKE.rgb(),  # Soft off-white cards for molecules
        Primary=Colors.BLUE.rgb(),  # Calm blue accents for titles / selections
        Secondary=Colors.DEEP_BLUE.rgb(),  # Darker blue shadows
        Highlight=Colors.CYAN.rgb(),  # Cool figure accents
        Text=Colors.BLACK.rgb(),  # Default black text
        SubtleText=Colors.GRAY.rgb(),  # Muted labels and legends
        GridLine=Colors.LIGHT_GRAY.rgb(),  # Light card separators
        Border=Colors.GRAY.rgb(),  # Soft edge outlines
    )

    LoFi = ThemeSettings(
        Background=Colors.LOFI_DARK.rgb(),  # Deep space purple base
        Surface=Colors.LOFI_SKY.rgb(),  # Raised surface under molecules
        Primary=Colors.VIOLET.rgb(),  # Richer violet accent
        Secondary=Colors.ACCENT_PURPLE.rgb(),  # Slightly darker variant
        Highlight=Colors.MAGENTA.rgb(),  # Pink/magenta accents
        Text=Colors.WHITE_SMOKE.rgb(),  # High-contrast text
        SubtleText=Colors.SLATE.rgb(),  # Cool-gray subtext
        GridLine=Colors.VIOLET.rgb(),  # Vivid violet separators
        Border=Colors.ACCENT_PURPLE.rgb(),  # Soft purple frame
    )

    Sea = ThemeSettings(
        Background=Colors.NAVY.rgb(),  # Deep sea footer/outer frame
        Surface=Colors.WHITE_SMOKE.rgb(),  # Light neutral molecule panels
        Primary=Colors.TEAL.rgb(),  # Balanced teal
        Secondary=Colors.ACCENT_TEAL.rgb(),  # Stronger cyan-teal variant
        Highlight=Colors.CYAN.rgb(),  # Aqua focus accents
        Text=Colors.WHITE_SMOKE.rgb(),  # High-contrast text on dark footer
        SubtleText=Colors.LIGHT_GRAY.rgb(),  # Muted labels
        GridLine=Colors.ACCENT_TEAL.rgb(),  # Medium teal grid separators
        Border=Colors.SLATE.rgb(),  # Gentle card frame
    )
