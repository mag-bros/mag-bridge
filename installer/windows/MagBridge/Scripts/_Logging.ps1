# ====================================================================
# _Logging.ps1 — minimal cross-version logger (Windows 7 compatible)
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
