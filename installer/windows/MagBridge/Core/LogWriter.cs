using System;
using System.Collections.Generic;
using System.Drawing;
using System.IO;
using System.Windows.Forms;

namespace MagBridge.Core
{
    public class LogWriter
    {
        private readonly object _lock = new();
        private readonly List<string> _buffer = new();   // 🧩 early logs stored here
        private readonly string _logFile;
        private RichTextBox? _targetBox;

        // ==========================================================
        // 🔹 Global singleton (like $global:Logger)
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
            {
                File.AppendAllText(_logFile, line + Environment.NewLine);

                // UI not yet attached → buffer it
                if (_targetBox == null || !_targetBox.IsHandleCreated || _targetBox.IsDisposed)
                {
                    _buffer.Add(line);
                    return;
                }
            }

            AppendToUi(line);
        }

        // ==========================================================
        // Flush buffered logs to UI
        // ==========================================================
        private void FlushBuffer()
        {
            lock (_lock)
            {
                if (_targetBox == null || _buffer.Count == 0)
                    return;

                foreach (var msg in _buffer)
                    AppendToUi(msg);

                _buffer.Clear();
            }
        }

        // ==========================================================
        // Append message to RichTextBox (thread-safe)
        // ==========================================================
        private void AppendToUi(string message)
        {
            if (_targetBox == null)
                return;

            try
            {
                if (_targetBox.InvokeRequired)
                {
                    _targetBox.BeginInvoke((Action)(() => AppendToUi(message)));
                    return;
                }

                Color color = DetermineColor(message);
                _targetBox.SelectionStart = _targetBox.TextLength;
                _targetBox.SelectionColor = color;
                _targetBox.AppendText(message + Environment.NewLine);
                _targetBox.SelectionColor = _targetBox.ForeColor;
                _targetBox.ScrollToCaret();
            }
            catch (ObjectDisposedException)
            {
                _targetBox = null;
            }
        }

        // ==========================================================
        // Color highlighting
        // ==========================================================
        private static Color DetermineColor(string message)
        {
            if (message.Contains("[ERR]", StringComparison.OrdinalIgnoreCase))
                return Color.FromArgb(220, 76, 70); // red
            if (message.Contains("[WARN]", StringComparison.OrdinalIgnoreCase))
                return Color.Goldenrod;
            if (message.Contains("[OK]", StringComparison.OrdinalIgnoreCase))
                return Color.LightGreen;
            if (message.Contains("[VER]", StringComparison.OrdinalIgnoreCase))
                return Color.Gray;
            if (message.Contains("[INFO]", StringComparison.OrdinalIgnoreCase))
                return Color.LightSkyBlue;
            return Color.WhiteSmoke;
        }

        // ==========================================================
        // Attach RichTextBox sink (with buffer flush)
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
                    Write("[VER] LogWriter attached to UI logBox (delayed bind).");
                    FlushBuffer();
                };
            }
            else
            {
                Write("[VER] LogWriter attached to UI logBox.");
                FlushBuffer();
            }
        }
    }
}
