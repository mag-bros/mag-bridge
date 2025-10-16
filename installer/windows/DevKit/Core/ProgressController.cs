using System;
using System.IO;
using System.Windows.Forms;
using System.Threading;

namespace DevKit.Core
{
    public class ProgressController
    {
        private readonly ProgressBar _progressBar;
        private readonly Label _statusLabel;
        private readonly TextBox? _logBox;
        private readonly string _logFile;
        private readonly CancellationTokenSource _cts = new();

        public CancellationToken Token => _cts.Token;

        public ProgressController(ProgressBar progressBar, Label statusLabel, TextBox? logBox = null)
        {
            _progressBar = progressBar;
            _statusLabel = statusLabel;
            _logBox = logBox;

            string logDir = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.CommonApplicationData), "DevKit", "Logs");
            Directory.CreateDirectory(logDir);
            _logFile = Path.Combine(logDir, $"devkit_{DateTime.Now:yyyyMMdd_HHmmss}.log");

            Log($"📄 Logging output to: {_logFile}");
        }

        public void Log(string message)
        {
            string line = $"{DateTime.Now:HH:mm:ss} {message}";
            Console.WriteLine(line);
            File.AppendAllText(_logFile, line + Environment.NewLine);

            if (_logBox != null && _logBox.IsHandleCreated)
            {
                _logBox.Invoke(() =>
                {
                    _logBox.AppendText(line + Environment.NewLine);
                    _logBox.SelectionStart = _logBox.TextLength;
                    _logBox.ScrollToCaret();
                });
            }
        }

        public void UpdateStatus(string status)
        {
            Log(status);
            if (_statusLabel.IsHandleCreated)
                _statusLabel.Invoke(() => _statusLabel.Text = status);
        }

        public void SetProgress(double percent)
        {
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
