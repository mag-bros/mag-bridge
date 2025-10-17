using MagBridge.Core;
using MagBridge.UI;

public sealed class WelcomeDialog : Form
{
    private readonly CheckedListBox list;
    private readonly Button okBtn;
    private readonly Button exitBtn;

    public IReadOnlyCollection<string> SelectedPackageKeys =>
        list.CheckedItems.Cast<PackageItem>().Select(i => i.Key).ToArray();

    private sealed class PackageItem
    {
        public string Key { get; }
        public string Display { get; }
        public PackageItem(string key, string display) { Key = key; Display = display; }
        public override string ToString() => Display;
    }
    public WelcomeDialog(Settings settings)
    {
        Text = $"Welcome — {settings.Name}";
        StartPosition = FormStartPosition.CenterParent;
        MinimumSize = new Size(620, 420); // slightly wider for all buttons
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

        // Package list
        list = new CheckedListBox
        {
            Dock = DockStyle.Fill,
            CheckOnClick = true,
            IntegralHeight = false,
            BorderStyle = BorderStyle.FixedSingle
        };
        // --- Bottom panel ---------------------------------------------------
        var bottomPanel = new Panel
        {
            Dock = DockStyle.Bottom,
            Height = 50,
            Padding = new Padding(12)
        };

        // Buttons (left side)
        var selectAll = new ThemedButton
        {
            Text = "Select All",
            Width = 70,
            Height = 30
        };

        var clearAll = new ThemedButton
        {
            Text = "Clear All",
            Width = 70,
            Height = 30
        };

        // Buttons (right side)
        okBtn = new ThemedButton
        {
            Text = "Continue",
            Width = 110,
            Height = 30
        };

        exitBtn = new ThemedButton
        {
            Text = "Exit",
            Width = 40,
            Height = 30
        };

        // Add buttons (order does NOT matter anymore)
        bottomPanel.Controls.Add(selectAll);
        bottomPanel.Controls.Add(clearAll);
        bottomPanel.Controls.Add(okBtn);
        bottomPanel.Controls.Add(exitBtn);

        // Layout handler
        bottomPanel.Layout += (_, __) =>
        {
            int margin = 12;
            int spacing = 10;
            int y = bottomPanel.ClientSize.Height - selectAll.Height - margin;

            // Left group
            selectAll.Location = new Point(margin, y);
            clearAll.Location = new Point(margin + selectAll.Width + spacing, y);

            // Right group
            exitBtn.Location = new Point(bottomPanel.ClientSize.Width - exitBtn.Width - margin, y);
            okBtn.Location = new Point(exitBtn.Left - okBtn.Width - spacing, y);
        };

        Controls.Add(list);
        Controls.Add(header);
        Controls.Add(bottomPanel);

        Theme.ApplyToForm(this);

        // Dynamic button positioning
        bottomPanel.Resize += (_, __) =>
        {
            int margin = 12;
            int spacing = 10;

            // Left side
            selectAll.Left = margin;
            selectAll.Top = bottomPanel.Height - selectAll.Height - margin;

            clearAll.Left = selectAll.Left + selectAll.Width + spacing;
            clearAll.Top = selectAll.Top;

            // Right side
            exitBtn.Left = bottomPanel.Width - exitBtn.Width - margin;
            exitBtn.Top = bottomPanel.Height - exitBtn.Height - margin;

            okBtn.Left = exitBtn.Left - okBtn.Width - spacing;
            okBtn.Top = exitBtn.Top;
        };

        // Populate: unique package keys
        var items = settings.Steps
            .Select(s => new { Key = string.IsNullOrWhiteSpace(s.PackageKey) ? s.Name : s.PackageKey, Display = s.Name })
            .GroupBy(x => x.Key, StringComparer.OrdinalIgnoreCase)
            .Select(g => new PackageItem(g.Key, g.First().Display))
            .OrderBy(i => i.Display, StringComparer.OrdinalIgnoreCase)
            .ToList();

        foreach (var it in items)
            list.Items.Add(it, settings.SelectedPackages.Contains(it.Key));

        // Button behavior
        selectAll.Click += (_, __) =>
        {
            for (int i = 0; i < list.Items.Count; i++)
                list.SetItemChecked(i, true);
        };

        clearAll.Click += (_, __) =>
        {
            for (int i = 0; i < list.Items.Count; i++)
                list.SetItemChecked(i, false);
        };

        okBtn.Click += (_, __) =>
        {
            if (list.CheckedItems.Count == 0)
            {
                MessageBox.Show("Select at least one item to continue.", "Nothing selected",
                    MessageBoxButtons.OK, MessageBoxIcon.Information);
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
