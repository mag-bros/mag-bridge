# ====================================================================
# Ensure-Electron.ps1 — ensure Electron is installed and operational
# ====================================================================

param([switch]$Force)

$ErrorActionPreference = 'Stop'
$env:MAGBRIDGE_LOG_SOURCE = 'Electron'

$PackageName  = 'electron'
$DisplayName  = 'Electron'
$RequiredVersion = '34.0.1'

# --- Import Chocolatey bootstrap (and Invoke-Choco) -------------------
. "$PSScriptRoot\Ensure-Choco.ps1"

# --- Helper ------------------------------------------------------------
function Get-InstalledElectronVersion {
    $libPath = Join-Path $env:ProgramData 'chocolatey\lib'
    if (-not (Test-Path $libPath)) { return $null }

    # Look for folder matching 'electron*'
    $pkgDir = Get-ChildItem -Path $libPath -Directory -Filter "$PackageName*" -ErrorAction SilentlyContinue | Select-Object -First 1
    if (-not $pkgDir) { return $null }

    # Look for .nuspec file and read <version> tag
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

    if ($installedVer -eq $RequiredVersion -and -not $Force) {
        Write-Host "[OK] ${DisplayName} $RequiredVersion already installed. Skipping."
        exit 0
    }
    elseif ($Force -and $installedVer) {
        Write-Host "[WARN] Force reinstall requested for ${DisplayName}."
    }
    elseif (-not $installedVer) {
        Write-Host "[INFO] ${DisplayName} not found or outdated — installation required."
    }

    # --- First install attempt (quiet) ---------------------------------
    Write-Host "[INFO] Beginning installation of ${DisplayName} $RequiredVersion..."
    $result = Invoke-Choco @('install', $PackageName, '--version', $RequiredVersion, '-y', '--use-enhanced-exit-codes')

    if ($result.ExitCode -eq 0 -or $result.ExitCode -eq 3010) {
        Write-Host "[OK] ${DisplayName} installed successfully."
    } else {
        Write-Host "[WARN] First install failed (exit $($result.ExitCode)). Attempting full cleanup and reinstall."

        Clean-PackageState -Pkg $PackageName
        Start-Sleep -Seconds 2

        $retry = Invoke-Choco @('install', $PackageName, '--version', $RequiredVersion, '-y', '-dv', '--force', '--use-enhanced-exit-codes')
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
    $installDir  = Join-Path $env:ProgramData "chocolatey\lib\$PackageName.$RequiredVersion\tools"

    if ($verifiedVer -eq $RequiredVersion -or (Test-Path $installDir)) {
        Write-Host "[OK] Verified installation of ${DisplayName} $RequiredVersion"
        Write-Host "[OK] ${DisplayName} is ready."
        exit 0
    } else {
        Write-Host "[WARN] Verification failed — version mismatch or path missing."
        Write-Host ("[VER] Expected: {0}  |  Found: {1}" -f $RequiredVersion, (if ($verifiedVer) { $verifiedVer } else { 'none' }))
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
