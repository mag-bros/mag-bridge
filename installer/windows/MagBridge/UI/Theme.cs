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

            Margin = new Padding(8, 0, 8, 0);
        }

        protected override void OnMouseEnter(EventArgs e)
        { hovered = true; Invalidate(); base.OnMouseEnter(e); }

        protected override void OnMouseLeave(EventArgs e)
        { hovered = false; pressed = false; Invalidate(); base.OnMouseLeave(e); }

        protected override void OnPaint(PaintEventArgs e)
        {
            var g = e.Graphics;
            var bounds = ClientRectangle;

            // 🧹 Always clear the surface completely before painting
            g.Clear(Parent?.BackColor ?? Theme.Surface);

            // 🎨 Determine fill color based on state
            Color fill = !Enabled
                ? Color.FromArgb(100, Theme.AccentDark) // translucent dim
                : pressed
                    ? Theme.AccentDark
                    : hovered
                        ? Theme.Accent
                        : Theme.ProgressBackground;

            // 🧱 Draw background + border
            using var bg = new SolidBrush(fill);
            using var border = new Pen(hovered ? Theme.ButtonOutline : Theme.AccentDark, 1.4f);
            using var textBrush = new SolidBrush(Theme.Text);

            g.SmoothingMode = System.Drawing.Drawing2D.SmoothingMode.AntiAlias;
            g.FillRectangle(bg, bounds);
            g.DrawRectangle(border, 0, 0, bounds.Width - 1, bounds.Height - 1);

            // 🪶 Center text
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

    /// <summary>
    /// Each number represents a percentage of the total bar width (not remaining space).
    /// The sum of all values should be about 100 to fill the entire row.
    /// Controls are placed left-to-right in Add() order, one per column.
    /// Example: {8,18,12,52,10} → label=8%, dropdown=18%, copy=12%, spacer=52%, cancel=10%.
    /// </summary>
    public sealed class ThemedBottomBar : TableLayoutPanel
    {
        /// <summary>
        /// If true, controls added without an explicit (col,row) are auto-slotted
        /// left-to-right into the next free column on row 0. Explicit positions are respected.
        /// </summary>
        public bool AutoSlot { get; init; } = true;

        public ThemedBottomBar(float[]? columnPercents = null)
        {
            Dock = DockStyle.Bottom;
            Height = 48;
            Padding = new Padding(12, 6, 12, 6);
            BackColor = Theme.Surface;
            DoubleBuffered = true;

            SetStyle(ControlStyles.AllPaintingInWmPaint |
                     ControlStyles.OptimizedDoubleBuffer |
                     ControlStyles.UserPaint, true);

            ConfigureColumns(columnPercents ?? new float[] { 10, 18, 12, 50, 10 }); // default: label, dropdown, copy, spacer, cancel

            RowCount = 1;
            RowStyles.Clear();
            RowStyles.Add(new RowStyle(SizeType.Percent, 100));

            AutoSize = false;
            GrowStyle = TableLayoutPanelGrowStyle.FixedSize;
        }

        /// <summary>Reconfigure the percent columns at runtime.</summary>
        public void ConfigureColumns(float[] percents)
        {
            if (percents is null || percents.Length == 0)
                throw new ArgumentException("Column percents must be non-empty.", nameof(percents));

            ColumnCount = percents.Length;
            ColumnStyles.Clear();
            foreach (var p in percents)
                ColumnStyles.Add(new ColumnStyle(SizeType.Percent, p));
            PerformLayout();
        }

        /// <summary>Convenience spacer if you want an explicit flexible gap column.</summary>
        public static Control Spacer() => new Panel { Margin = Padding.Empty, Dock = DockStyle.Fill };

        protected override void OnControlAdded(ControlEventArgs e)
        {
            base.OnControlAdded(e);
            var c = e.Control;
            if (c is null) return;

            // Always fill columns left → right, respecting Add() order
            if (AutoSlot)
            {
                int col = Math.Min(Controls.Count - 1, ColumnCount - 1);
                SetColumn(c, col);
                SetRow(c, 0);
            }

            if (c.Dock == DockStyle.None)
                c.Dock = DockStyle.Fill;
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
            Margin = new Padding(8, 0, 8, 0);
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
            Margin = new Padding(8, 0, 8, 0);
        }
    }

}
