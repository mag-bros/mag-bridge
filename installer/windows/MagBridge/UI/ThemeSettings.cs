using System.Drawing;

namespace MagBridge.UI
{
    public class ThemeSettings
    {
        public Color Background { get; init; }
        public Color Surface { get; init; }
        public Color Accent { get; init; }
        public Color AccentDark { get; init; }
        public Color Text { get; init; }
        public Color SubtleText { get; init; }
        public Color Error { get; init; }
        public Color ProgressBackground { get; init; }
        public Color ProgressFill { get; init; }
        public Color ProgressBorder { get; init; }
        public Color ButtonOutline { get; init; }
        // === LAVA (Cooler, deeper — almost black with faint red warmth) ============
        public static ThemeSettings Lava => new ThemeSettings
        {
            Background = Color.FromArgb(10, 4, 4),                // Near-black with subtle red tint
            Surface = Color.FromArgb(28, 10, 8),                  // Faint warm surface
            Accent = Color.FromArgb(180, 60, 25),                 // Muted dark orange
            AccentDark = Color.FromArgb(120, 35, 15),             // Deep ember
            Text = Color.WhiteSmoke,
            SubtleText = Color.FromArgb(180, 150, 130),
            Error = Color.FromArgb(230, 70, 70),
            ProgressBackground = Color.FromArgb(28, 10, 8),
            ProgressFill = Color.FromArgb(210, 80, 40),           // Dark molten orange
            ProgressBorder = Color.FromArgb(140, 50, 30),
            ButtonOutline = Color.FromArgb(160, 45, 30)
        };

        // === LO-FI (Deeper purple tone, more moody, better contrast) ===============
        public static ThemeSettings LoFi => new ThemeSettings
        {
            Background = Color.FromArgb(10, 8, 20),               // Much darker indigo-black
            Surface = Color.FromArgb(22, 18, 35),                 // Subtle lift
            Accent = Color.FromArgb(160, 50, 235),                // Slightly darker magenta
            AccentDark = Color.FromArgb(110, 30, 160),            // Hover tone deeper
            Text = Color.WhiteSmoke,
            SubtleText = Color.FromArgb(160, 140, 190),
            Error = Color.FromArgb(250, 80, 130),
            ProgressBackground = Color.FromArgb(22, 18, 35),
            ProgressFill = Color.FromArgb(200, 160, 40),          // Warm dark yellow progress
            ProgressBorder = Color.FromArgb(110, 30, 160),
            ButtonOutline = Color.FromArgb(90, 25, 130)
        };

        // === MATRIX (True cinematic green — dark, high-contrast, less neon) ========
        public static ThemeSettings Matrix => new ThemeSettings
        {
            Background = Color.FromArgb(3, 5, 3),                 // Nearly black green
            Surface = Color.FromArgb(8, 14, 8),                   // Slight depth
            Accent = Color.FromArgb(0, 190, 70),                  // Softer primary green
            AccentDark = Color.FromArgb(0, 120, 40),              // Hover/pressed
            Text = Color.FromArgb(180, 255, 180),                 // Softer bright green-white
            SubtleText = Color.FromArgb(100, 170, 100),
            Error = Color.FromArgb(255, 80, 80),
            ProgressBackground = Color.FromArgb(8, 14, 8),
            ProgressFill = Color.FromArgb(0, 170, 60),            // Muted digital fill
            ProgressBorder = Color.FromArgb(0, 120, 40),
            ButtonOutline = Color.FromArgb(0, 150, 55)            // Slightly darker outline
        };

        // === SEA (Refined: balanced deep blue-green with crisp contrast) ===========
        public static ThemeSettings Sea => new ThemeSettings
        {
            Background = Color.FromArgb(10, 24, 36),              // Deep midnight blue
            Surface = Color.FromArgb(20, 38, 52),                 // Slightly lighter card tone
            Accent = Color.FromArgb(0, 160, 175),                 // Calm teal
            AccentDark = Color.FromArgb(0, 115, 125),             // Hover/press tone
            Text = Color.WhiteSmoke,
            SubtleText = Color.FromArgb(160, 190, 200),
            Error = Color.FromArgb(230, 90, 85),                  // Muted coral red for alerts
            ProgressBackground = Color.FromArgb(20, 38, 52),
            ProgressFill = Color.FromArgb(0, 220, 255),           // Sharp aqua contrast
            ProgressBorder = Color.FromArgb(0, 135, 150),
            ButtonOutline = Color.FromArgb(150, 70, 65)
        };

        // === SANDSTORM (Desert dusk — dark yellows, green undertones, bold contrast) ===
        public static ThemeSettings Sandstorm => new ThemeSettings
        {
            Background = Color.FromArgb(18, 18, 10),              // Nearly black with olive hue
            Surface = Color.FromArgb(30, 28, 12),                 // Dusty dark brown-yellow
            Accent = Color.FromArgb(140, 100, 25),                // Muted desert gold
            AccentDark = Color.FromArgb(120, 100, 30),            // Deep olive-gold hover
            Text = Color.FromArgb(245, 240, 210),                 // Warm parchment white
            SubtleText = Color.FromArgb(200, 190, 150),
            Error = Color.FromArgb(255, 110, 70),                 // Sunset orange for warnings
            ProgressBackground = Color.FromArgb(30, 28, 12),
            ProgressFill = Color.FromArgb(230, 200, 60),          // Rich golden loader
            ProgressBorder = Color.FromArgb(150, 120, 40),
            ButtonOutline = Color.FromArgb(90, 110, 60)
        };

        // === WHITE (Clean readable light theme — dark blue hover, green progress) ===
        // === WHITE (Soft neutral light theme with cyan-blue accents) ===============
        public static ThemeSettings White => new ThemeSettings
        {
            Background = Color.FromArgb(245, 247, 250),          // Gentle cool white
            Surface = Color.FromArgb(255, 255, 255),             // Pure content background
            Accent = Color.FromArgb(40, 90, 200),                // Cyan-blue hover (balanced)
            AccentDark = Color.FromArgb(25, 70, 160),            // Pressed blue
            Text = Color.FromArgb(20, 20, 20),                   // Black readable text
            SubtleText = Color.FromArgb(90, 90, 90),             // Muted secondary gray
            Error = Color.FromArgb(210, 60, 50),                 // Standard alert red
            ProgressBackground = Color.FromArgb(235, 237, 240),
            ProgressFill = Color.FromArgb(40, 160, 80),          // Medium green progress
            ProgressBorder = Color.FromArgb(30, 120, 60),
            ButtonOutline = Color.FromArgb(35, 85, 190)
        };

        public static ThemeSettings Dark => new ThemeSettings
        {
            Background = Color.Black,                        // Primary window background
            Surface = SystemColors.ControlDarkDark,        // Panels / cards
            Accent = SystemColors.Highlight,              // System highlight (usually blue)
            AccentDark = ControlPaint.Dark(SystemColors.Highlight),  // Derived darker tone
            Text = SystemColors.ControlLightLight,      // Primary text color
            SubtleText = SystemColors.GrayText,               // Secondary/subtle text
            Error = Color.IndianRed,                     // Standard error accent
            ProgressBackground = SystemColors.ControlDark,          // Progress bar background
            ProgressFill = SystemColors.Highlight,              // Follows accent
            ProgressBorder = ControlPaint.Dark(SystemColors.Highlight),
            ButtonOutline = SystemColors.ControlDark             // Standard neutral outline
        };
    }
}
