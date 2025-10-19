using UITimer = System.Windows.Forms.Timer;
using System.ComponentModel;
using MagBridge.Core;
using MagBridge.UI;

public class ProgressForm : Form
{
    private readonly UITimer _timer = new() { Interval = 10 };
    private long _lastLogSize;
    private readonly ProgressBar progressBar;
    private readonly Label statusLabel;
    private readonly ThemedLogBox logBox;
    private readonly Button cancelButton;
    private readonly ThemedDropdown logLevelDropdown;
    private readonly Settings settings;

    private ProgressController controller;

    // ----------------------------------------------------------
    // Constructor
    // ----------------------------------------------------------
    public ProgressForm(Settings settings)
    {
        this.settings = settings;
        // Window basics
        Text = $"{settings.RunType} — v{settings.Version}";
        TopMost = true;
        MaximizeBox = true;
        MinimizeBox = true;
        SizeGripStyle = SizeGripStyle.Show;
        FormBorderStyle = FormBorderStyle.Sizable;
        Size = new Size(1200, 900);
        MinimumSize = new Size(700, 200);
        MaximumSize = new Size(2000, 1200);
        StartPosition = FormStartPosition.CenterScreen;

        // Header
        statusLabel = new Label
        {
            Text = "Initializing...",
            Dock = DockStyle.Top,
            Height = 30,
            TextAlign = ContentAlignment.MiddleCenter
        };

        // Progress
        progressBar = new ThemedProgressBar
        {
            Dock = DockStyle.Bottom,
            Height = 12,
            Style = ProgressBarStyle.Continuous,
            Maximum = 100
        };

        // Log box
        logBox = new ThemedLogBox
        {
            Dock = DockStyle.Fill,
            ReadOnly = true,
            Multiline = true,
            ScrollBars = RichTextBoxScrollBars.Vertical,
            WordWrap = false
        };

        // Cancel/Quit button
        cancelButton = new ThemedButton
        {
            Text = "Cancel",
        };
        cancelButton.Click += CancelButton_Click;

        // --- Log level dropdown ---
        var logLevelLabel = new ThemedLabel
        {
            Text = "Log level:"
        };
        logLevelDropdown = new ThemedDropdown
        {
            Width = 180
        };
        // This code will trigger when dropdown changes
        logLevelDropdown.BindEnum(LogWriter.Global.LogLevel, level =>
        {
            LogWriter.Global.SetLogLevel(level);
            LogWriter.Global.Write($"[INFO] Log level changed to {level}");
        });

        // --- Bottom control bar ---
        var bottomBar = new ThemedBottomBar(new float[] { 7, 12, 55, 20 });
        cancelButton.Dock = DockStyle.Right;
        bottomBar.Controls.Add(logLevelLabel);
        bottomBar.Controls.Add(logLevelDropdown);
        bottomBar.Controls.Add(cancelButton);

        // --- Top Level Form ---
        Controls.Add(logBox);
        Controls.Add(statusLabel);
        Controls.Add(progressBar);
        Controls.Add(bottomBar);

        Theme.ApplyToForm(this);
        _lastLogSize = new FileInfo(LogWriter.Global.LogFile).Length;
        _timer.Tick += (_, __) => CheckLogUpdate();
        _timer.Start();
        controller = new ProgressController(progressBar, statusLabel);
    }

    private void CheckLogUpdate()
    {
        var file = LogWriter.Global.LogFile;
        if (!File.Exists(file)) return;

        long currentSize = new FileInfo(file).Length;
        if (currentSize != _lastLogSize)
        {
            _lastLogSize = currentSize;
            RefreshLogBox();
        }
    }

    private void RefreshLogBox()
    {
        logBox.Clear();
        var lines = LogWriter.Global.FilterLogLevel();
        foreach (var line in lines)
        {
            Color color = LogWriter.Global.DetermineColor(line);
            logBox.SelectionStart = logBox.TextLength;
            logBox.SelectionColor = color;
            logBox.AppendText(line + Environment.NewLine);
        }
        logBox.SelectionColor = logBox.ForeColor;
        logBox.ScrollToCaret();
    }

    // ----------------------------------------------------------
    // Cancel button logic
    // ----------------------------------------------------------
    private void CancelButton_Click(object? sender, EventArgs e)
    {
        if (cancelButton.Text.Equals("Quit", StringComparison.OrdinalIgnoreCase))
        {
            Close();
            return;
        }

        controller.Cancel();
    }

    // ----------------------------------------------------------
    // OnShown — main startup routine
    // ----------------------------------------------------------
    protected override async void OnShown(EventArgs e)
    {
        base.OnShown(e);

        // Ensure handle exists before attachment
        if (!logBox.IsHandleCreated)
            await Task.Run(() => logBox.CreateControl());

        LogWriter.Global.Write("[VER] LogWriter attached post-handle creation.");

        await RunInAsyncLoop(settings);
    }

    // ----------------------------------------------------------
    // Main Progress Form loop
    // ----------------------------------------------------------
    private async Task RunInAsyncLoop(Settings settings)
    {
        try
        {
            var ctl = controller ?? throw new InvalidOperationException("ProgressController not initialized.");

            var selectedKeys = settings.SelectedPackages ?? new HashSet<string>(StringComparer.OrdinalIgnoreCase);
            var tasks = (selectedKeys.Count == 0)
                ? settings.Tasks
                : settings.Tasks
                    .Where(s => selectedKeys.Contains(string.IsNullOrWhiteSpace(s.PackageKey) ? s.Label : s.PackageKey))
                    .ToList();

            int total = tasks.Count;
            int current = 0;

            LogWriter.Global.Write($"[VER] Loaded configuration: {settings.RunType} - v{settings.Version}");
            LogWriter.Global.Write($"[INFO] User Selected packages: {string.Join(", ", tasks.Select(s => s.PackageKey))}");
            LogWriter.Global.Write($"[VER] Tasks to execute: {total}");
            ctl.UpdateStatus("Starting installation...");

            bool hasError = false;

            await Task.Run(async () =>
            {
                var ps_executor = new PowerShellExecutor(LogWriter.Global);

                foreach (var task in tasks)
                {
                    if (ctl.Token.IsCancellationRequested)
                        break;

                    var progressLabel = task.ProgressLabel ?? task.Label;

                    ctl.UpdateStatus($"Step {++current}/{total}: {progressLabel}");
                    LogWriter.Global.Write($"[VER] Executing task '{progressLabel}'");

                    LogWriter.Global.Write($"[INFO] === Running {Path.GetFileName(task.Script)} ===");
                    int exitCode = await ps_executor.RunScriptAsync(task, ctl.Token);

                    if (exitCode != 0)
                    {
                        LogWriter.Global.Write($"[ERR] Step '{task.PackageKey}' failed with exit code {exitCode}.");
                        ctl.UpdateStatus($"Step failed: {task.PackageKey}");
                        hasError = true;
                        break;
                    }

                    LogWriter.Global.Write($"[VER] Step completed successfully: {task.PackageKey}");
                    ctl.SetProgress((double)current / total * 100.0);
                }
            });

            // --- Post-run summary ---
            if (ctl.Token.IsCancellationRequested)
            {
                ctl.UpdateStatus("Installation cancelled by user.");
                LogWriter.Global.Write("[WARN] User cancelled installation.");
            }
            else if (hasError)
            {
                ctl.UpdateStatus("Installation failed.");
                LogWriter.Global.Write("[ERR] One or more tasks failed.");
            }
            else
            {
                ctl.UpdateStatus("All tasks completed successfully.");
                LogWriter.Global.Write("[SUCCESS] All tasks completed successfully. ");
                LogWriter.Global.Write(@"[INFO] What's next?

 - You may need to restart your terminal or computer 
     for environment changes (e.g. PATH) to take effect.
 - Verify the tool by running it manually in a new shell.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        All tasks completed successfully
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
");
                LogWriter.Global.Write("[OK] You better now close this window and get to work! c:");
            }

            ChangeButtonText(cancelButton, "Quit", () => Close());
        }
        catch (Exception ex)
        {
            controller?.UpdateStatus("Installation failed.");
            LogWriter.Global.Write($"[ERR] {ex.Message}");
            MessageBox.Show(ex.Message, "Error", MessageBoxButtons.OK, MessageBoxIcon.Error);
        }
    }

    /// <param name="button">The button control to update.</param>
    /// <param name="newText">The new text to display on the button.</param>
    /// <param name="onClick">Action to execute on button click; null keeps current behavior.</param>
    /// <param name="clearExistingHandlers">If true, removes existing Click handlers before assigning the new one.</param>
    private void ChangeButtonText(Button button, string newText, Action? onClick = null, bool clearExistingHandlers = false)
    {
        if (button.InvokeRequired)
        {
            button.Invoke((Action)(() => ChangeButtonText(button, newText, onClick, clearExistingHandlers)));
            return;
        }

        button.Enabled = true;
        button.Text = newText;

        if (clearExistingHandlers)
        {
            // Use reflection to clear all existing Click event handlers
            var eventField = typeof(Control).GetField("EventClick", System.Reflection.BindingFlags.Static | System.Reflection.BindingFlags.NonPublic);
            var eventKey = eventField?.GetValue(button);
            var eventsProp = typeof(Component).GetProperty("Events", System.Reflection.BindingFlags.Instance | System.Reflection.BindingFlags.NonPublic);
            var eventList = eventsProp?.GetValue(button, null) as EventHandlerList;
            eventList?.RemoveHandler(eventKey!, eventList[eventKey!]);
        }

        if (onClick != null)
            button.Click += (_, __) => onClick();
    }

    protected override void OnFormClosed(FormClosedEventArgs e)
    {
        _timer.Stop();
        _timer.Dispose();
        base.OnFormClosed(e);
    }


    /// <summary>
    /// Controls progress bar and status label, and delegates all logging to LogWriter.
    /// </summary>
    protected class ProgressController
    {
        private readonly ProgressBar _progressBar;
        private readonly Label _statusLabel;
        private readonly CancellationTokenSource _cts = new();

        public CancellationToken Token => _cts.Token;

        public ProgressController(ProgressBar progressBar, Label statusLabel)
        {
            _progressBar = progressBar ?? throw new ArgumentNullException(nameof(progressBar));
            _statusLabel = statusLabel ?? throw new ArgumentNullException(nameof(statusLabel));

            LogWriter.Global.Write("[VER] ProgressController initialized.");
        }

        public void UpdateStatus(string status)
        {
            LogWriter.Global.Write($"[VER] {status}");
            if (_statusLabel.IsHandleCreated)
                _statusLabel.Invoke(() => _statusLabel.Text = status);
        }

        public void SetProgress(double percent)
        {
            LogWriter.Global.Write($"[VER] Updating progress: {(int)Math.Round(percent)}%");
            if (_progressBar.IsHandleCreated)
            {
                _progressBar.Invoke(() =>
                {
                    _progressBar.Style = ProgressBarStyle.Continuous;
                    _progressBar.Value = Math.Clamp((int)percent, 0, 100);
                });
            }
        }

        public void Cancel() => _cts.Cancel();
    }
}
