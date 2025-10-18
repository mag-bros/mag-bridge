namespace MagBridge.Core
{
    public enum LogLevel
    {
        Verbose = 0,
        Info = 2,
        Ok = 3,
        Warning = 5,
        Success = 6,
        Error = 10
    }

    public class LogWriter
    {
        private LogLevel _currentLogLevel = LogLevel.Verbose;

        private readonly object _lock = new();
        private readonly List<string> _buffer = new();   // 🧩 early logs stored here
        private readonly string _logFile;
        private RichTextBox? _targetBox;
        private readonly List<string> _logHistory = new();
        // 🔹 Global singleton (like $global:Logger)
        private static readonly Lazy<LogWriter> _global = new(() => new LogWriter());
        public static LogWriter Global => _global.Value;

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

            AppendToLogBox(line);
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
                    AppendToLogBox(msg);

                _buffer.Clear();
            }
        }

        // ==========================================================
        // Append message to RichTextBox (thread-safe)
        // ==========================================================
        private void AppendToLogBox(string message)
        {
            if (_targetBox == null)
                return;

            try
            {
                if (_targetBox.InvokeRequired)
                {
                    _targetBox.BeginInvoke((Action)(() => AppendToLogBox(message)));
                    return;
                }

                // 🧩 Always store log in full history (unfiltered)
                _logHistory.Add(message);
                const int MaxEntries = 25000; // prevent memory bloat
                if (_logHistory.Count > MaxEntries)
                    _logHistory.RemoveAt(0);

                // 🧮 Determine message log level
                LogLevel messageLevel = DetermineLogLevel(message);

                // 🚫 Filter only what gets printed to the visible box
                if ((int)messageLevel < (int)_currentLogLevel)
                    return;

                // --- Visual display logic ---
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

        private static Color DetermineColor(string message)
        {
            if (message.Contains("[ERR]", StringComparison.OrdinalIgnoreCase))
                return Color.Red;
            if (message.Contains("[WARN]", StringComparison.OrdinalIgnoreCase))
                return Color.Goldenrod;
            if (message.Contains("[OK]", StringComparison.OrdinalIgnoreCase))
                return Color.LightGreen;
            if (message.Contains("[VER]", StringComparison.OrdinalIgnoreCase))
                return Color.Gray;
            if (message.Contains("[INFO]", StringComparison.OrdinalIgnoreCase))
                return Color.LightSkyBlue;
            if (message.Contains("[SUCCESS]", StringComparison.OrdinalIgnoreCase))
                return Color.Green;
            return Color.WhiteSmoke;
        }

        private static LogLevel DetermineLogLevel(string message)
        {
            if (message.Contains("[ERR]", StringComparison.OrdinalIgnoreCase)) return LogLevel.Error;
            if (message.Contains("[WARN]", StringComparison.OrdinalIgnoreCase)) return LogLevel.Warning;
            if (message.Contains("[OK]", StringComparison.OrdinalIgnoreCase)) return LogLevel.Ok;
            if (message.Contains("[SUCCESS]", StringComparison.OrdinalIgnoreCase)) return LogLevel.Success;
            if (message.Contains("[INFO]", StringComparison.OrdinalIgnoreCase)) return LogLevel.Info;
            if (message.Contains("[VER]", StringComparison.OrdinalIgnoreCase)) return LogLevel.Verbose;
            return LogLevel.Verbose; // default fallback
        }

        public void SetLogLevel(LogLevel level)
        {
            _currentLogLevel = level;
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
