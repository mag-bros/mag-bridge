using System.Drawing;

namespace MagBridge.UI
{
    public static class Theme
    {
        // --- Core Palette  ---------------
        public static readonly Color Background = Color.FromArgb(18, 32, 47);        // Deep blue-gray
        public static readonly Color Surface = Color.FromArgb(28, 46, 65);        // Card panels
        public static readonly Color Accent = Color.FromArgb(0, 173, 181);       // Sea-green cyan
        public static readonly Color AccentDark = Color.FromArgb(0, 145, 156);
        public static readonly Color Text = Color.WhiteSmoke;
        public static readonly Color SubtleText = Color.FromArgb(170, 190, 200);
        public static readonly Color Error = Color.FromArgb(220, 76, 70);

        // --- Progress bar colors --------------------------------------------
        public static readonly Color ProgressBackground = Color.FromArgb(28, 46, 65);
        public static readonly Color ProgressFill = Accent;
        public static readonly Color ProgressBorder = AccentDark;

        // --- Fonts ---------------------------------------------------------
        public static readonly Font PrimaryFont = new Font("Segoe UI", 10, FontStyle.Regular);
        public static readonly Font TitleFont = new Font("Segoe UI Semibold", 11.5f);
        public static readonly Font MonoFont = new Font("Consolas", 10);
        public static int ButtonBarHeight => 54;

        // --- Helpers -------------------------------------------------------
        public static void ApplyToForm(Form form)
        {
            form.BackColor = Background;
            form.ForeColor = Text;
            form.Font = PrimaryFont;
        }

        public static void PaintTextBox(Graphics g, Rectangle bounds, string text, bool focused, bool multiline = false)
        {
            Color bg = Surface;
            Color border = focused ? Accent : AccentDark;
            Color fg = Text;

            using var bgBrush = new SolidBrush(bg);
            using var borderPen = new Pen(border, 1);
            using var textBrush = new SolidBrush(fg);
            g.FillRectangle(bgBrush, bounds);

            var textRect = new Rectangle(bounds.X + 6, bounds.Y + 3, bounds.Width - 12, bounds.Height - 6);
            var fmt = new StringFormat
            {
                Alignment = StringAlignment.Near,
                LineAlignment = multiline ? StringAlignment.Near : StringAlignment.Center,
                Trimming = StringTrimming.EllipsisCharacter
            };

            g.DrawString(text, PrimaryFont, textBrush, textRect, fmt);
            g.DrawRectangle(borderPen, bounds.X, bounds.Y, bounds.Width - 1, bounds.Height - 1);
        }

        public static void PaintButton(Graphics g, Rectangle bounds, string text, bool hovered, bool pressed)
        {
            Color fill = pressed ? AccentDark : hovered ? Accent : ProgressBackground;
            using var bg = new SolidBrush(fill);
            using var border = new Pen(AccentDark, 1);
            using var textBrush = new SolidBrush(Text);

            g.FillRectangle(bg, bounds);
            g.DrawRectangle(border, 0, 0, bounds.Width - 1, bounds.Height - 1);

            // Center text
            var fmt = new StringFormat { Alignment = StringAlignment.Center, LineAlignment = StringAlignment.Center };
            g.DrawString(text, PrimaryFont, textBrush, bounds, fmt);
        }

        public static void PaintProgressBar(Graphics g, Rectangle bounds, int value, int max)
        {
            double ratio = (double)value / max;
            int fillWidth = (int)(bounds.Width * ratio);

            using var bg = new SolidBrush(ProgressBackground);
            using var fill = new SolidBrush(ProgressFill);
            using var border = new Pen(ProgressBorder, 1);

            g.FillRectangle(bg, bounds);
            if (fillWidth > 0)
                g.FillRectangle(fill, new Rectangle(bounds.X, bounds.Y, fillWidth, bounds.Height));

            g.DrawRectangle(border, bounds.X, bounds.Y, bounds.Width - 1, bounds.Height - 1);
        }
    }

    public class ThemedProgressBar : ProgressBar
    {
        public ThemedProgressBar()
        {
            SetStyle(ControlStyles.UserPaint, true);
            BackColor = Theme.ProgressBackground;
        }

        protected override void OnPaint(PaintEventArgs e)
        {
            Theme.PaintProgressBar(e.Graphics, ClientRectangle, Value, Maximum);
        }
    }

    public class ThemedButton : Button
    {
        private bool hovered;
        private bool pressed;

        protected override Size DefaultSize => new Size(120, 36);

        public ThemedButton()
        {
            SetStyle(ControlStyles.AllPaintingInWmPaint |
                     ControlStyles.UserPaint |
                     ControlStyles.OptimizedDoubleBuffer, true);

            FlatStyle = FlatStyle.Flat;
            FlatAppearance.BorderSize = 0;
            BackColor = Theme.ProgressBackground;
            ForeColor = Theme.Text;
            Font = Theme.PrimaryFont;
        }

        protected override void OnMouseEnter(EventArgs e)
        { hovered = true; Invalidate(); base.OnMouseEnter(e); }

        protected override void OnMouseLeave(EventArgs e)
        { hovered = false; pressed = false; Invalidate(); base.OnMouseLeave(e); }

        protected override void OnMouseDown(MouseEventArgs e)
        { pressed = true; Invalidate(); base.OnMouseDown(e); }

        protected override void OnMouseUp(MouseEventArgs e)
        { pressed = false; Invalidate(); base.OnMouseUp(e); }

        protected override void OnPaint(PaintEventArgs e)
        {
            Theme.PaintButton(e.Graphics, ClientRectangle, Text, hovered, pressed);
        }
    }
    public class ThemedTextBox : TextBox
    {
        public ThemedTextBox()
        {
            // Native painting is better for multiline/scrollable text.
            // Drop UserPaint to avoid losing caret and drag selection.
            SetStyle(ControlStyles.OptimizedDoubleBuffer, true);

            BorderStyle = BorderStyle.FixedSingle;
            BackColor = Theme.Surface;
            ForeColor = Theme.Text;
            Font = Theme.PrimaryFont;
        }

        protected override void OnEnter(EventArgs e)
        {
            base.OnEnter(e);
            Invalidate();
        }

        protected override void OnLeave(EventArgs e)
        {
            base.OnLeave(e);
            Invalidate();
        }

        protected override void OnCreateControl()
        {
            base.OnCreateControl();
            // Ensure scrollbars look consistent
            if (Multiline)
                ScrollBars = ScrollBars.Vertical;
        }
    }

}
