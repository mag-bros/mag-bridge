using System.Diagnostics;
using MagBridge.Core;
using MagBridge.UI;

public class ProgressForm : Form
{
    private readonly ProgressBar progressBar;
    private readonly Label statusLabel;
    private readonly ThemedLogBox logBox;
    private readonly Button cancelButton;

    private Process? currentProcess;
    private ProgressController controller;

    // ----------------------------------------------------------
    // Constructor
    // ----------------------------------------------------------
    public ProgressForm()
    {
        // Window basics
        TopMost = true;
        MaximizeBox = true;
        MinimizeBox = true;
        SizeGripStyle = SizeGripStyle.Show;
        FormBorderStyle = FormBorderStyle.Sizable;
        MinimumSize = new Size(1000, 500);
        MaximumSize = new Size(1400, 800);
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
            Dock = DockStyle.Bottom
        };
        cancelButton.Click += CancelButton_Click;

        Controls.Add(logBox);
        Controls.Add(statusLabel);
        Controls.Add(progressBar);
        Controls.Add(cancelButton);

        Theme.ApplyToForm(this);
        controller = new ProgressController(progressBar, statusLabel, logBox, LogWriter.Global);
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

        LogWriter.Global.Attach(logBox);
        LogWriter.Global.Write("[INFO] LogWriter attached post-handle creation.");

        await RunInstallerAsync();
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

        var proc = currentProcess;
        if (proc == null)
            return;

        try
        {
            cancelButton.Enabled = false;
            cancelButton.Text = "Cancelling...";
            LogWriter.Global.Write("[INFO] Cancelling current step...");

            if (!proc.HasExited)
            {
                proc.Kill(true);
                LogWriter.Global.Write("[WARN] Process terminated by user.");
            }
            else
            {
                LogWriter.Global.Write("[INFO] Process already exited before cancellation.");
            }
        }
        catch (InvalidOperationException)
        {
            LogWriter.Global.Write("[INFO] Process was already closed — no termination needed.");
        }
        catch (Exception ex)
        {
            LogWriter.Global.Write($"[ERR] Unexpected termination error: {ex.Message}");
        }
    }

    // ----------------------------------------------------------
    // Main installer loop
    // ----------------------------------------------------------
    private async Task RunInstallerAsync()
    {
        try
        {
            var ctl = controller ?? throw new InvalidOperationException("ProgressController not initialized.");
            var settings = Tag as Settings ?? throw new InvalidOperationException("Installer settings not provided.");

            var selectedKeys = settings.SelectedPackages ?? new HashSet<string>(StringComparer.OrdinalIgnoreCase);
            var stepsToRun = (selectedKeys.Count == 0)
                ? settings.Steps
                : settings.Steps
                    .Where(s => selectedKeys.Contains(string.IsNullOrWhiteSpace(s.PackageKey) ? s.Label : s.PackageKey))
                    .ToList();

            int total = stepsToRun.Count;
            int current = 0;

            LogWriter.Global.Write($"[VER] Loaded configuration: {settings.RunType} v{settings.Version}");
            LogWriter.Global.Write($"[INFO] Selected packages: {string.Join(", ", stepsToRun.Select(s => s.Label))}");
            LogWriter.Global.Write($"[INFO] Steps to execute: {total}");
            ctl.UpdateStatus("Starting installation...");

            bool hasError = false;

            await Task.Run(async () =>
            {
                foreach (var step in stepsToRun)
                {
                    if (ctl.Token.IsCancellationRequested)
                        break;

                    var progressLabel = step.ProgressLabel ?? step.Label;

                    ctl.UpdateStatus($"Step {++current}/{total}: {progressLabel}");
                    LogWriter.Global.Write($"[INFO] Executing step '{progressLabel}'");

                    string scriptPath = Path.Combine(AppContext.BaseDirectory, step.Action);
                    if (!File.Exists(scriptPath))
                    {
                        LogWriter.Global.Write($"[WARN] Missing script for '{step.PackageKey}' — skipped ({scriptPath})");
                        continue;
                    }

                    LogWriter.Global.Write($"[OUT] === Running {Path.GetFileName(scriptPath)} ===");

                    string loggingPath = Path.Combine(AppContext.BaseDirectory, "Scripts", "_HostLogging.ps1");
                    string command = $"-NoProfile -ExecutionPolicy Bypass -Command \"& {{ . '{loggingPath}'; . '{scriptPath}' }}\"";

                    var psi = new ProcessStartInfo("powershell.exe", command)
                    {
                        RedirectStandardOutput = true,
                        RedirectStandardError = true,
                        UseShellExecute = false,
                        CreateNoWindow = true
                    };

                    using var proc = Process.Start(psi)
                        ?? throw new InvalidOperationException($"Failed to start process for '{step.PackageKey}'");

                    currentProcess = proc;

                    proc.OutputDataReceived += (_, e) =>
                    {
                        if (!string.IsNullOrWhiteSpace(e.Data))
                            LogWriter.Global.Write($"[OUT] [{step.PackageKey}] {e.Data}");
                    };

                    proc.ErrorDataReceived += (_, e) =>
                    {
                        if (!string.IsNullOrWhiteSpace(e.Data))
                            LogWriter.Global.Write($"[ERR] [{step.PackageKey}] {e.Data}");
                    };

                    proc.BeginOutputReadLine();
                    proc.BeginErrorReadLine();

                    try
                    {
                        await proc.WaitForExitAsync(ctl.Token);
                    }
                    catch (OperationCanceledException)
                    {
                        LogWriter.Global.Write($"[INFO] Cancellation requested during '{step.PackageKey}'");
                        break;
                    }

                    int exitCode = proc.HasExited ? proc.ExitCode : -1;

                    if (exitCode != 0)
                    {
                        LogWriter.Global.Write($"[ERR] Step '{step.PackageKey}' failed with exit code {exitCode}.");
                        ctl.UpdateStatus($"Step failed: {step.PackageKey}");
                        hasError = true;
                        break;
                    }

                    LogWriter.Global.Write($"[OK] Step completed successfully: {step.PackageKey}");
                    ctl.SetProgress((double)current / total * 100.0);
                    currentProcess = null;
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
                LogWriter.Global.Write("[ERR] One or more steps failed.");
            }
            else
            {
                ctl.UpdateStatus("All steps completed successfully.");
                LogWriter.Global.Write("[OK] Installation completed successfully.");
            }

            ConvertCancelToQuit();
        }
        catch (Exception ex)
        {
            controller?.UpdateStatus("Installation failed.");
            LogWriter.Global.Write($"[ERR] {ex.Message}");
            MessageBox.Show(ex.Message, "Error", MessageBoxButtons.OK, MessageBoxIcon.Error);
        }
    }

    // ----------------------------------------------------------
    // Convert Cancel button to Quit
    // ----------------------------------------------------------
    private void ConvertCancelToQuit()
    {
        if (cancelButton.InvokeRequired)
        {
            cancelButton.Invoke((Action)ConvertCancelToQuit);
            return;
        }

        cancelButton.Enabled = true;
        cancelButton.Text = "Quit";
        cancelButton.Click += (_, __) => Close();
    }
}
