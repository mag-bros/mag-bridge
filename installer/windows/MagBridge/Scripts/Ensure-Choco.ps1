# ====================================================================
# Ensure-Choco.ps1 — ensure Chocolatey is installed and operational
# Dependencies: _Logging.ps1  (dot-sourced)
# ====================================================================

$ErrorActionPreference = 'Stop'

# # --- Logging initialization ------------------------------------------
# try {
#     $logPath = Join-Path (Split-Path -Parent $MyInvocation.MyCommand.Path) "_Logging.ps1"
#     if (Test-Path $logPath) {
#         . $logPath
#         Log "[VER] Loaded logging module from $logPath"
#     }
#     else {
#         Write-Warning "_Logging.ps1 not found at $logPath — continuing without structured logging."
#         function Log($m) { Write-Host $m }
#     }
# }
# catch {
#     Write-Warning "Failed to initialize logging: $($_.Exception.Message)"
#     function Log($m) { Write-Host $m }
# }

# --- Main logic ------------------------------------------------------
$env:MAGBRIDGE_LOG_SOURCE = 'Chocolatey'

try {
    Log "[INFO] Checking for existing installation..."
    $chocoCmd = Get-Command choco -ErrorAction SilentlyContinue

    if (-not $chocoCmd) {
        Log "[WARN] Chocolatey not found. Attempting installation."

        try {
            Set-ExecutionPolicy Bypass -Scope Process -Force
            [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12

            $installScript = 'https://community.chocolatey.org/install.ps1'
            Log "[INFO] Downloading installer from $installScript"

            iex ((New-Object System.Net.WebClient).DownloadString($installScript))

            $chocoCmd = Get-Command choco -ErrorAction SilentlyContinue
            if (-not $chocoCmd) {
                Log "[ERR] Installation reported success but choco.exe not found on PATH."
                exit 1
            }

            Log "[OK] Installation completed successfully."
        }
        catch {
            Log "[ERR] Installation failed: $($_.Exception.Message)"
            exit 1
        }
    }
    else {
        Log "[OK] Existing installation detected at $($chocoCmd.Source)"
    }

    try {
        $version = choco --version 2>$null
        if ([string]::IsNullOrWhiteSpace($version)) {
            Log "[ERR] choco.exe returned no version information."
            exit 1
        }

        Log "[VER] Version $version"
    }
    catch {
        Log "[ERR] Executable check failed: $($_.Exception.Message)"
        exit 1
    }

    Log "[OK] Validation successful. Proceeding to next step."
    exit 0
}
catch {
    Log "[ERR] Unexpected error: $($_.Exception.Message)"
    exit 1
}
finally {
    $ErrorActionPreference = 'Continue'
}
