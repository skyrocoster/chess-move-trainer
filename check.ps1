$ErrorActionPreference = "Stop"

function Invoke-CommandCapture([scriptblock]$block) {
    $tempFile = [System.IO.Path]::GetTempFileName()
    try {
        $ErrorActionPreference = "Continue"
        $global:LASTEXITCODE = 0
        & $block > $tempFile 2>&1
        $exitCode = $LASTEXITCODE
        $output = Get-Content $tempFile -ErrorAction SilentlyContinue
        if (-not $output) { $output = @() }
        return @{ ExitCode = $exitCode; Output = $output }
    } catch {
        $output = Get-Content $tempFile -ErrorAction SilentlyContinue
        if (-not $output) { $output = @() }
        return @{ ExitCode = 1; Output = @($output) + $_.Exception.Message }
    } finally {
        Remove-Item $tempFile -ErrorAction SilentlyContinue
    }
}

function Invoke-Step($name, [scriptblock]$command, [switch]$showSuccess) {
    $result = Invoke-CommandCapture $command
    if ($result.ExitCode -eq 0) {
        if ($showSuccess) {
            Write-Host "Passed: $name" -ForegroundColor Green
        }
        return $true
    }

    Write-Host "--- $name failed ---" -ForegroundColor Red
    $result.Output | Write-Host
    return $false
}

$fixes = @(
    , @("Documentation generation", { & .\.venv\Scripts\python.exe scripts\check_docs.py --write-generated })
    , @("Ruff lint fix", { & .\.venv\Scripts\python.exe -m ruff check --fix . })
    , @("Ruff format", { & .\.venv\Scripts\python.exe -m ruff format . })
    , @("ESLint fix", { & npm run lint --prefix frontend -- --fix })
    , @("Prettier format", { & npm run format --prefix frontend })
)

$checks = @(
    , @("Documentation check", { & .\.venv\Scripts\python.exe scripts\check_docs.py --check })
    , @("Ruff lint check", { & .\.venv\Scripts\python.exe -m ruff check . })
    , @("Ruff format check", { & .\.venv\Scripts\python.exe -m ruff format --check . })
    , @("Python tests", { & .\.venv\Scripts\python.exe -m pytest })
    , @("Frontend tests", { Push-Location frontend; try { & .\node_modules\.bin\vitest.cmd run } finally { Pop-Location } })
    , @("ESLint check", { & npm run lint --prefix frontend })
    , @("Prettier check", { & .\frontend\node_modules\.bin\prettier.cmd --check frontend })
    , @("Frontend build", { & npm run build --prefix frontend })
    , @("Source size check", { & .\.venv\Scripts\python.exe scripts\check_size.py --source-max 500 --test-max 700 })
    , @("End-to-end tests", { & .\node_modules\.bin\playwright.cmd test --config tests\e2e\playwright.config.ts })
)

$failed = $false

foreach ($step in $fixes) {
    if (-not (Invoke-Step $step[0] $step[1])) {
        $failed = $true
    }
}

foreach ($step in $checks) {
    if (-not (Invoke-Step $step[0] $step[1] -showSuccess)) {
        $failed = $true
    }
}

if ($failed) {
    exit 1
}
