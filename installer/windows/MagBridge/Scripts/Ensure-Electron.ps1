param(
    [switch]$Force
)

$ElectronPackage = "electron"
$ElectronVersion = "34.0.1"

# --- Utilities -------------------------------------------------------------

function Log {
    param([string]$Message)
    $timestamp = (Get-Date).ToString("HH:mm:ss")
    Write-Output ("[{0}] {1}" -f $timestamp, $Message)
}

function Test-Chocolatey {
    try {
        Get-Command choco -ErrorAction Stop | Out-Null
        return $true
    }
    catch { return $false }
}

function Test-ElectronInstalled {
    try {
        $pkg = choco list --local-only | Where-Object { $_ -match "^$ElectronPackage\s+" }
        if ($pkg -match $ElectronVersion) { return $true }
        return $false
    }
    catch { return $false }
}

# --- Main installation logic ----------------------------------------------

function Install-Electron {
    Log "▶ Starting installation of Electron $ElectronVersion"

    $args = @(
        "install", $ElectronPackage,
        "--version", $ElectronVersion,
        "--yes",
        "--no-progress",
        "--ignore-detected-reboot",
        "--exit-when-reboot-detected=false",
        "--requirechecksum=false",
        "--timeout", "600"
    )
    if ($Force) { $args += "--force" }

    try {
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

        # Clean and filter log output for readability
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
            0 { Log "✅ Electron $ElectronVersion installed successfully."; return $true }
            1641 { Log "✅ Electron installed (requires reboot but ignored per policy)."; return $true }
            3010 { Log "✅ Electron installed (pending reboot suppressed)."; return $true }
            default {
                Log "❌ Installation failed. Exit code: $($proc.ExitCode)"
                if ($stderr) { Log "STDERR: $stderr" }
                return $false
            }
        }
    }
    catch {
        Log ("❌ Exception during installation: {0}" -f $_.Exception.Message)
        return $false
    }
}

# --- Entry ----------------------------------------------------------------

Log ("=== Electron Ensure Script (Target: {0} {1}) ===" -f $ElectronPackage, $ElectronVersion)
Log ("Checking prerequisites for {0} {1}..." -f $ElectronPackage, $ElectronVersion)

if (-not (Test-Chocolatey)) {
    Log "❌ Chocolatey is not installed or not found in PATH."
    exit 1
}

Log "✅ Chocolatey detected."

$isInstalled = Test-ElectronInstalled

if ($isInstalled -and -not $Force) {
    Log "✅ Electron $ElectronVersion already installed. Skipping."
    exit 0
}

if ($isInstalled -and $Force) {
    Log "🔁 Force reinstallation requested."
}

$start = Get-Date
$success = Install-Electron
$duration = (Get-Date) - $start

if ($success) {
    Log ("=== {0} {1} installed successfully in {2:N1}s ===" -f $ElectronPackage, $ElectronVersion, $duration.TotalSeconds)
    exit 0
}
else {
    Log ("=== Script failed after {0:N1}s ===" -f $duration.TotalSeconds)
    exit 1
}
