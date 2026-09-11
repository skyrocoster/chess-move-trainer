[CmdletBinding()]
param(
    [Parameter(Position = 0)]
    [ValidateSet("start", "stop", "restart", "rebuild", "status", "logs")]
    [string]$Action = "status",

    [Parameter(Position = 1)]
    [ValidateSet("all", "backend", "frontend", "storybook")]
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

& docker info --format "{{.ServerVersion}}" *> $null
if ($LASTEXITCODE -ne 0) {
    throw "Docker Desktop is not running. Start Docker Desktop and try again."
}

$Services = if ($Service -eq "all") { @() } else { @($Service) }

switch ($Action) {
    "start" {
        Invoke-Compose (@("up", "--detach", "--wait", "--wait-timeout", "180") + $Services)
    }
    "stop" {
        Invoke-Compose (@("stop") + $Services)
    }
    "restart" {
        Invoke-Compose (@("restart") + $Services)
        Invoke-Compose (@("up", "--detach", "--wait", "--wait-timeout", "180", "--no-recreate") + $Services)
    }
    "rebuild" {
        Invoke-Compose (@("up", "--detach", "--build", "--force-recreate", "--wait", "--wait-timeout", "300") + $Services)
    }
    "status" {
        Invoke-Compose (@("ps", "--all") + $Services)
    }
    "logs" {
        Invoke-Compose (@("logs", "--tail", "100", "--no-log-prefix") + $Services)
    }
}
