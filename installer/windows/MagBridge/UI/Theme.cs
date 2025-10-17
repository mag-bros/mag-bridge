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
            var g = e.Graphics;
            var bounds = ClientRectangle;

            double ratio = (double)Value / Maximum;
            int fillWidth = (int)(bounds.Width * ratio);

            using var bg = new SolidBrush(Theme.ProgressBackground);
            using var fill = new SolidBrush(Theme.ProgressFill);
            using var border = new Pen(Theme.ProgressBorder, 1);

            g.FillRectangle(bg, bounds);
            if (fillWidth > 0)
                g.FillRectangle(fill, new Rectangle(bounds.X, bounds.Y, fillWidth, bounds.Height));

            g.DrawRectangle(border, bounds.X, bounds.Y, bounds.Width - 1, bounds.Height - 1);
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
            var g = e.Graphics;
            var bounds = ClientRectangle;

            Color fill = pressed ? Theme.AccentDark : hovered ? Theme.Accent : Theme.ProgressBackground;
            using var bg = new SolidBrush(fill);
            using var border = new Pen(Theme.AccentDark, 1);
            using var textBrush = new SolidBrush(Theme.Text);

            g.FillRectangle(bg, bounds);
            g.DrawRectangle(border, 0, 0, bounds.Width - 1, bounds.Height - 1);

            var fmt = new StringFormat
            {
                Alignment = StringAlignment.Center,
                LineAlignment = StringAlignment.Center
            };

            g.DrawString(Text, Theme.PrimaryFont, textBrush, bounds, fmt);
        }

    }

    public class ThemedTextBox : TextBox
    {
        private bool focused;

        public ThemedTextBox()
        {
            SetStyle(ControlStyles.OptimizedDoubleBuffer, true);
            BorderStyle = BorderStyle.FixedSingle;
            BackColor = Theme.Surface;
            ForeColor = Theme.Text;
            Font = Theme.PrimaryFont;
        }

        protected override void OnEnter(EventArgs e)
        {
            focused = true;
            Invalidate();
            base.OnEnter(e);
        }

        protected override void OnLeave(EventArgs e)
        {
            focused = false;
            Invalidate();
            base.OnLeave(e);
        }

        protected override void OnCreateControl()
        {
            base.OnCreateControl();
            if (Multiline)
                ScrollBars = ScrollBars.Vertical;
        }

        protected override void OnPaint(PaintEventArgs e)
        {
            var g = e.Graphics;
            var bounds = ClientRectangle;

            Color bg = Theme.Surface;
            Color border = focused ? Theme.Accent : Theme.AccentDark;
            Color fg = Theme.Text;

            using var bgBrush = new SolidBrush(bg);
            using var borderPen = new Pen(border, 1);
            using var textBrush = new SolidBrush(fg);

            g.FillRectangle(bgBrush, bounds);

            var textRect = new Rectangle(bounds.X + 6, bounds.Y + 3, bounds.Width - 12, bounds.Height - 6);
            var fmt = new StringFormat
            {
                Alignment = StringAlignment.Near,
                LineAlignment = Multiline ? StringAlignment.Near : StringAlignment.Center,
                Trimming = StringTrimming.EllipsisCharacter
            };

            g.DrawString(Text, Theme.PrimaryFont, textBrush, textRect, fmt);
            g.DrawRectangle(borderPen, bounds.X, bounds.Y, bounds.Width - 1, bounds.Height - 1);
        }
    }

}
