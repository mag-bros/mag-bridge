# ====================================================================
# Ensure-GnuMake.ps1 — ensure GNU Make is installed and operational
# ====================================================================

$ErrorActionPreference = 'Stop'

# --- Main logic ------------------------------------------------------
$env:MAGBRIDGE_LOG_SOURCE = 'GnuMake'
$PackageName = 'make'
$DisplayName = 'GNU Make'

function Resolve-MakePath {
    $cmd = Get-Command make.exe -ErrorAction SilentlyContinue
    if ($cmd) { return $cmd.Source }

    $cinst = Join-Path $env:ProgramData 'chocolatey'
    $cbin  = Join-Path $cinst 'bin\make.exe'
    if (Test-Path $cbin) { return $cbin }

    $lib = Join-Path $cinst 'lib'
    if (Test-Path $lib) {
        $cand = Get-ChildItem -Path $lib -Recurse -Filter make.exe -ErrorAction SilentlyContinue | Select-Object -First 1
        if ($cand) { return $cand.FullName }
    }
    return $null
}

try {
    Log "[INFO] Checking prerequisites"

    $choco = Get-Command choco -ErrorAction SilentlyContinue
    if (-not $choco) {
        Log "[WARN] Chocolatey not found; invoking Ensure-Choco.ps1"
        $ensureChoco = Join-Path $script:ScriptRoot 'Ensure-Choco.ps1'
        if (-not (Test-Path $ensureChoco)) {
            Log "[ERR] Ensure-Choco.ps1 not found at $ensureChoco"
            exit 1
        }

        & powershell -NoProfile -ExecutionPolicy Bypass -File $ensureChoco
        if ($LASTEXITCODE -ne 0) {
            Log "[ERR] Ensure-Choco.ps1 failed with exit code $LASTEXITCODE"
            exit 1
        }

        $choco = Get-Command choco -ErrorAction SilentlyContinue
        if (-not $choco) {
            Log "[ERR] Chocolatey still not available after Ensure-Choco.ps1"
            exit 1
        }
    }
    else {
        Log "[INFO] Chocolatey detected at $($choco.Source)"
    }

    # --- Detection ---
    $existing = Resolve-MakePath
    if ($existing) {
        try {
            $verOut = & "$existing" --version 2>$null
            if ($LASTEXITCODE -eq 0 -and $verOut) {
                $line = ($verOut -split "`r?`n")[0]
                Log "[OK] Detected existing installation: $line"
                exit 0
            }
        }
        catch {
            Log "[WARN] make.exe present but version check failed: $($_.Exception.Message)"
        }
        Log "[WARN] $DisplayName present but unhealthy; will reinstall."
    }
    else {
        Log "[WARN] $DisplayName not found; beginning installation."
    }

    # --- Install/repair ---
    $args = @(
        'install', $PackageName,
        '--yes', '--no-progress',
        '--ignore-detected-reboot',
        '--exit-when-reboot-detected=false',
        '--requirechecksum=false'
    )

    $psi = New-Object System.Diagnostics.ProcessStartInfo
    $psi.FileName = (Get-Command choco).Source
    $psi.Arguments = ($args -join ' ')
    $psi.RedirectStandardOutput = $true
    $psi.RedirectStandardError = $true
    $psi.UseShellExecute = $false
    $psi.CreateNoWindow = $true

    Log "[INFO] Executing: choco $($psi.Arguments)"
    $proc = [System.Diagnostics.Process]::Start($psi)
    if (-not $proc) {
        Log "[ERR] Failed to start Chocolatey process — executable not found or permission issue."
        exit 1
    }

    $stdout = $proc.StandardOutput.ReadToEnd()
    $stderr = $proc.StandardError.ReadToEnd()
    $proc.WaitForExit()

    $filtered = $stdout -split "`r?`n" | Where-Object { $_ -and ($_ -notmatch 'reboot|compare|validation') }
    foreach ($line in $filtered) {
        if ($line -match '(?i)already installed') { Log "[WARN] $line" }
        elseif ($line -match '(?i)installed successfully|The install of') { Log "[OK] $line" }
        elseif ($line -match '(?i)failed|error|not found') { Log "[ERR] $line" }
        else { Log "[INFO] $line" }
    }

    switch ($proc.ExitCode) {
        0     { Log "[OK] $DisplayName installed successfully via Chocolatey."; $installed = $true }
        1641  { Log "[WARN] $DisplayName installed; reboot requested (suppressed)."; $installed = $true }
        3010  { Log "[WARN] $DisplayName installed; pending reboot ignored."; $installed = $true }
        default {
            Log "[ERR] Chocolatey returned exit code $($proc.ExitCode). STDERR: $stderr"
            $installed = $false
        }
    }

    if (-not $installed) {
        Log "[ERR] $DisplayName installation failed."
        exit 3
    }

    # --- Verify ---
    $resolved = Resolve-MakePath
    if ($resolved) {
        $out = & "$resolved" --version 2>$null
        if ($LASTEXITCODE -eq 0 -and $out) {
            $first = ($out -split "`r?`n")[0]
            Log "[OK] Verified installation: $first"
            Log "[OK] $DisplayName is ready."
            exit 0
        }
        else {
            Log "[WARN] Version check failed after install."
            exit 2
        }
    }
    else {
        Log "[WARN] $DisplayName appears installed but PATH not refreshed."
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
