using System;
using System.Collections.Generic;
using System.IO;
using System.Text.Json;

namespace MagBridge.Core
{
    /// <summary>
    /// Represents the static runtime configuration for the installer.
    /// All referenced files (Configs/app.json, Licenses/LICENSE.txt, Assets/icon.ico)
    /// are ensured at build time by the .csproj.
    /// </summary>
    public class Settings
    {
        public string Name { get; set; } = "Unnamed Installer";
        public string Version { get; set; } = "1.0.0";
        public string Description { get; set; } = "";
        public string Icon { get; set; } = "Assets\\icon.ico";
        public string LicenseFile { get; set; } = "Licenses\\LICENSE.txt";
        public List<InstallStep> Steps { get; set; } = new();

        /// <summary>
        /// Loads the application settings from the fixed build output path.
        /// </summary>
        public static Settings Load()
        {
            string baseDir = AppContext.BaseDirectory;
            string configPath = Path.Combine(baseDir, "Configs", "app.json");

            if (!File.Exists(configPath))
                throw new FileNotFoundException($"Configuration file not found: {configPath}");

            string json = File.ReadAllText(configPath);
            var options = new JsonSerializerOptions { PropertyNameCaseInsensitive = true };

            return JsonSerializer.Deserialize<Settings>(json, options) ?? new Settings();
        }

        /// <summary>
        /// Loads the license text referenced by the current settings.
        /// </summary>
        public string LoadLicenseText()
        {
            string licensePath = Path.Combine(AppContext.BaseDirectory, LicenseFile);

            if (!File.Exists(licensePath))
                return $"License file not found: {licensePath}";

            try
            {
                return File.ReadAllText(licensePath);
            }
            catch (Exception ex)
            {
                return $"Error reading license file ({licensePath}): {ex.Message}";
            }
        }

        /// <summary>
        /// Returns the resolved icon path (used for UI display or window icon binding).
        /// </summary>
        public string GetIconPath()
        {
            return Path.Combine(AppContext.BaseDirectory, Icon);
        }
    }

    public class InstallStep
    {
        public string Name { get; set; } = "";
        public string Action { get; set; } = "";
    }
}
