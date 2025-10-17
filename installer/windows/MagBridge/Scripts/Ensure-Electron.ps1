param(
    [switch]$Force
)

$ElectronPackage = "electron"
$ElectronVersion = "34.0.1"

# --- Utilities -------------------------------------------------------------
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
        return ($pkg -match $ElectronVersion)
    }
    catch { return $false }
}

# --- Main installation logic ----------------------------------------------
function Install-Electron {
    Write-Output "Starting installation of $ElectronPackage $ElectronVersion"

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
        $psi.RedirectStandardError  = $true
        $psi.UseShellExecute = $false
        $psi.CreateNoWindow = $true

        $proc = [System.Diagnostics.Process]::Start($psi)
        $stdout = $proc.StandardOutput.ReadToEnd()
        $stderr = $proc.StandardError.ReadToEnd()
        $proc.WaitForExit()

        # Filter noise
        $filtered = $stdout -split "`r?`n" | Where-Object {
            $_ -and ($_ -notmatch "reboot") -and ($_ -notmatch "compare") -and ($_ -notmatch "validation")
        }
        foreach ($line in $filtered) { Write-Output $line }

        # Expose exit code to caller for messaging
        $script:ElectronExitCode = $proc.ExitCode

        switch ($proc.ExitCode) {
            0    { Write-Output "$ElectronPackage $ElectronVersion installed successfully."; return $true }
            1641 { Write-Warning "$ElectronPackage installed (reboot required, ignored).";  return $true }
            3010 { Write-Warning "$ElectronPackage installed (pending reboot suppressed)."; return $true }
            default {
                if ($stderr) { Write-Output "STDERR: $stderr" }
                return $false
            }
        }
    }
    catch {
        $script:ElectronExitCode = -1
        Write-Output ("Exception during installation: {0}" -f $_.Exception.Message)
        return $false
    }
}

# --- Entry -----------------------------------------------------------------
Write-Output "=== Electron Ensure Script (Target: $ElectronPackage $ElectronVersion) ==="
Write-Output "Checking prerequisites for $ElectronPackage..."

if (-not (Test-Chocolatey)) {
    Write-Error "Chocolatey not installed or not found in PATH."
    exit 1
}

Write-Output "Chocolatey detected."

$isInstalled = Test-ElectronInstalled

if ($isInstalled -and -not $Force) {
    Write-Output "$ElectronPackage $ElectronVersion already installed. Skipping."
    exit 0
}

if ($isInstalled -and $Force) {
    Write-Warning "Force reinstallation requested for $ElectronPackage."
}

$start   = Get-Date
$success = Install-Electron
$duration = (Get-Date) - $start

if ($success) {
    Write-Output ("$ElectronPackage $ElectronVersion installed successfully in {0:N1}s" -f $duration.TotalSeconds)
    exit 0
}
else {
    $code = if ($script:ElectronExitCode) { $script:ElectronExitCode } else { 1 }
    Write-Error ("Script failed after {0:N1}s (Exit code {1})" -f $duration.TotalSeconds, $code)
    exit 1
}
