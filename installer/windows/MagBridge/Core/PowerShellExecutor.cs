using System.Diagnostics;
using System.Text;

namespace MagBridge.Core
{
    /// <summary>
    /// Executes PowerShell scripts with real-time log streaming, correct exit-code propagation,
    /// and integrated LogWriter output. Safe for Windows 7 PowerShell 5.1 and newer.
    /// </summary>
    public class PowerShellExecutor
    {
        private readonly LogWriter _logger;
        private readonly string PsExe = "powershell.exe";

        public PowerShellExecutor(LogWriter logger)
        {
            _logger = logger ?? throw new ArgumentNullException(nameof(logger));
        }

        /// <summary>
        /// Runs a PowerShell script asynchronously.
        /// Returns the true process exit code.
        /// </summary>
        public async Task<int> RunScriptAsync(TaskParams task, CancellationToken token = default)
        {
            if (!File.Exists(task.Script))
            {
                _logger.Write($"[ERR] Script not found: {task.Script}");
                return -1;
            }

            var command = new PowerShellCommandBuilder()
                .WithImports(
                    Path.Combine(AppContext.BaseDirectory, "Scripts", "_Helpers.ps1"),
                    Path.Combine(AppContext.BaseDirectory, "Scripts", "ScriptTemplate.ps1 ")
                )
                .WithScript(task.Script)
                .WithPackage(task.PackageKey, task.PreferredVersion, task.MinimalRequiredVersion)
                .Build();

            var psi = new ProcessStartInfo
            {
                FileName = PsExe,
                Arguments = command,
                RedirectStandardOutput = true,
                RedirectStandardError = true,
                UseShellExecute = false,
                CreateNoWindow = true
            };

            using var proc = new Process { StartInfo = psi, EnableRaisingEvents = true };
            proc.Start();

            var cts = CancellationTokenSource.CreateLinkedTokenSource(token);
            var killTask = Task.Run(async () =>
            {
                try
                {
                    await Task.Delay(Timeout.Infinite, cts.Token); // waits until cancelled
                }
                catch (OperationCanceledException)
                {
                    if (!proc.HasExited)
                    {
                        try
                        {
                            proc.Kill(entireProcessTree: true);
                            _logger.Write($"[WARN] Script '{Path.GetFileName(task.Script)}' killed on cancellation.");
                        }
                        catch (Exception ex)
                        {
                            _logger.Write($"[ERR] Kill failed: {ex.Message}");
                        }
                    }
                }
            });

            var outTask = Task.Run(async () =>
            {
                using var reader = proc.StandardOutput;
                string? line;
                while ((line = await reader.ReadLineAsync()) != null && !token.IsCancellationRequested)
                    _logger.Write($"[{task.PackageKey ?? Path.GetFileNameWithoutExtension(task.Script)}] {line}");
            }, token);

            var errTask = Task.Run(async () =>
            {
                using var reader = proc.StandardError;
                string? line;
                while ((line = await reader.ReadLineAsync()) != null && !token.IsCancellationRequested)
                    _logger.Write($"[ERR] [{task.PackageKey ?? Path.GetFileNameWithoutExtension(task.Script)}] {line}");
            }, token);

            await Task.WhenAll(outTask, errTask, proc.WaitForExitAsync(token).ContinueWith(_ => cts.Cancel()));
            int exitCode = proc.ExitCode;
            _logger.Write($"[VER] Script '{Path.GetFileName(task.Script)}' exited with code {exitCode}");
            return exitCode;
        }

        protected sealed class PowerShellCommandBuilder
        {
            private readonly List<string> _imports = new();
            private string _script = string.Empty;
            private string _packageKey = string.Empty;
            private string _preferredVersion = string.Empty;
            private string _minimumRequiredVersion = string.Empty;

            /// <summary>
            /// Adds one or more import paths to be dot-sourced before the main script.
            /// </summary>
            public PowerShellCommandBuilder WithImports(params string[] imports)
            {
                if (imports is { Length: > 0 })
                    _imports.AddRange(imports.Where(i => !string.IsNullOrWhiteSpace(i)));

                return this;
            }

            /// <summary>
            /// Sets the main PowerShell script path.
            /// </summary>
            public PowerShellCommandBuilder WithScript(string scriptPath)
            {
                _script = scriptPath ?? string.Empty;
                return this;
            }

            /// <summary>
            /// Sets package details for Ensure-* scripts.
            /// </summary>
            public PowerShellCommandBuilder WithPackage(
                string? packageKey,
                string? preferredVersion,
                string? minimumRequiredVersion)
            {
                _packageKey = packageKey ?? string.Empty;
                _preferredVersion = preferredVersion ?? string.Empty;
                _minimumRequiredVersion = minimumRequiredVersion ?? string.Empty;
                return this;
            }

            /// <summary>
            /// Builds the final PowerShell command string ready to execute.
            /// </summary>
            public string Build()
            {
                if (string.IsNullOrWhiteSpace(_script))
                    throw new InvalidOperationException("Main script path must be set before building the command.");

                var sb = new StringBuilder();
                sb.AppendLine("-NoProfile -ExecutionPolicy Bypass -Command \"& {");

                foreach (var import in _imports)
                    sb.AppendLine($"    . {Sanitize(import)};");

                sb.AppendLine($"    . {Sanitize(_script)} -PackageKey {Sanitize(_packageKey)} `");
                sb.AppendLine($"        -PreferredVersion {Sanitize(_preferredVersion)} `");
                sb.AppendLine($"        -MinimumRequiredVersion {Sanitize(_minimumRequiredVersion)}");
                sb.AppendLine("    exit $LASTEXITCODE");
                sb.Append("}\"");

                return sb.ToString();
            }

            /// <summary>
            /// Escapes and quotes a string for safe embedding in PowerShell commands.
            /// Produces a single-quoted literal (so no interpolation, variable expansion, etc.).
            /// </summary>
            private static string Sanitize(string input)
            {
                if (string.IsNullOrWhiteSpace(input))
                    return "''"; // empty literal string in PowerShell

                // 1. Trim outer spaces
                var trimmed = input.Trim();

                // 2. Escape single quotes by doubling them
                //    e.g. O'Hara -> 'O''Hara'
                var escaped = trimmed.Replace("'", "''");

                // 3. Wrap in single quotes to form a literal
                //    This avoids any interpretation of &, $, `, (, ), etc.
                return $"'{escaped}'";
            }
        }

    }
}
