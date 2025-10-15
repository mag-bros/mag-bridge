# 🔒 --- Admin check -----------------------------------------------------------
# Ensures the installer runs with Administrator privileges.
# Prompts user to elevate if not already elevated (supports GUI and headless mode).
# Example:
#   Authorize-Environment

function Authorize-Environment {

    $principal = [Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()
    if (-not $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {

        $useConsoleFallback = $false
        $userAccepted = $false

        # --- Try to load GUI library --------------------------------------------
        try {
            # PowerShell 2.0/3.0 on Win7 sometimes doesn't have WPF; try WinForms first
            try {
                Add-Type -AssemblyName System.Windows.Forms -ErrorAction Stop
                $res = [System.Windows.Forms.MessageBox]::Show(
                    "Administrator rights are required to continue.`n`nClick YES to restart this installer with elevated privileges.",
                    "GNU Make Installer",
                    [System.Windows.Forms.MessageBoxButtons]::YesNo,
                    [System.Windows.Forms.MessageBoxIcon]::Question
                )
                $userAccepted = ($res -eq [System.Windows.Forms.DialogResult]::Yes)
            } catch {
                # If WinForms fails, try WPF (PresentationFramework)
                Add-Type -AssemblyName PresentationFramework -ErrorAction Stop
                $res = [System.Windows.MessageBox]::Show(
                    "Administrator rights are required to continue.`n`nClick YES to restart this installer with elevated privileges.",
                    "GNU Make Installer",
                    [System.Windows.MessageBoxButton]::YesNo,
                    [System.Windows.MessageBoxImage]::Question
                )
                $userAccepted = ($res -eq [System.Windows.MessageBoxResult]::Yes)
            }
        } catch {
            # No GUI subsystem available (headless mode, CI/CD, etc.)
            $useConsoleFallback = $true
        }

        # --- Fallback to console prompt -----------------------------------------
        if ($useConsoleFallback) {
            Write-Host ""
            Write-Host "========================================================"
            Write-Host "Administrator rights are required to continue."
            Write-Host "Run this script again as Administrator."
            Write-Host "========================================================"
            Write-Host ""
            $response = Read-Host "Restart automatically with admin rights? (Y/N)"
            if ($response -match '^[Yy]') { $userAccepted = $true }
        }

        # --- Relaunch elevated if confirmed -------------------------------------
        if ($userAccepted) {
            $shellExe = if ($PSVersionTable.PSEdition -eq 'Core') { 'pwsh' } else { 'powershell.exe' }
            $scriptPath = if ($PSCommandPath) { $PSCommandPath } else { $MyInvocation.MyCommand.Definition }
            $args = "-NoLogo -NoProfile -ExecutionPolicy Bypass -File `"$scriptPath`""

            try {
                Start-Process -FilePath $shellExe -ArgumentList $args -Verb RunAs | Out-Null
            } catch {
                Write-Host "❌ Failed to elevate privileges. Please run manually as Administrator."
            }
        }

        exit 0
    }
}
