# ====================================================================
# ScriptTemplate.ps1 — Shared base class and helper functions
# for all "Ensure-*" installation scripts.
# Provides standardized logging, configuration, and task flow.
# ====================================================================

class ScriptTemplate {
    [string]$PackageKey
    [string]$PackageName
    [string]$PreferredVersion
    [string]$MinimumRequiredVersion
    [string]$InstallPath
    [string]$InstallSource
    [string]$InstallerCommand
    [ScriptBlock]$BootstrapAction
    [ScriptBlock]$VerifyAction
    [ScriptBlock]$PostInstallAction

    ScriptTemplate(
        [string]$pkgKey,
        [string]$pkgName,
        [string]$prefVer,
        [string]$minVer,
        [string]$path,
        [string]$src,
        [string]$cmd
    ) {
        $this.PackageKey = if ($pkgKey) { $pkgKey } else { "UnknownPackage" }
        $this.PackageName = if ($pkgName) { $pkgName } else { "unknown" }
        $this.PreferredVersion = if ($prefVer) { $prefVer } else { "latest" }
        $this.MinimumRequiredVersion = if ($minVer) { $minVer } else { "0.0.0" }
        $this.InstallPath = if ($path) { $path } else { "C:\ProgramData\DefaultPath" }
        $this.InstallSource = if ($src) { $src } else { "https://example.org" }
        $this.InstallerCommand = if ($cmd) { $cmd } else { "choco" }
    }

    [void] Log([string]$Level, [string]$Message) {
        Write-Host "[$Level] $Message"
    }

    [void] Info([string]$msg) { $this.Log("INFO", $msg) }
    [void] Ok([string]$msg) { $this.Log("OK", $msg) }
    [void] Warn([string]$msg) { $this.Log("WARN", $msg) }
    [void] Err([string]$msg) { $this.Log("ERR", $msg) }
    [void] Ver([string]$msg) { $this.Log("VER", $msg) }

    [void] RunBootstrap() {
        if ($null -ne $this.BootstrapAction) {
            $this.Ver("Executing bootstrap for {$this.PackageKey}...")
            & $this.BootstrapAction
        }
    }

    [void] RunVerify() {
        if ($null -ne $this.VerifyAction) {
            $this.Ver("Verifying {$this.PackageKey} installation...")
            & $this.VerifyAction
        }
    }

    [void] RunPostInstall() {
        if ($null -ne $this.PostInstallAction) {
            $this.Ver("Running post-install tasks for {$this.PackageKey}...")
            & $this.PostInstallAction
        }
    }
}

# ====================================================================
# Common install logic — shared for all Ensure-* scripts
# ====================================================================

function Invoke-Ensure {
    param([ScriptTemplate]$Config)

    $ErrorActionPreference = 'Stop'
    $pkg = $Config.PackageKey
    $verPref = $Config.PreferredVersion
    $verMin = $Config.MinimumRequiredVersion

    $Config.Ver("Checking system for existing {$pkg}...")
    $userVersion = Get-ChocoVersion $Config.PackageName -Silent

    if ($userVersion) {
        $Config.Ver("Detected {$pkg} version {$userVersion}")
    }
    else {
        $Config.Info("{$pkg} not detected on this system.")
    }

    # Minimum check
    if ($userVersion -and $verMin -and (Compare-Version $userVersion $verMin) -lt 0) {
        $Config.Err("Installed version {$userVersion} is older than minimum required {$verMin}.")
        $Config.Info("Manual approval required before upgrading {$pkg}.")
        exit 10
    }

    if ($userVersion -and $verMin -and (Compare-Version $userVersion $verMin) -ge 0) {
        if ($verMin -eq '0.0.0') {
            $Config.Info("Installed version {$userVersion}; minimum requirement not specified or not important.")
        }
        else {
            $Config.Ok("Installed version {$userVersion} meets minimum requirement ({$verMin}).")
        }
        exit 0
    }

    # --- install attempt loop ---
    $attempts = @()
    if (-not $userVersion) {
        $attempts += @{ Ver = $verPref; Force = $false }
        $attempts += @{ Ver = $verPref; Force = $true }
    }
    elseif ($verMin) {
        $attempts += @{ Ver = $verMin; Force = $false }
        $attempts += @{ Ver = $verMin; Force = $true }
    }

    foreach ($a in $attempts) {
        $v = $a.Ver
        if (-not $v) { continue }
        $Config.Ver("Ensuring package state for {$pkg} (v{$v}, Force={$($a.Force)})...")
        $args = @('install', $Config.PackageName, '--version', $v, '-y', '--use-enhanced-exit-codes')
        if ($a.Force) { $args += '--force' }

        $res = Invoke-Choco $args
        if ($res.ExitCode -eq 0 -or $res.ExitCode -eq 3010) {
            $Config.Ok("{$pkg} v{$v} installed successfully.")
            break
        }
        else {
            $Config.Warn("Installation of {$pkg} v{$v} failed (exit {$($res.ExitCode)}).")
            if ($res.StdErr) { $Config.Ver("STDERR: {$($res.StdErr.Trim())}") }
        }
    }

    # Verification phase
    $Config.RunVerify()
    $Config.Ok("{$pkg} process completed.")

    if ($LASTEXITCODE -ne 0) {
        exit $LASTEXITCODE
    }
}
