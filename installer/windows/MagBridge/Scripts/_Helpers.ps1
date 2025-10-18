# ============================================================
# Helper: Compare-Version
# Returns: -1 if v1 < v2, 0 if equal, +1 if v1 > v2
# ============================================================

function Compare-Version {
    param([string]$v1, [string]$v2)

    if ([string]::IsNullOrWhiteSpace($v1) -or [string]::IsNullOrWhiteSpace($v2)) {
        return 0
    }

    $a = $v1.Split('.') | ForEach-Object { [int]$_ }
    $b = $v2.Split('.') | ForEach-Object { [int]$_ }

    for ($i = 0; $i -lt [Math]::Max($a.Count, $b.Count); $i++) {
        $x = if ($i -lt $a.Count) { $a[$i] } else { 0 }
        $y = if ($i -lt $b.Count) { $b[$i] } else { 0 }
        if ($x -lt $y) { return -1 }
        if ($x -gt $y) { return 1 }
    }
    return 0
}

# Reusable Chocolatey command runner
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

# ============================================================
# Helper: Get-ChocoVersion
# Returns installed package version from `choco list --local-only --limit-output`
# Example:
#   Get-ChocoVersion 'electron'  →  34.0.1
#   Get-ChocoVersion 'nonexistent'  →  $null
# ============================================================
function Get-ChocoVersion {
    param(
        [Parameter(Mandatory = $true)]
        [string]$PackageName,

        [switch]$Silent  # optional: suppress output
    )

    try {
        $output = choco list --local-only --limit-output 2>$null
        if (-not $output) { return $null }

        $line = $output | Where-Object { $_ -match ("^" + [Regex]::Escape($PackageName) + "\|") } | Select-Object -First 1
        if (-not $line) { return $null }

        $version = ($line -split '\|')[1].Trim()
        if (-not $Silent) {
            Write-Host "[VER] Detected $PackageName version: $version"
        }
        return $version
    }
    catch {
        if (-not $Silent) {
            Write-Host "[ERR] Failed to get version for ${PackageName}: $($_.Exception.Message)"
        }
        return $null
    }
}
