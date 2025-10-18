# ====================================================================
# Ensure-Electron.ps1 — ensure Electron is installed and operational
# Dependencies: _Logging.ps1 (auto-loaded)
# ====================================================================

param([switch]$Force)

$ErrorActionPreference = 'Stop'
$env:MAGBRIDGE_LOG_SOURCE = 'Electron'

$ElectronPackage = 'electron'
$ElectronVersion = '34.0.1'

try {
    Log "[INFO] Checking prerequisites for $ElectronPackage..."

    # --- Verify Chocolatey presence ----------------------------------------
    try {
        $chocoCmd = Get-Command choco -ErrorAction SilentlyContinue
        if (-not $chocoCmd) {
            Log "[ERR] Chocolatey not installed or not found in PATH."
            exit 1
        }
        Log "[OK] Chocolatey detected at $($chocoCmd.Source)"
    }
    catch {
        Log "[ERR] Failed to check Chocolatey presence: $($_.Exception.Message)"
        exit 1
    }

    # --- Determine existing installation -----------------------------------
    try {
        $pkgList = choco list --local-only | Where-Object { $_ -match "^$ElectronPackage\s+" }
        $isInstalled = $pkgList -match $ElectronVersion

        if ($isInstalled -and -not $Force) {
            Log "[OK] $ElectronPackage $ElectronVersion already installed. Skipping."
            exit 0
        }

        if ($isInstalled -and $Force) {
            Log "[WARN] Force reinstallation requested for $ElectronPackage."
        }

        if (-not $isInstalled) {
            Log "[INFO] $ElectronPackage not found or outdated — installation required."
        }
    }
    catch {
        Log "[WARN] Failed to determine existing installation: $($_.Exception.Message)"
    }

    # --- Installation (delegated to shared helper) --------------------------
    Log "[INFO] Beginning installation of $ElectronPackage $ElectronVersion..."
    $success = Invoke-ChocoInstall -Package $ElectronPackage -Version $ElectronVersion -Force:$Force

    if (-not $success) {
        Log "[ERR] $ElectronPackage installation failed or incomplete."
        exit 3
    }

    # --- Verification -------------------------------------------------------
    try {
        $pkgList = choco list --local-only | Where-Object { $_ -match "^$ElectronPackage\s+" }
        $confirmed = $pkgList -match $ElectronVersion
        if ($confirmed) {
            Log "[VER] Verified installation of $ElectronPackage $ElectronVersion"
            Log "[OK] $ElectronPackage is ready."
            exit 0
        } else {
            Log "[WARN] Verification failed — version not found in local package list."
            exit 2
        }
    }
    catch {
        Log "[WARN] Verification failed: $($_.Exception.Message)"
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
