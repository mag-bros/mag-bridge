function Invoke-BackgroundStep {
    param(
        [Parameter(Mandatory)][scriptblock]$Action,
        [string]$Message = "Running step...",
        [int]$Step,
        [int]$Total
    )

    if (-not $script:UIAvailable) {
        # Console mode: just execute directly
        Write-LogInfo $Message
        & $Action
        return
    }

    # GUI mode with progress form
    Update-ProgressForm -Ui $script:InstallerState.Ui -Step $Step -Total $Total -Message $Message
    [System.Windows.Forms.Application]::DoEvents()

    $rs = [runspacefactory]::CreateRunspace()
    $rs.Open()
    $ps = [powershell]::Create()
    $ps.Runspace = $rs
    $ps.AddScript($Action) | Out-Null

    $handle = $ps.BeginInvoke()

    while (-not $handle.IsCompleted) {
        [System.Windows.Forms.Application]::DoEvents()
        Start-Sleep -Milliseconds 100
    }

    $ps.EndInvoke($handle)
    $ps.Dispose()
    $rs.Close()
    $rs.Dispose()
}


function Reactivate-ProgressUI {
    if ($script:InstallerState?.Ui?.Form -and -not $script:InstallerState.Ui.Form.IsDisposed) {
        $f = $script:InstallerState.Ui.Form
        $f.TopMost = $true
        $f.Show()
        $f.BringToFront()
        $f.Activate()
        $f.Invalidate()
        $f.Update()
        [System.Windows.Forms.Application]::DoEvents()
    }
}

