using System;
using System.Diagnostics;
using System.Drawing;
using System.IO;
using System.Threading.Tasks;
using System.Windows.Forms;
using MagBridge.Core;
using MagBridge.UI;

public class ProgressForm : Form
{
    private readonly ProgressBar progressBar;
    private readonly Label statusLabel;
    private readonly TextBox logBox;
    private readonly Button cancelButton;

    private ProgressController controller = null!;
    private Process? currentProcess;

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

        // Log
        logBox = new ThemedTextBox
        {
            Dock = DockStyle.Fill,
            Multiline = true,
            ReadOnly = true,
            ScrollBars = ScrollBars.Vertical,
            WordWrap = false
        };

        // Cancel/Quit
        cancelButton = new ThemedButton
        {
            Text = "Cancel",
            Dock = DockStyle.Bottom
        };

        Controls.Add(logBox);
        Controls.Add(progressBar);
        Controls.Add(statusLabel);
        Controls.Add(cancelButton);

        Theme.ApplyToForm(this);
    }

    protected override async void OnShown(EventArgs e)
    {
        base.OnShown(e);

        controller = new ProgressController(progressBar, statusLabel, logBox);

        cancelButton.Click += (_, __) =>
        {
            if (cancelButton.Text.Equals("Quit", StringComparison.OrdinalIgnoreCase))
            {
                Close();
                return;
            }

            controller.Cancel();

            // Safely attempt to terminate running process (race-condition proof)
            var proc = currentProcess;
            if (proc != null)
            {
                try
                {
                    cancelButton.Enabled = false;
                    cancelButton.Text = "Cancelling...";
                    controller.Log("Cancelling current step...");

                    if (!proc.HasExited)
                    {
                        proc.Kill(true);
                        controller.Log("Process terminated by user.");
                    }
                    else
                    {
                        controller.Log("Process already exited before cancellation.");
                    }
                }
                catch (InvalidOperationException)
                {
                    controller.Log("Process was already closed — no termination needed.");
                }
                catch (Exception ex)
                {
                    controller.Log($"[ERR] Unexpected termination error: {ex.Message}");
                }
            }
        };

        await RunInstallerAsync();
    }

    private async Task RunInstallerAsync()
    {
        try
        {
            var ctl = controller ?? throw new InvalidOperationException("ProgressController not initialized.");
            var settings = Tag as Settings ?? throw new InvalidOperationException("Installer settings not provided.");

            // --- Filter steps ------------------------------------------------
            var selectedKeys = settings.SelectedPackages ?? new HashSet<string>(StringComparer.OrdinalIgnoreCase);
            var stepsToRun = (selectedKeys.Count == 0)
                ? settings.Steps
                : settings.Steps
                    .Where(s => selectedKeys.Contains(
                        string.IsNullOrWhiteSpace(s.PackageKey) ? s.Label : s.PackageKey))
                    .ToList();

            int total = stepsToRun.Count;
            int current = 0;

            ctl.Log($"Loaded configuration: {settings.RunType} v{settings.Version}");
            ctl.Log($"Selected packages: {string.Join(", ", stepsToRun.Select(s => s.Label))}");
            ctl.Log($"Steps to execute: {total}");
            ctl.UpdateStatus("Starting installation...");

            bool hasError = false;

            // --- Core execution loop ----------------------------------------
            await Task.Run(async () =>
            {
                foreach (var step in stepsToRun)
                {
                    if (ctl.Token.IsCancellationRequested)
                        break;

                    var progressLabel = step.ProgressLabel ?? step.Label;

                    ctl.UpdateStatus($"Step {++current}/{total}: {progressLabel}");
                    ctl.Log($"[INFO] Executing step '{progressLabel}'");

                    // Resolve script path
                    string scriptPath = Path.Combine(AppContext.BaseDirectory, step.Action);
                    if (!File.Exists(scriptPath))
                    {
                        ctl.Log($"[WARN] Missing script for '{step.PackageKey}' — skipped ({scriptPath})");
                        continue;
                    }

                    ctl.Log($"[INFO] === Running {Path.GetFileName(scriptPath)} ===");

                    string loggingPath = Path.Combine(AppContext.BaseDirectory, "Scripts", "_Logging.ps1");
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
                            ctl.Log($"[INFO] [{step.PackageKey}] {e.Data}");
                    };

                    proc.ErrorDataReceived += (_, e) =>
                    {
                        if (!string.IsNullOrWhiteSpace(e.Data))
                            ctl.Log($"[ERR] [{step.PackageKey}] {e.Data}");
                    };

                    proc.BeginOutputReadLine();
                    proc.BeginErrorReadLine();

                    try
                    {
                        await proc.WaitForExitAsync(ctl.Token);
                    }
                    catch (OperationCanceledException)
                    {
                        ctl.Log($"[INFO] Cancellation requested during '{step.PackageKey}'");
                        break;
                    }

                    int exitCode = proc.HasExited ? proc.ExitCode : -1;

                    if (exitCode != 0)
                    {
                        ctl.Log($"[ERR] Step '{step.PackageKey}' failed with exit code {exitCode}.");
                        ctl.UpdateStatus($"Step failed: {step.PackageKey}");
                        hasError = true;
                        break;
                    }

                    ctl.Log($"[OK] Step completed successfully: {step.PackageKey}");
                    ctl.SetProgress((double)current / total * 100.0);
                    currentProcess = null;
                }
            });

            // --- Post-run summary -------------------------------------------
            if (ctl.Token.IsCancellationRequested)
            {
                ctl.UpdateStatus("Installation cancelled by user.");
                ctl.Log("[INFO] User cancelled installation.");
            }
            else if (hasError)
            {
                ctl.UpdateStatus("Installation failed.");
                ctl.Log("[ERR] One or more steps failed.");
            }
            else
            {
                ctl.UpdateStatus("All steps completed successfully.");
                ctl.Log("[INFO] Installation completed successfully.");
            }

            ConvertCancelToQuit();
        }
        catch (OperationCanceledException)
        {
            controller.UpdateStatus("Installation cancelled.");
            controller.Log("[INFO] Operation cancelled by user.");

            if (currentProcess != null)
            {
                try
                {
                    if (!currentProcess.HasExited)
                    {
                        currentProcess.Kill(true);
                        controller.Log("[WARN] Process forcibly terminated.");
                    }
                }
                catch (Exception ex)
                {
                    controller.Log($"[ERR] Failed to terminate process: {ex.Message}");
                }
                finally
                {
                    try { currentProcess.Dispose(); } catch { }
                    currentProcess = null;
                }
            }

            _ = Task.Run(async () =>
            {
                await Task.Delay(666);
                if (IsHandleCreated)
                    BeginInvoke((Action)Close);
            });
        }
        catch (Exception ex)
        {
            controller.UpdateStatus("Installation failed.");
            controller.Log($"[ERR] {ex.Message}");
            MessageBox.Show(ex.Message, "Error", MessageBoxButtons.OK, MessageBoxIcon.Error);
        }
    }

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
