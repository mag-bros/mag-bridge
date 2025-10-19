using MagBridge.Core;
using MagBridge.UI;
public sealed class WelcomeDialog : Form
{
    private readonly CheckedListBox checkBox;
    private readonly ThemedButton okBtn;
    private readonly ThemedButton exitBtn;
    private readonly ThemedButton selectAll;
    private readonly ThemedButton clearAll;
    private readonly ThemedTable bottomPanel;
    private readonly ThemedTable rightPanel;
    private readonly ThemedTable centerPanel;
    private readonly ThemedLabel themeLabel; // Declare as readonly
    private readonly ThemedLabel header;
    private readonly List<ThemedButton> _themeButtons = new();
    private readonly List<(string Name, ThemeSettings Settings)> _themes =
    [
        ("Sea",        ThemeSettings.Sea),
        ("White",      ThemeSettings.White),
        ("Dark",       ThemeSettings.Dark),
        ("LoFi",       ThemeSettings.LoFi),
        ("Sandstorm",  ThemeSettings.Sandstorm),
        ("Lava",       ThemeSettings.Lava),
        ("Matrix",     ThemeSettings.Matrix)
    ];

    public WelcomeDialog(Settings settings)
    {
        Text = $"Welcome — {settings.Name} - {settings.Version}";
        StartPosition = FormStartPosition.CenterParent;
        MinimumSize = new Size(620, 420);
        MaximizeBox = false;
        MinimizeBox = false;
        FormBorderStyle = FormBorderStyle.FixedDialog;

        // Initialize themeLabel
        themeLabel = new ThemedLabel
        {
            Text = "Select the software/components to install:",
            Dock = DockStyle.Top,
            Height = 44,
            Padding = new Padding(12, 12, 12, 0)  // Set padding on all sides, top margin via Padding
        };

        // Header + List
        header = new ThemedLabel
        {
            Text = "Select the software/components to install:",
            Dock = DockStyle.Top,
            Height = 44,
            Padding = new Padding(12, 12, 12, 0)
        };
        var headerPanel = new Panel
        {
            Dock = DockStyle.Top,
            Height = 44,  // Ensure the header has fixed height
            Padding = new Padding(12, 12, 12, 0)  // Add padding to the top to create space
        };
        checkBox = new CheckedListBox { Dock = DockStyle.Fill, CheckOnClick = true, IntegralHeight = false, BorderStyle = BorderStyle.FixedSingle };
        centerPanel = new ThemedTable(ThemedTable.BarOrientation.Vertical, new float[] { 10, 90 }) { Dock = DockStyle.Fill, Padding = new Padding(0), Margin = new Padding(0) };
        headerPanel.Controls.Add(header);
        centerPanel.Controls.Add(headerPanel);
        centerPanel.Controls.Add(checkBox);

        // Theme Buttons
        foreach (var theme in _themes)
        {
            var btn = new ThemedButton { Text = theme.Name, Margin = new Padding(6, 4, 6, 8), Tag = theme.Settings };

            btn.Click += (_, __) =>
            {
                Theme.SetTheme(theme.Settings);

                // Reapply highlight after theme change
                HighlightActiveButton(btn);
            };
            _themeButtons.Add(btn);
        }

        // Layout: Adaptive spacing for themes
        float baseRowWeight = Math.Max(10f, 100f / (_themeButtons.Count + 4));
        var layoutWeights = new List<float> { 8 };
        layoutWeights.AddRange(Enumerable.Repeat(baseRowWeight, _themeButtons.Count));
        layoutWeights.Add(8);
        rightPanel = new ThemedTable(ThemedTable.BarOrientation.Vertical, layoutWeights.ToArray())
        {
            Width = 120,
            Dock = DockStyle.Right,
            Padding = new Padding(8, 12, 8, 12),
            Margin = new Padding(8, 0, 8, 0)
        };
        rightPanel.Controls.Add(themeLabel); // Ensure themeLabel is added here
        rightPanel.Controls.AddRange(_themeButtons.ToArray());
        rightPanel.Controls.Add(ThemedTable.Spacer());

        // Highlight active button

        // Bottom Panel
        selectAll = new ThemedButton { Text = "Select All", Height = 42, Margin = new Padding(4, 6, 4, 6) };
        clearAll = new ThemedButton { Text = "Clear All", Height = 42, Margin = new Padding(4, 6, 4, 6) };
        okBtn = new ThemedButton { Text = "Continue", Height = 42, Margin = new Padding(4, 6, 4, 6) };
        exitBtn = new ThemedButton { Text = "Exit", Height = 42, Margin = new Padding(4, 6, 4, 6) };
        bottomPanel = new ThemedTable(new float[] { 15, 15, 38, 16, 16 })
        { Dock = DockStyle.Bottom, Padding = new Padding(10, 4, 10, 6) };
        bottomPanel.Controls.Add(selectAll);
        bottomPanel.Controls.Add(clearAll);
        bottomPanel.Controls.Add(ThemedTable.Spacer());
        bottomPanel.Controls.Add(okBtn);
        bottomPanel.Controls.Add(exitBtn);

        // Add all panels to form
        Controls.Add(centerPanel);
        Controls.Add(rightPanel);
        Controls.Add(bottomPanel);
        HighlightActiveButton(_themeButtons.FirstOrDefault(btn => btn.Tag.Equals(Theme.CurrentTheme)) ?? _themeButtons.First());

        // Apply initial theme
        Theme.ApplyToForm(this);
        Theme.ThemeChanged += () => Theme.ApplyToForm(this);

        // Populate list
        foreach (var task in settings.GetDisplayTasks())
            checkBox.Items.Add(task, task.PreChecked);

        // Button actions
        okBtn.Click += (_, __) =>
        {
            if (checkBox.CheckedItems.Count == 0)
            {
                MessageBox.Show("Select at least one item to continue.", "Nothing selected", MessageBoxButtons.OK, MessageBoxIcon.Information);
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

        // Select all / clear all actions
        selectAll.Click += (_, __) => { for (int i = 0; i < checkBox.Items.Count; i++) checkBox.SetItemChecked(i, true); };
        clearAll.Click += (_, __) => { for (int i = 0; i < checkBox.Items.Count; i++) checkBox.SetItemChecked(i, false); };
    }

    private void HighlightActiveButton(ThemedButton active)
    {
        foreach (var b in _themeButtons)
        {
            b.IsActive = (b == active);  // Only set IsActive to true for the active button
            b.Invalidate();  // Refresh the button appearance
        }
    }

    private IReadOnlyCollection<string> SelectedPackageKeys =>
        checkBox.CheckedItems.Cast<TaskParams>()
            .Select(s => string.IsNullOrWhiteSpace(s.PackageKey) ? s.Label : s.PackageKey)
            .ToArray();
}
