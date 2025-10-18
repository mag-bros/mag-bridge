using System.ComponentModel.Composition.Hosting;
using Microsoft.VisualBasic.Logging;

namespace MagBridge.Core
{
    public enum LogLevel
    {
        Verbose = 0,
        Info = 2,
        Ok = 3,
        Warning = 5,
        Error = 10,
        Success = 99
    }

    public class LogWriter
    {
        private static LogWriter? _instance;
        private static readonly object _sync = new();
        private Settings? _settings;

        public static LogWriter Global
        {
            get
            {
                lock (_sync)
                {
                    // Auto-bootstrap logger for pre-init use
                    return _instance ??= new LogWriter(settings: null);
                }
            }
        }

        public static void Init(Settings settings, RichTextBox? targetBox = null)
        {
            if (settings == null)
                throw new ArgumentNullException(nameof(settings));

            lock (_sync)
            {
                // If Global already created a bootstrap logger, just reconfigure it
                if (_instance == null)
                    _instance = new LogWriter(settings, targetBox);
                else
                {
                    _instance.SetSettings(settings);
                    _instance.SetTargetLogBox(targetBox);
                    _instance.SetLogLevel(settings.LoggingLevel);
                }

                _instance.Write($"[INFO] Logging system activated — runtime configuration loaded (Level: {settings.LoggingLevel}).");
            }
        }

        // ==================================================
        // Instance part
        // ==================================================
        private readonly object _lock = new();
        private readonly List<string> _buffer = new();
        private readonly string _logFile;
        private readonly List<string> _logHistory = new();
        private RichTextBox? _targetBox;
        private LogLevel _currentLogLevel = LogLevel.Info;

        // ==========================================================
        // LogWriter Constructor
        // ==========================================================
        private LogWriter(Settings? settings = null, RichTextBox? targetBox = null)
        {
            _settings = settings;
            _targetBox = targetBox;
            _currentLogLevel = settings?.LoggingLevel ?? LogLevel.Info;

            // Determine log directory (fallback to Temp if needed)
            var logDir = Path.Combine(
                Environment.GetFolderPath(Environment.SpecialFolder.CommonApplicationData),
                "MagBridge", "Logs");

            if (!Directory.Exists(logDir))
            {
                try { Directory.CreateDirectory(logDir); }
                catch
                {
                    logDir = Path.Combine(Path.GetTempPath(), "MagBridge", "Logs");
                    Directory.CreateDirectory(logDir);
                    Write("[WARN] Using temporary log directory (CommonAppData unavailable).");
                }
            }

            _logFile = Path.Combine(logDir, $"devkit_{DateTime.Now:yyyyMMdd_HHmmss}.log");

            // Header
            Write($"[VER] LogWriter {(settings is null ? "bootstrap" : "configured")} instance created.");
            Write($"[INFO] Log file: {_logFile} (Level: {_currentLogLevel})");
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

                // 🧩 Always store full verbose logs in full history (unfiltered)
                _logHistory.Add(message);
                const int MaxEntries = 25000; // prevent memory bloat
                if (_logHistory.Count > MaxEntries)
                    _logHistory.RemoveAt(0);

                // 🧮 Determine message log level
                LogLevel msgLevel = DetermineLogLevel(message);

                // 🚫 Filter only what gets printed to the visible box
                bool filterLogLevel = (int)msgLevel < (int)_currentLogLevel;
                if (filterLogLevel) return;

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

        public void SetSettings(Settings settings)
        {
            _settings = settings;
        }

        private void SetTargetLogBox(RichTextBox? targetBox)
        {
            _targetBox = targetBox;
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
