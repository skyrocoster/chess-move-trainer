[CmdletBinding()]
param(
    [Parameter(Position = 0)]
    [ValidateSet("start", "stop", "restart", "rebuild", "status", "logs")]
    [string]$Action = "status",

    [Parameter(Position = 1)]
    [ValidateSet("all", "backend", "frontend", "storybook", "worker", "worker-six")]
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
            Stop-AcceleratedWorkers
            Invoke-Compose (@(
                    "up", "--detach", "--scale", "worker=1", "--wait", "--wait-timeout", "180"
                ))
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
