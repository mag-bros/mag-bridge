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

        // === LO-FI (Retro neon purple–pink–blue) ============================
        public static ThemeSettings LoFi => new ThemeSettings
        {
            Background = Color.FromArgb(22, 18, 35),             // Deep indigo-black
            Surface = Color.FromArgb(35, 28, 58),                // Slightly brighter surface
            Accent = Color.FromArgb(185, 70, 255),               // Vivid magenta
            AccentDark = Color.FromArgb(140, 40, 210),           // Muted violet
            Text = Color.WhiteSmoke,
            SubtleText = Color.FromArgb(180, 160, 210),
            Error = Color.FromArgb(250, 80, 130),
            ProgressBackground = Color.FromArgb(35, 28, 58),
            ProgressFill = Color.FromArgb(110, 120, 255),        // Cool neon blue
            ProgressBorder = Color.FromArgb(90, 80, 180),
            ButtonOutline = Color.FromArgb(140, 40, 210)
        };

        // === LAVA (Dark, energetic reds/oranges) ============================
        public static ThemeSettings Lava => new ThemeSettings
        {
            Background = Color.FromArgb(30, 10, 8),              // Deep brownish black
            Surface = Color.FromArgb(45, 18, 12),                // Warm red-brown surface
            Accent = Color.FromArgb(255, 90, 40),                // Lava orange
            AccentDark = Color.FromArgb(200, 50, 25),            // Deep ember
            Text = Color.WhiteSmoke,
            SubtleText = Color.FromArgb(200, 170, 150),
            Error = Color.FromArgb(255, 70, 70),
            ProgressBackground = Color.FromArgb(45, 18, 12),
            ProgressFill = Color.FromArgb(255, 120, 60),         // Hot orange-red
            ProgressBorder = Color.FromArgb(180, 70, 40),
            ButtonOutline = Color.FromArgb(255, 100, 60)
        };

        // === MATRIX (Digital green-on-black) ================================
        public static ThemeSettings Matrix => new ThemeSettings
        {
            Background = Color.FromArgb(5, 10, 5),               // Near black
            Surface = Color.FromArgb(10, 20, 10),                // Dark green-gray
            Accent = Color.FromArgb(0, 255, 90),                 // Matrix bright green
            AccentDark = Color.FromArgb(0, 180, 60),             // Dimmer accent
            Text = Color.FromArgb(190, 255, 190),                // Soft green-white text
            SubtleText = Color.FromArgb(100, 180, 100),
            Error = Color.FromArgb(255, 60, 60),
            ProgressBackground = Color.FromArgb(10, 20, 10),
            ProgressFill = Color.FromArgb(0, 255, 100),
            ProgressBorder = Color.FromArgb(0, 180, 70),
            ButtonOutline = Color.FromArgb(0, 255, 100)
        };

        // === SEA (Deep ocean blue-green with subtle red accent) =============
        public static ThemeSettings Sea => new ThemeSettings
        {
            Background = Color.FromArgb(12, 28, 42),             // Deep navy
            Surface = Color.FromArgb(22, 40, 56),                // Slightly lighter card tone
            Accent = Color.FromArgb(0, 173, 181),                // Teal-green (original)
            AccentDark = Color.FromArgb(0, 120, 130),
            Text = Color.WhiteSmoke,
            SubtleText = Color.FromArgb(160, 190, 200),
            Error = Color.FromArgb(240, 90, 80),                 // Coral red pop for contrast
            ProgressBackground = Color.FromArgb(22, 40, 56),
            ProgressFill = Color.FromArgb(0, 190, 200),
            ProgressBorder = Color.FromArgb(0, 120, 130),
            ButtonOutline = Color.FromArgb(240, 90, 80)          // Same red hue as subtle accent
        };
    }
}
