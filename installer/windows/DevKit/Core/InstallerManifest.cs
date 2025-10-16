using System.Collections.Generic;
using System.IO;
using System.Text.Json;

namespace DevKit.Core
{
    public class InstallStep
    {
        public string Name { get; set; } = "";
        public string Action { get; set; } = "";
    }

    public class InstallerManifest
    {
        public List<InstallStep> Steps { get; set; } = new();

        public static InstallerManifest Load(string baseDir)
        {
            string manifestPath = Path.Combine(baseDir, "installer.json");
            if (!File.Exists(manifestPath))
                throw new FileNotFoundException($"Installer manifest not found: {manifestPath}");

            string json = File.ReadAllText(manifestPath);
            var options = new JsonSerializerOptions { PropertyNameCaseInsensitive = true };
            return JsonSerializer.Deserialize<InstallerManifest>(json, options) ?? new InstallerManifest();
        }
    }
}
