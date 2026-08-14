$ErrorActionPreference = "Stop"
& .\.venv\Scripts\python.exe scripts\check_docs.py --check
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
& .\.venv\Scripts\python.exe -m pytest
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
Push-Location frontend
& .\node_modules\.bin\vitest.cmd run
if ($LASTEXITCODE -ne 0) {
    Pop-Location
    exit $LASTEXITCODE
}
Pop-Location
npm run lint --prefix frontend
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
npm run format:check --prefix frontend
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
npm run build --prefix frontend
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
& .\.venv\Scripts\python.exe scripts\check_size.py --source-max 300 --test-max 500
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
& node_modules\.bin\playwright.cmd test --config tests\e2e\playwright.config.ts
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
Write-Host "All local checks passed."
