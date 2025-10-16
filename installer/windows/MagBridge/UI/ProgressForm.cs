using System;
using System.Diagnostics;
using System.IO;
using System.Linq;
using System.Threading.Tasks;
using System.Windows.Forms;
using MagBridge.Core;

public class ProgressForm : Form
{
    private readonly ProgressBar progressBar;
    private readonly Label statusLabel;
    private readonly TextBox logBox;
    private readonly Button cancelButton;
    private ProgressController controller;
    private Process? currentProcess;

    public ProgressForm()
    {
        TopMost = true;
        BringToFront();
        Focus();

        MaximizeBox = true;
        MinimizeBox = true;
        SizeGripStyle = SizeGripStyle.Show;
        FormBorderStyle = FormBorderStyle.Sizable;
        MinimumSize = new Size(1000, 350);
        MaximumSize = new Size(1400, 800);
        StartPosition = FormStartPosition.CenterScreen;

        statusLabel = new Label
        {
            Text = "Initializing...",
            Dock = DockStyle.Top,
            Height = 30,
            TextAlign = System.Drawing.ContentAlignment.MiddleCenter
        };

        progressBar = new ProgressBar
        {
            Dock = DockStyle.Top,
            Height = 25,
            Style = ProgressBarStyle.Continuous,
            Value = 0
        };

        logBox = new TextBox
        {
            Dock = DockStyle.Fill,
            Multiline = true,
            ReadOnly = true,
            ScrollBars = ScrollBars.Vertical
        };

        cancelButton = new Button
        {
            Text = "Cancel",
            Dock = DockStyle.Bottom,
            Height = 35
        };

        Controls.Add(logBox);
        Controls.Add(progressBar);
        Controls.Add(statusLabel);
        Controls.Add(cancelButton);
    }

    protected override async void OnShown(EventArgs e)
    {
        base.OnShown(e);
        controller = new ProgressController(progressBar, statusLabel, logBox);

        cancelButton.Click += (_, __) =>
        {
            if (cancelButton.Text == "Quit")
            {
                Close();
                return;
            }

            controller.Cancel();
            if (currentProcess != null && !currentProcess.HasExited)
            {
                try
                {
                    cancelButton.Enabled = false;
                    cancelButton.Text = "Cancelling...";
                    controller.Log("⚠️ Cancelling current step...");
                    currentProcess.Kill();
                    controller.Log("🛑 Process terminated by user.");
                }
                catch (Exception ex)
                {
                    controller.Log($"[ERR] Failed to terminate process: {ex.Message}");
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

                    using (currentProcess = Process.Start(psi)
                           ?? throw new InvalidOperationException("Failed to start PowerShell process."))
                    {
                        currentProcess.OutputDataReceived += (_, e) =>
                        {
                            if (!string.IsNullOrWhiteSpace(e.Data))
                                ctl.Log($"[OUT] {e.Data}");
                        };

                        currentProcess.ErrorDataReceived += (_, e) =>
                        {
                            if (!string.IsNullOrWhiteSpace(e.Data))
                                ctl.Log($"[ERR] {e.Data}");
                        };

                        currentProcess.BeginOutputReadLine();
                        currentProcess.BeginErrorReadLine();

                        await currentProcess.WaitForExitAsync(ctl.Token);

                        if (ctl.Token.IsCancellationRequested)
                        {
                            ctl.Log("Cancellation requested during step execution.");
                            break;
                        }

                        if (currentProcess.ExitCode != 0)
                        {
                            ctl.Log($"Error: Step '{step.Name}' failed (Exit code {currentProcess.ExitCode}).");
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

            Invoke(() =>
            {
                cancelButton.Text = "Quit";
                cancelButton.Enabled = true;
            });
        }
        catch (OperationCanceledException)
        {
            controller.UpdateStatus("Installation cancelled.");
            controller.Log("Operation cancelled by user.");

            if (currentProcess is { HasExited: false })
            {
                try
                {
                    currentProcess.Kill(true);
                    controller.Log("Process forcibly terminated.");
                }
                catch (Exception ex)
                {
                    controller.Log($"Failed to terminate process: {ex.Message}");
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

        // Update appearance and behavior
        cancelButton.Enabled = true;
        cancelButton.Text = "Quit";
        cancelButton.Click += (_, __) => Close();
    }

}
