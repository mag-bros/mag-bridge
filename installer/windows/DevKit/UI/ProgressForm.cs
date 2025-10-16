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

    public ProgressForm()
    {
        Text = "DevKit Installer";
        Width = 600;
        Height = 420;
        StartPosition = FormStartPosition.CenterScreen;
        FormBorderStyle = FormBorderStyle.FixedDialog;
        MaximizeBox = false;

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
        cancelButton.Click += (_, __) => controller.Cancel();
        await RunInstallerAsync();
    }

    private async Task RunInstallerAsync()
    {
        try
        {
            string baseDir = AppContext.BaseDirectory;
            var manifest = InstallerManifest.Load(baseDir);
            int total = manifest.Steps.Count;
            int current = 0;

            await Task.Run(async () =>
            {
                foreach (var step in manifest.Steps)
                {
                    if (controller.Token.IsCancellationRequested)
                        break;

                    string scriptPath = Path.Combine(baseDir, step.Action);
                    if (!File.Exists(scriptPath))
                    {
                        controller.Log($"⚠️ Missing script for step: {step.Name} ({scriptPath})");
                        continue;
                    }

                    controller.UpdateStatus($"Step {++current}/{total}: {step.Name}");
                    controller.Log($"🧩 Executing {step.Name}\n  {scriptPath}");

                    var psi = new ProcessStartInfo("powershell.exe",
                        $"-NoProfile -ExecutionPolicy Bypass -File \"{scriptPath}\"")
                    {
                        RedirectStandardOutput = true,
                        RedirectStandardError = true,
                        UseShellExecute = false,
                        CreateNoWindow = true
                    };

                    using var proc = Process.Start(psi)!;
                    proc.OutputDataReceived += (s, e) =>
                    {
                        if (!string.IsNullOrEmpty(e.Data))
                            controller.Log($"[OUT] {e.Data}");
                    };
                    proc.ErrorDataReceived += (s, e) =>
                    {
                        if (!string.IsNullOrEmpty(e.Data))
                            controller.Log($"[ERR] {e.Data}");
                    };

                    proc.BeginOutputReadLine();
                    proc.BeginErrorReadLine();
                    await proc.WaitForExitAsync(controller.Token);

                    if (proc.ExitCode != 0)
                    {
                        controller.Log($"❌ Step failed: {step.Name}. Exit code {proc.ExitCode}");
                        break;
                    }

                    double progress = (double)current / total * 100.0;
                    controller.SetProgress(progress);
                    controller.Log($"✅ Step {current}/{total} complete: {step.Name}");
                }
            });

            if (controller.Token.IsCancellationRequested)
            {
                controller.UpdateStatus("❌ Installation cancelled by user.");
                controller.Log("User cancelled installation.");
            }
            else
            {
                controller.UpdateStatus("✅ All steps completed successfully!");
                controller.Log("Installation completed successfully.");
            }

            // Close();
        }
        catch (OperationCanceledException)
        {
            controller.UpdateStatus("❌ Installation cancelled.");
            controller.Log("Operation cancelled by user.");
        }
        catch (Exception ex)
        {
            controller.UpdateStatus("❌ Installation failed.");
            controller.Log($"[ERR] {ex}");
            MessageBox.Show(ex.Message, "Error", MessageBoxButtons.OK, MessageBoxIcon.Error);
        }
    }

}
