// namespace MagBridge.Core
// {
//     /// <summary>
//     /// Controls progress bar and status label, and delegates all logging to LogWriter.
//     /// </summary>
//     public class ProgressController
//     {
//         private readonly ProgressBar _progressBar;
//         private readonly Label _statusLabel;
//         private readonly CancellationTokenSource _cts = new();

//         public CancellationToken Token => _cts.Token;

//         public ProgressController(ProgressBar progressBar, Label statusLabel, RichTextBox? logBox, LogWriter logger)
//         {
//             _progressBar = progressBar ?? throw new ArgumentNullException(nameof(progressBar));
//             _statusLabel = statusLabel ?? throw new ArgumentNullException(nameof(statusLabel));

//             LogWriter.Global.Write("[VER] ProgressController initialized.");
//         }

//         public void UpdateStatus(string status)
//         {
//             LogWriter.Global.Write($"[VER] {status}");
//             if (_statusLabel.IsHandleCreated)
//                 _statusLabel.Invoke(() => _statusLabel.Text = status);
//         }

//         public void SetProgress(double percent)
//         {
//             LogWriter.Global.Write($"[VER] Updating progress: {percent}%");
//             if (_progressBar.IsHandleCreated)
//             {
//                 _progressBar.Invoke(() =>
//                 {
//                     _progressBar.Style = ProgressBarStyle.Continuous;
//                     _progressBar.Value = Math.Clamp((int)percent, 0, 100);
//                 });
//             }
//         }

//         public void Cancel() => _cts.Cancel();
//     }

// }
