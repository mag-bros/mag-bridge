using MagBridge.Core;

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

    public class ThemedBottomBar : TableLayoutPanel
    {
        public ThemedBottomBar(float[]? columnPercents = null)
        {
            Dock = DockStyle.Bottom;
            Height = 48;
            Padding = new Padding(12, 6, 12, 6);
            BackColor = Theme.Surface;
            RowCount = 1;
            ColumnCount = 4;
            DoubleBuffered = true;

            var percents = columnPercents ?? new float[] { 5, 10, 65, 20 };
            foreach (var p in percents)
                ColumnStyles.Add(new ColumnStyle(SizeType.Percent, p));

            RowStyles.Add(new RowStyle(SizeType.Percent, 100));

            RowStyles.Add(new RowStyle(SizeType.Percent, 100));

            // Ensure internal layout behaves like the old version (manual placement)
            AutoSize = false;
            GrowStyle = TableLayoutPanelGrowStyle.FixedSize;
        }

        protected override void OnLayout(LayoutEventArgs e)
        {
            base.OnLayout(e);

            var label = Controls.OfType<Label>().FirstOrDefault();
            var dropdown = Controls.OfType<ComboBox>().FirstOrDefault();
            var button = Controls.OfType<Button>().FirstOrDefault();

            if (label == null && dropdown == null && button == null)
                return;

            SuspendLayout();

            // Clear layout slots once
            foreach (Control c in Controls)
                SetCellPosition(c, new TableLayoutPanelCellPosition(0, 0));

            if (label != null)
            {
                SetColumn(label, 0);
                label.Anchor = AnchorStyles.Left | AnchorStyles.Top | AnchorStyles.Bottom;
            }

            if (dropdown != null)
            {
                SetColumn(dropdown, 1);
                dropdown.Anchor = AnchorStyles.Left | AnchorStyles.Top | AnchorStyles.Bottom;
            }

            if (button != null)
            {
                SetColumn(button, 3);
                button.Anchor = AnchorStyles.Right | AnchorStyles.Top | AnchorStyles.Bottom;
            }

            ResumeLayout();
        }
    }

    public class ThemedDropdown : ComboBox
    {
        private bool _logLevelBound;
        private EventHandler? _enumHandler;

        public ThemedDropdown()
        {
            DropDownStyle = ComboBoxStyle.DropDownList;
            FlatStyle = FlatStyle.Flat;
            BackColor = Theme.Surface;
            ForeColor = Theme.Text;
            Font = Theme.PrimaryFont;
            IntegralHeight = false;
            MaxDropDownItems = 12;
            DrawMode = DrawMode.Normal;

            SetStyle(ControlStyles.OptimizedDoubleBuffer | ControlStyles.AllPaintingInWmPaint, true);
        }

        // Light custom border rendering
        protected override void OnPaint(PaintEventArgs e)
        {
            base.OnPaint(e);

            // Draw a thin border to match themed controls
            using var pen = new Pen(Theme.AccentDark, 1);
            var rect = ClientRectangle;
            rect.Width -= 1;
            rect.Height -= 1;
            e.Graphics.DrawRectangle(pen, rect);
        }

        public void BindEnum<TEnum>(TEnum initialValue, Action<TEnum>? onChanged = null)
            where TEnum : struct, Enum
        {
            // Unhook previous
            if (_enumHandler != null)
            {
                SelectedIndexChanged -= _enumHandler;
                _enumHandler = null;
            }

            // Manual fill avoids DataSource reset quirks
            DataSource = null;
            Items.Clear();
            foreach (var v in Enum.GetValues(typeof(TEnum)))
                Items.Add(v);

            // Select by value equality
            int idx = -1;
            for (int i = 0; i < Items.Count; i++)
                if (Items[i] is TEnum tv && tv.Equals(initialValue)) { idx = i; break; }
            SelectedIndex = idx >= 0 ? idx : (Items.Count > 0 ? 0 : -1);

            // Change callback
            if (onChanged != null)
            {
                _enumHandler = (_, __) =>
                {
                    if (SelectedItem is TEnum val) onChanged(val);
                };
                SelectedIndexChanged += _enumHandler;
            }
        }

        public TEnum GetSelected<TEnum>() where TEnum : struct, System.Enum
            => SelectedItem is TEnum val ? val : default;

        // Specialized binding for LogService.LogLevel
        public void BindLogLevelDropdown()
        {
            if (_logLevelBound)
                return;

            Items.Clear();
            foreach (var level in System.Enum.GetValues(typeof(LogLevel)))
                Items.Add(level);
            var current = LogService.Global.LogLevel;
            int matchIndex = -1;
            for (int i = 0; i < Items.Count; i++)
            {
                if (Items[i] is LogLevel lv && lv.Equals(current))
                {
                    matchIndex = i;
                    break;
                }
            }
            SelectedIndex = matchIndex >= 0 ? matchIndex : (Items.Count > 0 ? 0 : -1);

            SelectedIndexChanged += (_, __) =>
            {
                if (SelectedItem is LogLevel selected)
                {
                    LogService.Global.SetLogLevel(selected);
                    LogService.Global.Write($"[INFO] Log level changed to {selected}");
                }
            };

            _logLevelBound = true;
        }
    }

    public class ThemedLabel : TextBox
    {
        public ThemedLabel()
        {
            ReadOnly = true;
            BorderStyle = BorderStyle.None;
            Multiline = false;
            TabStop = false;
            AutoSize = true;
            BackColor = Theme.Surface;
            ForeColor = Theme.Text;
            Font = Theme.PrimaryFont;
        }
    }

}
