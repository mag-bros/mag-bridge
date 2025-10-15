# --- Determine script root ----------------------------------------------
if ($MyInvocation.MyCommand.Path) {
    $ScriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
} else {
    $ScriptRoot = Split-Path -Parent ([System.Diagnostics.Process]::GetCurrentProcess().MainModule.FileName)
}
$UtilsDir = Join-Path $ScriptRoot 'utils'

# --- Quick Path Verification  ----------------------------------------
$checkPath = Join-Path $UtilsDir 'admin_check.ps1'
if (-not (Test-Path $checkPath)) {
    Write-Host "Invalid ScriptRoot — missing admin_check.ps1 in $UtilsDir"
    throw "Invalid ScriptRoot — missing admin_check.ps1 in $UtilsDir"
}

# --- Import Scripts -----------------------------------------------------
. (Join-Path $UtilsDir 'admin_check.ps1')
. (Join-Path $UtilsDir 'logging.ps1')
. (Join-Path $UtilsDir 'helpers.ps1')
. (Join-Path $UtilsDir 'welcome.ps1')
. (Join-Path $UtilsDir 'progress.ps1')
. (Join-Path $UtilsDir 'goodbye.ps1')
. (Join-Path $UtilsDir 'choco.ps1')
. (Join-Path $UtilsDir 'gnu_make.ps1')

# 🧩 --- Entry Point: Start-MagBridgeInstaller ---------------------------
# Main controller for the MagBridge GNU Make installer.
# Initializes environment, runs installation steps, and shows summary.
# Example:
#   Start-MagBridgeInstaller

try {

    Write-Host "Starting MagBridge Installer..."
    Authorize-Environment
    Check-UIAvailable
    Show-WelcomeForm

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
    $script:InstallerState.Ui = New-ProgressForm -Title "MagBridge Dependencies Installer" -Max $script:InstallerState.StepsTotal
    if ($script:UIAvailable -and $script:InstallerState.Ui.Form) {
        $script:InstallerState.Ui.Form.Show()
        Invoke-UiPump
    }

    try {
        # --- Step 1: Chocolatey --------------------------------------------------
        if ($Global:InstallOptions.Chocolatey) {
            Advance-Step "Ensuring Chocolatey..."
            Ensure-Choco
            if ($script:ChocoAvailable) {
                Write-LogOk "Chocolatey available."
            } else {
                Write-LogFail "Chocolatey not found or installation failed. Dependent steps will be skipped."
            }
        }

        # --- Step 2: GNU Make ----------------------------------------------------
        if ($Global:InstallOptions.Make) {
            if ($script:ChocoAvailable) {
                Ensure-GnuMake -AdvanceStep
                if ($script:GnuMakeAvailable) {
                    Write-LogOk "GNU Make is available."
                } else {
                    Write-LogFail "GNU Make installation or verification failed."
                }
            } else {
                Advance-Step "Skipping GNU Make (Chocolatey unavailable)..."
                Write-LogWarn "Skipped GNU Make because Chocolatey was not installed."
            }
        }
    } finally {
        # --- Always close UI to prevent hanging ----------------------------------
        Close-ProgressForm $script:InstallerState.Ui
    }

    # --- Step 3: Update PATH ----------------------------------------------------
    if ($Global:InstallOptions.Chocolatey -or $Global:InstallOptions.Make) {
        Advance-Step "Updating PATH..."
        Ensure-Path
    } else {
        Advance-Step "Skipping PATH update..."
        Write-LogInfo "PATH update skipped (no installable components selected)."
    }

    # --- Step 4: Final summary ---------------------------------------------------
    Advance-Step "Finalizing installation..."

    try {
        # Optional sanity echo (short summary in log only)
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

        Show-GoodbyeForm 
    } catch {
        Write-LogFail "Error during finalization: $($_.Exception.Message)"
    } finally {
        Close-ProgressForm $script:InstallerState.Ui
        Write-Host "✅ Installer finished."
    }


} catch {
    Write-Host "Fatal error: $($_.Exception.Message)"
    exit 1
}
