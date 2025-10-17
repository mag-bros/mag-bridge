# Ensure-GnuMake.ps1
# Ensures GNU Make is installed; installs via Chocolatey if missing.
# Emits structured, timestamped logs compatible with MagBridge PowerShell host.
# No reboot is triggered, and irrelevant Chocolatey chatter is filtered out.

$PackageName = "make"
$DisplayName = "GNU Make"

# --- Header ---------------------------------------------------------------
Write-Host ("=== {0} Ensure Script ===" -f $DisplayName)
Write-Host "Checking prerequisites..."

try {
    $choco = Get-Command choco.exe -ErrorAction Stop
    Write-Host ("Chocolatey detected at {0}" -f $choco.Source)
}
catch {
    Write-Error "Chocolatey not installed — cannot continue."
    exit 1
}

# --- Detection phase ------------------------------------------------------
try {
    $cmd = Get-Command make.exe -ErrorAction SilentlyContinue
    if ($cmd) {
        $ver = (& $cmd.Source --version 2>$null)
        if ($LASTEXITCODE -eq 0 -and $ver) {
            $line = ($ver -split "`r?`n")[0]
            Write-Host ("{0} detected: {1}" -f $DisplayName, $line)
            exit 0
        }
    }
    Write-Warning ("{0} not found — beginning installation." -f $DisplayName)
}
catch {
    Write-Error ("Error while checking existing installation: {0}" -f $_.Exception.Message)
}

# --- Installation phase ---------------------------------------------------
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
    $psi.RedirectStandardError  = $true
    $psi.UseShellExecute = $false
    $psi.CreateNoWindow = $true

    $proc = [System.Diagnostics.Process]::Start($psi)
    $stdout = $proc.StandardOutput.ReadToEnd()
    $stderr = $proc.StandardError.ReadToEnd()
    $proc.WaitForExit()

    # Filter unneeded chatter
    $filtered = $stdout -split "`r?`n" | Where-Object {
        $_ -and ($_ -notmatch "reboot") -and ($_ -notmatch "compare") -and ($_ -notmatch "validation")
    }

    foreach ($line in $filtered) {
        if ($line -match "already installed") {
            Write-Warning $line
        }
        elseif ($line -match "installed successfully") {
            Write-Host $line
        }
        elseif ($line -match "failed") {
            Write-Error $line
        }
        else {
            Write-Host $line
        }
    }

    switch ($proc.ExitCode) {
        0 {
            Write-Host ("{0} installed successfully." -f $DisplayName)
            $success = $true
        }
        1641 {
            Write-Warning ("{0} installed (reboot requested but suppressed)." -f $DisplayName)
            $success = $true
        }
        3010 {
            Write-Warning ("{0} installed (pending reboot ignored)." -f $DisplayName)
            $success = $true
        }
        default {
            Write-Error ("Installation failed. Exit code: {0}" -f $proc.ExitCode)
            if ($stderr) { Write-Error ("STDERR: {0}" -f $stderr) }
            $success = $false
        }
    }
}
catch {
    Write-Error ("Exception during installation: {0}" -f $_.Exception.Message)
    $success = $false
}

# --- Verification phase ---------------------------------------------------
if ($success) {
    $cmd2 = Get-Command make.exe -ErrorAction SilentlyContinue
    if ($cmd2) {
        $ver2 = (& $cmd2.Source --version 2>$null)
        if ($LASTEXITCODE -eq 0 -and $ver2) {
            $line2 = ($ver2 -split "`r?`n")[0]
            Write-Host ("Verified installation: {0}" -f $line2)
            Write-Host ("=== {0} installation completed successfully ===" -f $DisplayName)
            exit 0
        }
    }
    Write-Warning ("{0} installed but verification failed — PATH may require refresh." -f $DisplayName)
    exit 2
}
else {
    Write-Error ("{0} installation failed or incomplete." -f $DisplayName)
    exit 3
}
