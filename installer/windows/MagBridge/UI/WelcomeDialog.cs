using MagBridge.Core;
using MagBridge.UI;

public sealed class WelcomeDialog : Form
{
    private readonly CheckedListBox checkBox;
    private readonly Button okBtn;
    private readonly Button exitBtn;

    public IReadOnlyCollection<string> SelectedPackageKeys =>
        checkBox.CheckedItems.Cast<TaskParams>()
            .Select(s => string.IsNullOrWhiteSpace(s.PackageKey) ? s.Label : s.PackageKey)
            .ToArray();

    private sealed class PackageItem
    {
        public string Key { get; }
        public string Display { get; }
        public PackageItem(string key, string display) { Key = key; Display = display; }
        public override string ToString() => Display;
    }

    public WelcomeDialog(Settings settings)
    {
        Text = $"Welcome — {settings.Name} - {settings.Version}";
        StartPosition = FormStartPosition.CenterParent;
        MinimumSize = new Size(620, 420);
        MaximizeBox = false;
        MinimizeBox = false;
        FormBorderStyle = FormBorderStyle.FixedDialog;

        // Header
        var header = new Label
        {
            Text = "Select the software/components to install:",
            Dock = DockStyle.Top,
            Height = 44,
            TextAlign = ContentAlignment.MiddleLeft,
            Padding = new Padding(12, 12, 12, 0)
        };

        // List
        checkBox = new CheckedListBox
        {
            Dock = DockStyle.Fill,
            CheckOnClick = true,
            IntegralHeight = false,
            BorderStyle = BorderStyle.FixedSingle
        };

        // ───────────────────────────────────────────────
        // CENTER PANEL (header + list in one container)
        // ───────────────────────────────────────────────
        var centerPanel = new ThemedTable(ThemedTable.BarOrientation.Vertical, new float[] { 10, 90 })
        {
            Dock = DockStyle.Fill,
            Padding = new Padding(0),
            Margin = new Padding(0)
        };
        centerPanel.Controls.Add(header);
        centerPanel.Controls.Add(checkBox);

        // ───────────────────────────────────────────────
        // RIGHT THEME PANEL
        // ───────────────────────────────────────────────
        var themeLabel = new ThemedLabel
        {
            Text = "Theme:",
            TextAlign = HorizontalAlignment.Center,
            Dock = DockStyle.Fill,
            Margin = new Padding(4, 2, 4, 10)
        };
        var themeSea = new ThemedButton { Text = "Sea", Margin = new Padding(6, 4, 6, 8) };
        var themeWhite = new ThemedButton { Text = "White", Margin = new Padding(6, 4, 6, 8) };
        var themeMatrix = new ThemedButton { Text = "Matrix", Margin = new Padding(6, 4, 6, 8) };
        var themeLofi = new ThemedButton { Text = "LoFi", Margin = new Padding(6, 4, 6, 8) };
        var themeSandstorm = new ThemedButton { Text = "Sandstorm", Margin = new Padding(6, 4, 6, 8) };
        var themeLava = new ThemedButton { Text = "Lava", Margin = new Padding(6, 4, 6, 8) };

        themeSea.Click += (_, __) => Theme.SetTheme(ThemeSettings.Sea);
        themeWhite.Click += (_, __) => Theme.SetTheme(ThemeSettings.White);
        themeMatrix.Click += (_, __) => Theme.SetTheme(ThemeSettings.Matrix);
        themeLofi.Click += (_, __) => Theme.SetTheme(ThemeSettings.LoFi);
        themeSandstorm.Click += (_, __) => Theme.SetTheme(ThemeSettings.Sandstorm);
        themeLava.Click += (_, __) => Theme.SetTheme(ThemeSettings.Lava);

        var rightPanel = new ThemedTable(ThemedTable.BarOrientation.Vertical, new float[] { 8, 12, 12, 12, 12, 12, 12, 20 })
        {
            Width = 120,
            Dock = DockStyle.Right,
            Padding = new Padding(8, 12, 8, 12),
            Margin = new Padding(8, 0, 8, 0)
        };
        rightPanel.Controls.Add(themeLabel);
        rightPanel.Controls.Add(themeSea);
        rightPanel.Controls.Add(themeWhite);
        rightPanel.Controls.Add(themeMatrix);
        rightPanel.Controls.Add(themeLofi);
        rightPanel.Controls.Add(themeSandstorm);
        rightPanel.Controls.Add(themeLava);
        rightPanel.Controls.Add(ThemedTable.Spacer());

        // ───────────────────────────────────────────────
        // BOTTOM ACTION BAR
        // ───────────────────────────────────────────────
        var selectAll = new ThemedButton { Text = "Select All", Height = 42, Margin = new Padding(4, 6, 4, 6) };
        var clearAll = new ThemedButton { Text = "Clear All", Height = 42, Margin = new Padding(4, 6, 4, 6) };
        okBtn = new ThemedButton { Text = "Continue", Height = 42, Margin = new Padding(4, 6, 4, 6) };
        exitBtn = new ThemedButton { Text = "Exit", Height = 42, Margin = new Padding(4, 6, 4, 6) };

        var bottomPanel = new ThemedTable(new float[] { 15, 15, 38, 16, 16 })
        {
            Dock = DockStyle.Bottom,
            Padding = new Padding(10, 4, 10, 6)
        };
        bottomPanel.Controls.Add(selectAll);
        bottomPanel.Controls.Add(clearAll);
        bottomPanel.Controls.Add(ThemedTable.Spacer());
        bottomPanel.Controls.Add(okBtn);
        bottomPanel.Controls.Add(exitBtn);

        // ───────────────────────────────────────────────
        // Add to form
        // ───────────────────────────────────────────────
        Controls.Add(centerPanel);
        Controls.Add(rightPanel);
        Controls.Add(bottomPanel);

        Theme.ApplyToForm(this);
        Theme.ThemeChanged += () => Theme.ApplyToForm(this);

        // Populate list
        foreach (var task in settings.GetDisplayTasks())
            checkBox.Items.Add(task, task.PreChecked);

        // Button logic
        selectAll.Click += (_, __) =>
        {
            for (int i = 0; i < checkBox.Items.Count; i++)
                checkBox.SetItemChecked(i, true);
        };

        clearAll.Click += (_, __) =>
        {
            for (int i = 0; i < checkBox.Items.Count; i++)
                checkBox.SetItemChecked(i, false);
        };

        okBtn.Click += (_, __) =>
        {
            if (checkBox.CheckedItems.Count == 0)
            {
                MessageBox.Show("Select at least one item to continue.",
                    "Nothing selected", MessageBoxButtons.OK, MessageBoxIcon.Information);
                return;
            }
            DialogResult = DialogResult.OK;
            Close();
        };

        exitBtn.Click += (_, __) =>
        {
            DialogResult = DialogResult.Cancel;
            Close();
        };
    }

}
