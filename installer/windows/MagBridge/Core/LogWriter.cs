using System;
using System.Drawing;
using System.IO;
using System.Windows.Forms;

namespace MagBridge.Core
{
    /// <summary>
    /// Handles all logging output: console, file, and RichTextBox UI (colored).
    /// Each instance writes to its own log file and can be safely shared between threads.
    /// </summary>
    public class LogWriter
    {
        private readonly RichTextBox? _uiBox;
        private readonly string _logFilePath;
        private readonly object _lock = new();

        public string LogFilePath => _logFilePath;

        public LogWriter(RichTextBox? uiBox = null)
        {
            _uiBox = uiBox;

            string dir = Path.Combine(
                Environment.GetFolderPath(Environment.SpecialFolder.CommonApplicationData),
                "MagBridge", "Logs");

            Directory.CreateDirectory(dir);
            _logFilePath = Path.Combine(dir, $"devkit_{DateTime.Now:yyyyMMdd_HHmmss}.log");

            Write("[INFO] LogWriter initialized.");
            Write($"[VER] Log file: {_logFilePath}");
        }

        /// <summary>
        /// Writes a line to console, file, and optionally to a RichTextBox.
        /// </summary>
        public void Write(string message)
        {
            string line = $"[{DateTime.Now:HH:mm:ss}] {message}";

            // Console
            Console.WriteLine(line);

            // File (thread-safe)
            lock (_lock)
            {
                File.AppendAllText(_logFilePath, line + Environment.NewLine);
            }

            // UI
            if (_uiBox is { IsHandleCreated: true })
            {
                _uiBox.BeginInvoke((Action)(() =>
                {
                    var color = DetermineColor(message);
                    int start = _uiBox.TextLength;

                    _uiBox.SelectionStart = start;
                    _uiBox.SelectionLength = 0;
                    _uiBox.SelectionColor = color;
                    _uiBox.AppendText(line + Environment.NewLine);
                    _uiBox.SelectionColor = _uiBox.ForeColor;
                    _uiBox.ScrollToCaret();
                }));
            }
        }

        private static Color DetermineColor(string message)
        {
            if (message.Contains("[ERR]", StringComparison.OrdinalIgnoreCase)) return Color.FromArgb(220, 76, 70);
            if (message.Contains("[WARN]", StringComparison.OrdinalIgnoreCase)) return Color.Goldenrod;
            if (message.Contains("[OK]", StringComparison.OrdinalIgnoreCase)) return Color.LightGreen;
            if (message.Contains("[INFO]", StringComparison.OrdinalIgnoreCase)) return Color.LightSkyBlue;
            if (message.Contains("[VER]", StringComparison.OrdinalIgnoreCase)) return Color.FromArgb(150, 150, 150);
            return Color.LightGray;
        }
    }
}
