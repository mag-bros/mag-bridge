# ====================================================================
# Ensure-Choco.ps1 — ensure Chocolatey is installed and operational
# ====================================================================

$ErrorActionPreference = 'Stop'

# --- Helper -------------------------------------------------------------
function Invoke-Choco {
    param([string[]]$ChocoArgs)

    $cmd = Get-Command choco -ErrorAction SilentlyContinue
    if (-not $cmd) {
        Write-Host "[ERR] Cannot invoke Chocolatey: not found."
        return [PSCustomObject]@{ ExitCode = 1; StdOut = ''; StdErr = 'choco not found' }
    }

    $psi = New-Object System.Diagnostics.ProcessStartInfo
    $psi.FileName = $cmd.Source
    $psi.Arguments = ($ChocoArgs -join ' ')
    $psi.RedirectStandardOutput = $true
    $psi.RedirectStandardError  = $true
    $psi.UseShellExecute = $false
    $psi.CreateNoWindow = $true

    Write-Host "[INFO] Executing: choco $($psi.Arguments)"

    $proc = [System.Diagnostics.Process]::Start($psi)
    $stdout = $proc.StandardOutput.ReadToEnd()
    $stderr = $proc.StandardError.ReadToEnd()
    $proc.WaitForExit()
    Write-Host "[VER] choco exited with code $($proc.ExitCode)"

    foreach ($line in ($stdout -split "`r?`n")) {
        if ($line -match '(?i)(error|fail|not found|exception)') { Write-Host "[ERR] $line" }
        elseif ($line -match '(?i)(success|installed|completed|ok)') { Write-Host "[OK] $line" }
        elseif ($line) { Write-Host "[INFO] $line" }
    }

    [PSCustomObject]@{
        ExitCode = $proc.ExitCode
        StdOut   = $stdout
        StdErr   = $stderr
    }
}

# --- Main ---------------------------------------------------------------
try {
    Write-Host "[INFO] Checking for Chocolatey..."
    $choco = Get-Command choco -ErrorAction SilentlyContinue

    if (-not $choco) {
        Write-Host "[WARN] Chocolatey not found. Starting installation..."

        $installScript = Join-Path $env:TEMP "install_choco.ps1"
        Invoke-WebRequest -Uri "https://community.chocolatey.org/install.ps1" -OutFile $installScript -UseBasicParsing
        Write-Host "[VER] Downloaded installer script to $installScript"

        Set-ExecutionPolicy Bypass -Scope Process -Force
        try {
            & powershell -NoProfile -ExecutionPolicy Bypass -File $installScript | ForEach-Object { Write-Host "[INFO] $_" }
        } catch {
            Write-Host "[ERR] Chocolatey install script failed: $($_.Exception.Message)"
            exit 1
        }

        Remove-Item $installScript -Force -ErrorAction SilentlyContinue
        $choco = Get-Command choco -ErrorAction SilentlyContinue
        if (-not $choco) {
            Write-Host "[ERR] Chocolatey installation failed; choco.exe not found."
            exit 1
        }
        Write-Host "[OK] Chocolatey installed at $($choco.Source)"
    } else {
        Write-Host "[OK] Chocolatey found at $($choco.Source)"
    }

    # Verify Chocolatey works
    $ver = & choco -v 2>$null
    if ($LASTEXITCODE -ne 0 -or -not $ver) {
        Write-Host "[ERR] Chocolatey executable present but version check failed."
        exit 2
    }

    Write-Host "[OK] Chocolatey operational — version $ver"

    # Optional: ensure default source exists
    $sources = & choco source list --limit-output
    if ($sources -notmatch 'community\.chocolatey\.org') {
        Write-Host "[WARN] Default source missing — restoring..."
        & choco source add -n=chocolatey -s="https://community.chocolatey.org/api/v2/" --priority=1 --allow-self-service | Out-Null
        Write-Host "[OK] Source restored."
    }

    Write-Host "[OK] Chocolatey is ready."
    exit 0
}
catch {
    Write-Host "[ERR] Unexpected error: $($_.Exception.Message)"
    exit 3
}
finally {
    $ErrorActionPreference = 'Continue'
}
