# ====================================================================
# Ensure-Choco.ps1 — ensure Chocolatey is installed and operational
# _Helpers.ps1 must be sourced upstream (Invoke-Choco, Compare-Version, Get-ChocoVersion)
# ====================================================================

param(
    [string]$PackageKey = "chocolatey",   # display key from JSON / UI
    [string]$PreferredVersion = "2.5.1",  # used when installing fresh
    [string]$MinimumRequiredVersion = ""  # if set and installed < min -> exit 10 (ask user)
)

$ErrorActionPreference = 'Stop'

# Internals: exe name vs package id
$ChocoExeName = 'choco'
$ChocoPkgId = 'chocolatey'
$chocoPath = 'C:\ProgramData\chocolatey'
$chocoOfficialInstallScript = 'https://community.chocolatey.org/install.ps1'

# -- local helper: run official bootstrap once --------------------------------
function Invoke-ChocoBootstrap {
    param()

    $installScript = Join-Path $env:TEMP "install_${ChocoPkgId}.ps1"
    try {
        # From Chocolatey maintainers
        Invoke-WebRequest -Uri "${chocoOfficialInstallScript}" -OutFile $installScript -UseBasicParsing
        Write-Host "[VER] Downloaded installer script to $installScript"

        Set-ExecutionPolicy Bypass -Scope Process -Force
        & powershell -NoProfile -ExecutionPolicy Bypass -File $installScript | ForEach-Object { Write-Host "[VER] $_" }
    }
    finally {
        Remove-Item $installScript -Force -ErrorAction SilentlyContinue
    }
}

# -- local helper: interpret Chocolatey success codes -------------------------
function Test-ChocoSuccessCode {
    param([int]$Code)
    # 0 OK; 1605/1614 “not installed” benign; 1641/3010 reboot; 350/1604 reboot-detected path if feature enabled
    return @(0, 1605, 1614, 1641, 3010, 350, 1604) -contains $Code
}

try {
    Write-Host "[VER] Checking system for Chocolatey..."
    $cmd = Get-Command $ChocoExeName -ErrorAction SilentlyContinue

    # 1) Not found at all -> run official bootstrap
    if (-not $cmd) {
        Write-Host "[INFO] Chocolatey not found — starting automatic installation..."
        Invoke-ChocoBootstrap

        # Re-check
        $cmd = Get-Command $ChocoExeName -ErrorAction SilentlyContinue
        if (-not $cmd) {
            # Common pitfall: stale dir present, bootstrap refuses to overwrite
            $chocoDir = Join-Path $env:ProgramData 'chocolatey'
            if (Test-Path $chocoDir) {
                Write-Host "[INFO] Chocolatey directory found but executable missing — possible stale install."
                Write-Host "[VER] Stale install dir: $chocoDir"
                $backup = "${chocoDir}_backup_$(Get-Date -Format 'yyyyMMdd_HHmmss')"
                try {
                    Write-Host "[INFO] Preparing retry — renaming old Chocolatey folder..."
                    Rename-Item -Path $chocoDir -NewName $backup -ErrorAction Stop
                    Write-Host "[VER] Renamed stale folder to: $backup"
                }
                catch {
                    Write-Host "[WARN] Could not rename old Chocolatey directory — $($_.Exception.Message)"
                    Write-Host "[INFO] Attempting safe fallback cleanup..."
                    try {
                        # Attempt to release file locks (only affects local PowerShell sessions)
                        Get-Process | Where-Object { $_.Path -like "*chocolatey*" -or $_.Modules.FileName -like "*chocolatey*" } `
                        | ForEach-Object {
                            Write-Host "[VER] Releasing handle from process $($_.ProcessName) (PID: $($_.Id))"
                            Stop-Process -Id $_.Id -Force -ErrorAction SilentlyContinue
                        }

                        # Now fallback: move contents into a timestamped subfolder
                        $backup = "${chocoDir}_partialbackup_$(Get-Date -Format 'yyyyMMdd_HHmmss')"
                        New-Item -ItemType Directory -Path $backup -Force | Out-Null
                        Get-ChildItem -Path $chocoDir -ErrorAction SilentlyContinue | Move-Item -Destination $backup -Force -ErrorAction SilentlyContinue

                        Write-Host "[OK] Moved locked Chocolatey files safely to: $backup"
                    }
                    catch {
                        Write-Host "[ERR] Fallback cleanup failed: $($_.Exception.Message)"
                        Write-Host "[WARN] Manual action required — please remove or rename '${chocoPath}' and retry."
                        exit 2
                    }
                }

                # Retry bootstrap after cleanup
                Write-Host "[INFO] Retrying Chocolatey bootstrap..."
                Invoke-ChocoBootstrap
                $cmd = Get-Command $ChocoExeName -ErrorAction SilentlyContinue
            }
        }

        if (-not $cmd) {
            # Chocolatey bootstrap completed but PATH may not yet be refreshed.
            $chocoBin = Join-Path $env:ProgramData 'chocolatey\bin\choco.exe'
            if (Test-Path $chocoBin) {
                Write-Host "[INFO] Chocolatey executable detected at $chocoBin (PATH not yet updated)."
                $cmd = Get-Command $chocoBin -ErrorAction SilentlyContinue
                if ($cmd) {
                    Write-Host "[OK] Chocolatey installation verified via direct path."
                }
                else {
                    Write-Host "[WARN] Chocolatey installed; shell PATH update pending - restart PowerShell Terminal to activate."
                }
            }
            else {
                Write-Host "[ERR] Chocolatey installation failed; executable not found after cleanup + retry."
                exit 3
            }
        }

        Write-Host "[OK] Chocolatey available at: $($cmd.Source)"
    }
    else {
        Write-Host "[OK] Chocolatey present at: $($cmd.Source)"
        Write-Host "[VER] choco path: $($cmd.Source)"
    }

    # 2) Configure exit-code features for consistent handling later
    try {
        Write-Host "[VER] Enabling Chocolatey exit code features..."
        & choco feature enable -n=usePackageExitCodes  | Out-Null
        & choco feature enable -n=useEnhancedExitCodes | Out-Null
        & choco feature enable -n=exitOnRebootDetected | Out-Null
        Write-Host "[OK] Chocolatey exit code features configured."
    }
    catch {
        Write-Host "[INFO] Optional Chocolatey features skipped — $($_.Exception.Message)"
    }

    # 3) Detect installed version (package id is 'chocolatey')
    $userVersion = Get-ChocoVersion $ChocoPkgId
    if ($userVersion) {
        Write-Host "[INFO] Chocolatey detected."
        Write-Host "[VER] Installed version: $userVersion"
    }
    else {
        Write-Host "[INFO] Chocolatey not yet registered in package list — possibly fresh install."
    }

    # 4) Version policy
    if ($userVersion -and $MinimumRequiredVersion -and (Compare-Version $userVersion $MinimumRequiredVersion) -lt 0) {
        Write-Host "[ERR] Installed version $userVersion is older than minimum required $MinimumRequiredVersion."
        Write-Host "[INFO] Manual approval required before upgrading Chocolatey to $MinimumRequiredVersion."
        exit 10
    }

    # If we have a minimum, and installed meets it -> done
    if ($userVersion -and $MinimumRequiredVersion -and (Compare-Version $userVersion $MinimumRequiredVersion) -ge 0) {
        Write-Host "[OK] Installed version $userVersion meets minimum required $MinimumRequiredVersion."
        exit 0
    }

    # Fresh install case (rare if we reached here) OR explicit upgrade path:
    # Only use choco to manage 'chocolatey' when choco is available (we are here).
    $attempts = @()

    if (-not $userVersion) {
        # fresh install: use preferred
        $attempts += @{ Ver = $PreferredVersion; Force = $false }
        $attempts += @{ Ver = $PreferredVersion; Force = $true }
    }
    elseif ($MinimumRequiredVersion) {
        # optional: bring to minimum if we decide to do automatic upgrades in future
        $attempts += @{ Ver = $MinimumRequiredVersion; Force = $false }
        $attempts += @{ Ver = $MinimumRequiredVersion; Force = $true }
    }

    foreach ($a in $attempts) {
        $ver = $a.Ver
        if (-not $ver) { continue }

        Write-Host "[VER] Ensuring package state (v$ver, Force=$($a.Force))..."
        $args = @('install', $ChocoPkgId, '--version', $ver, '-y', '--use-enhanced-exit-codes')
        if ($a.Force) { $args += '--force' }

        $res = Invoke-Choco $args
        if (Test-ChocoSuccessCode $res.ExitCode) {
            Write-Host "[OK] chocolatey $ver ensured."
            break
        }
        else {
            Write-Host "[WARN] chocolatey ensure attempt failed (exit $($res.ExitCode))."
            if ($res.StdErr) { Write-Host "[VER] STDERR: $($res.StdErr.Trim())" }
        }
    }

    # 5) Final verification
    Write-Host "[INFO] Verifying Chocolatey installation..."
    Start-Sleep -Seconds 1

    $cmd = Get-Command $ChocoExeName -ErrorAction SilentlyContinue
    $finalVersion = Get-ChocoVersion $ChocoPkgId

    if ($finalVersion) {
        Write-Host "[OK] Verified $ChocoPkgId installation — version $finalVersion"

        if ($cmd) {
            Write-Host "[OK] Chocolatey ready. Version $finalVersion"
        }
        else {
            Write-Host "[INFO] PATH not yet refreshed — restart PowerShell to enable choco.exe command."
            Write-Host "[INFO] You can run Chocolatey from: ${chocoPath}\bin\choco.exe"
        }

        exit 0
    }
    else {
        if (-not $cmd) { Write-Host "[INFO] choco.exe not yet registered in PATH (restart may be required)." }
        Write-Host "[ERR] Verification failed — executable missing. Try rerunning or rebooting."
        exit 3
    }
}
catch {
    Write-Host "[ERR] Unexpected error in Ensure-Choco.ps1: $($_.Exception.Message)"
    exit 9
}
finally {
    $ErrorActionPreference = 'Continue'
}

if ($LASTEXITCODE -ne 0) {
    exit $LASTEXITCODE
}
