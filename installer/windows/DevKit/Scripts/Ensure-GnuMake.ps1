# 🧰 Ensure-GnuMake.ps1
# Ensures GNU Make is installed; installs via Chocolatey if missing.
# Emits timestamped, plain text logs for DevKit integration.
# No reboot is triggered, and irrelevant Chocolatey chatter is filtered out.

[CmdletBinding()]
param()

$PackageName = "make"
$DisplayName = "GNU Make"

function Log {
    param([string]$Message)
    $timestamp = (Get-Date).ToString("HH:mm:ss")
    Write-Output ("[{0}] {1}" -f $timestamp, $Message)
}

# --- Prerequisite check ----------------------------------------------------
Log ("=== {0} Ensure Script ===" -f $DisplayName)
Log "Checking prerequisites..."

try {
    $choco = Get-Command choco.exe -ErrorAction Stop
    Log "✅ Chocolatey detected at $($choco.Source)"
}
catch {
    Log "❌ Chocolatey not installed — cannot continue."
    exit 1
}

# --- Detection phase -------------------------------------------------------
try {
    $cmd = Get-Command make.exe -ErrorAction SilentlyContinue
    if ($cmd) {
        $ver = (& $cmd.Source --version 2>$null)
        if ($LASTEXITCODE -eq 0 -and $ver) {
            $line = ($ver -split "`r?`n")[0]
            Log "✅ $DisplayName detected: $line"
            exit 0
        }
    }
    Log "⚙️ $DisplayName not found — beginning installation."
}
catch {
    Log ("❌ Error while checking existing installation: {0}" -f $_.Exception.Message)
}

# --- Installation phase ----------------------------------------------------
try {
    $args = @(
        "install", $PackageName,
        "--yes",
        "--no-progress",
        "--ignore-detected-reboot",
        "--exit-when-reboot-detected=false",
        "--requirechecksum=false"
    )

    $psi = New-Object System.Diagnostics.ProcessStartInfo
    $psi.FileName = "choco"
    $psi.Arguments = ($args -join " ")
    $psi.RedirectStandardOutput = $true
    $psi.RedirectStandardError = $true
    $psi.UseShellExecute = $false
    $psi.CreateNoWindow = $true

    $proc = [System.Diagnostics.Process]::Start($psi)
    $stdout = $proc.StandardOutput.ReadToEnd()
    $stderr = $proc.StandardError.ReadToEnd()
    $proc.WaitForExit()

    # Filter unneeded chatter
    $filtered = $stdout -split "`r?`n" | Where-Object {
        $_ -and ($_ -notmatch "reboot") -and ($_ -notmatch "compare") -and ($_ -notmatch "validations")
    }

    foreach ($line in $filtered) {
        if ($line -match "already installed") {
            Log "ℹ $line"
        }
        elseif ($line -match "installed successfully") {
            Log "✅ $line"
        }
        elseif ($line -match "failed") {
            Log "❌ $line"
        }
        else {
            Log "… $line"
        }
    }

    switch ($proc.ExitCode) {
        0 { Log "✅ $DisplayName installed successfully."; $success = $true }
        1641 { Log "✅ Installed (reboot requested but suppressed)."; $success = $true }
        3010 { Log "✅ Installed (pending reboot ignored)."; $success = $true }
        default {
            Log "❌ Installation failed. Exit code: $($proc.ExitCode)"
            if ($stderr) { Log "STDERR: $stderr" }
            $success = $false
        }
    }
}
catch {
    Log ("❌ Exception during installation: {0}" -f $_.Exception.Message)
    $success = $false
}

# --- Verification phase ----------------------------------------------------
if ($success) {
    $cmd2 = Get-Command make.exe -ErrorAction SilentlyContinue
    if ($cmd2) {
        $ver2 = (& $cmd2.Source --version 2>$null)
        if ($LASTEXITCODE -eq 0 -and $ver2) {
            $line2 = ($ver2 -split "`r?`n")[0]
            Log "✅ Verified installation: $line2"
            Log ("=== {0} installation completed successfully ===" -f $DisplayName)
            exit 0
        }
    }
    Log "⚠️ $DisplayName installed but verification failed — PATH may require refresh."
    exit 2
}
else {
    Log ("❌ {0} installation failed or incomplete." -f $DisplayName)
    exit 3
}
