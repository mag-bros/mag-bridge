# ====================================================================
# Ensure-Choco.ps1 — ensures a package (e.g., Chocolatey) is installed and operational
# Helpers.ps1 must be sourced upstream (providing Invoke-Choco, Compare-Version, etc.)
# ====================================================================

param(
    [string]$PackageKey,                # e.g. "chocolatey"
    [string]$PreferredVersion = "2.5.1",
    [string]$MinimumRequiredVersion = ""
)

$ErrorActionPreference = 'Stop'

try {
    Write-Host "[INFO] Checking for package: $PackageKey..."
    $cmd = Get-Command $PackageKey -ErrorAction SilentlyContinue

    # ---------------------------------------------------------------
    # 🧩 1. Installation missing → bootstrap (special case: Chocolatey)
    # ---------------------------------------------------------------
    if (-not $cmd -and $PackageKey -eq 'choco') {
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
    elseif (-not $cmd) {
        Write-Host "[WARN] Command '$PackageKey' not found in PATH — checking Chocolatey..."
    }
    else {
        Write-Host "[OK] Found command '$PackageKey' at $($cmd.Source)"
    }

    # ---------------------------------------------------------------
    # 🧩 2. Detect installed version
    # ---------------------------------------------------------------
    $userVersion = (& choco list --local-only --limit-output | `
        Where-Object { $_ -match "^$PackageKey\s" } | `
        ForEach-Object { ($_ -split '\s+')[1] }) 2>$null

    if ($userVersion) {
        Write-Host "[VER] Detected installed version: $userVersion"
    }
    else {
        Write-Host "[INFO] No installed version detected for $PackageKey."
    }

    # ---------------------------------------------------------------
    # 🧩 3. Version checks
    # ---------------------------------------------------------------
    if ($userVersion -and $MinimumRequiredVersion -and (Compare-Version $userVersion $MinimumRequiredVersion) -lt 0) {
        Write-Host "[ERR] Installed version $userVersion is older than minimum required $MinimumRequiredVersion."
        Write-Host "[ERR] User approval required before upgrade. Exiting with code 10."
        exit 10
    }

    if ($userVersion -and (Compare-Version $userVersion $PreferredVersion) -ge 0) {
        Write-Host "[OK] Installed version $userVersion meets or exceeds preferred $PreferredVersion."
        exit 0
    }

    # ---------------------------------------------------------------
    # 🧩 4. Installation or upgrade attempts
    # ---------------------------------------------------------------
    $attempts = @(
        @{ Ver = $PreferredVersion; Force = $false },
        @{ Ver = $PreferredVersion; Force = $true },
        @{ Ver = $MinimumRequiredVersion; Force = $false },
        @{ Ver = $MinimumRequiredVersion; Force = $true }
    )

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

    # ---------------------------------------------------------------
    # 🧩 5. Verification
    # ---------------------------------------------------------------
    $finalVersion = (& choco list --local-only --limit-output | `
        Where-Object { $_ -match "^$PackageKey\s" } | `
        ForEach-Object { ($_ -split '\s+')[1] }) 2>$null

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
    Write-Host "[ERR] Failed to install ${PackageKey}: $($_.Exception.Message)"
    exit 9
}
finally {
    $ErrorActionPreference = 'Continue'
}
