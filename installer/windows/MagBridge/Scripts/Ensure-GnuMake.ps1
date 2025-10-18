# ====================================================================
# Ensure-GnuMake.ps1 — ensure GNU Make is installed and operational
# ====================================================================

$ErrorActionPreference = 'Stop'

$PackageName  = 'make'
$DisplayName  = 'GNU Make'

# --- Import Chocolatey bootstrap (and Invoke-Choco) -------------------
. "$PSScriptRoot\Ensure-Choco.ps1"

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

function Clean-PackageState {
    param([string]$Pkg)
    Write-Host "[INFO] Cleaning residual files for $Pkg..."
    try { & choco uninstall $Pkg -y --force | Out-Null }
    catch { Write-Host "[WARN] Uninstall command failed or package missing." }

    try {
        Remove-Item -Recurse -Force "$env:ProgramData\chocolatey\lib\$Pkg" -ErrorAction SilentlyContinue
        Remove-Item -Recurse -Force "$env:ProgramData\chocolatey\.chocolatey\$Pkg*" -ErrorAction SilentlyContinue
    } catch {
        Write-Host "[WARN] Cleanup error: $($_.Exception.Message)"
    }
}

# --- Main ---------------------------------------------------------------
try {
    Write-Host "[INFO] Checking for Chocolatey..."
    $choco = Get-Command choco -ErrorAction SilentlyContinue
    if (-not $choco) {
        Write-Host "[ERR] Chocolatey not found even after Ensure-Choco."
        exit 1
    }
    Write-Host "[OK] Chocolatey found at $($choco.Source)"

    # --- Detect existing make.exe --------------------------------------
    $makePath = Resolve-MakePath
    if ($makePath) {
        try {
            $ver = & "$makePath" --version 2>$null
            if ($LASTEXITCODE -eq 0 -and $ver) {
                Write-Host "[OK] Detected ${DisplayName}: $($ver.Split('`n')[0])"
                exit 0
            }
        } catch {
            Write-Host "[WARN] Detected ${DisplayName} but version check failed — reinstalling."
        }
    } else {
        Write-Host "[INFO] ${DisplayName} not found — starting installation."
    }

    # --- First install attempt ----------------------------------------
    $result = Invoke-Choco @('install', $PackageName, '-y')
    if ($result.ExitCode -eq 0 -or $result.ExitCode -eq 3010) {
        Write-Host "[OK] ${DisplayName} installed successfully."
    } else {
        Write-Host "[WARN] First install failed (exit $($result.ExitCode)). Attempting full cleanup and reinstall."

        Clean-PackageState -Pkg $PackageName
        Start-Sleep -Seconds 2

        $retry = Invoke-Choco @('install', $PackageName, '-y', '-dv', '--force', '--use-enhanced-exit-codes')
        if ($retry.ExitCode -eq 0 -or $retry.ExitCode -eq 3010) {
            Write-Host "[OK] Reinstall succeeded after cleanup."
        } else {
            Write-Host "[ERR] Reinstall failed again (exit $($retry.ExitCode))."
            if ($retry.StdErr) { Write-Host "[ERR] STDERR: $($retry.StdErr.Trim())" }
            exit 3
        }
    }

    # --- Verification -------------------------------------------------
    $resolved = Resolve-MakePath
    if ($resolved) {
        $verOut = & "$resolved" --version 2>$null
        if ($LASTEXITCODE -eq 0 -and $verOut) {
            Write-Host "[OK] Verified installation: $($verOut.Split('`n')[0])"
            Write-Host "[OK] ${DisplayName} is ready."
            exit 0
        } else {
            Write-Host "[WARN] Version check failed post-install."
            exit 2
        }
    } else {
        Write-Host "[WARN] make.exe not located after install (PATH not refreshed)."
        exit 2
    }
}
catch {
    Write-Host "[ERR] Unexpected error: $($_.Exception.Message)"
    exit 3
}
finally {
    $ErrorActionPreference = 'Continue'
}
