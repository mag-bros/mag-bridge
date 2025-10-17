# ====================================================================
# _Logging.ps1 — shared logging helpers for MagBridge install scripts
# Compatible with Windows PowerShell 5.1 and PowerShell 7+
# ====================================================================

try {
    if ($PSScriptRoot) {
        $script:ScriptRoot = $PSScriptRoot
    } elseif ($MyInvocation.MyCommand.Path) {
        $script:ScriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
    } else {
        $script:ScriptRoot = (Get-Location).Path
    }
} catch {
    Write-Warning "Failed to resolve ScriptRoot: $($_.Exception.Message)"
    $script:ScriptRoot = (Get-Location).Path
}

# --- Log Level / Color configuration ---------------------------------
if ($env:MAGBRIDGE_LOG_LEVEL) {
    $global:MAGBRIDGE_LOG_LEVEL = $env:MAGBRIDGE_LOG_LEVEL.ToUpperInvariant()
} else {
    $global:MAGBRIDGE_LOG_LEVEL = 'INFO'
}

$global:NO_COLOR = [bool]$env:NO_COLOR


$global:NO_COLOR = [bool]$env:NO_COLOR

function Write-LogLine {
    param (
        [string]$Level,
        [string]$Message,
        [ConsoleColor]$Color = 'Gray'
    )

    $src = $env:MAGBRIDGE_LOG_SOURCE
    if (-not $src) { $src = 'Generic' }

    $line = "$Message"
    if ($global:NO_COLOR) {
        Write-Host $line
    } else {
        Write-Host $line -ForegroundColor $Color
    }
}

function Log-Info { param([string]$msg)
    if ($global:MAGBRIDGE_LOG_LEVEL -in @('INFO', 'DEBUG')) {
        Write-LogLine 'INFO' $msg 'Gray'
    }
}
function Log-Warn { param([string]$msg)
    if ($global:MAGBRIDGE_LOG_LEVEL -in @('WARN', 'INFO', 'DEBUG')) {
        Write-LogLine 'WARN' $msg 'Yellow'
    }
}
function Log-Error { param([string]$msg)
    Write-LogLine 'ERR' $msg 'Red'
}
function Log-Ok { param([string]$msg)
    Write-LogLine 'OK' $msg 'Green'
}
