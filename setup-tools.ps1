$ErrorActionPreference = "Stop"

$python = Join-Path $PSScriptRoot ".venv\Scripts\python.exe"
if (-not (Test-Path -LiteralPath $python -PathType Leaf)) {
    Write-Error "Expected virtual environment interpreter was not found: $python"
    exit 1
}

& $python -m pip install --editable $PSScriptRoot --no-deps
if ($LASTEXITCODE -ne 0) {
    Write-Error "Editable project installation failed with exit code $LASTEXITCODE."
    exit $LASTEXITCODE
}
