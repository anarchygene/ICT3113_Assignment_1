<#
.SYNOPSIS
  SERVICE PC ONLY. Saves the API, Ollama and database container logs to evidence/step5/logs.
  Run after every batch of JMeter runs and before any container is recreated.
#>
param([string]$Tag = (Get-Date).ToUniversalTime().ToString('yyyyMMddTHHmmssZ'))
$ErrorActionPreference = 'Stop'
$Root = Resolve-Path (Join-Path $PSScriptRoot '..\..')
$Logs = Join-Path $Root 'evidence\step5\logs'
New-Item -ItemType Directory -Force -Path $Logs | Out-Null
Push-Location $Root
try {
  $model = ((Get-Content .env | Select-String '^OLLAMA_MODEL=') -replace '^OLLAMA_MODEL=', '') -replace '[:.]', '-'
  foreach ($svc in 'api', 'ollama', 'db') {
    $file = Join-Path $Logs "$svc-$model-$Tag.log"
    docker compose logs --no-color --timestamps $svc | Out-File -Encoding utf8 $file
    Write-Host "saved $file"
  }
  # R8 evidence: restarts and out-of-memory kills since each container was created.
  $ids = docker compose ps -q
  docker inspect --format '{{.Name}} created={{.Created}} started={{.State.StartedAt}} restarts={{.RestartCount}} oomkilled={{.State.OOMKilled}} status={{.State.Status}}' $ids |
    Out-File -Encoding utf8 (Join-Path $Logs "containers-$model-$Tag.txt")
  docker stats --no-stream --format '{{.Name}} cpu={{.CPUPerc}} mem={{.MemUsage}}' |
    Out-File -Append -Encoding utf8 (Join-Path $Logs "containers-$model-$Tag.txt")
}
finally { Pop-Location }
