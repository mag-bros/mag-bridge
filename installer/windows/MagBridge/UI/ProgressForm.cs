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

            // Filter steps based on user selections
            var selectedKeys = settings.SelectedPackages ?? new HashSet<string>(StringComparer.OrdinalIgnoreCase);
            List<InstallStep> stepsToRun;

            if (selectedKeys.Count == 0)
            {
                // Nothing selected, run all
                stepsToRun = settings.Steps;
            }
            else
            {
                // Run only selected packages (match by PackageKey, fallback to Name)
                stepsToRun = settings.Steps
                    .Where(s => selectedKeys.Contains(
                        string.IsNullOrWhiteSpace(s.PackageKey) ? s.Name : s.PackageKey))
                    .ToList();
            }

            int total = stepsToRun.Count;
            int current = 0;

            ctl.Log($"Loaded configuration: {settings.Name} v{settings.Version}");
            ctl.Log($"Selected packages: {string.Join(", ", stepsToRun.Select(s => s.Name))}");
            ctl.Log($"Steps to execute: {total}");

            bool hasError = false;

            await Task.Run(async () =>
            {
                foreach (var step in stepsToRun)
                {
                    if (ctl.Token.IsCancellationRequested)
                        break;

                    string scriptPath = Path.Combine(AppContext.BaseDirectory, step.Action);
                    if (!File.Exists(scriptPath))
                    {
                        ctl.Log($"[WARN] Missing script for step '{step.Name}' ({scriptPath})");
                        continue;
                    }

                    ctl.UpdateStatus($"Step {++current}/{total}: {step.Name}");
                    ctl.Log($"[INFO] Executing step '{step.Name}'");
                    ctl.Log($"[INFO] Script: {scriptPath}");

                    var psi = new ProcessStartInfo("powershell.exe",
                        $"-NoProfile -ExecutionPolicy Bypass -File \"{scriptPath}\"")
                    {
                        RedirectStandardOutput = true,
                        RedirectStandardError = true,
                        UseShellExecute = false,
                        CreateNoWindow = true
                    };

                    using (var proc = Process.Start(psi) ?? throw new InvalidOperationException("Failed to start PowerShell process."))
                    {
                        currentProcess = proc;

                        proc.OutputDataReceived += (_, e) =>
                        {
                            if (!string.IsNullOrWhiteSpace(e.Data))
                                ctl.Log($"[OUT] {e.Data}");
                        };

                        proc.ErrorDataReceived += (_, e) =>
                        {
                            if (!string.IsNullOrWhiteSpace(e.Data))
                                ctl.Log($"[ERR] {e.Data}");
                        };

                        proc.BeginOutputReadLine();
                        proc.BeginErrorReadLine();

                        try
                        {
                            await proc.WaitForExitAsync(ctl.Token);
                        }
                        catch (OperationCanceledException)
                        {
                            ctl.Log("[INFO] Cancellation requested; stopping execution.");
                            break;
                        }

                        int exitCode;
                        try { exitCode = proc.ExitCode; }
                        catch { exitCode = -1; }

                        if (exitCode != 0)
                        {
                            ctl.Log($"[ERR] Step '{step.Name}' failed with exit code {exitCode}.");
                            ctl.UpdateStatus($"Step failed: {step.Name}");
                            hasError = true;
                            break;
                        }

                        ctl.Log($"[INFO] Step {current}/{total} completed successfully.");
                        ctl.SetProgress((double)current / total * 100.0);
                    }

                    currentProcess = null;
                }
            });

            // Post-run status logic
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

            var proc = currentProcess;
            if (proc != null)
            {
                try
                {
                    if (!proc.HasExited)
                    {
                        proc.Kill(true);
                        controller.Log("[WARN] Process forcibly terminated.");
                    }
                }
                catch (Exception ex)
                {
                    controller.Log($"[ERR] Failed to terminate process: {ex.Message}");
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
