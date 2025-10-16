if ([Threading.Thread]::CurrentThread.ApartmentState -ne 'STA') {
    Write-Host "Re-launching in STA..."
    $self = $PSCommandPath
    Start-Process powershell.exe -Verb RunAs -ArgumentList @('-NoProfile', '-ExecutionPolicy', 'Bypass', '-STA', '-File', "`"$self`"")
    exit 0
}

# --- Determine script root ---------------------------------------------------
try {
    if ($MyInvocation.MyCommand.Path) {
        $candidate = Split-Path -Parent $MyInvocation.MyCommand.Path
    } elseif ([System.Diagnostics.Process]::GetCurrentProcess().MainModule.FileName) {
        $candidate = Split-Path -Parent ([System.Diagnostics.Process]::GetCurrentProcess().MainModule.FileName)
    } elseif (Get-Location) {
        $candidate = (Get-Location).Path
    } elseif ($PSScriptRoot) {
        $candidate = $PSScriptRoot
    } else {
        throw "Unable to determine script root — all fallbacks failed."
    }

    # Normalize and assign globally
    $script:ScriptRoot = (Resolve-Path -Path $candidate).Path
    Write-Host "📂 ScriptRoot resolved to: $script:ScriptRoot"
} catch {
    Write-Warning "Failed to resolve ScriptRoot: $($_.Exception.Message)"
    $script:ScriptRoot = (Get-Location).Path
}


$script:InstallerScript = Join-Path $script:ScriptRoot 'install.ps1'

# --- UtilsDir Quick Path Verification  ----------------------------------------
$UtilsDir = Join-Path $script:ScriptRoot 'utils'
$checkPath = Join-Path $UtilsDir 'auth.ps1'
if (-not (Test-Path $checkPath)) {
    Write-Host "Invalid ScriptRoot — missing admin_check.ps1 in $UtilsDir"
    throw "Invalid ScriptRoot — missing admin_check.ps1 in $UtilsDir"
}

# --- Import Scripts -----------------------------------------------------
. (Join-Path $UtilsDir 'auth.ps1')
. (Join-Path $UtilsDir 'license.ps1')
. (Join-Path $UtilsDir 'helpers.ps1')
. (Join-Path $UtilsDir 'logging.ps1')
. (Join-Path $UtilsDir 'welcome.ps1')
. (Join-Path $UtilsDir 'progress.ps1')
. (Join-Path $UtilsDir 'runspace.ps1')
. (Join-Path $UtilsDir 'goodbye.ps1')
. (Join-Path $UtilsDir 'choco.ps1')
. (Join-Path $UtilsDir 'makegnu.ps1')

# 🧩 --- Entry Point: Start-MagBridgeInstaller ---------------------------
# Main controller for the MagBridge GNU Make installer.
# Initializes environment, runs installation steps, and shows summary.
# Example:
#   Start-MagBridgeInstaller

try {

    Write-Host "Starting MagBridge Installer..."
    Authorize-Environment
    Check-UIAvailable
    Show-WelcomeDialog
    # --- License agreement step --------------------------------------------------
    $accepted = Show-LicenseDialog -OwnerForm $script:InstallerState.Ui.Form
    if (-not $accepted) { return }

    # bring the progress form back
    Reactivate-ProgressUI

    Advance-Step "Preparing installation..."

    # --- Compute steps based on user choices -------------------------------------
    $selectedSteps = @()
    if ($Global:InstallOptions.Chocolatey) { $selectedSteps += 'Chocolatey' }
    if ($Global:InstallOptions.Make) { $selectedSteps += 'GnuMake' }

    # --- Shared Installer State -------------------------------------
    $script:InstallerState = [PSCustomObject]@{
        StepsTotal  = [Math]::Max(1, $selectedSteps.Count)
        StepCurrent = 0
        Ui          = $null
    }

    # --- Progress UI -------------------------------------------------------------
    $script:InstallerState.ProgressForm = New-ProgressForm -Title "MagBridge Dependencies Installer" -Max $script:InstallerState.StepsTotal

    if ($script:UIAvailable -and $script:InstallerState.ProgressForm.Form) {
        $script:InstallerState.ProgressForm.Form.Show()
        [System.Windows.Forms.Application]::DoEvents()
    }

    try {
        # --- Step 1: Chocolatey --------------------------------------------------
        if ($Global:InstallOptions.Chocolatey) {
            Advance-Step "Ensuring Chocolatey..." -Action { Ensure-Choco } -Background -DelayMs 888

            if ($script:ChocoAvailable) {
                Write-LogOk "Chocolatey available."
            } else {
                Write-LogFail "Chocolatey not found or installation failed. Dependent steps will be skipped."
            }
        }

        # --- Step 2: GNU Make ----------------------------------------------------
        if ($Global:InstallOptions.Make) {
            if ($script:ChocoAvailable) {
                Advance-Step "Ensuring GNU Make..." -Action { Ensure-GnuMake -AdvanceStep } -Background -DelayMs 888

                if ($script:GnuMakeAvailable) {
                    Write-LogOk "GNU Make is available."
                } else {
                    Write-LogFail "GNU Make installation or verification failed."
                }
            } else {
                Advance-Step "Skipping GNU Make (Chocolatey unavailable)..." -DelayMs 888
                Write-LogWarn "Skipped GNU Make because Chocolatey was not installed."
            }
        }

        # --- Step 3: Update PATH -------------------------------------------------
        Advance-Step "Updating PATH..." -Action { Ensure-Path } -DelayMs 888

        # --- Step 4: Final summary ----------------------------------------------
        Advance-Step "Finalizing installation..." -DelayMs 888
        if ($script:ChocoAvailable) {
            Write-LogInfo "Chocolatey: available."
        } else {
            Write-LogWarn "Chocolatey: not installed or unavailable."
        }

        if ($script:GnuMakeAvailable) {
            Write-LogInfo "GNU Make: available."
        } else {
            Write-LogWarn "GNU Make: not installed or unavailable."
        }
    } catch {
        Write-LogFail "Fatal installer error: $($_.Exception.Message)"
    } finally {
        # --- Always close progress form before showing goodbye ------------------
        Close-ProgressForm $script:InstallerState.ProgressForm
    }

    # --- Goodbye summary --------------------------------------------------------
    Show-GoodbyeDialog
    Write-Host "✅ Installer finished."

} catch {
    Write-Host "Fatal error: $($_.Exception.Message)"
    exit 1
}
