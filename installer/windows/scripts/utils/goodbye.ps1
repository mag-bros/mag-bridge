# 👋 --- Show-GoodbyeForm -----------------------------------------------------
# Displays installation summary; optional restart; GUI + console modes.
function Show-GoodbyeForm {
    param([object]$Ui = $script:InstallerState.Ui)

    $summary = ($report -join "`n")
    $goodbyeText = @"
MagBridge Project — Installation Complete 🎉

$summary

Installation finished successfully.
You can now use 'make' in new PowerShell or CMD sessions.

A restart is recommended so PATH updates take effect.
Would you like to restart now?
"@

    if ($script:UIAvailable) {
        try {
            Add-Type -AssemblyName PresentationFramework -ErrorAction Stop
            $res = [System.Windows.MessageBox]::Show(
                $goodbyeText,
                "GNU Make Installer — Summary",
                [System.Windows.MessageBoxButton]::YesNo,
                [System.Windows.MessageBoxImage]::Information
            )
            if ($res -eq [System.Windows.MessageBoxResult]::Yes) {
                Write-Host "🔄 Restarting system..."
                shutdown.exe /r /t 5 /c "Rebooting to complete GNU Make installation."
            } else {
                Write-Host "ℹ️  Please restart your computer later."
            }
        } catch {
            Write-LogWarn "GUI summary failed; switching to console mode."
            $script:UIAvailable = $false
        }
    }

    if (-not $script:UIAvailable) {
        Write-Host ""
        Write-Host "========================================================"
        Write-Host " MagBridge Project — Installation Complete 🎉"
        Write-Host "--------------------------------------------------------"
        Write-Host ($report -join "`n")
        Write-Host ""
        Write-Host "You can now use 'make' in new shells."
        Write-Host "A system restart is recommended."
        Write-Host "========================================================"

        if (-not ($env:CI -or $env:GITHUB_ACTIONS)) {
            $resp = Read-Host "Restart now? (Y/N)"
            if ($resp -match '^[Yy]') {
                Write-Host "🔄 Restarting system..."
                shutdown.exe /r /t 5 /c "Rebooting to complete GNU Make installation."
            } else {
                Write-Host "ℹ️  Please restart your computer later."
            }
        } else {
            Write-LogInfo "CI environment detected — skipping reboot."
        }
    }

    exit 0
}
