namespace MagBridge.Core
{
    /// <summary>
    /// Controls progress bar and status label, and delegates all logging to LogWriter.
    /// </summary>
    public class ProgressController
    {
        private readonly ProgressBar _progressBar;
        private readonly Label _statusLabel;
        private readonly LogWriter _logger;
        private readonly CancellationTokenSource _cts = new();

        public CancellationToken Token => _cts.Token;
        public LogWriter Logger => _logger;

        public ProgressController(ProgressBar progressBar, Label statusLabel, RichTextBox? logBox = null)
        {
            _progressBar = progressBar;
            _statusLabel = statusLabel;
            _logger = new LogWriter(logBox);

            _logger.Write("[INFO] ProgressController initialized.");
        }

        public void UpdateStatus(string status)
        {
            _logger.Write($"[INFO] {status}");
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
