# ====================================================================
# Emits plain text with semantic [TAG] prefixes for C# to colorize.
# ====================================================================

function Log {
    param([string]$Message)

    # Default tags recognized by the host
    if ($Message -notmatch '^\[(INFO|WARN|ERR|OK|VER)\]') {
        $Message = "[INFO] $Message"
    }

    Write-Output $Message
}

# ====================================================================
# Post-script exit normalization
# This ensures every Ensure-* script exits with a consistent code
# ====================================================================
function Set-HostExitCode {
    param([int]$Code = 0)

    if ((Test-Path variable:LASTEXITCODE) -and ($LASTEXITCODE -ne 0)) {
        $global:LASTEXITCODE = $LASTEXITCODE
    } else {
        $global:LASTEXITCODE = $Code
    }

    exit $global:LASTEXITCODE
}
