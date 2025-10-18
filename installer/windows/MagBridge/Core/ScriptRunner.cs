using System.Diagnostics;

namespace MagBridge.Core
{
    public class ScriptRunner
    {
        private readonly LogWriter _logger;

        public ScriptRunner(LogWriter logger)
        {
            _logger = logger;
        }

        public async Task<int> RunScriptAsync(string scriptPath)
        {
            string loggingPath = Path.Combine(AppContext.BaseDirectory, "Scripts", "_Logging.ps1");
            string command = $"-NoProfile -ExecutionPolicy Bypass -Command \"& {{ . '{loggingPath}'; . '{scriptPath}' }}\"";

            var psi = new ProcessStartInfo("powershell.exe", command)
            {
                RedirectStandardOutput = true,
                RedirectStandardError = true,
                UseShellExecute = false,
                CreateNoWindow = true
            };

            using var proc = new Process { StartInfo = psi, EnableRaisingEvents = true };
            proc.Start();

            var outTask = Task.Run(async () =>
            {
                using var reader = proc.StandardOutput;
                string? line;
                while ((line = await reader.ReadLineAsync()) != null)
                    _logger.Write(line);
            });

            var errTask = Task.Run(async () =>
            {
                using var reader = proc.StandardError;
                string? line;
                while ((line = await reader.ReadLineAsync()) != null)
                    _logger.Write("[ERR] " + line);
            });

            await Task.WhenAll(outTask, errTask);
            proc.WaitForExit();
            return proc.ExitCode;
        }
    }
}
