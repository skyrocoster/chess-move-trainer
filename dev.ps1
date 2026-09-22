[CmdletBinding()]
param(
    [Parameter(Position = 0)]
    [ValidateSet("start", "stop", "restart", "rebuild", "status", "logs", "update", "setup")]
    [string]$Action = "status",

    [Parameter(Position = 1)]
    [ValidateSet("all", "backend", "frontend", "storybook", "datasette", "worker", "worker-six")]
    [string]$Service = "all"
)

$ErrorActionPreference = "Stop"
$ComposeFile = Join-Path $PSScriptRoot "compose.yaml"

function Invoke-Compose {
    param([string[]]$Arguments)

    & docker compose --file $ComposeFile --project-directory $PSScriptRoot @Arguments
    if ($LASTEXITCODE -ne 0) {
        throw "Docker Compose failed with exit code $LASTEXITCODE."
    }
}

$WorkerProfile = "worker-six"

$UpdateBudgetMs = if ($env:CHESS_START_UPDATE_BUDGET_MS) {
    [int]$env:CHESS_START_UPDATE_BUDGET_MS
}
else {
    900000
}
$SetupBudgetMs = if ($env:CHESS_DEV_SETUP_BUDGET_MS) {
    [int]$env:CHESS_DEV_SETUP_BUDGET_MS
}
else {
    3600000
}
$ProbeBudgetMs = if ($env:CHESS_DEV_PROBE_BUDGET_MS) {
    [int]$env:CHESS_DEV_PROBE_BUDGET_MS
}
else {
    60000
}
$ProbeContainerName = "chess-move-trainer-db-probe"
$UpdateContainerName = "chess-move-trainer-db-update"
$SetupContainerName = "chess-move-trainer-db-setup"
$SetupCleanupContainerName = "chess-move-trainer-db-setup-cleanup"
$LiveDatabaseContainerPath = "data/database/chess.db"
$ProbePython = "import sys; from pathlib import Path; sys.exit(0 if Path('data/database/chess.db').exists() else 1)"
$SetupCleanupPython = "from pathlib import Path; [Path('data/database/chess.db' + suffix).unlink(missing_ok=True) for suffix in ('', '-journal', '-wal', '-shm')]"

function Invoke-BudgetedComposeRun {
    param(
        [string]$ContainerName,
        [string[]]$RunArgs,
        [int]$BudgetMs,
        [string]$Label
    )

    & docker rm -f $ContainerName *> $null
    $dockerArgs = @("compose", "--file", $ComposeFile, "--project-directory", $PSScriptRoot, "run") + $RunArgs
    $argString = (($dockerArgs | ForEach-Object {
            if ($_ -match '[\s"]') {
                '"' + ($_ -replace '"', '\"') + '"'
            }
            else {
                $_
            }
        }) -join " ")
    $proc = Start-Process -FilePath "docker" -ArgumentList $argString -NoNewWindow -PassThru
    $timeoutSeconds = [int][math]::Ceiling($BudgetMs / 1000)
    Wait-Process -InputObject $proc -Timeout $timeoutSeconds -ErrorAction SilentlyContinue
    if (-not $proc.HasExited) {
        Write-Warning ("{0} timed out after {1} ms; removing container {2}." -f $Label, $BudgetMs, $ContainerName)
        & docker rm -f $ContainerName *> $null
        Wait-Process -InputObject $proc -Timeout 30 -ErrorAction SilentlyContinue
        if (-not $proc.HasExited) {
            try {
                $proc.Kill()
            }
            catch {
            }
            Wait-Process -InputObject $proc -Timeout 10 -ErrorAction SilentlyContinue
        }
        & docker rm -f $ContainerName *> $null
        return [pscustomobject]@{
            TimedOut = $true
            ExitCode = $null
        }
    }
    & docker rm -f $ContainerName *> $null
    return [pscustomobject]@{
        TimedOut = $false
        ExitCode = $proc.ExitCode
    }
}

function Test-LiveDatabaseExists {
    $probeArgs = @(
        "--rm", "--no-deps", "--name", $ProbeContainerName, "worker",
        "python", "-c", $ProbePython
    )
    $result = Invoke-BudgetedComposeRun -ContainerName $ProbeContainerName `
        -RunArgs $probeArgs -BudgetMs $ProbeBudgetMs -Label "Live-database probe"
    if ($result.TimedOut) {
        throw "Live-database probe timed out after $ProbeBudgetMs ms."
    }
    if ($result.ExitCode -eq 0) {
        return $true
    }
    if ($result.ExitCode -eq 1) {
        return $false
    }
    throw ("Live-database probe failed with exit code {0}." -f $result.ExitCode)
}

function Test-StackHealthy {
    $mode = (Get-WorkerMode).Label
    if ($mode -ne "normal" -and $mode -ne "accelerated-six") {
        return $false
    }
    $json = & docker compose --file $ComposeFile --project-directory $PSScriptRoot `
        --profile $WorkerProfile ps --all --format json backend frontend datasette
    if ($LASTEXITCODE -ne 0) {
        throw "Docker Compose status failed with exit code $LASTEXITCODE."
    }
    $rows = @()
    if (-not [string]::IsNullOrWhiteSpace(($json -join ""))) {
        try {
            $rows = @($json | ForEach-Object { $_ | ConvertFrom-Json })
        }
        catch {
            throw "Docker Compose returned invalid status JSON."
        }
    }
    foreach ($serviceName in @("backend", "frontend", "datasette")) {
        $row = @($rows | Where-Object { $_.Service -eq $serviceName }) | Select-Object -First 1
        if ($null -eq $row) {
            return $false
        }
        if ($row.State -ne "running") {
            return $false
        }
        if ($row.Health -ne "healthy") {
            return $false
        }
    }
    return $true
}

function Invoke-DatabaseUpdates {
    param([int]$BudgetMs)

    $steps = @(
        @{ Label = "Update games"; Command = @("update", "games") },
        @{ Label = "Update openings"; Command = @("update", "openings") }
    )
    foreach ($step in $steps) {
        $runArgs = @(
            "--rm", "--no-deps", "--name", $UpdateContainerName, "worker",
            "python", "-m", "chess_move_trainer.database"
        ) + $step.Command + @("--database", $LiveDatabaseContainerPath)
        $result = Invoke-BudgetedComposeRun -ContainerName $UpdateContainerName `
            -RunArgs $runArgs -BudgetMs $BudgetMs -Label $step.Label
        if ($result.TimedOut) {
            return @{ Ok = $false; Reason = ("{0} timed out after {1} ms" -f $step.Label, $BudgetMs) }
        }
        if ($result.ExitCode -ne 0) {
            return @{ Ok = $false; Reason = ("{0} exited with code {1}" -f $step.Label, $result.ExitCode) }
        }
    }
    return @{ Ok = $true; Reason = "" }
}

function Invoke-WorkerCompose {
    param([string[]]$Arguments)

    Invoke-Compose (@("--profile", $WorkerProfile) + $Arguments)
}

function Get-WorkerRows {
    $json = & docker compose --file $ComposeFile --project-directory $PSScriptRoot `
        --profile $WorkerProfile ps --all --format json worker worker-six
    if ($LASTEXITCODE -ne 0) {
        throw "Docker Compose worker status failed with exit code $LASTEXITCODE."
    }
    if ([string]::IsNullOrWhiteSpace(($json -join ""))) {
        return @()
    }
    try {
        return @($json | ForEach-Object { $_ | ConvertFrom-Json })
    }
    catch {
        throw "Docker Compose returned invalid worker status JSON."
    }
}

function Get-WorkerMode {
    $rows = @(Get-WorkerRows)
    $normalRunning = @($rows | Where-Object {
            $_.Service -eq "worker" -and $_.State -eq "running"
        }).Count
    $acceleratedRunning = @($rows | Where-Object {
            $_.Service -eq "worker-six" -and $_.State -eq "running"
        }).Count

    $label = if ($normalRunning -eq 1 -and $acceleratedRunning -eq 0) {
        "normal"
    }
    elseif ($normalRunning -eq 0 -and $acceleratedRunning -eq 6) {
        "accelerated-six"
    }
    elseif ($normalRunning -eq 0 -and $acceleratedRunning -eq 0) {
        "stopped"
    }
    elseif ($normalRunning -gt 0 -and $acceleratedRunning -gt 0) {
        "invalid/mixed"
    }
    else {
        "invalid/partial"
    }

    return [pscustomobject]@{
        Label = $label
        NormalRunning = $normalRunning
        AcceleratedRunning = $acceleratedRunning
    }
}

function Assert-WorkerCounts {
    param(
        [int]$NormalRunning,
        [int]$AcceleratedRunning
    )

    if ($NormalRunning -ne 0 -or $AcceleratedRunning -ne 0) {
        throw (
            "Analysis workers did not stop cleanly: normal=$NormalRunning, " +
            "accelerated=$AcceleratedRunning."
        )
    }
}

function Stop-NormalWorker {
    Invoke-Compose @("stop", "worker")
}

function Stop-AcceleratedWorkers {
    Invoke-WorkerCompose @("stop", "worker-six")
}

function Start-NormalWorker {
    Stop-AcceleratedWorkers
    $before = Get-WorkerMode
    if ($before.AcceleratedRunning -ne 0) {
        throw "Accelerated workers are still running; normal mode was not started."
    }
    Invoke-Compose @(
        "up", "--detach", "--scale", "worker=1", "--wait", "--wait-timeout", "180", "worker"
    )
}

function Start-AcceleratedWorkers {
    Stop-NormalWorker
    $before = Get-WorkerMode
    if ($before.NormalRunning -ne 0) {
        throw "The normal worker is still running; accelerated mode was not started."
    }
    Invoke-WorkerCompose @(
        "up", "--detach", "--scale", "worker-six=6", "--wait", "--wait-timeout", "180", "worker-six"
    )
}

& docker info --format "{{.ServerVersion}}" *> $null
if ($LASTEXITCODE -ne 0) {
    throw "Docker Desktop is not running. Start Docker Desktop and try again."
}

$Services = if ($Service -eq "all") { @() } else { @($Service) }

switch ($Action) {
    "start" {
        if ($Service -eq "worker-six") {
            Start-AcceleratedWorkers
        }
        elseif ($Service -eq "worker") {
            Start-NormalWorker
        }
        elseif ($Service -eq "all") {
            if (Test-StackHealthy) {
                Write-Output "Stack is already healthy; leaving it alone (no data update, no worker-mode change)."
            }
            else {
                if (-not (Test-LiveDatabaseExists)) {
                    throw "No live database found in the chess-database volume. Run powershell -ExecutionPolicy Bypass -File ./dev.ps1 setup once to create it, then start again."
                }
                $modeBefore = (Get-WorkerMode).Label
                if ($modeBefore -eq "invalid/mixed" -or $modeBefore -eq "invalid/partial") {
                    Write-Warning ("Workers are in state '{0}'; stopping them before the data update." -f $modeBefore)
                }
                Stop-AcceleratedWorkers
                Stop-NormalWorker
                $updateOutcome = Invoke-DatabaseUpdates -BudgetMs $UpdateBudgetMs
                if (-not $updateOutcome.Ok) {
                    Write-Warning ("Data update did not complete ({0}); starting services on the existing data." -f $updateOutcome.Reason)
                }
                if ($modeBefore -eq "accelerated-six") {
                    Start-AcceleratedWorkers
                    Invoke-Compose @(
                        "up", "--detach", "--wait", "--wait-timeout", "180",
                        "backend", "frontend", "storybook", "datasette"
                    )
                }
                else {
                    Stop-AcceleratedWorkers
                    Invoke-Compose (@(
                            "up", "--detach", "--scale", "worker=1", "--wait", "--wait-timeout", "180"
                        ))
                }
            }
        }
        else {
            Invoke-Compose (@("up", "--detach", "--wait", "--wait-timeout", "180") + $Services)
        }
    }
    "stop" {
        if ($Service -eq "worker-six" -or $Service -eq "worker") {
            Stop-AcceleratedWorkers
            Stop-NormalWorker
            $state = Get-WorkerMode
            Assert-WorkerCounts $state.NormalRunning $state.AcceleratedRunning
        }
        elseif ($Service -eq "all") {
            Invoke-WorkerCompose @("stop")
            $state = Get-WorkerMode
            Assert-WorkerCounts $state.NormalRunning $state.AcceleratedRunning
        }
        else {
            Invoke-Compose (@("stop") + $Services)
        }
    }
    "restart" {
        if ($Service -eq "worker-six") {
            Stop-AcceleratedWorkers
            Start-AcceleratedWorkers
        }
        elseif ($Service -eq "worker") {
            Start-NormalWorker
        }
        elseif ($Service -eq "all") {
            Invoke-WorkerCompose @("stop")
            $state = Get-WorkerMode
            Assert-WorkerCounts $state.NormalRunning $state.AcceleratedRunning
            Invoke-Compose @(
                "up", "--detach", "--scale", "worker=1", "--wait", "--wait-timeout", "180"
            )
        }
        else {
            Invoke-Compose (@("restart") + $Services)
            Invoke-Compose (@("up", "--detach", "--wait", "--wait-timeout", "180", "--no-recreate") + $Services)
        }
    }
    "rebuild" {
        if ($Service -eq "worker-six") {
            Stop-NormalWorker
            Invoke-WorkerCompose @(
                "up", "--detach", "--build", "--force-recreate", "--scale", "worker-six=6",
                "--wait", "--wait-timeout", "300", "worker-six"
            )
        }
        elseif ($Service -eq "worker") {
            Stop-AcceleratedWorkers
            Invoke-Compose @(
                "up", "--detach", "--build", "--force-recreate", "--scale", "worker=1",
                "--wait", "--wait-timeout", "300", "worker"
            )
        }
        elseif ($Service -eq "all") {
            Stop-AcceleratedWorkers
            Invoke-Compose @(
                "up", "--detach", "--build", "--force-recreate", "--scale", "worker=1",
                "--wait", "--wait-timeout", "300"
            )
        }
        else {
            Invoke-Compose (@("up", "--detach", "--build", "--force-recreate", "--wait", "--wait-timeout", "300") + $Services)
        }
    }
    "update" {
        if ($Service -ne "all") {
            throw "The update action only supports the 'all' target."
        }
        if (-not (Test-LiveDatabaseExists)) {
            throw "No live database found in the chess-database volume. Run powershell -ExecutionPolicy Bypass -File ./dev.ps1 setup once to create it."
        }
        $mode = Get-WorkerMode
        if ($mode.Label -eq "invalid/mixed" -or $mode.Label -eq "invalid/partial") {
            throw ("Refusing to update while workers are in state '{0}'. Resolve the worker state first." -f $mode.Label)
        }
        $activeMode = $mode.Label
        Stop-AcceleratedWorkers
        Stop-NormalWorker
        $paused = Get-WorkerMode
        Assert-WorkerCounts $paused.NormalRunning $paused.AcceleratedRunning
        $updateOutcome = Invoke-DatabaseUpdates -BudgetMs $UpdateBudgetMs
        if ($activeMode -eq "accelerated-six") {
            Start-AcceleratedWorkers
        }
        elseif ($activeMode -eq "normal") {
            Start-NormalWorker
        }
        if (-not $updateOutcome.Ok) {
            throw ("Data update failed ({0}); workers were restored to mode '{1}'." -f $updateOutcome.Reason, $activeMode)
        }
        Write-Output ("Data update completed; workers restored to mode '{0}'." -f $activeMode)
    }
    "setup" {
        if ($Service -ne "all") {
            throw "The setup action only supports the 'all' target."
        }
        if (Test-LiveDatabaseExists) {
            throw "Live database already exists in the chess-database volume; setup refused to avoid overwriting it."
        }
        $setupArgs = @(
            "--rm", "--no-deps", "--name", $SetupContainerName, "worker",
            "python", "-m", "chess_move_trainer.database",
            "setup", "--database", $LiveDatabaseContainerPath
        )
        $result = Invoke-BudgetedComposeRun -ContainerName $SetupContainerName `
            -RunArgs $setupArgs -BudgetMs $SetupBudgetMs -Label "Setup"
        if ($result.TimedOut) {
            Write-Warning ("Setup timed out after {0} ms; removing the partial database it created." -f $SetupBudgetMs)
            $cleanupArgs = @(
                "--rm", "--no-deps", "--name", $SetupCleanupContainerName, "worker",
                "python", "-c", $SetupCleanupPython
            )
            $cleanup = Invoke-BudgetedComposeRun -ContainerName $SetupCleanupContainerName `
                -RunArgs $cleanupArgs -BudgetMs $ProbeBudgetMs -Label "Setup cleanup"
            if ($cleanup.TimedOut -or $cleanup.ExitCode -ne 0) {
                throw "Setup timed out and partial-database cleanup did not complete; inspect the chess-database volume before retrying."
            }
            throw ("Setup timed out after {0} ms; its partial database was removed." -f $SetupBudgetMs)
        }
        if ($result.ExitCode -ne 0) {
            throw ("Setup exited with code {0}." -f $result.ExitCode)
        }
        Write-Output "Setup completed: live database created in the chess-database volume."
    }
    "status" {
        if ($Service -eq "all") {
            Invoke-WorkerCompose @("ps", "--all")
            $state = Get-WorkerMode
            Write-Output (
                "Worker mode: {0} (normal running={1}, accelerated running={2})" -f
                $state.Label, $state.NormalRunning, $state.AcceleratedRunning
            )
        }
        elseif ($Service -eq "worker" -or $Service -eq "worker-six") {
            Invoke-WorkerCompose @("ps", "--all", "worker", "worker-six")
            $state = Get-WorkerMode
            Write-Output (
                "Worker mode: {0} (normal running={1}, accelerated running={2})" -f
                $state.Label, $state.NormalRunning, $state.AcceleratedRunning
            )
        }
        else {
            Invoke-Compose (@("ps", "--all") + $Services)
        }
    }
    "logs" {
        if ($Service -eq "all") {
            Invoke-WorkerCompose @("logs", "--tail", "100", "--no-log-prefix")
        }
        elseif ($Service -eq "worker-six") {
            Invoke-WorkerCompose @("logs", "--tail", "100", "--no-log-prefix", "worker-six")
        }
        else {
            Invoke-Compose (@("logs", "--tail", "100", "--no-log-prefix") + $Services)
        }
    }
}
