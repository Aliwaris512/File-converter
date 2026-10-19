$ErrorActionPreference = 'Stop'

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectRoot = Resolve-Path (Join-Path $scriptDir '..')

Set-Location $projectRoot

$python = Join-Path $projectRoot ".venv\Scripts\python.exe"
if (-not (Test-Path $python)) {
    throw "Project virtual environment not found: $python. Install dependencies first."
}

& $python -m PyInstaller --noconfirm --distpath "$projectRoot\dist" --workpath "$projectRoot\build" .\pyinstaller.spec
if ($LASTEXITCODE -ne 0) {
    throw "PyInstaller build failed with exit code $LASTEXITCODE."
}
Write-Host "Executable build complete. Output directory: $projectRoot\dist\LocalFileConverter"
