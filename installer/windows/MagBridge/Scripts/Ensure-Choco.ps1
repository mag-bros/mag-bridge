# ====================================================================
# Ensure-Choco.ps1 — ensure Chocolatey is installed and operational
# ====================================================================

$ErrorActionPreference = 'Stop'

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

# ====================================================================
# Invoke-ChocoInstall — Unified installer for MagBridge scripts
# Handles installation, upgrade, repair, and validation via Chocolatey.
# Integrates with the unified logging (Log "[TAG] message") interface.
# ====================================================================
function Invoke-ChocoInstall {
    param(
        [Parameter(Mandatory=$true)][string]$Package,
        [Parameter(Mandatory=$false)][string]$Version,
        [switch]$Force,
        [switch]$UpgradeIfExists,
        [int]$Timeout = 600
    )

    $ErrorActionPreference = 'Stop'
    Log "[INFO] Preparing Chocolatey operation for package: $Package"

    # --- Verify Chocolatey availability ------------------------------------
    try {
        $chocoCmd = Get-Command choco -ErrorAction SilentlyContinue
        if (-not $chocoCmd) {
            Log "[ERR] Chocolatey not found in PATH."
            return $false
        }
        Log "[VER] Using Chocolatey at $($chocoCmd.Source)"
    }
    catch {
        Log "[ERR] Unable to check Chocolatey presence: $($_.Exception.Message)"
        return $false
    }

    # --- Compose arguments -------------------------------------------------
    $args = @('install', $Package,
        '--yes',
        '--no-progress',
        '--ignore-detected-reboot',
        '--exit-when-reboot-detected=false',
        '--requirechecksum=false',
        '--allow-empty-checksums',
        '--force-dependencies',
        '--timeout', "$Timeout"
    )

    if ($Version) { $args += @('--version', $Version) }
    if ($Force)   { $args += '--force' }

    # If requested, use 'upgrade' instead of 'install' when package exists
    if ($UpgradeIfExists) {
        $local = choco list --local-only | Where-Object { $_ -match "^$Package\s+" }
        if ($local) {
            Log "[INFO] Existing installation found — switching to upgrade mode."
            $args[0] = 'upgrade'
        }
    }

    $psi = New-Object System.Diagnostics.ProcessStartInfo
    $psi.FileName = 'choco'
    $psi.Arguments = ($args -join ' ')
    $psi.RedirectStandardOutput = $true
    $psi.RedirectStandardError  = $true
    $psi.UseShellExecute = $false
    $psi.CreateNoWindow = $true

    Log "[INFO] Executing: choco $($psi.Arguments)"

    $proc = [System.Diagnostics.Process]::Start($psi)
    if (-not $proc) {
        Log "[ERR] Failed to start Chocolatey process."
        return $false
    }

    $stdout = $proc.StandardOutput.ReadToEnd()
    $stderr = $proc.StandardError.ReadToEnd()
    $proc.WaitForExit()

    # --- Filter noise ------------------------------------------------------
    $filtered = $stdout -split "`r?`n" | Where-Object {
        $_ -and ($_ -notmatch 'reboot|compare|validation')
    }

    foreach ($line in $filtered) {
        if ($line -match '(?i)already installed') {
            Log "[WARN] $line"
        }
        elseif ($line -match '(?i)installed successfully|The install of|has been installed') {
            Log "[OK] $line"
        }
        elseif ($line -match '(?i)failed|error|not found|exception') {
            Log "[ERR] $line"
        }
        elseif ($line -match '(?i)upgraded|upgrade successful') {
            Log "[OK] $line"
        }
        elseif ($line -match '(?i)downloading|installing|extracting') {
            Log "[INFO] $line"
        }
        else {
            Log "[INFO] $line"
        }
    }

    # --- Exit code handling -----------------------------------------------
    switch ($proc.ExitCode) {
        0     { Log "[OK] $Package installation completed successfully."; return $true }
        1641  { Log "[WARN] $Package installed; reboot requested (suppressed)."; return $true }
        3010  { Log "[WARN] $Package installed; pending reboot ignored."; return $true }
        default {
            Log "[ERR] Chocolatey returned exit code $($proc.ExitCode)."
            if ($stderr) { Log "[ERR] STDERR: $stderr" }
            return $false
        }
    }
}
