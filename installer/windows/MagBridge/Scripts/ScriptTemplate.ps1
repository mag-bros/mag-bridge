# ====================================================================
# ScriptTemplate.ps1 — Shared base class and helper functions
#   - Provides standardized logging, configuration, and task flow.
# All Ensure-* scripts share the same life cycle:
# 1. check 
# 2. install
# 3. verify
# 4. done
# ====================================================================

class ScriptTemplate {
    [string]$PackageKey
    [string]$PackageName
    [string]$PreferredVersion
    [string]$MinimumRequiredVersion
    [string]$InstallPath
    [string]$InstallSource
    [string]$Command
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
        $this.Command = if ($cmd) { $cmd } else { "choco" }
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
    param([ScriptTemplate]$Template)

    $ErrorActionPreference = 'Stop'
    $pkg = $Template.PackageKey
    $verPref = $Template.PreferredVersion
    $verMin = $Template.MinimumRequiredVersion

    $Template.Ver("Checking system for existing {$pkg}...")
    $userVersion = Get-ChocoVersion $Template.PackageName -Silent

    if ($userVersion) {
        $Template.Ver("Detected {$pkg} version {$userVersion}")
    }
    else {
        $Template.Info("{$pkg} not detected on this system.")
    }

    # Minimum check
    if ($userVersion -and $verMin -and (Compare-Version $userVersion $verMin) -lt 0) {
        $Template.Err("Installed version {$userVersion} is older than minimum required {$verMin}.")
        $Template.Info("Manual approval required before upgrading {$pkg}.")
        exit 10
    }

    if ($userVersion -and $verMin -and (Compare-Version $userVersion $verMin) -ge 0) {
        if ($verMin -eq '0.0.0') {
            $Template.Info("Installed version {$userVersion}; minimum requirement not specified or not important.")
        }
        else {
            $Template.Ok("Installed version {$userVersion} meets minimum requirement ({$verMin}).")
        }
        exit 0
    }

    # --- install attempt loop ---
    $scenarios = @()
    if (-not $userVersion) {
        $scenarios += @{ Ver = $verPref; Force = $false }
        $scenarios += @{ Ver = $verPref; Force = $true }
    }
    elseif ($verMin) {
        $scenarios += @{ Ver = $verMin; Force = $false }
        $scenarios += @{ Ver = $verMin; Force = $true }
    }

    foreach ($scenario in $scenarios) {
        $v = $scenario.Ver
        if (-not $v) { continue }
        $Template.Ver("Ensuring package state for {$pkg} (v{$v}, Force={$($scenario.Force)})...")
        $params = @('install', $Template.PackageName, '--version', $v, '-y', '--use-enhanced-exit-codes')
        if ($scenario.Force) { $params += '--force' }

        $res = Invoke-Choco $params
        if ($res.ExitCode -eq 0 -or $res.ExitCode -eq 3010) {
            $Template.Ok("{$pkg} v{$v} installed successfully.")
            break
        }
        else {
            $Template.Warn("Installation of {$pkg} v{$v} failed (exit {$($res.ExitCode)}).")
            if ($res.StdErr) { $Template.Ver("STDERR: {$($res.StdErr.Trim())}") }
        }
    }

    # Verification phase
    $Template.RunVerify()
    $Template.Ok("{$pkg} process completed.")

    # Forward the last non-zero exit code so the caller detects failure
    if ($LASTEXITCODE -and $LASTEXITCODE -ne 0) {
        exit $LASTEXITCODE
    }
}
