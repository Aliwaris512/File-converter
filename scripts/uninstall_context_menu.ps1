$projectDir = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$venvPython = Join-Path $projectDir ".venv\Scripts\python.exe"

if (-not (Test-Path $venvPython)) {
    throw "Project virtual environment not found: $venvPython. Run this script with the project's installed Python environment."
}

& $venvPython (Join-Path $projectDir "scripts\uninstall_context_menu.py")
if ($LASTEXITCODE -ne 0) {
    throw "Context-menu removal failed with exit code $LASTEXITCODE."
}
