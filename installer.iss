[Setup]
; AppNameはインストーラーとプログラム追加と削除に表示される名前です
AppName=SD Forge Queue Manager
AppVersion=1.0
AppPublisher=Solodev
DefaultDirName={autopf}\SDForgeQueueManager
DefaultGroupName=SDForgeQueueManager
; アンインストール時にアイコンを削除するための設定
UninstallDisplayIcon={app}\SDForgeQueueManager.exe
Compression=lzma2
SolidCompression=yes
; 出力先のディレクトリ
OutputDir=dist
OutputBaseFilename=SDForgeQueueManager_Setup
; 管理者権限を要求する場合（Program Filesにインストールする場合に必要）
PrivilegesRequired=admin

[Languages]
Name: "japanese"; MessagesFile: "compiler:Languages\Japanese.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
; ビルドしたexeファイルを指定
Source: "e:\program_files\solodev\auto_stable\dist\SDForgeQueueManager.exe"; DestDir: "{app}"; Flags: ignoreversion
; 必要に応じて設定ファイルのサンプルなども同梱可能
Source: "e:\program_files\solodev\auto_stable\config.example.json"; DestDir: "{app}"; Flags: ignoreversion
Source: "e:\program_files\solodev\auto_stable\presets.example.json"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\SD Forge Queue Manager"; Filename: "{app}\SDForgeQueueManager.exe"
Name: "{commondesktop}\SD Forge Queue Manager"; Filename: "{app}\SDForgeQueueManager.exe"; Tasks: desktopicon

[Run]
; インストール完了後に起動するオプション
Filename: "{app}\SDForgeQueueManager.exe"; Description: "{cm:LaunchProgram,SD Forge Queue Manager}"; Flags: nowait postinstall skipifsilent
