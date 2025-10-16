# 🔒 --- Authorize-Environment -----------------------------------------------------------
# Automatically relaunches the main installer script with elevation.

function Authorize-Environment {
    $principal = [Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()
    $isAdmin = $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

    if ($isAdmin) {
        Write-Host "🔐 Running with Administrator privileges."
        return $true
    }

    Write-Host "⚙️  Elevation required — requesting Administrator rights..."

    $shellExe = if ($PSVersionTable.PSEdition -eq 'Core') { 'pwsh.exe' } else { 'powershell.exe' }
    $scriptPath = if ($script:InstallerScript) { $script:InstallerScript } else { $MyInvocation.MyCommand.Definition }
    $workingDir = (Split-Path -Parent $scriptPath)

    $args = @('-NoLogo', '-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', "`"$scriptPath`"", '-Elevated')

    try {
        Start-Process -FilePath $shellExe `
            -ArgumentList $args `
            -Verb RunAs `
            -WorkingDirectory $workingDir `
            -WindowStyle Normal | Out-Null
        Write-Host "🔁 Relaunched as Administrator."
    } catch {
        Write-Host "❌ Failed to elevate privileges: $($_.Exception.Message)"
        return $false
    }

    Start-Sleep -Milliseconds 300
    exit
}
