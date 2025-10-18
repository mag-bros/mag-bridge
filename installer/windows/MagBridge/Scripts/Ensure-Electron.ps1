# ====================================================================
# Ensure-Electron.ps1 — ensure Electron is installed and operational
# ====================================================================

param(
    [string]$PreferredVersion = "latest"
)

$ErrorActionPreference = 'Stop'

$PackageName  = 'electron'
$DisplayName  = 'Electron'

# --- Import Chocolatey bootstrap (and Invoke-Choco) -------------------
. "$PSScriptRoot\Ensure-Choco.ps1"

# --- Helper ------------------------------------------------------------
function Get-InstalledElectronVersion {
    $libPath = Join-Path $env:ProgramData 'chocolatey\lib'
    if (-not (Test-Path $libPath)) { return $null }

    $pkgDir = Get-ChildItem -Path $libPath -Directory -Filter "$PackageName*" -ErrorAction SilentlyContinue | Select-Object -First 1
    if (-not $pkgDir) { return $null }

    $nuspec = Get-ChildItem -Path $pkgDir.FullName -Recurse -Filter "$PackageName.nuspec" -ErrorAction SilentlyContinue | Select-Object -First 1
    if ($nuspec) {
        $xml = [xml](Get-Content $nuspec.FullName)
        return $xml.package.metadata.version
    }
    return $null
}

function Clean-PackageState {
    param([string]$Pkg)
    Write-Host "[INFO] Cleaning residual files for $Pkg..."
    try { & choco uninstall $Pkg -y --force | Out-Null }
    catch { Write-Host "[WARN] Uninstall command failed or package missing." }

    try {
        Remove-Item -Recurse -Force "$env:ProgramData\chocolatey\lib\$Pkg*" -ErrorAction SilentlyContinue
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

    # --- Detect existing Electron --------------------------------------
    $installedVer = Get-InstalledElectronVersion
    if ($installedVer) {
        Write-Host "[VER] Detected existing ${DisplayName} version $installedVer"
    }

    if ($installedVer -eq $PreferredVersion) {
        Write-Host "[OK] ${DisplayName} $PreferredVersion already installed. Skipping."
        exit 0
    } elseif (-not $installedVer) {
        Write-Host "[INFO] ${DisplayName} not found or outdated — installation required."
    } else {
        Write-Host "[WARN] Existing ${DisplayName} version differs — reinstalling."
    }

    # --- First install attempt (quiet) ---------------------------------
    Write-Host "[INFO] Beginning installation of ${DisplayName} $PreferredVersion..."
    $result = Invoke-Choco @('install', $PackageName, '--version', $PreferredVersion, '-y', '--use-enhanced-exit-codes')

    if ($result.ExitCode -eq 0 -or $result.ExitCode -eq 3010) {
        Write-Host "[OK] ${DisplayName} installed successfully."
    } else {
        Write-Host "[WARN] First install failed (exit $($result.ExitCode)). Attempting full cleanup and reinstall."

        Clean-PackageState -Pkg $PackageName
        Start-Sleep -Seconds 2

        $retry = Invoke-Choco @('install', $PackageName, '--version', $PreferredVersion, '-y', '-dv', '--force', '--use-enhanced-exit-codes')
        if ($retry.ExitCode -eq 0 -or $retry.ExitCode -eq 3010) {
            Write-Host "[OK] Reinstall succeeded after cleanup."
        } else {
            Write-Host "[ERR] Reinstall failed again (exit $($retry.ExitCode))."
            if ($retry.StdErr) { Write-Host "[ERR] STDERR: $($retry.StdErr.Trim())" }
            exit 3
        }
    }

    # --- Verification -------------------------------------------------
    Write-Host "[INFO] Verifying $DisplayName installation..."
    Start-Sleep -Seconds 2

    $verifiedVer = Get-InstalledElectronVersion
    $installDir  = Join-Path $env:ProgramData "chocolatey\lib\$PackageName.$PreferredVersion\tools"

    if ($verifiedVer -eq $PreferredVersion -or (Test-Path $installDir)) {
        Write-Host "[OK] Verified installation of ${DisplayName} $PreferredVersion"
        Write-Host "[OK] ${DisplayName} is ready."
        exit 0
    } else {
        Write-Host "[WARN] Verification failed — version mismatch or path missing."
        Write-Host ("[VER] Expected: {0}  |  Found: {1}" -f $PreferredVersion, (if ($verifiedVer) { $verifiedVer } else { 'none' }))
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
