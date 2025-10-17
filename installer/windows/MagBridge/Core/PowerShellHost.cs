using System;
using System.IO;
using System.Linq;
using System.Management.Automation;
using System.Threading.Tasks;

namespace MagBridge
{
    /// <summary>
    /// Hosts a PowerShell runspace inside this .NET process (no external powershell.exe).
    /// Captures output, errors, and logs to a file.
    /// </summary>
    public class PowerShellHost
    {
        private readonly string _logPath;

        public PowerShellHost()
        {
            string logDir = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.CommonApplicationData), "MagBridge", "Logs");
            Directory.CreateDirectory(logDir);
            _logPath = Path.Combine(logDir, $"devkit_{DateTime.Now:yyyyMMdd_HHmmss}.log");
        }

        public async Task ExecuteScriptAsync(string scriptPath)
        {
            string scriptContent = await File.ReadAllTextAsync(scriptPath);

            Console.WriteLine($"🧩 Executing PowerShell script:\n  {scriptPath}");
            Console.WriteLine($"📄 Logging output to: {_logPath}\n");

            using (PowerShell ps = PowerShell.Create())
            {
                ps.AddScript(scriptContent);

                ps.Streams.Error.DataAdded += (_, e) =>
                {
                    var record = ps.Streams.Error[e.Index];
                    Log($"[ERROR] {record}");
                };

                ps.Streams.Information.DataAdded += (_, e) =>
                {
                    var info = ps.Streams.Information[e.Index];
                    Log($"[INFO] {info.MessageData}");
                };

                ps.Streams.Warning.DataAdded += (_, e) =>
                {
                    var warning = ps.Streams.Warning[e.Index];
                    Log($"[WARN] {warning.Message}");
                };

                var results = ps.Invoke();

                if (ps.HadErrors)
                {
                    throw new InvalidOperationException("PowerShell script encountered errors.");
                }

                foreach (var line in results.Select(r => r?.ToString()))
                    Log($"{line}");

                Console.WriteLine("PowerShell execution finished successfully.");
            }
        }

        private void Log(string message)
        {
            string line = $"{DateTime.Now:HH:mm:ss} {message}";
            Console.WriteLine(line);
            File.AppendAllText(_logPath, line + Environment.NewLine);
        }
    }
}
