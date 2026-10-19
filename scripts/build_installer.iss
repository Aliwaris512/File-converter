[Setup]
AppName=LocalFile Converter
AppVersion=1.0.0
DefaultDirName={userpf}\LocalFile Converter
DefaultGroupName=LocalFile Converter
OutputBaseFilename=LocalFileConverterSetup
Compression=lzma
SolidCompression=yes
PrivilegesRequired=none

[Files]
Source: "..\dist\LocalFileConverter\*"; DestDir: "{app}"; Flags: recursesubdirs createallsubdirs

[Icons]
Name: "{group}\LocalFile Converter"; Filename: "{app}\LocalFileConverter.exe"

[Run]
Filename: "{app}\LocalFileConverter.exe"; Parameters: "--install-context-menu"; Flags: runhidden waituntilterminated
Filename: "{app}\LocalFileConverter.exe"; Description: "Launch LocalFile Converter"; Flags: nowait postinstall

[UninstallRun]
Filename: "{app}\LocalFileConverter.exe"; Parameters: "--uninstall-context-menu"; Flags: runhidden waituntilterminated
