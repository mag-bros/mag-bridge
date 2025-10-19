using System.Text.Json;
using System.Text.Json.Serialization;

namespace MagBridge.Core
{
    /// <summary>
    /// Represents installer configuration loaded from app-config.json.
    /// </summary>

    public class Settings
    {
        [JsonPropertyName("name")]
        public string Name { get; set; } = "Unnamed Installer";

        [JsonPropertyName("version")]
        public string Version { get; set; } = "1.0.0";

        [JsonPropertyName("description")]
        public string Description { get; set; } = "";

        [JsonPropertyName("icon")]
        public string Icon { get; set; } = "Assets\\icon.ico";

        [JsonPropertyName("licenseFile")]
        public string LicenseFile { get; set; } = "Licenses\\LICENSE.txt";

        [JsonPropertyName("runType")]
        public string RunType { get; set; } = "Default";

        [JsonPropertyName("loggingLevel")]
        [JsonConverter(typeof(JsonStringEnumConverter))]
        public LogLevel LoggingLevel { get; set; } = LogLevel.Info;

        // This maps "tasks" array in JSON → Tasks list in C#
        [JsonPropertyName("tasks")]
        public List<TaskParams> Tasks { get; set; } = new();

        [JsonIgnore]
        public HashSet<string> SelectedPackages { get; set; } =
            new(StringComparer.OrdinalIgnoreCase);

        public static Settings Load()
        {
            var path = Path.Combine(AppContext.BaseDirectory, "Configs", "app-config.json");
            if (!File.Exists(path))
                throw new FileNotFoundException($"Configuration file not found: {path}");

            var json = File.ReadAllText(path);

            var options = new JsonSerializerOptions
            {
                PropertyNameCaseInsensitive = true,
                ReadCommentHandling = JsonCommentHandling.Skip,
                AllowTrailingCommas = true
            };

            var settings = JsonSerializer.Deserialize<Settings>(json, options) ?? new Settings();

            // --- Resolve and validate script paths ----------------------
            foreach (var task in settings.Tasks)
            {
                if (string.IsNullOrWhiteSpace(task.Script))
                {
                    LogService.Global.Write($"[ERR] Task '{task.Label}' has no Script defined.");
                    continue;
                }

                // Convert relative → absolute
                if (!Path.IsPathRooted(task.Script))
                    task.Script = Path.Combine(AppContext.BaseDirectory, task.Script);

                if (!File.Exists(task.Script))
                    LogService.Global.Write($"[ERR] Missing script for '{task.PackageKey ?? task.Label}' — expected at: {task.Script}");
                else
                    LogService.Global.Write($"[VER] Registered script for '{task.PackageKey ?? task.Label}': {task.Script}");
            }

            return settings;
        }

        public string LoadLicenseText()
        {
            var path = Path.Combine(AppContext.BaseDirectory, LicenseFile);
            return File.Exists(path)
                ? File.ReadAllText(path)
                : $"License file not found: {path}";
        }

        public string GetIconPath() => Path.Combine(AppContext.BaseDirectory, Icon);

        public IEnumerable<TaskParams> GetDisplayTasks()
        {
            return Tasks
                .GroupBy(s => s.Key, StringComparer.OrdinalIgnoreCase)
                .Select(g => g.First())
                .OrderBy(s => s.Label, StringComparer.OrdinalIgnoreCase);
        }

        public override string ToString() => $"{Name} v{Version} ({RunType})";
    }

    public class TaskParams
    {
        [JsonPropertyName("progressLabel")]
        public string ProgressLabel { get; set; } = "";

        [JsonPropertyName("label")]
        public string Label { get; set; } = "";

        [JsonPropertyName("script")]
        public string Script { get; set; } = "";

        [JsonPropertyName("packageKey")]
        public string? PackageKey { get; set; }

        [JsonPropertyName("preChecked")]
        public bool PreChecked { get; set; } = true;

        [JsonPropertyName("preferredVersion")]
        public string PreferredVersion { get; set; } = "";

        [JsonPropertyName("minimalRequiredVersion")]
        public string MinimalRequiredVersion { get; set; } = "";

        [JsonIgnore]
        public string Key => string.IsNullOrWhiteSpace(PackageKey) ? Label : PackageKey;

        public override string ToString() => Label;

        [JsonIgnore]
        public bool IsCheckedByDefault => PreChecked;
    }
}
