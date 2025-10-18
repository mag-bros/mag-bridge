# ====================================================================
# Ensure-GnuMake.ps1 — ensure GNU Make is installed and operational
# Dependencies: _HostLogging.ps1 (dot-sourced by host)
# ====================================================================

$ErrorActionPreference = 'Stop'
$env:MAGBRIDGE_LOG_SOURCE = 'GnuMake'

$PackageName  = 'make'
$DisplayName  = 'GNU Make'
$script:GnuMakeExitCode = 0

# --- Helper -------------------------------------------------------------
function Resolve-MakePath {
    $cmd = Get-Command make.exe -ErrorAction SilentlyContinue
    if ($cmd) { return $cmd.Source }

    $libPath = Join-Path $env:ProgramData 'chocolatey\lib'
    if (Test-Path $libPath) {
        $cand = Get-ChildItem -Path $libPath -Recurse -Filter make.exe -ErrorAction SilentlyContinue | Select-Object -First 1
        if ($cand) { return $cand.FullName }
    }
    return $null
}

function Invoke-Choco {
    param([string[]]$Args)

    $psi = New-Object System.Diagnostics.ProcessStartInfo
    $psi.FileName = (Get-Command choco).Source
    $psi.Arguments = ($Args -join ' ')
    $psi.RedirectStandardOutput = $true
    $psi.RedirectStandardError  = $true
    $psi.UseShellExecute = $false
    $psi.CreateNoWindow = $true

    Log "[INFO] Executing: choco $($psi.Arguments)"

    $proc = [System.Diagnostics.Process]::Start($psi)
    $stdout = $proc.StandardOutput.ReadToEnd()
    $stderr = $proc.StandardError.ReadToEnd()
    $proc.WaitForExit()

    # Stream log output
    foreach ($line in ($stdout -split "`r?`n")) {
        if ($line -match 'error|fail|not found') { Log "[ERR] $line" }
        elseif ($line -match 'install|success')  { Log "[OK] $line" }
        elseif ($line)                           { Log "[INFO] $line" }
    }

    [PSCustomObject]@{
        ExitCode = $proc.ExitCode
        StdOut   = $stdout
        StdErr   = $stderr
    }
}

function Clean-PackageState {
    param([string]$Pkg)
    Log "[INFO] Cleaning residual files for $Pkg..."
    try {
        & choco uninstall $Pkg -y --force | Out-Null
    } catch {
        Log "[WARN] Uninstall command failed or package missing."
    }

    try {
        Remove-Item -Recurse -Force "$env:ProgramData\chocolatey\lib\$Pkg" -ErrorAction SilentlyContinue
        Remove-Item -Recurse -Force "$env:ProgramData\chocolatey\.chocolatey\$Pkg*" -ErrorAction SilentlyContinue
    } catch {
        Log "[WARN] Cleanup error: $($_.Exception.Message)"
    }
}

# --- Main ---------------------------------------------------------------
try {
    Log "[INFO] Checking for Chocolatey..."
    $choco = Get-Command choco -ErrorAction SilentlyContinue
    if (-not $choco) {
        Log "[ERR] Chocolatey not found in PATH."
        exit 1
    }
    Log "[OK] Chocolatey found at $($choco.Source)"

    $makePath = Resolve-MakePath
    if ($makePath) {
        try {
            $ver = & "$makePath" --version 2>$null
            if ($LASTEXITCODE -eq 0 -and $ver) {
                Log "[OK] Detected $DisplayName: $($ver.Split('`n')[0])"
                exit 0
            }
        } catch {
            Log "[WARN] Detected $DisplayName but version check failed — reinstalling."
        }
    } else {
        Log "[WARN] $DisplayName not found — starting installation."
    }

    # --- First install attempt ---
    $result = Invoke-Choco @('install', $PackageName, '-y', '--no-progress')
    if ($result.ExitCode -eq 0) {
        Log "[OK] $DisplayName installed successfully."
    } else {
        Log "[WARN] First install failed (exit $($result.ExitCode)). Attempting full cleanup and reinstall."

        Clean-PackageState -Pkg $PackageName
        Start-Sleep -Seconds 2

        $retry = Invoke-Choco @('install', $PackageName, '-y', '--no-progress', '--force')
        if ($retry.ExitCode -eq 0) {
            Log "[OK] Reinstall succeeded after cleanup."
        } else {
            Log "[ERR] Reinstall failed again (exit $($retry.ExitCode))."
            if ($retry.StdErr) { Log "[ERR] STDERR: $($retry.StdErr.Trim())" }
            exit 3
        }
    }

    # --- Verification ---
    $resolved = Resolve-MakePath
    if ($resolved) {
        $verOut = & "$resolved" --version 2>$null
        if ($LASTEXITCODE -eq 0 -and $verOut) {
            Log "[OK] Verified installation: $($verOut.Split('`n')[0])"
            Log "[OK] $DisplayName is ready."
            exit 0
        } else {
            Log "[WARN] Version check failed post-install."
            exit 2
        }
    } else {
        Log "[WARN] make.exe not located after install (PATH not refreshed)."
        exit 2
    }
}
catch {
    Log "[ERR] Unexpected error: $($_.Exception.Message)"
    exit 3
}
finally {
    $ErrorActionPreference = 'Continue'
}
