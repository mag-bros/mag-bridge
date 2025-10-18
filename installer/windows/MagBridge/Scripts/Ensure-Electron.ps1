# ====================================================================
# Ensure-Electron.ps1 — ensure Electron is installed and operational
# _Helpers.ps1 must be sourced upstream (providing Invoke-Choco, Compare-Version, etc.)
# ====================================================================

param(
    [string]$PreferredVersion = "34.0.1",
    [string]$PackageKey = "Electron",
    [string]$MinimumRequiredVersion = ""
)

$ErrorActionPreference = 'Stop'
$PackageName = 'electron'
$chocoPath = 'C:\ProgramData\chocolatey'

# --- MAIN -----------------------------------------------------------
try {
    Write-Host "[VER] Checking system for existing {PackageKey} installation..."
    $userVersion = Get-ChocoVersion $PackageName -Silent

    if ($userVersion) {
        Write-Host "[VER] Detected existing {PackageKey} version: {userVersion}"
    }
    else {
        Write-Host "[INFO] {PackageKey} not detected on this system."
    }

    # 1️⃣ Too old version?
    if ($userVersion -and $MinimumRequiredVersion) {
        $cmp = Compare-Version $userVersion $MinimumRequiredVersion
        if ($cmp -lt 0) {
            Write-Host "[ERR] Installed version {userVersion} is older than minimum required {MinimumRequiredVersion}."
            Write-Host "[INFO] Manual approval required before upgrading {PackageKey} to {MinimumRequiredVersion}."
            exit 10
        }
    }

    # 2️⃣ Already meets minimum required version
    if ($userVersion -and $MinimumRequiredVersion -and (Compare-Version $userVersion $MinimumRequiredVersion) -ge 0) {
        Write-Host "[OK] Installed version {userVersion} meets minimum requirement ({MinimumRequiredVersion})."
        exit 0
    }

    # 3️⃣ Installation or upgrade attempts
    $attempts = @()
    if (-not $userVersion) {
        # Fresh install — use preferred version
        $attempts += @{ Ver = $PreferredVersion; Force = $false }
        $attempts += @{ Ver = $PreferredVersion; Force = $true }
    }
    else {
        # Too old or missing minimum — use minimum required
        $attempts += @{ Ver = $MinimumRequiredVersion; Force = $false }
        $attempts += @{ Ver = $MinimumRequiredVersion; Force = $true }
    }

    foreach ($a in $attempts) {
        $ver = $a.Ver
        if (-not $ver) { continue } # skip if version is empty

        Write-Host "[VER] Ensuring package state for {PackageKey} (v{ver}, Force={($a.Force)})..."
        $args = @('install', $PackageName, '--version', $ver, '-y', '--use-enhanced-exit-codes')
        if ($a.Force) { $args += '--force' }

        $res = Invoke-Choco $args
        if ($res.ExitCode -eq 0 -or $res.ExitCode -eq 3010) {
            Write-Host "[OK] {PackageKey} v{ver} installed successfully."
            break
        }
        else {
            Write-Host "[WARN] Installation of {PackageKey} v{ver} failed (exit {($res.ExitCode)})."
            if ($res.StdErr) { Write-Host "[VER] STDERR: {($res.StdErr.Trim())}" }
        }
    }   

    # 4️⃣ Verify installation result
    Write-Host "[INFO] Verifying {PackageKey} installation..."
    Start-Sleep -Seconds 2
    $finalVer = Get-ChocoVersion $PackageName -Silent

    if (-not $finalVer) {
        Write-Host "[ERR] Verification failed — {PackageKey} not found after installation."
        exit 3
    }

    if ((Compare-Version $finalVer $PreferredVersion) -ge 0) {
        Write-Host "[OK] {PackageKey} verified — version {finalVer} (meets preferred {PreferredVersion})."
        exit 0
    }

    if ($MinimumRequiredVersion -and (Compare-Version $finalVer $MinimumRequiredVersion) -ge 0) {
        Write-Host "[OK] {PackageKey} meets minimum requirement ({finalVer} ≥ {MinimumRequiredVersion})."
        exit 0
    }

    Write-Host "[ERR] Installation completed but version {finalVer} is below requirement ({PreferredVersion})."
    exit 2
}
catch {
    Write-Host "[ERR] Unexpected error in Ensure-Electron.ps1: {($_.Exception.Message)}"
    exit 9
}
finally {
    $ErrorActionPreference = 'Continue'
}

if ($LASTEXITCODE -ne 0) {
    exit $LASTEXITCODE
}
