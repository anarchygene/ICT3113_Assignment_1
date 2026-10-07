# Load-generator PC setup (second PC, JMeter only)

The assignment requires JMeter to run on a different machine from the service. This PC only generates traffic. It never runs Docker, Ollama or the API for assessed runs.

## 1. Before you start (on the SERVICE PC, done by its owner)

The service PC is on Wi-Fi `kenyap` at **192.168.1.106** (check again with `ipconfig` if the router may have changed it). Windows marks the network as *Public*, which blocks incoming connections, so allow the API port **once**, in an *Administrator* PowerShell **on the service PC**:

```powershell
New-NetFirewallRule -DisplayName "ICT3113 API 8000" -Direction Inbound -Protocol TCP -LocalPort 8000 -Action Allow -Profile Any
```

Remove it after the assignment with `Remove-NetFirewallRule -DisplayName "ICT3113 API 8000"`.

## 2. One-time setup on this PC

1. Connect to the **same** Wi-Fi as the service PC (or Ethernet on the same router). Plug in the charger. Settings → System → Power → *Screen and sleep* → set *Never* while plugged in. Close heavy apps.
2. Install Java 17 or newer (`java -version` must work), e.g. Eclipse Temurin 17 from https://adoptium.net/.
3. Download **Apache JMeter 5.6.3** (binary zip) from https://jmeter.apache.org/download_jmeter.cgi and unzip it to `C:\tools\apache-jmeter-5.6.3`. No plugins are needed: the Open Model Thread Group is built in.
4. Clone or pull the team repository and open PowerShell in the repository root:
   ```powershell
   git pull
   ```
5. Check connectivity (must print `{"status":"ok"}`):
   ```powershell
   curl.exe http://192.168.1.106:8000/health
   ```
   If this times out, step 1 (the firewall rule) has not been done, or the two PCs are on different networks.
6. Record this PC's hardware for the report:
   ```powershell
   "Captured: $(Get-Date -Format o)" | Out-File -Encoding utf8 evidence\step4\load-generator-hardware.txt
   Get-CimInstance Win32_Processor | Select-Object Name, NumberOfCores, NumberOfLogicalProcessors, MaxClockSpeed | Format-List | Out-File -Append -Encoding utf8 evidence\step4\load-generator-hardware.txt
   Get-CimInstance Win32_ComputerSystem | Select-Object Manufacturer, Model, @{Name='RAM_GB'; Expression={[math]::Round($_.TotalPhysicalMemory / 1GB, 2)}} | Format-List | Out-File -Append -Encoding utf8 evidence\step4\load-generator-hardware.txt
   Get-CimInstance Win32_OperatingSystem | Select-Object Caption, Version, OSArchitecture | Format-List | Out-File -Append -Encoding utf8 evidence\step4\load-generator-hardware.txt
   Get-NetAdapter | Where-Object Status -eq Up | Select-Object Name, InterfaceDescription, LinkSpeed | Format-Table | Out-File -Append -Encoding utf8 evidence\step4\load-generator-hardware.txt
   java -version 2>&1 | Out-File -Encoding utf8 evidence\step4\jmeter-version.txt
   & C:\tools\apache-jmeter-5.6.3\bin\jmeter.bat --version | Out-File -Append -Encoding utf8 evidence\step4\jmeter-version.txt
   git add evidence\step4; git commit -m "Record load-generator environment"; git push
   ```

## 3. Running a batch (only when the service PC owner says a model is deployed)

```powershell
git pull
.\step5\jmeter\run_loadgen.ps1 -ServiceHost 192.168.1.106 -ModelLabel <label> -Levels average,peak,headroom -JMeter C:\tools\apache-jmeter-5.6.3\bin\jmeter.bat
```

`<label>` is exactly one of `gemma3-1b`, `qwen3-4b` or `llama3.1-8b`, whichever the service PC owner has just deployed. The batch runs 9 runs of about 24 minutes each (≈3 h 40 min). Leave the PC alone while it runs. When it finishes:

```powershell
git add step5\results
git commit -m "Step 5 load results <label>"
git push
```

Stress test (only for `qwen3-4b`, after its load batch):

```powershell
.\step5\jmeter\run_loadgen.ps1 -ServiceHost 192.168.1.106 -ModelLabel qwen3-4b -Stress -RampStartPerHour 60 -RampEndPerHour 1200 -RampMin 40 -JMeter C:\tools\apache-jmeter-5.6.3\bin\jmeter.bat
```

Rules: do not edit the `.jmx`, rates or durations; do not delete or re-run a finished run because the numbers look bad. If something external breaks a run (PC slept, Wi-Fi dropped), keep the folder, rename it `run<N>_invalid` and tell the team.

## 4. Prompt to paste into Claude Code on this PC (optional)

> I'm the load-generator operator for our ICT3113 Assignment 1. Open the team repo and follow `step5/LOADGEN_SETUP.md` exactly: check Java 17+ and JMeter 5.6.3 at `C:\tools\apache-jmeter-5.6.3` (tell me if I must install them, and don't download anything without asking me first), `git pull`, check `curl.exe http://192.168.1.106:8000/health`, then record this PC's hardware into `evidence/step4` as in section 2 step 6 and commit/push it. Do NOT start any JMeter batch until I tell you which model label is deployed. When I do, run `step5/jmeter/run_loadgen.ps1` with that label as shown in section 3 (run it in the background, it takes ~3 h 40 min), and when it finishes, commit and push `step5/results`. Never edit the test plan, rates or durations, never delete result folders, and don't run anything else CPU-heavy on this PC during a batch.
