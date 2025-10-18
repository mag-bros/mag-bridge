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
        /// Runs a PowerShell script asynchronously.
        /// Returns the true process exit code.
        /// </summary>
        public async Task<int> RunScriptAsync(TaskConfig task, CancellationToken token = default)
        {
            if (!File.Exists(task.Script))
            {
                _logger.Write($"[ERR] Script not found: {task.Script}");
                return -1;
            }
            // Sourcing additional scripts instruction
            // string loggingPath = Path.Combine(AppContext.Base    Directory, "Scripts", "_HostLogging.ps1");
            // string escapedLog = loggingPath.Replace("'", "''");

            string sanitizedScript = task.Script.Replace("'", "''");
            string command = $"-NoProfile -ExecutionPolicy Bypass -Command \"& {{ . '{sanitizedScript}' -PreferredVersion '{task.PreferredVersion}'; exit $LASTEXITCODE }}\"";

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
                    _logger.Write($"[OUT] [{task.PackageKey ?? Path.GetFileNameWithoutExtension(task.Script)}] {line}");
                }
            }, token);

            var errTask = Task.Run(async () =>
            {
                using var reader = proc.StandardError;
                string? line;
                while ((line = await reader.ReadLineAsync()) != null)
                {
                    if (token.IsCancellationRequested) break;
                    _logger.Write($"[ERR] [{task.PackageKey ?? Path.GetFileNameWithoutExtension(task.Script)}] {line}");
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
                        _logger.Write($"[WARN] Script process forcibly terminated ({Path.GetFileName(task.Script)}).");
                    }
                }
                catch (Exception ex)
                {
                    _logger.Write($"[ERR] Failed to terminate script: {ex.Message}");
                }
                return -2;
            }

            int exitCode = proc.ExitCode;
            _logger.Write($"[VER] Script '{Path.GetFileName(task.Script)}' exited with code {exitCode}");
            return exitCode;
        }
    }
}
