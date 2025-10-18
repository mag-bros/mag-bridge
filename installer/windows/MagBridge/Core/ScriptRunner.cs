using System.Diagnostics;

namespace MagBridge.Core
{
    /// <summary>
    /// Executes PowerShell scripts with real-time log streaming, correct exit-code propagation,
    /// and integrated LogWriter output. Safe for Windows 7 PowerShell 5.1 and newer.
    /// </summary>
    public class ScriptRunner
    {
        private readonly LogWriter _logger;

        public ScriptRunner(LogWriter logger)
        {
            _logger = logger ?? throw new ArgumentNullException(nameof(logger));
        }

        /// <summary>
        /// Runs a PowerShell script with logging support.
        /// Returns the true process exit code.
        /// </summary>
        public async Task<int> RunScriptAsync(string scriptPath, string? sourceTag = null, CancellationToken token = default)
        {
            if (!File.Exists(scriptPath))
            {
                _logger.Write($"[ERR] Script not found: {scriptPath}");
                return -1;
            }
            // string loggingPath = Path.Combine(AppContext.BaseDirectory, "Scripts", "_HostLogging.ps1");

            // --- Correct PowerShell command construction ---
            // Note: "exit $LASTEXITCODE" ensures inner script exit code bubbles up
            // string escapedLog = loggingPath.Replace("'", "''");
            string sanitizedScript = scriptPath.Replace("'", "''");
            string command = $"-NoProfile -ExecutionPolicy Bypass -Command \"& {{ . '{sanitizedScript}'; exit $LASTEXITCODE }}\"";

            var psi = new ProcessStartInfo("powershell.exe", command)
            {
                RedirectStandardOutput = true,
                RedirectStandardError = true,
                UseShellExecute = false,
                CreateNoWindow = true
            };

            using var proc = new Process { StartInfo = psi, EnableRaisingEvents = true };
            proc.Start();

            // --- Async streaming of stdout/stderr ---
            var outTask = Task.Run(async () =>
            {
                using var reader = proc.StandardOutput;
                string? line;
                while ((line = await reader.ReadLineAsync()) != null)
                {
                    if (token.IsCancellationRequested) break;
                    _logger.Write($"[OUT] [{sourceTag ?? Path.GetFileNameWithoutExtension(scriptPath)}] {line}");
                }
            }, token);

            var errTask = Task.Run(async () =>
            {
                using var reader = proc.StandardError;
                string? line;
                while ((line = await reader.ReadLineAsync()) != null)
                {
                    if (token.IsCancellationRequested) break;
                    _logger.Write($"[ERR] [{sourceTag ?? Path.GetFileNameWithoutExtension(scriptPath)}] {line}");
                }
            }, token);

            // --- Wait for process completion ---
            await Task.WhenAll(outTask, errTask);

            try
            {
                await proc.WaitForExitAsync(token);
            }
            catch (OperationCanceledException)
            {
                try
                {
                    if (!proc.HasExited)
                    {
                        proc.Kill(true);
                        _logger.Write($"[WARN] Script process forcibly terminated ({Path.GetFileName(scriptPath)}).");
                    }
                }
                catch (Exception ex)
                {
                    _logger.Write($"[ERR] Failed to terminate script: {ex.Message}");
                }
                return -2;
            }

            int exitCode = proc.ExitCode;
            _logger.Write($"[VER] Script '{Path.GetFileName(scriptPath)}' exited with code {exitCode}");
            return exitCode;
        }
    }
}
