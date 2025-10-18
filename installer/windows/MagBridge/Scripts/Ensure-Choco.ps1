# ====================================================================
# Ensure-Choco.ps1 — ensure Chocolatey is installed and operational
# _Helpers.ps1 must be sourced upstream (providing Invoke-Choco, Compare-Version, etc.)
# ====================================================================

param(
    [string]$PackageKey = "chocolatey",
    [string]$PreferredVersion = "2.5.1",
    [string]$MinimumRequiredVersion = ""
)

$ErrorActionPreference = 'Stop'
$PackageName = 'choco'

try {
    Write-Host "[INFO] Checking for package: $PackageKey..."
    $cmd = Get-Command $PackageName -ErrorAction SilentlyContinue

    # 1️⃣ If not found at all, bootstrap Chocolatey itself
    if (-not $cmd) {
        Write-Host "[WARN] $PackageKey not found. Starting installation bootstrap..."

        $installScript = Join-Path $env:TEMP "install_${PackageKey}.ps1"
        try {
            Invoke-WebRequest -Uri "https://community.chocolatey.org/install.ps1" `
                -OutFile $installScript -UseBasicParsing
            Write-Host "[VER] Downloaded installer script to $installScript"

            Set-ExecutionPolicy Bypass -Scope Process -Force
            & powershell -NoProfile -ExecutionPolicy Bypass -File $installScript |
            ForEach-Object { Write-Host "[INFO] $_" }

            Remove-Item $installScript -Force -ErrorAction SilentlyContinue
        }
        catch {
            Write-Host "[ERR] Failed to install ${PackageKey}: $($_.Exception.Message)"
            exit 1
        }

        $cmd = Get-Command choco -ErrorAction SilentlyContinue
        if (-not $cmd) {
            Write-Host "[ERR] $PackageKey installation failed; executable not found."
            exit 1
        }

        Write-Host "[OK] $PackageKey installed successfully at $($cmd.Source)"
    }

    # 2️⃣ Detect installed version via Chocolatey list
    $userVersion = Get-ChocoVersion $PackageKey
    if ($userVersion) {
        Write-Host "[VER] Detected installed version: $userVersion"
    }
    else {
        Write-Host "[INFO] No installed version detected for $PackageKey."
    }

    # 3️⃣ Version logic
    if ($userVersion -and $MinimumRequiredVersion -and (Compare-Version $userVersion $MinimumRequiredVersion) -lt 0) {
        Write-Host "[ERR] Installed version $userVersion is older than minimum required $MinimumRequiredVersion."
        Write-Host "[ERR] Manual user approval required before upgrade. Exiting with code 10."
        exit 10
    }

    if ($userVersion -and $MinimumRequiredVersion -and (Compare-Version $userVersion $MinimumRequiredVersion) -ge 0) {
        Write-Host "[OK] Installed version $userVersion meets minimum required $MinimumRequiredVersion."
        exit 0
    }

    # 4️⃣ Installation attempts (fresh install or upgrade)
    $attempts = @()

    if (-not $userVersion) {
        $attempts += @{ Ver = $PreferredVersion; Force = $false }
        $attempts += @{ Ver = $PreferredVersion; Force = $true }
    }
    else {
        $attempts += @{ Ver = $MinimumRequiredVersion; Force = $false }
        $attempts += @{ Ver = $MinimumRequiredVersion; Force = $true }
    }

    foreach ($a in $attempts) {
        $ver = $a.Ver
        if (-not $ver) { continue }

        Write-Host "[INFO] Attempting installation of $PackageKey version $ver (Force=$($a.Force))..."
        $args = @('install', $PackageKey, '--version', $ver, '-y', '--use-enhanced-exit-codes')
        if ($a.Force) { $args += '--force' }

        $res = Invoke-Choco $args

        if ($res.ExitCode -eq 0 -or $res.ExitCode -eq 3010) {
            Write-Host "[OK] $PackageKey $ver installed successfully."
            break
        }
        else {
            Write-Host "[WARN] Installation of $PackageKey $ver failed (exit $($res.ExitCode))."
            if ($res.StdErr) { Write-Host "[ERR] STDERR: $($res.StdErr.Trim())" }
        }
    }

    # 5️⃣ Verification
    Write-Host "[INFO] Verifying $PackageKey installation..."
    Start-Sleep -Seconds 2
    $finalVersion = Get-ChocoVersion $PackageKey

    if ($finalVersion) {
        Write-Host "[OK] Verified $PackageKey installation — version $finalVersion"
        exit 0
    }
    else {
        Write-Host "[ERR] Verification failed — $PackageKey not found after installation."
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
