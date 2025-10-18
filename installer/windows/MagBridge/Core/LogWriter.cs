using System;
using System.Drawing;
using System.IO;
using System.Windows.Forms;
using System.Threading;

namespace MagBridge.Core
{
    public class LogWriter
    {
        private RichTextBox? _targetBox;          // no longer readonly — can be swapped
        private readonly string _logFile;
        private readonly object _lock = new();

        // ==========================================================
        // 🔹 Global instance (like $global:Logger in PowerShell)
        // ==========================================================
        private static readonly Lazy<LogWriter> _global = new(() => new LogWriter());
        public static LogWriter Global => _global.Value;

        // ==========================================================
        // Constructors
        // ==========================================================
        public LogWriter(RichTextBox? targetBox = null)
        {
            _targetBox = targetBox;

            string logDir = Path.Combine(
                Environment.GetFolderPath(Environment.SpecialFolder.CommonApplicationData),
                "MagBridge", "Logs");

            Directory.CreateDirectory(logDir);
            _logFile = Path.Combine(logDir, $"devkit_{DateTime.Now:yyyyMMdd_HHmmss}.log");
        }

        // ==========================================================
        // Core logging logic
        // ==========================================================
        public void Write(string message)
        {
            string line = $"[{DateTime.Now:HH:mm:ss}] {message}";

            // Console
            Console.WriteLine(line);

            // File
            lock (_lock)
                File.AppendAllText(_logFile, line + Environment.NewLine);

            // UI output (optional)
            if (_targetBox is { IsHandleCreated: true } && !_targetBox.IsDisposed)
            {
                try
                {
                    _targetBox.BeginInvoke((Action)(() =>
                    {
                        Color color = DetermineColor(message);
                        _targetBox.SelectionStart = _targetBox.TextLength;
                        _targetBox.SelectionColor = color;
                        _targetBox.AppendText(line + Environment.NewLine);
                        _targetBox.SelectionColor = _targetBox.ForeColor;
                        _targetBox.ScrollToCaret();
                    }));
                }
                catch (ObjectDisposedException)
                {
                    _targetBox = null; // detach if control is gone
                }
            }
        }

        private static Color DetermineColor(string message)
        {
            if (message.Contains("[ERR]", StringComparison.OrdinalIgnoreCase))
                return Color.FromArgb(220, 76, 70); // red
            if (message.Contains("[WARN]", StringComparison.OrdinalIgnoreCase))
                return Color.Goldenrod; // yellow
            if (message.Contains("[OK]", StringComparison.OrdinalIgnoreCase))
                return Color.LightGreen;
            if (message.Contains("[VER]", StringComparison.OrdinalIgnoreCase))
                return Color.Gray;
            if (message.Contains("[INFO]", StringComparison.OrdinalIgnoreCase))
                return Color.LightSkyBlue;
            return Color.WhiteSmoke;
        }

        // ==========================================================
        // Dynamic UI sink binding
        // ==========================================================
        public void Attach(RichTextBox? target)
        {
            _targetBox = target;

            if (_targetBox == null)
            {
                Console.WriteLine("[WARN] Detached UI log sink (no active RichTextBox).");
                return;
            }

            if (!_targetBox.IsHandleCreated)
            {
                _targetBox.HandleCreated += (_, __) =>
                {
                    Write("[INFO] LogWriter attached to UI logBox (delayed bind).");
                };
            }
            else
            {
                Write("[INFO] LogWriter attached to UI logBox.");
            }
        }
    }
}
