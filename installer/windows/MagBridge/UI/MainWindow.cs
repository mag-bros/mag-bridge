using System;
using System.Windows.Forms;

namespace MagBridge
{
    /// <summary>
    /// Simple MagBridge installer window: status label + progress bar + log box.
    /// UI updates are thread-safe.
    /// </summary>
    public class MainWindow : Form
    {
        private readonly Label _statusLabel;
        private readonly ProgressBar _progressBar;
        private readonly TextBox _logBox;

        public MainWindow()
        {
            Text = "MagBridge Installer";
            Width = 600;
            Height = 300;
            StartPosition = FormStartPosition.CenterScreen;

            _statusLabel = new Label
            {
                Text = "Preparing...",
                AutoSize = false,
                Left = 10,
                Top = 10,
                Width = ClientSize.Width - 20,
                Height = 20
            };
            Controls.Add(_statusLabel);

            _progressBar = new ProgressBar
            {
                Left = 10,
                Top = 40,
                Width = ClientSize.Width - 20,
                Height = 24,
                Minimum = 0,
                Maximum = 100,
                Value = 0
            };
            Controls.Add(_progressBar);

            _logBox = new TextBox
            {
                Left = 10,
                Top = 72,
                Width = ClientSize.Width - 20,
                Height = ClientSize.Height - 82,
                Multiline = true,
                ScrollBars = ScrollBars.Vertical,
                ReadOnly = true
            };
            Controls.Add(_logBox);

            Resize += (_, __) =>
            {
                _statusLabel.Width = ClientSize.Width - 20;
                _progressBar.Width = ClientSize.Width - 20;
                _logBox.Width = ClientSize.Width - 20;
                _logBox.Height = ClientSize.Height - 82;
            };
        }

        public void SetStatus(string text)
        {
            if (InvokeRequired)
            {
                Invoke(new Action(() => SetStatus(text)));
                return;
            }
            _statusLabel.Text = text;
            AppendLog($"STATUS: {text}");
        }

        public void SetProgress(int currentIndex, int totalSteps)
        {
            if (InvokeRequired)
            {
                Invoke(new Action(() => SetProgress(currentIndex, totalSteps)));
                return;
            }

            if (totalSteps <= 0)
            {
                _progressBar.Value = 0;
                return;
            }

            double pct = (double)currentIndex / totalSteps;
            int val = (int)Math.Round(pct * _progressBar.Maximum);
            _progressBar.Value = Math.Min(Math.Max(val, _progressBar.Minimum), _progressBar.Maximum);
        }

        public void AppendLog(string line)
        {
            if (InvokeRequired)
            {
                Invoke(new Action(() => AppendLog(line)));
                return;
            }
            _logBox.AppendText($"{DateTime.Now:HH:mm:ss} {line}{Environment.NewLine}");
        }
    }
}
