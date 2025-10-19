namespace MagBridge.Core
{
    public enum LogLevel
    {
        Verbose = 0,
        Info = 2,
        Ok = 3,
        Warning = 5,
        Error = 10,
        Success = 99,
        Docs = 999
    }

    public class LogWriter
    {

        private static readonly Dictionary<LogLevel, (string Tag, int Weight, Color Color)> LogLevelMap = new()
        {
            [LogLevel.Verbose] = ("[VER]", 0, Color.Gray),
            [LogLevel.Info] = ("[INFO]", 2, Color.LightSkyBlue),
            [LogLevel.Ok] = ("[OK]", 3, Color.LightGreen),
            [LogLevel.Warning] = ("[WARN]", 5, Color.Goldenrod),
            [LogLevel.Error] = ("[ERR]", 10, Color.Red),
            [LogLevel.Success] = ("[SUCCESS]", 99, Color.Green),
            [LogLevel.Docs] = ("[DOCS]", 999, Color.LightSkyBlue)
        };

        private static readonly object _sync = new();
        private static LogWriter? _instance;
        public event Action<LogMessage>? LogUpdated;

        private Settings? _settings;
        private LogLevel _logLevel = LogLevel.Info;
        private readonly string _logFile;

        private readonly object _lock = new();
        private readonly List<string> _buffer = new();
        private readonly List<LogMessage> _logHistory = new();

        public string LogFile => _logFile;
        public LogLevel LogLevel => _logLevel;
        public object Lock => _lock;
        public int LogHistoryCount => _logHistory.Count;

        // Constructor
        private LogWriter(Settings? settings = null)
        {
            _settings = settings;
            _logLevel = settings?.LoggingLevel ?? LogLevel.Info;

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
            Write($"[INFO] Log file: {_logFile} (Level: {_logLevel})");
        }

        // ==========================================================
        // Singleton Global API Start
        // ==========================================================

        public void Write(string message)
        {
            var line = $"[{DateTime.Now:HH:mm:ss}] {message}";
            Console.WriteLine(line);

            var msg = LogMessage.FromRaw(line, LogLevelMap);

            lock (_lock)
            {
                File.AppendAllText(_logFile, line + Environment.NewLine);
                _logHistory.Add(msg);
                if (_logHistory.Count > 25000)
                    _logHistory.RemoveAt(0);
            }

            // 🔔 Notify subscribers asynchronously (don’t block logger)
            Task.Run(() => LogUpdated?.Invoke(msg));
        }

        public List<LogMessage> FilterLogLevel()
        {
            lock (_lock)
            {
                return _logHistory
                    .Where(m => (int)m.Level >= (int)_logLevel)
                    .ToList();
            }
        }

        public void SetLogLevel(LogLevel newLevel)
        {
            _logLevel = newLevel;
        }

        private void ApplySettings(Settings settings)
        {
            _settings = settings;
        }

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

        public static void Init(Settings settings)
        {
            if (settings == null)
                throw new ArgumentNullException(nameof(settings));

            lock (_sync)
            {
                if (_instance != null)
                {
                    _instance.ApplySettings(settings);
                    _instance.SetLogLevel(settings.LoggingLevel);
                }
                else { _instance = new LogWriter(settings); }

                _instance.Write($"[INFO] Logging system activated — runtime configuration loaded (LogLevel: {settings.LoggingLevel}).");
            }
        }
    }

    public class LogMessage
    {
        public string Raw { get; }
        public LogLevel Level { get; }
        public string Tag { get; }
        public Color Color { get; }

        public LogMessage(string raw, LogLevel level, string tag, Color color)
        {
            Raw = raw;
            Level = level;
            Tag = tag;
            Color = color;
        }

        public static LogMessage FromRaw(string raw, Dictionary<LogLevel, (string Tag, int Weight, Color Color)> levelMap)
        {
            var level = DeserializeLogLevel(raw, levelMap);

            (string Tag, int Weight, Color Color) meta =
                levelMap.TryGetValue(level, out var m) ? m : ("[VER]", 0, Color.Gray);

            return new LogMessage(raw, level, meta.Tag, meta.Color);
        }

        private static LogLevel DeserializeLogLevel(string message, Dictionary<LogLevel, (string Tag, int Weight, Color Color)> levelMap)
        {
            foreach (var kv in levelMap)
            {
                if (message.Contains(kv.Value.Tag, StringComparison.OrdinalIgnoreCase))
                    return kv.Key;
            }
            return LogLevel.Verbose;
        }

        public override string ToString() => Raw;
    }


}
