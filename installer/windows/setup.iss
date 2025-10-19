; ============================================================
; MagBridge Installer Script - Inno Setup (with dynamic paths)
; ============================================================
#define ROOT_DIR "{src}"
#define BUILD_DIR "{#ROOT_DIR}/build"
#define INSTALL_SRC "{#ROOT_DIR}/scripts/install.ps1"
#define UNINSTALL_SRC "{#ROOT_DIR}/scripts/uninstall.ps1"
#define APP_CONFIG "{#ROOT_DIR}/configs/sdk-installer.json"
#define APP_LICENSE "{#ROOT_DIR}/licenses/sdk-license.txt"
#define APP_ICON "{#ROOT_DIR}/assets/sdk.ico"
#define TITLE "MagBridge Dependencies Installer"

[Setup]
AppName={#TITLE}
AppVersion=1.0.0
DefaultDirName={pf}\MagBridge
DefaultGroupName=MagBridge
OutputDir={#BUILD_DIR}
OutputBaseFilename=MagBridge_Installer
Compression=lzma
SolidCompression=yes
WizardStyle=modern
DisableProgramGroupPage=yes
DisableReadyPage=yes

; =======================
; Application Files
; =======================
[Files]
Source: "{#ROOT_DIR}/MagBridge/bin/Debug/net8.0-windows/MagBridge.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "{#INSTALL_SRC}"; DestDir: "{app}\scripts"; Flags: ignoreversion
Source: "{#UNINSTALL_SRC}"; DestDir: "{app}\scripts"; Flags: ignoreversion
Source: "{#APP_CONFIG}"; DestDir: "{app}\configs"; Flags: ignoreversion
Source: "{#APP_LICENSE}"; DestDir: "{app}\licenses"; Flags: ignoreversion
Source: "{#APP_ICON}"; DestDir: "{app}\assets"; Flags: ignoreversion

; =======================
; Registry Keys (Optional)
; =======================
[Registry]
Root: HKCU; Subkey: "Software\MagBridge"; ValueType: string; ValueName: "InstallLocation"; ValueData: "{app}"

; =======================
; Shortcuts
; =======================
[Icons]
Name: "{group}\MagBridge"; Filename: "{app}\MagBridge.exe"
Name: "{group}\Uninstall MagBridge"; Filename: "{app}\uninstall.exe"

; =======================
; Run PowerShell Scripts after installation
; =======================
[Run]
Filename: "powershell.exe"; Parameters: "-ExecutionPolicy Bypass -File ""{app}\scripts\install.ps1"""; StatusMsg: "Running installation script..."; Flags: runhidden

; =======================
; Uninstaller Section
; =======================
[UninstallDelete]
Type: filesandordirs; Name: "{app}\scripts"
Type: filesandordirs; Name: "{app}\configs"
Type: filesandordirs; Name: "{app}\licenses"
Type: filesandordirs; Name: "{app}\assets"

[UninstallRun]
Filename: "powershell.exe"; Parameters: "-ExecutionPolicy Bypass -File ""{app}\scripts\uninstall.ps1"""; StatusMsg: "Running uninstallation script..."; Flags: runhidden

[Code]
function GetRootDir: String;
begin
  Result := ExpandConstant('{src}');
end;

function GetBuildDir: String;
begin
  Result := ExpandConstant('{src}\build');
end;
