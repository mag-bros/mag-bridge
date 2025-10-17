using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text.Json;

namespace MagBridge.Core
{
    /// <summary>
    /// Represents installer configuration loaded from app.json.
    /// </summary>
    public class Settings
    {
        public string Name { get; set; } = "Unnamed Installer";
        public string Version { get; set; } = "1.0.0";
        public string Description { get; set; } = "";
        public string Icon { get; set; } = "Assets\\icon.ico";
        public string LicenseFile { get; set; } = "Licenses\\LICENSE.txt";

        /// <summary>
        /// Defines the installation mode or preset (e.g. "SDK", "Runtime", "Full").
        /// Optional; defaults to "Default".
        /// </summary>
        public string RunType { get; set; } = "Default";

        public List<InstallStep> Steps { get; set; } = new();

        public HashSet<string> SelectedPackages { get; set; } =
            new(StringComparer.OrdinalIgnoreCase);

        public static Settings Load()
        {
            var path = Path.Combine(AppContext.BaseDirectory, "Configs", "app.json");
            if (!File.Exists(path))
                throw new FileNotFoundException($"Configuration file not found: {path}");

            var json = File.ReadAllText(path);
            var options = new JsonSerializerOptions
            {
                PropertyNameCaseInsensitive = true,
                ReadCommentHandling = JsonCommentHandling.Skip,
                AllowTrailingCommas = true
            };
            return JsonSerializer.Deserialize<Settings>(json, options) ?? new Settings();
        }

        public string LoadLicenseText()
        {
            var path = Path.Combine(AppContext.BaseDirectory, LicenseFile);
            return File.Exists(path)
                ? File.ReadAllText(path)
                : $"License file not found: {path}";
        }

        public string GetIconPath() => Path.Combine(AppContext.BaseDirectory, Icon);

        public IEnumerable<InstallStep> GetDisplaySteps()
        {
            return Steps
                .GroupBy(s => s.Key, StringComparer.OrdinalIgnoreCase)
                .Select(g => g.First())
                .OrderBy(s => s.Label, StringComparer.OrdinalIgnoreCase);
        }

        /// <summary>
        /// Returns a readable summary string for logs or diagnostics.
        /// </summary>
        public override string ToString()
            => $"{Name} v{Version} ({RunType})";
    }

    /// <summary>
    /// Represents a single installer step as defined in app.json.
    /// Also used directly as UI item (e.g., in CheckedListBox).
    /// </summary>
    public class InstallStep
    {
        public string ProgressLabel { get; set; } = "";
        public string Label { get; set; } = "";
        public string Action { get; set; } = "";
        public string? PackageKey { get; set; }
        public bool PreChecked { get; set; } = true;

        /// <summary>
        /// Unique key identifying this step, based on PackageKey or Label.
        /// </summary>
        public string Key => string.IsNullOrWhiteSpace(PackageKey) ? Label : PackageKey;

        /// <summary>
        /// Display text for UI list controls.
        /// </summary>
        public override string ToString() => Label;

        /// <summary>
        /// Whether this item should be shown as checked by default.
        /// </summary>
        public bool IsCheckedByDefault => PreChecked;
    }
}

