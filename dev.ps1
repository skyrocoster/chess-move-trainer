param(
    [ValidateSet("backend", "frontend", "all")]
    [string]$Mode = "all"
)
$ErrorActionPreference = "Stop"
& .\.venv\Scripts\python.exe scripts\dev.py $Mode
exit $LASTEXITCODE
