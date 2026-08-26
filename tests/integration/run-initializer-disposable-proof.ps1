$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest
$source = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$temps = @()

function New-ProofCopy {
    $path = Join-Path ([IO.Path]::GetTempPath()) ("initializer-proof-" + [guid]::NewGuid().ToString("N"))
    Copy-Item $source $path -Recurse -Force -Exclude ".git"
    $script:temps += $path
    return $path
}

function Initialize-ProofGit([string]$Path) {
    & git -C $Path init --quiet
    if ($LASTEXITCODE -ne 0) { throw "Could not initialize proof Git repository." }
    & git -C $Path config user.email "initializer-proof@example.invalid"
    & git -C $Path config user.name "Initializer Proof"
    Set-Content (Join-Path $Path "proof-history-marker.txt") "original history"
    & git -C $Path add proof-history-marker.txt
    & git -C $Path commit --quiet -m "proof history marker"
    if ($LASTEXITCODE -ne 0) { throw "Could not create proof Git history." }
    return (& git -C $Path rev-parse HEAD).Trim()
}

function Get-ProofGitHead([string]$Path) {
    $ErrorActionPreference = "SilentlyContinue"
    $head = (& git -C $Path rev-parse HEAD 2>$null | Out-String).Trim()
    if ($LASTEXITCODE -ne 0) { return "" }
    return $head
}

function Invoke-ProofInitializer([string]$Path, [switch]$Keep, [switch]$ReplaceHistory) {
    $arguments = @(
        "-ProjectSlug", "proof-project", "-DisplayTitle", "Proof Project",
        "-ProjectDescription", "A disposable proof project.", "-DocsBrand", "Proof Project Docs",
        "-CleanGenerated", "-NonInteractive"
    )
    if ($Keep) { $arguments += "-KeepInitializer" }
    if ($ReplaceHistory) { $arguments += @("-ReplaceGitHistory", "-ConfirmHistoryReplacement") }
    & powershell -NoProfile -ExecutionPolicy Bypass -File (Join-Path $Path "initialize.ps1") @arguments
    if ($LASTEXITCODE -ne 0) { throw "Initializer failed in $Path." }
}

try {
    $before = (& git -C $source rev-parse --is-inside-work-tree 2>$null)

    # Retained rerun, cleanup, branding, omitted upstream, and default history preservation.
    $retained = New-ProofCopy
    New-Item (Join-Path $retained "node_modules") -ItemType Directory -Force | Out-Null
    New-Item (Join-Path $retained ".pytest_cache") -ItemType Directory -Force | Out-Null
    Set-Content (Join-Path $retained "unknown-ignored.txt") "must remain"
    $retainedHead = Initialize-ProofGit $retained
    Invoke-ProofInitializer $retained -Keep
    if (Test-Path (Join-Path $retained "node_modules")) { throw "node_modules was not cleaned." }
    if (-not (Test-Path (Join-Path $retained "unknown-ignored.txt"))) { throw "Unknown file was deleted." }
    if (-not (Select-String -Path (Join-Path $retained "docs/README.md") -Pattern "manual" -Quiet)) { throw "Upstream guidance missing." }
    if ((Get-ProofGitHead $retained) -ne $retainedHead) { throw "Default history was not preserved." }
    Invoke-ProofInitializer $retained -Keep
    if ((Get-ProofGitHead $retained) -ne $retainedHead) { throw "Retained rerun changed history." }

    # Successful default completion removes the initializer while preserving history.
    $removed = New-ProofCopy
    $removedHead = Initialize-ProofGit $removed
    Invoke-ProofInitializer $removed
    if (Test-Path (Join-Path $removed "initialize.ps1")) { throw "Initializer was not removed after success." }
    if ((Get-ProofGitHead $removed) -ne $removedHead) { throw "Default completion changed history." }

    # Explicitly confirmed history replacement removes the known original commit.
    $replaced = New-ProofCopy
    $replacedHead = Initialize-ProofGit $replaced
    Invoke-ProofInitializer $replaced -Keep -ReplaceHistory
    if (-not (Test-Path (Join-Path $replaced ".git"))) { throw "Replacement Git repository was not created." }
    if ((Get-ProofGitHead $replaced) -eq $replacedHead) { throw "History replacement did not replace history." }

    # Setup must recreate dependencies in a clean disposable copy.
    $setup = New-ProofCopy
    Remove-Item (Join-Path $setup ".venv"), (Join-Path $setup "node_modules"), (Join-Path $setup "frontend/node_modules") -Recurse -Force -ErrorAction SilentlyContinue
    Push-Location $setup
    try {
        & powershell -NoProfile -ExecutionPolicy Bypass -File (Join-Path $setup "setup.ps1")
        if ($LASTEXITCODE -ne 0) { throw "setup.ps1 failed." }
    } finally {
        Pop-Location
    }
    if (-not (Test-Path (Join-Path $setup ".venv/Scripts/python.exe"))) { throw "setup.ps1 did not recreate the Python environment." }
    if (-not (Test-Path (Join-Path $setup "node_modules"))) { throw "setup.ps1 did not recreate root dependencies." }
    if (-not (Test-Path (Join-Path $setup "frontend/node_modules"))) { throw "setup.ps1 did not recreate frontend dependencies." }

    $after = (& git -C $source rev-parse --is-inside-work-tree 2>$null)
    if ($before -ne $after) { throw "Source repository state changed." }
    Write-Host "Disposable initializer proof passed: cleanup, branding, history, removal, setup, rerun, and temp cleanup."
} finally {
    if ((Get-Location).Path -ne $source) { Set-Location $source }
    foreach ($temp in $temps) {
        if (Test-Path $temp) { Remove-Item $temp -Recurse -Force }
    }
}
