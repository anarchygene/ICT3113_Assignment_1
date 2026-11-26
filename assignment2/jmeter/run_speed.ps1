<#
.SYNOPSIS
  A2 speed tests, LOAD-GENERATOR PC side (brief Step 4). Never run this on the Lenovo.

  Reads the rate, run length, response timeout and drain pause from assignment2/results/speed/S.json
  (written on the Lenovo by `speed_service.py measure-s`; git pull first). Uses the A1 open-loop plan
  (step5/jmeter/ticket_triage.jmx) with the fixed A2 workload (assignment2/workload/speed_tickets.tsv),
  same tickets in the same order every run. Before EACH run it waits until you confirm the Lenovo printed
  READY for that config and run (`speed_service.py run <config> <run>`).

.EXAMPLE
  git pull
  .\assignment2\jmeter\run_speed.ps1 -ServiceHost <Lenovo IP, e.g. 192.168.1.103> -Config llama -JMeter C:\tools\apache-jmeter-5.6.3\bin\jmeter.bat
#>
param(
  [Parameter(Mandatory)] [string]$ServiceHost,
  [Parameter(Mandatory)] [ValidateSet('llama', 'qwen', 'gemma', 'cascadeA', 'cascadeB', 'cascadeA_lock', 'cascadeB_lock')] [string]$Config,
  [int[]]$Runs = @(1, 2, 3),
  [int]$Port = 8000,
  # GET /search traffic per hour during the run. 0 = none. Must be the same for every configuration.
  [double]$SearchPerHour = 0,
  [string]$JMeter = 'jmeter.bat',
  [string]$OutRoot = '',
  [switch]$NoWait   # testing only: do not wait for the Lenovo's READY
)
$ErrorActionPreference = 'Stop'
$Repo = Resolve-Path (Join-Path $PSScriptRoot '..\..')
if (-not $OutRoot) { $OutRoot = Join-Path $Repo 'assignment2\results\speed' }
$S = Get-Content (Join-Path $OutRoot 'S.json') -Raw | ConvertFrom-Json
$Jmx = Join-Path $Repo 'step5\jmeter\ticket_triage.jmx'
$Tickets = (Join-Path $Repo 'assignment2\workload\speed_tickets.tsv') -replace '\\', '/'
$Search = (Join-Path $Repo 'step5\data\search_terms.csv') -replace '\\', '/'
$Base = "http://${ServiceHost}:$Port"
$inv = [Globalization.CultureInfo]::InvariantCulture
function F([double]$x) { $x.ToString('0.####', $inv) }

$post = "rate($(F $S.rate_per_min)/min) random_arrivals($(F $S.run_min) min) pause($(F $S.pause_min) min)"
$search = if ($SearchPerHour -gt 0) { "rate($(F ($SearchPerHour / 60))/min) random_arrivals($(F $S.run_min) min) pause($(F $S.pause_min) min)" } else { 'pause(1 s)' }
Write-Host "S = $($S.S_s) s -> one ticket every $($S.interval_s) s; run $($S.run_min) min; timeout $($S.response_timeout_s) s; pause $($S.pause_min) min"
Write-Host "POST schedule:   $post"
Write-Host "Search schedule: $search"
Invoke-RestMethod "$Base/health" -TimeoutSec 10 | Out-Null

foreach ($run in $Runs) {
  $dir = Join-Path $OutRoot "$Config\run$run"
  if (Test-Path (Join-Path $dir 'results.jtl')) { Write-Warning "Skipping $dir (results.jtl exists)"; continue }
  New-Item -ItemType Directory -Force -Path $dir | Out-Null
  if (-not $NoWait) { Read-Host "`nWhen the Lenovo shows '*** READY $Config run $run ***', press ENTER to start" | Out-Null }

  @"
host=$ServiceHost
port=$Port
tickets_file=$Tickets
search_file=$Search
post_schedule=$post
search_schedule=$search
post_seed=$run
search_seed=$(100 + $run)
response_timeout_ms=$([int]($S.response_timeout_s * 1000))
jmeter.save.saveservice.output_format=csv
jmeter.save.saveservice.timestamp_format=ms
sampleresult.timestamp.start=true
sample_variables=reqid,row
"@ | Set-Content -Path (Join-Path $dir 'run.properties') -Encoding ascii

  $statsBefore = (Invoke-RestMethod "$Base/stats" -TimeoutSec 30).total
  $started = Get-Date -Format o
  & $JMeter -n -t $Jmx -q (Join-Path $dir 'run.properties') -l (Join-Path $dir 'results.jtl') -j (Join-Path $dir 'jmeter.log') |
    Tee-Object -FilePath (Join-Path $dir 'console.log')
  if ($LASTEXITCODE -ne 0) { throw "JMeter exited with $LASTEXITCODE" }
  $statsAfter = (Invoke-RestMethod "$Base/stats" -TimeoutSec 30).total

  [ordered]@{
    config = $Config; run = $run; loadgen_host = $env:COMPUTERNAME; service_host = $ServiceHost
    S_s = $S.S_s; rate_per_min = $S.rate_per_min; run_min = $S.run_min; response_timeout_s = $S.response_timeout_s
    pause_min = $S.pause_min; search_per_hour = $SearchPerHour; post_schedule = $post; search_schedule = $search
    started_local = $started; finished_local = (Get-Date -Format o)
    stats_before = $statsBefore; stats_after = $statsAfter; stats_delta = $statsAfter - $statsBefore
  } | ConvertTo-Json | Set-Content (Join-Path $dir 'meta_loadgen.json') -Encoding utf8
  Write-Host "`nRun $run finished: /stats +$($statsAfter - $statsBefore). Now press ENTER on the Lenovo to save its logs.`a"
}
Write-Host "All runs done. git add assignment2\results\speed\$Config; commit; push."
