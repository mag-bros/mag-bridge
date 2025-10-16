using System;
using System.Diagnostics;
using System.IO;
using System.Linq;
using System.Threading.Tasks;
using System.Windows.Forms;
using DevKit.Core;

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
            string baseDir = AppContext.BaseDirectory;
            var manifest = InstallerManifest.Load(baseDir);
            int total = manifest.Steps.Count;
            int current = 0;

            await Task.Run(async () =>
            {
                foreach (var step in manifest.Steps)
                {
                    if (ctl.Token.IsCancellationRequested)
                        break;

                    string scriptPath = Path.Combine(baseDir, step.Action);
                    if (!File.Exists(scriptPath))
                    {
                        ctl.Log($"⚠️ Missing script for step: {step.Name} ({scriptPath})");
                        continue;
                    }

                    ctl.UpdateStatus($"Step {++current}/{total}: {step.Name}");
                    ctl.Log($"🧩 Executing {step.Name}\n  {scriptPath}");

                    var psi = new ProcessStartInfo("powershell.exe",
                        $"-NoProfile -ExecutionPolicy Bypass -File \"{scriptPath}\"")
                    {
                        RedirectStandardOutput = true,
                        RedirectStandardError = true,
                        UseShellExecute = false,
                        CreateNoWindow = true
                    };

                    currentProcess = Process.Start(psi);
                    if (currentProcess == null)
                        throw new InvalidOperationException("Failed to start PowerShell process.");

                    currentProcess.OutputDataReceived += (s, e) =>
                    {
                        if (!string.IsNullOrEmpty(e.Data))
                            ctl.Log($"[OUT] {e.Data}");
                    };
                    currentProcess.ErrorDataReceived += (s, e) =>
                    {
                        if (!string.IsNullOrEmpty(e.Data))
                            ctl.Log($"[ERR] {e.Data}");
                    };

                    currentProcess.BeginOutputReadLine();
                    currentProcess.BeginErrorReadLine();

                    await currentProcess.WaitForExitAsync(ctl.Token);

                    currentProcess.CancelOutputRead();
                    currentProcess.CancelErrorRead();
                    currentProcess.Dispose();
                    currentProcess = null;

                    if (ctl.Token.IsCancellationRequested)
                        break;

                    double progress = (double)current / total * 100.0;
                    ctl.SetProgress(progress);
                    ctl.Log($"✅ Step {current}/{total} complete: {step.Name}");
                }
            });

            if (ctl.Token.IsCancellationRequested)
            {
                ctl.UpdateStatus("❌ Installation cancelled by user.");
                ctl.Log("User cancelled installation.");
            }
            else
            {
                ctl.UpdateStatus("✅ All steps completed successfully!");
                ctl.Log("Installation completed successfully.");
            }

            // After installation completes → change Cancel → Quit
            Invoke(() =>
            {
                cancelButton.Text = "Quit";
                cancelButton.Enabled = true;
            });
        }
        catch (OperationCanceledException)
        {
            controller.UpdateStatus("❌ Installation cancelled.");
            controller.Log("Operation cancelled by user.");

            if (currentProcess != null && !currentProcess.HasExited)
                currentProcess.Kill(true);

            _ = Task.Run(async () =>
            {
                await Task.Delay(666);
                if (IsHandleCreated)
                    BeginInvoke((Action)Close);
            });
        }
        catch (Exception ex)
        {
            controller.UpdateStatus("❌ Installation failed.");
            controller.Log($"[ERR] {ex}");
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
