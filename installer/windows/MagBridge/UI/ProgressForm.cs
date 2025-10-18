using System;
using System.Diagnostics;
using System.Drawing;
using System.IO;
using System.Linq;
using System.Threading;
using System.Threading.Tasks;
using System.Windows.Forms;
using MagBridge.Core;
using MagBridge.UI;

public class ProgressForm : Form
{
    // --- Fields -------------------------------------------------------------
    private readonly ProgressBar progressBar;
    private readonly Label statusLabel;
    private readonly RichTextBox logBox;
    private readonly Button cancelButton;

    private ProgressController controller = null!;
    private LogWriter logger = null!;
    private Process? currentProcess;

    // --- Ctor / UI ----------------------------------------------------------
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

        // Log (RichTextBox to support color)
        logBox = new RichTextBox
        {
            Dock = DockStyle.Fill,
            ReadOnly = true,
            DetectUrls = false,
            ScrollBars = RichTextBoxScrollBars.Vertical,
            WordWrap = false,
            HideSelection = false,
            BorderStyle = BorderStyle.FixedSingle,
            BackColor = Theme.Surface,
            ForeColor = Theme.Text,
            Font = Theme.MonoFont
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

    // --- Lifecycle ----------------------------------------------------------
    protected override async void OnShown(EventArgs e)
    {
        base.OnShown(e);

        controller = new ProgressController(progressBar, statusLabel, logBox);
        logger = controller.Logger;

        cancelButton.Click += (_, __) =>
        {
            if (cancelButton.Text.Equals("Quit", StringComparison.OrdinalIgnoreCase))
            {
                Close();
                return;
            }

            controller.Cancel();
            logger.Write("[WARN] Cancellation requested by user.");

            var proc = currentProcess;
            if (proc != null)
            {
                try
                {
                    cancelButton.Enabled = false;
                    cancelButton.Text = "Cancelling...";
                    logger.Write("[INFO] Attempting to terminate running process...");

                    if (!proc.HasExited)
                    {
                        proc.Kill(entireProcessTree: true);
                        logger.Write("[WARN] Process forcibly terminated.");
                    }
                    else
                    {
                        logger.Write("[INFO] Process already exited before cancellation.");
                    }
                }
                catch (InvalidOperationException)
                {
                    logger.Write("[INFO] Process already closed — no termination needed.");
                }
                catch (Exception ex)
                {
                    logger.Write($"[ERR] Unexpected termination error: {ex.Message}");
                }
            }
        };

        await RunInstallerAsync(controller);
    }

    // --- Core run loop ------------------------------------------------------
    private async Task RunInstallerAsync(ProgressController ctl)
    {
        try
        {
            var settings = Tag as Settings ?? throw new InvalidOperationException("Installer settings not provided.");

            // Filter steps by SelectedPackages (fallback = all)
            var selected = settings.SelectedPackages ?? new System.Collections.Generic.HashSet<string>(StringComparer.OrdinalIgnoreCase);
            var stepsToRun = (selected.Count == 0)
                ? settings.Steps
                : settings.Steps.Where(s =>
                        selected.Contains(string.IsNullOrWhiteSpace(s.PackageKey) ? s.Label : s.PackageKey))
                  .ToList();

            int total = stepsToRun.Count;
            int current = 0;

            logger.Write($"[INFO] Loaded configuration: {settings.Name} v{settings.Version}");
            logger.Write($"[VER] Selected packages: {string.Join(", ", stepsToRun.Select(s => s.Label))}");
            logger.Write($"[INFO] Steps to execute: {total}");

            bool hasError = false;

            await Task.Run(async () =>
            {
                foreach (var step in stepsToRun)
                {
                    if (ctl.Token.IsCancellationRequested) break;

                    string progressLabel = string.IsNullOrWhiteSpace(step.ProgressLabel) ? step.Label : step.ProgressLabel;
                    string scriptPath = Path.Combine(AppContext.BaseDirectory, step.Action);

                    if (!File.Exists(scriptPath))
                    {
                        logger.Write($"[WARN] Missing script for step '{step.Label}' ({scriptPath})");
                        continue;
                    }

                    ctl.UpdateStatus($"Step {current + 1}/{total}: {progressLabel}");
                    logger.Write($"[INFO] Executing step '{progressLabel}'");
                    logger.Write($"[VER] Script: {scriptPath}");

                    int exitCode = await RunScriptAsync(scriptPath, ctl.Token);
                    if (exitCode != 0)
                    {
                        logger.Write($"[ERR] Step '{step.Label}' failed with exit code {exitCode}.");
                        ctl.UpdateStatus($"Step failed: {step.Label}");
                        hasError = true;
                        break;
                    }

                    current++;
                    logger.Write($"[OK] Step {current}/{total} completed successfully.");
                    ctl.SetProgress((double)current / Math.Max(total, 1) * 100.0);
                }
            });

            if (ctl.Token.IsCancellationRequested)
            {
                ctl.UpdateStatus("Installation cancelled by user.");
                logger.Write("[INFO] User cancelled installation.");
            }
            else if (hasError)
            {
                ctl.UpdateStatus("Installation failed.");
                logger.Write("[ERR] One or more steps failed.");
            }
            else
            {
                ctl.UpdateStatus("All steps completed successfully.");
                logger.Write("[OK] Installation completed successfully.");
            }

            ConvertCancelToQuit();
        }
        catch (OperationCanceledException)
        {
            controller.UpdateStatus("Installation cancelled.");
            logger.Write("[INFO] Operation cancelled by user.");

            var proc = currentProcess;
            if (proc != null)
            {
                try
                {
                    if (!proc.HasExited)
                    {
                        proc.Kill(entireProcessTree: true);
                        logger.Write("[WARN] Process forcibly terminated.");
                    }
                }
                catch (Exception ex)
                {
                    logger.Write($"[ERR] Failed to terminate process: {ex.Message}");
                }
                finally
                {
                    try { proc.Dispose(); } catch { }
                    currentProcess = null;
                }
            }

            _ = Task.Run(async () =>
            {
                await Task.Delay(666);
                if (IsHandleCreated) BeginInvoke((Action)Close);
            });
        }
        catch (Exception ex)
        {
            controller.UpdateStatus("Installation failed.");
            logger.Write($"[ERR] {ex.Message}");
            MessageBox.Show(ex.Message, "Error", MessageBoxButtons.OK, MessageBoxIcon.Error);
        }
    }

    // --- PowerShell runner (real-time streaming, _Logging.ps1 preloaded) ---
    private async Task<int> RunScriptAsync(string scriptPath, CancellationToken token)
    {
        string loggingPath = Path.Combine(AppContext.BaseDirectory, "Scripts", "_Logging.ps1");
        string command = $"-NoProfile -ExecutionPolicy Bypass -Command \"& {{ . '{loggingPath}'; . '{scriptPath}' }}\"";

        var psi = new ProcessStartInfo("powershell.exe", command)
        {
            RedirectStandardOutput = true,
            RedirectStandardError = true,
            UseShellExecute = false,
            CreateNoWindow = true
        };

        using var proc = new Process { StartInfo = psi, EnableRaisingEvents = true };
        currentProcess = proc;

        var tcs = new TaskCompletionSource<int>(TaskCreationOptions.RunContinuationsAsynchronously);

        proc.OutputDataReceived += (_, e) =>
        {
            if (!string.IsNullOrWhiteSpace(e.Data))
                logger.Write(e.Data.Trim());
        };
        proc.ErrorDataReceived += (_, e) =>
        {
            if (!string.IsNullOrWhiteSpace(e.Data))
                logger.Write("[ERR] " + e.Data.Trim());
        };
        proc.Exited += (_, __) =>
        {
            try { tcs.TrySetResult(proc.ExitCode); }
            catch { tcs.TrySetResult(-1); }
        };

        proc.Start();
        proc.BeginOutputReadLine();
        proc.BeginErrorReadLine();

        using (token.Register(() =>
        {
            try
            {
                if (!proc.HasExited) proc.Kill(entireProcessTree: true);
            }
            catch { /* best effort */ }
        }))
        {
            int code = await tcs.Task.ConfigureAwait(false);
            currentProcess = null;
            return code;
        }
    }

    // --- Helpers ------------------------------------------------------------
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
