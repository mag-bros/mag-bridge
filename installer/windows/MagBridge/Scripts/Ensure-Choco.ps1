# ====================================================================
# Ensure-Choco.ps1 — ensure Chocolatey is installed and operational
# ====================================================================

$ErrorActionPreference = 'Stop'

try {
    Log-Info  "Checking for existing installation..."
    $chocoCmd = Get-Command choco -ErrorAction SilentlyContinue

    if (-not $chocoCmd) {
        Log-Warn "Chocolatey not found. Attempting installation."

        try {
            Set-ExecutionPolicy Bypass -Scope Process -Force
            [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12

            $installScript = 'https://community.chocolatey.org/install.ps1'
            Log-Info "Downloading installer from $installScript"
            iex ((New-Object System.Net.WebClient).DownloadString($installScript))

            $chocoCmd = Get-Command choco -ErrorAction SilentlyContinue
            if (-not $chocoCmd) {
                Log-Error "Installation reported success but choco.exe not found on PATH."
                exit 1
            }

            Log-Info "Installation completed successfully."
        }
        catch {
            Log-Error "Installation failed: $($_.Exception.Message)"
            exit 1
        }
    }
    else {
        Log-Info "Existing installation detected at $($chocoCmd.Source)"
    }

    try {
        $version = choco --version 2>$null
        if ([string]::IsNullOrWhiteSpace($version)) {
            Log-Error "choco.exe returned no version information."
            exit 1
        }

        Log-Info "Operational. Version $version"
    }
    catch {
        Log-Error "Executable check failed: $($_.Exception.Message)"
        exit 1
    }

    Log-Info "Validation successful. Proceeding to next step."
    exit 0
}
catch {
    Log-Error "Unexpected error: $($_.Exception.Message)"
    exit 1
}
finally {
    $ErrorActionPreference = 'Continue'
}
