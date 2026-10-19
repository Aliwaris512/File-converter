$projectDir = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$venvPython = Join-Path $projectDir ".venv\Scripts\python.exe"

if (-not (Test-Path $venvPython)) {
    throw "Project virtual environment not found: $venvPython. Install dependencies first."
}

& $venvPython (Join-Path $projectDir "scripts\install_context_menu.py")
if ($LASTEXITCODE -ne 0) {
    throw "Context-menu installation failed with exit code $LASTEXITCODE."
}
