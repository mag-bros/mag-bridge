# Add new installer feature

'''
installer/
 ├─ windows/
 │   ├─ install.ps1          # entrypoint (calls steps)
 │   ├─ ui_helpers.ps1       # New-ProgressForm, Update-ProgressForm, etc.
 │   ├─ logging.ps1          # Write-LogInfo, Write-LogOk, etc.
 │   ├─ choco.ps1            # Ensure-Choco
 │   ├─ make.ps1             # Ensure-GnuMake
 │   ├─ env.ps1              # Ensure-Path, Update-EnvironmentPath
 │   ├─ runspace.ps1         #  The Main Loop
 │   ├─ TODO::IMPROVE_UX.ps1         # 🔥 NEW: background async executor
 │   └─ utils.ps1
'''

