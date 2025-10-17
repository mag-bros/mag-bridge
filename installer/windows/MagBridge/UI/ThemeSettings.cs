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

        public static ThemeSettings Dark => new ThemeSettings
        {
            Background = Color.FromArgb(18, 32, 47),
            Surface = Color.FromArgb(28, 46, 65),
            Accent = Color.FromArgb(0, 173, 181),
            AccentDark = Color.FromArgb(0, 145, 156),
            Text = Color.WhiteSmoke,
            SubtleText = Color.FromArgb(170, 190, 200),
            Error = Color.FromArgb(220, 76, 70),
            ProgressBackground = Color.FromArgb(28, 46, 65),
            ProgressFill = Color.FromArgb(0, 173, 181),
            ProgressBorder = Color.FromArgb(0, 145, 156)
        };

        public static ThemeSettings Sea => new ThemeSettings
        {
            Background = Color.FromArgb(10, 40, 60),
            Surface = Color.FromArgb(20, 60, 80),
            Accent = Color.FromArgb(0, 200, 255),
            AccentDark = Color.FromArgb(0, 150, 200),
            Text = Color.White,
            SubtleText = Color.LightCyan,
            Error = Color.FromArgb(255, 100, 100),
            ProgressBackground = Color.FromArgb(20, 60, 80),
            ProgressFill = Color.FromArgb(0, 200, 255),
            ProgressBorder = Color.FromArgb(0, 150, 200)
        };
    }
}
