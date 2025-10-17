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
        MinimumSize = new Size(1000, 350);
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
        logBox = new TextBox
        {
            Dock = DockStyle.Fill,
            Multiline = true,
            ReadOnly = true,
            ScrollBars = ScrollBars.Vertical
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

            int total = settings.Steps.Count;
            int current = 0;

            ctl.Log($"Loaded configuration: {settings.Name} v{settings.Version}");
            ctl.Log($"Steps to execute: {total}");

            await Task.Run(async () =>
            {
                foreach (var step in settings.Steps)
                {
                    if (ctl.Token.IsCancellationRequested)
                        break;

                    string scriptPath = Path.Combine(AppContext.BaseDirectory, step.Action);
                    if (!File.Exists(scriptPath))
                    {
                        ctl.Log($"Warning: Missing script for step '{step.Name}' ({scriptPath})");
                        continue;
                    }

                    ctl.UpdateStatus($"Step {++current}/{total}: {step.Name}");
                    ctl.Log($"Executing step: {step.Name}");
                    ctl.Log($"  Script: {scriptPath}");

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
                        // publish to field for cancel handler
                        currentProcess = proc;

                        proc.OutputDataReceived += (_, ev) =>
                        {
                            if (!string.IsNullOrWhiteSpace(ev.Data))
                                ctl.Log($"[OUT] {ev.Data}");
                        };

                        proc.ErrorDataReceived += (_, ev) =>
                        {
                            if (!string.IsNullOrWhiteSpace(ev.Data))
                                ctl.Log($"[ERR] {ev.Data}");
                        };

                        proc.BeginOutputReadLine();
                        proc.BeginErrorReadLine();

                        try
                        {
                            // Wait in a race-safe manner; if cancellation happens, token throws
                            await proc.WaitForExitAsync(ctl.Token);
                        }
                        catch (OperationCanceledException)
                        {
                            // swallow here; outer flow will handle cancelled state
                        }
                        catch (InvalidOperationException)
                        {
                            // Process may have already exited/disposed; ignore safely
                            ctl.Log("Process already terminated — skipping wait.");
                        }
                        finally
                        {
                            // Best-effort cleanup
                            try { proc.CancelOutputRead(); } catch { /* ignore */ }
                            try { proc.CancelErrorRead(); } catch { /* ignore */ }
                            try { proc.Dispose(); } catch { /* ignore */ }
                            currentProcess = null;
                        }

                        if (ctl.Token.IsCancellationRequested)
                        {
                            ctl.Log("Cancellation requested during step execution.");
                            break;
                        }

                        // If we reached here normally, verify exit code
                        // Use a guarded read to avoid InvalidOperationException
                        int exitCode = 0;
                        try { exitCode = proc.ExitCode; } catch { /* process gone; treat as success */ }

                        if (exitCode != 0)
                        {
                            ctl.Log($"Error: Step '{step.Name}' failed (Exit code {exitCode}).");
                            break;
                        }

                        ctl.Log($"Step {current}/{total} completed successfully.");
                        double progress = (double)current / total * 100.0;
                        ctl.SetProgress(progress);
                    }
                }
            });

            if (ctl.Token.IsCancellationRequested)
            {
                ctl.UpdateStatus("Installation cancelled by user.");
                ctl.Log("User cancelled installation.");
            }
            else
            {
                ctl.UpdateStatus("All steps completed successfully.");
                ctl.Log("Installation completed successfully.");
            }

            ConvertCancelToQuit();
        }
        catch (OperationCanceledException)
        {
            controller.UpdateStatus("Installation cancelled.");
            controller.Log("Operation cancelled by user.");

            var proc = currentProcess;
            if (proc != null)
            {
                try
                {
                    if (!proc.HasExited)
                    {
                        proc.Kill(true);
                        controller.Log("Process forcibly terminated.");
                    }
                }
                catch (Exception ex)
                {
                    controller.Log($"Failed to terminate process: {ex.Message}");
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
            controller.Log($"Error: {ex}");
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
