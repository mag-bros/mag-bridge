namespace MagBridge.UI
{
    // ============================================================
    //  THEME DEFINITION
    // ============================================================
    public static class Theme
    {
        private static ThemeSettings _current = ThemeSettings.Sea;

        // --- Core Palette ---------------
        public static Color Background => _current.Background;
        public static Color Surface => _current.Surface;
        public static Color Accent => _current.Accent;
        public static Color AccentDark => _current.AccentDark;
        public static Color Text => _current.Text;
        public static Color SubtleText => _current.SubtleText;
        public static Color Error => _current.Error;
        public static Color ButtonOutline => _current.ButtonOutline;

        // --- Progress bar colors --------------------------------
        public static Color ProgressBackground => _current.ProgressBackground;
        public static Color ProgressFill => _current.ProgressFill;
        public static Color ProgressBorder => _current.ProgressBorder;

        // --- Fonts -----------------------------------------------
        public static readonly Font PrimaryFont = new Font("Segoe UI", 10, FontStyle.Regular);
        public static readonly Font TitleFont = new Font("Segoe UI Semibold", 11.5f);
        public static readonly Font MonoFont = new Font("Consolas", 10);
        public static int ButtonBarHeight => 54;

        // --- Helpers ---------------------------------------------
        public static void ApplyToForm(Form form)
        {
            form.BackColor = Background;
            form.ForeColor = Text;
            form.Font = PrimaryFont;
        }
    }

    // ============================================================
    //  THEMED PROGRESS BAR
    // ============================================================
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

    // ============================================================
    //  THEMED BUTTON
    // ============================================================
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

            Color fill = pressed
                ? Theme.AccentDark
                : hovered
                    ? Theme.Accent
                    : Theme.ProgressBackground;

            using var bg = new SolidBrush(fill);
            using var border = new Pen(hovered ? Theme.ButtonOutline : Theme.AccentDark, 1.4f);
            using var textBrush = new SolidBrush(Theme.Text);

            g.SmoothingMode = System.Drawing.Drawing2D.SmoothingMode.AntiAlias;
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

    // ============================================================
    //  THEMED TEXT BOX (for plain input)
    // ============================================================
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
            Color border = focused ? Theme.ButtonOutline : Theme.AccentDark;
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

    // ============================================================
    //  THEMED LOG BOX (RichTextBox for colored logs)
    // ============================================================
    public class ThemedLogBox : RichTextBox
    {
        private bool focused;

        public ThemedLogBox()
        {
            BorderStyle = BorderStyle.FixedSingle;
            BackColor = Theme.Surface;
            ForeColor = Theme.Text;
            Font = Theme.MonoFont;
            ReadOnly = true;
            DetectUrls = false;
            ScrollBars = RichTextBoxScrollBars.Vertical;
            WordWrap = false;
            HideSelection = false;
            SetStyle(ControlStyles.OptimizedDoubleBuffer | ControlStyles.AllPaintingInWmPaint, true);
        }

        public void AppendSafe(string text, Color? color = null)
        {
            if (InvokeRequired)
            {
                BeginInvoke((Action)(() => AppendSafe(text, color)));
                return;
            }

            if (color.HasValue)
            {
                int start = TextLength;
                SelectionStart = start;
                SelectionLength = 0;
                SelectionColor = color.Value;
                AppendText(text);
                SelectionColor = ForeColor;
            }
            else
            {
                AppendText(text);
            }

            ScrollToCaret();
        }

        protected override void OnEnter(EventArgs e)
        { focused = true; Invalidate(); base.OnEnter(e); }

        protected override void OnLeave(EventArgs e)
        { focused = false; Invalidate(); base.OnLeave(e); }

        protected override void OnPaint(PaintEventArgs e)
        {
            base.OnPaint(e);
            var g = e.Graphics;
            var bounds = ClientRectangle;
            var borderColor = focused ? Theme.ButtonOutline : Theme.AccentDark;

            using var pen = new Pen(borderColor, 1);
            g.DrawRectangle(pen, bounds.X, bounds.Y, bounds.Width - 1, bounds.Height - 1);
        }
    }

    public class ThemedDropdown : ComboBox
    {
        public ThemedDropdown()
        {
            DropDownStyle = ComboBoxStyle.DropDownList;
            FlatStyle = FlatStyle.Flat;
            BackColor = Theme.Surface;
            ForeColor = Theme.Text;
            Font = Theme.PrimaryFont;
            IntegralHeight = false;
            MaxDropDownItems = 12;
            DrawMode = DrawMode.OwnerDrawFixed; // so we can theme items
            ItemHeight = Math.Max(18, (int)Math.Ceiling(Font.GetHeight()) + 4);

            SetStyle(ControlStyles.OptimizedDoubleBuffer | ControlStyles.AllPaintingInWmPaint, true);
        }

        // Owner-draw items (keeps them on brand)
        protected override void OnDrawItem(DrawItemEventArgs e)
        {
            e.DrawBackground();
            if (e.Index >= 0 && e.Index < Items.Count)
            {
                var isSelected = (e.State & DrawItemState.Selected) == DrawItemState.Selected;
                using var bg = new SolidBrush(isSelected ? Theme.AccentDark : BackColor);
                using var fg = new SolidBrush(ForeColor);

                e.Graphics.FillRectangle(bg, e.Bounds);
                var text = GetItemText(Items[e.Index]);
                e.Graphics.DrawString(text, Font, fg, e.Bounds.X + 6, e.Bounds.Y + 2);
            }
            e.DrawFocusRectangle();
            base.OnDrawItem(e);
        }

        // Thin custom border to match your themed controls
        protected override void OnPaint(PaintEventArgs e)
        {
            base.OnPaint(e); // ComboBox painting is mostly native; border is drawn below via WndProc
        }

        protected override void WndProc(ref Message m)
        {
            base.WndProc(ref m);
            const int WM_PAINT = 0x000F;
            if (m.Msg == WM_PAINT && !DroppedDown)
            {
                using var g = CreateGraphics();
                using var pen = new Pen(Theme.AccentDark, 1);
                var r = ClientRectangle;
                g.DrawRectangle(pen, 0, 0, r.Width - 1, r.Height - 1);
            }
        }

        // ---------- Convenience: bind any enum cleanly ----------
        public void BindEnum<TEnum>(TEnum initialValue, Action<TEnum>? onChanged = null) where TEnum : struct, Enum
        {
            DataSource = Enum.GetValues(typeof(TEnum));
            SelectedItem = initialValue;

            SelectionChangeCommitted += (_, __) =>
            {
                if (SelectedItem is TEnum val)
                    onChanged?.Invoke(val);
            };
        }

        public TEnum GetSelected<TEnum>() where TEnum : struct, Enum
            => SelectedItem is TEnum val ? val : default;
    }

    public class ThemedBottomBar : Panel
    {
        public ThemedBottomBar()
        {
            Dock = DockStyle.Bottom;
            Height = 48;
            Padding = new Padding(12, 6, 12, 6);
            BackColor = Theme.Surface;
            SetStyle(ControlStyles.OptimizedDoubleBuffer | ControlStyles.AllPaintingInWmPaint, true);
        }

        protected override void OnLayout(LayoutEventArgs e)
        {
            base.OnLayout(e);

            var dropdown = Controls.OfType<ComboBox>().FirstOrDefault();
            var button = Controls.OfType<Button>().FirstOrDefault();
            if (dropdown == null && button == null) return;

            if (dropdown != null)
            {
                dropdown.Anchor = AnchorStyles.Left | AnchorStyles.Top;
                dropdown.Location = new Point(Padding.Left, (Height - dropdown.Height) / 2);
            }

            if (button != null)
            {
                button.Anchor = AnchorStyles.Right | AnchorStyles.Top;
                button.Location = new Point(
                    Width - button.Width - Padding.Right,
                    (Height - button.Height) / 2);
            }
        }
    }
}
