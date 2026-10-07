<#
.SYNOPSIS
  SERVICE PC ONLY. Deploys one candidate model under identical conditions before its Step 5 tests.

  1. Saves the current API log (recreating the container would otherwise discard it).
  2. Sets OLLAMA_MODEL in .env and recreates only the api container.
  3. Warms the model with two synthetic, non-dataset tickets, then empties the tickets table
     so every candidate starts from the same empty database.
  4. Records `ollama ps` and the deployed configuration under evidence/step5/.

.EXAMPLE
  .\step5\service\switch_model.ps1 -Model qwen3:4b-instruct-2507-q4_K_M
#>
param(
  [Parameter(Mandatory)]
  [ValidateSet('gemma3:1b-it-q4_K_M', 'qwen3:4b-instruct-2507-q4_K_M', 'llama3.1:8b-instruct-q4_K_M')]
  [string]$Model
)
$ErrorActionPreference = 'Stop'
$Root = Resolve-Path (Join-Path $PSScriptRoot '..\..')
Set-Location $Root
$Evidence = Join-Path $Root 'evidence\step5'
New-Item -ItemType Directory -Force -Path "$Evidence\logs" | Out-Null
$Stamp = (Get-Date).ToUniversalTime().ToString('yyyyMMddTHHmmssZ')

& "$PSScriptRoot\save_logs.ps1" -Tag "before-switch-$Stamp"

(Get-Content .env) -replace '^OLLAMA_MODEL=.*', "OLLAMA_MODEL=$Model" | Set-Content .env -Encoding ascii
docker compose up -d --force-recreate api
if ($LASTEXITCODE -ne 0) { throw 'docker compose up failed' }

for ($i = 0; $i -lt 60; $i++) {
  try { Invoke-RestMethod http://localhost:8000/health -TimeoutSec 5 | Out-Null; break } catch { Start-Sleep 2 }
}

# Synthetic warm-up text, deliberately not from the dataset or golden set.
$warm = @(
  'Warm-up request. My debit card was declined at a store although my checking account had funds.',
  'Warm-up request. A collection agency keeps calling me about a medical bill I already paid.'
)
foreach ($n in $warm) {
  $body = @{ narrative = $n } | ConvertTo-Json
  # The warm-up only needs to load the model; an invalid (502) answer is logged, not fatal.
  try {
    $r = Invoke-RestMethod -Method Post -Uri http://localhost:8000/tickets -ContentType 'application/json' `
      -Body $body -Headers @{ 'X-Request-ID' = "warmup-$Stamp-$([guid]::NewGuid())" } -TimeoutSec 600
    Write-Host "warm-up -> $($r.category) ($($r.model))"
  }
  catch { Write-Host "warm-up -> HTTP error (model loaded; answer rejected): $($_.ErrorDetails.Message)" }
}

# Pass psql arguments directly: Windows PowerShell 5.1 mangles nested quotes in native arguments.
$envFile = Get-Content .env
$pgUser = ($envFile | Select-String '^POSTGRES_USER=') -replace '^POSTGRES_USER=', ''
$pgDb = ($envFile | Select-String '^POSTGRES_DB=') -replace '^POSTGRES_DB=', ''
docker compose exec -T db psql -U $pgUser -d $pgDb -c 'TRUNCATE tickets RESTART IDENTITY'
if ($LASTEXITCODE -ne 0) { throw 'TRUNCATE failed' }
$stats = Invoke-RestMethod http://localhost:8000/stats
if ($stats.total -ne 0) { throw "Database not empty after reset: $($stats.total)" }

$safe = $Model -replace '[:.]', '-'
@(
  "Deployed: $Model at $Stamp (UTC)"
  'ollama ps:'
  (docker compose exec -T ollama ollama ps)
  'docker compose ps:'
  (docker compose ps)
) | Set-Content "$Evidence\deploy-$safe-$Stamp.txt" -Encoding utf8
Get-Content "$Evidence\deploy-$safe-$Stamp.txt"
Write-Host "Ready: $Model deployed, warmed, database empty. Tell the load-generator operator to start."
