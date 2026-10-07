<#
.SYNOPSIS
  Runs the Step 5 open-loop JMeter tests from the LOAD-GENERATOR PC (never the service PC).

.EXAMPLE
  # Load tests: three runs at each level for the model currently deployed on the service PC
  .\step5\jmeter\run_loadgen.ps1 -ServiceHost 192.168.1.23 -ModelLabel qwen3-4b -Levels average,peak,headroom

.EXAMPLE
  # Stress ramp (one run): POST arrivals ramp linearly 60/h -> 1200/h over 40 min, searches fixed at 316/h
  .\step5\jmeter\run_loadgen.ps1 -ServiceHost 192.168.1.23 -ModelLabel qwen3-4b -Stress -RampStartPerHour 60 -RampEndPerHour 1200 -RampMin 40

  ModelLabel must match the model the service PC operator has deployed (they tell you).
  Results go to step5\results\<ModelLabel>\<level>\run<N>\ ; commit and push them afterwards.
#>
param(
  [Parameter(Mandatory)] [string]$ServiceHost,
  [int]$Port = 8000,
  [Parameter(Mandatory)] [ValidateSet('gemma3-1b', 'qwen3-4b', 'llama3.1-8b')] [string]$ModelLabel,
  [string[]]$Levels = @('average', 'peak', 'headroom'),
  [int[]]$Runs = @(1, 2, 3),
  [double]$WarmupMin = 2,
  [double]$MeasureMin = 20,
  [double]$DrainMin = 1,
  [int]$CooldownSec = 60,
  [switch]$Stress,
  [int]$RampStartPerHour = 60,
  [int]$RampEndPerHour = 1200,
  [double]$RampMin = 40,
  [string]$JMeter = 'jmeter.bat',
  [string]$OutRoot = ''
)
$ErrorActionPreference = 'Stop'

# POST tickets/hour, GET searches/hour. Values from STEP4.md section 7 / workload/WORKLOAD.md section 8.
$LevelRates = @{
  offpeak  = @(18, 55)
  average  = @(43, 130)
  peak     = @(81, 243)
  headroom = @(105, 316)
  burst    = @(130, 316)
  surge    = @(243, 316)
}

$Step5 = Split-Path -Parent $PSScriptRoot
$Jmx = Join-Path $PSScriptRoot 'ticket_triage.jmx'
$TicketsFile = (Join-Path $Step5 'data\tickets_load.tsv') -replace '\\', '/'
$SearchFile = (Join-Path $Step5 'data\search_terms.csv') -replace '\\', '/'
$BaseUrl = "http://${ServiceHost}:$Port"
if (-not $OutRoot) { $OutRoot = Join-Path $Step5 'results' }

function Get-Json([string]$Path) {
  Invoke-RestMethod -Uri "$BaseUrl$Path" -TimeoutSec 30 | ConvertTo-Json -Depth 5
}

Get-Json '/health' | Out-Null   # fail fast if the service is unreachable

if ($Stress) {
  $total = $WarmupMin + $RampMin
  $plans = @(@{
      Level          = "stress_${RampStartPerHour}-${RampEndPerHour}ph_${RampMin}min"
      Run            = 1
      PostSchedule   = "rate($RampStartPerHour/hour) random_arrivals($WarmupMin min) rate($RampStartPerHour/hour) random_arrivals($RampMin min) rate($RampEndPerHour/hour) pause($DrainMin min)"
      SearchSchedule = "rate(316/hour) random_arrivals($total min) pause($DrainMin min)"
      Meta           = @{ post_per_hour_start = $RampStartPerHour; post_per_hour_end = $RampEndPerHour; ramp_min = $RampMin; search_per_hour = 316 }
    })
}
else {
  $total = $WarmupMin + $MeasureMin
  $plans = foreach ($level in $Levels) {
    if (-not $LevelRates.ContainsKey($level)) { throw "Unknown level '$level'" }
    $post, $search = $LevelRates[$level]
    foreach ($run in $Runs) {
      @{
        Level          = $level
        Run            = $run
        PostSchedule   = "rate($post/hour) random_arrivals($total min) pause($DrainMin min)"
        SearchSchedule = "rate($search/hour) random_arrivals($total min) pause($DrainMin min)"
        Meta           = @{ post_per_hour = $post; search_per_hour = $search }
      }
    }
  }
}

foreach ($p in $plans) {
  $outDir = Join-Path $OutRoot "$ModelLabel\$($p.Level)\run$($p.Run)"
  if (Test-Path (Join-Path $outDir 'results.jtl')) {
    Write-Warning "Skipping $outDir (results.jtl already exists; delete the folder to re-run)"
    continue
  }
  New-Item -ItemType Directory -Force -Path $outDir | Out-Null
  Write-Host "=== $ModelLabel / $($p.Level) / run $($p.Run) -> $outDir"

  # Seeds differ per run (reproducible but not identical arrival patterns).
  $props = @"
host=$ServiceHost
port=$Port
tickets_file=$TicketsFile
search_file=$SearchFile
post_schedule=$($p.PostSchedule)
search_schedule=$($p.SearchSchedule)
post_seed=$($p.Run)
search_seed=$(100 + $p.Run)
response_timeout_ms=310000
jmeter.save.saveservice.output_format=csv
jmeter.save.saveservice.timestamp_format=ms
sampleresult.timestamp.start=true
sample_variables=reqid,row
"@
  $propsFile = Join-Path $outDir 'run.properties'
  Set-Content -Path $propsFile -Value $props -Encoding ascii

  Get-Json '/stats' | Set-Content (Join-Path $outDir 'stats_before.json') -Encoding utf8
  $meta = $p.Meta + @{
    model_label = $ModelLabel; level = $p.Level; run = $p.Run
    warmup_min = $WarmupMin; measure_min = $(if ($Stress) { $RampMin } else { $MeasureMin }); drain_min = $DrainMin
    service_host = $ServiceHost; port = $Port; loadgen_host = $env:COMPUTERNAME
    started_local = (Get-Date -Format o)
  }

  & $JMeter -n -t $Jmx -q $propsFile `
    -l (Join-Path $outDir 'results.jtl') `
    -j (Join-Path $outDir 'jmeter.log') | Tee-Object -FilePath (Join-Path $outDir 'console.log')
  if ($LASTEXITCODE -ne 0) { throw "JMeter exited with $LASTEXITCODE" }

  Get-Json '/stats' | Set-Content (Join-Path $outDir 'stats_after.json') -Encoding utf8
  $meta.finished_local = (Get-Date -Format o)
  $meta | ConvertTo-Json | Set-Content (Join-Path $outDir 'meta.json') -Encoding utf8

  Write-Host "Cooling down $CooldownSec s"
  Start-Sleep -Seconds $CooldownSec
}
Write-Host 'All runs finished. Commit and push step5\results.'
