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

        private Settings? _settings;
        private LogLevel _logLevel = LogLevel.Info;
        private readonly string _logFile;

        private readonly object _lock = new();
        private readonly List<string> _buffer = new();
        private readonly List<string> _logHistory = new();

        public string LogFile => _logFile;
        public LogLevel LogLevel => _logLevel;

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
            string line = $"[{DateTime.Now:HH:mm:ss}] {message}";
            // Console Logging
            Console.WriteLine(line);
            // File Logging
            lock (_lock) { File.AppendAllText(_logFile, line + Environment.NewLine); }
            _logHistory.Add(line);
        }

        // Reads the main LogFile
        // Returns a list of log lines for current LogLevel
        public List<string> FilterLogLevel()
        {
            if (!File.Exists(_logFile))
                return new List<string>();

            // Select all tags where key >= current _logLevel
            var tags = LogLevelMap
                .Where(kv => (int)kv.Key >= (int)_logLevel)
                .Select(kv => kv.Value.Tag)
                .ToArray();

            var result = new List<string>();
            foreach (var line in File.ReadLines(_logFile))
            {
                foreach (var tag in tags)
                {
                    if (line.Contains(tag, StringComparison.OrdinalIgnoreCase))
                    {
                        result.Add(line);
                        break; // stop checking tags once matched
                    }
                }
            }
            return result;
        }

        public Color DetermineColor(string message)
        {
            var level = DetermineLogLevel(message);
            return LogLevelMap.TryGetValue(level, out var meta) ? meta.Color : Color.WhiteSmoke;
        }

        private LogLevel DetermineLogLevel(string message) =>
            LogLevelMap.FirstOrDefault(kv =>
                message.Contains(kv.Value.Tag, StringComparison.OrdinalIgnoreCase)).Key;

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
}
