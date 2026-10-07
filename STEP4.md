# Step 4 Candidate Models Requirements and Prediction Record

This document defines the candidate model set, the client acceptance requirements, and the prediction record for Assignment 1. Complete every field marked `TBD BEFORE BENCHMARK`, verify the golden set, and commit this document before sending any golden-set ticket through a candidate model.

## 1. Preconditions and freeze point

Step 5 must not begin until all of the following are complete:

- [x] The golden set contains 150 to 200 tickets and uses only the seven exact category names.
- [ ] Two independent label sheets, the labelling protocol, disagreement resolutions, and the agreement statistic are retained. *Partly met: tickets were labelled by one member and reviewed by a second (not blind double-labelling); 14 disagreements are recorded with resolutions in the workbook, and Cohen's kappa = 0.896 (`scripts/agreement.py`, `evidence/step1/agreement.txt`).*
- [x] The final golden set is committed.
- [x] All three model tags and locally observed digests are recorded below.
- [x] The test hardware and software environment is recorded below.
- [x] Every numerical prediction in Section 6 is completed.
- [x] This prediction record is committed.

The commit containing the frozen golden set and completed prediction record must predate the first benchmark run. Record that commit here:

`Freeze commit: 3567f8057758a4ed6ebd8bc018c3c707dc3b579e`

## Exact procedure for the Step 4 owner

One person should own this procedure so the tags, hardware record, requirements, and predictions are frozen consistently. Other members should review the content, but nobody should send golden-set tickets to a model until the two freeze commits at the end of this procedure exist.

Run the commands below in **PowerShell from the repository root on the designated service PC**, unless a step says to use the load-generator PC. Do not discard or reset another team member's uncommitted work if `git status` is not clean.

### Step 1 Check the repository and golden-set history

```powershell
git status --short
git branch --show-current
git log -1 --oneline
git log --oneline -- "ICT3113 Golden Set P1-9.xlsx"
```

Expected outcome:

- The current branch and latest commit are known.
- The golden-set workbook appears in Git history.
- Any output from `git status --short` is understood before continuing.

Open `ICT3113 Golden Set P1-9.xlsx` and finish the Step 1 checks before continuing. In particular, confirm that `Just Data!A2:C161` contains 160 unique tickets and that every value in `Just Data!B2:B161` uses one of the seven exact category strings in R7. The current workbook must be corrected so `Credit Card` becomes `Credit card` before the golden set is frozen again. Confirm that the labelling protocol, two independent label sheets, agreement calculation, and disagreement resolutions are retained as supporting files.

Commit any necessary Step 1 correction before proceeding. Do not run a candidate model on a golden narrative to help decide a label.

### Step 2 Create the Step 4 evidence folder

```powershell
New-Item -ItemType Directory -Force -Path evidence\step4 | Out-Null
```

The `evidence/step4` folder is not ignored by the current `.gitignore`, so the text evidence created below can be committed.

### Step 3 Validate the Compose configuration

Ensure Docker Desktop or Docker Engine is running, then execute:

```powershell
docker compose config --quiet
if ($LASTEXITCODE -ne 0) { throw "Compose configuration is invalid" }

docker compose version | Tee-Object -FilePath evidence\step4\docker-compose-version.txt
docker version | Tee-Object -FilePath evidence\step4\docker-version.txt
```

Do not change the Ollama or Docker versions between candidate runs. If the pinned Ollama image cannot pull or run one of the chosen tags, agree on and commit one Ollama-version change before freezing Step 4, then use that version for every candidate.

### Step 4 Record the service-machine hardware

Run the following on the service PC:

```powershell
"Captured: $(Get-Date -Format o)" | Set-Content evidence\step4\service-hardware.txt

Get-CimInstance Win32_Processor |
  Select-Object Name, NumberOfCores, NumberOfLogicalProcessors, MaxClockSpeed |
  Format-List |
  Out-File -Append evidence\step4\service-hardware.txt

Get-CimInstance Win32_ComputerSystem |
  Select-Object Manufacturer, Model,
    @{Name='RAM_GB'; Expression={[math]::Round($_.TotalPhysicalMemory / 1GB, 2)}} |
  Format-List |
  Out-File -Append evidence\step4\service-hardware.txt

Get-CimInstance Win32_OperatingSystem |
  Select-Object Caption, Version, OSArchitecture |
  Format-List |
  Out-File -Append evidence\step4\service-hardware.txt
```

If `Get-CimInstance` is blocked by local policy, run `systeminfo`, save its output as `evidence/step4/service-hardware.txt`, and record the physical-core count separately from Task Manager or the CPU manufacturer's specification.

### Step 5 Start only the database and Ollama

```powershell
docker compose up -d db ollama
docker compose ps
docker compose exec -T ollama ollama --version |
  Tee-Object -FilePath evidence\step4\ollama-version.txt
```

Do not start accuracy or load testing here. Pulling and inspecting model metadata is Step 4; sending test narratives is Step 5.

### Step 6 Pull the three exact model tags

```powershell
docker compose exec ollama ollama pull gemma3:1b-it-q4_K_M
docker compose exec ollama ollama pull qwen3:4b-instruct-2507-q4_K_M
docker compose exec ollama ollama pull llama3.1:8b-instruct-q4_K_M
```

All three commands must finish successfully. Do not replace a failed model with a different tag without updating the candidate justification and committing that decision before benchmarking.

### Step 7 Capture the local IDs, quantization, metadata, and model files

```powershell
docker compose exec -T ollama ollama list |
  Tee-Object -FilePath evidence\step4\ollama-list.txt

$models = @(
  'gemma3:1b-it-q4_K_M',
  'qwen3:4b-instruct-2507-q4_K_M',
  'llama3.1:8b-instruct-q4_K_M'
)

foreach ($model in $models) {
  $safeName = $model -replace '[:.]', '-'
  docker compose exec -T ollama ollama show $model |
    Out-File -Encoding utf8 "evidence\step4\$safeName-show.txt"
  docker compose exec -T ollama ollama show $model --modelfile |
    Out-File -Encoding utf8 "evidence\step4\$safeName-modelfile.txt"
}
```

Copy the locally reported model ID or digest from `evidence/step4/ollama-list.txt` into the table in Section 2.1. Record the pull date and the matching evidence filenames. Check the `show` output confirms the intended parameter size and quantization.

### Step 8 Record the separate load-generator environment

On the PC that will run JMeter, run:

```powershell
"Captured: $(Get-Date -Format o)" | Set-Content load-generator-hardware.txt

Get-CimInstance Win32_Processor |
  Select-Object Name, NumberOfCores, NumberOfLogicalProcessors, MaxClockSpeed |
  Format-List |
  Out-File -Append load-generator-hardware.txt

Get-CimInstance Win32_ComputerSystem |
  Select-Object Manufacturer, Model,
    @{Name='RAM_GB'; Expression={[math]::Round($_.TotalPhysicalMemory / 1GB, 2)}} |
  Format-List |
  Out-File -Append load-generator-hardware.txt

Get-CimInstance Win32_OperatingSystem |
  Select-Object Caption, Version, OSArchitecture |
  Format-List |
  Out-File -Append load-generator-hardware.txt

jmeter --version 2>&1 | Tee-Object -FilePath jmeter-version.txt
```

Copy `load-generator-hardware.txt` and `jmeter-version.txt` into `evidence/step4` in the repository. Record whether the machines use Ethernet or Wi-Fi and the approximate link speed. Do not run JMeter on the service PC for assessed measurements.

### Step 9 Fix the common inference configuration

Inspect the current classifier configuration:

```powershell
Select-String -Path app\classifier.py -Pattern 'temperature|format|options'
Select-String -Path .env.example -Pattern 'OLLAMA_MODEL|OLLAMA_TIMEOUT'
```

Before freezing Step 4, agree on and record:

- `temperature: 0` and JSON response mode.
- One fixed context size for all three candidates. `4096` tokens is sufficient for the supplied ticket lengths and avoids comparing unnecessarily different context-memory allocations.
- The exact system prompt and request construction already stored in `app/classifier.py`.
- One Ollama version and one `Q4_K_M` quantization level.

The team added an explicit `num_ctx: 4096` option to `app/classifier.py` before the freeze. Any other configuration correction must also be committed before the freeze. Do not tune the prompt or inference settings separately for each candidate after viewing results.

### Step 10 Complete the environment table

Use the evidence from Steps 3, 4, 5, and 8 to replace every environment `TBD BEFORE BENCHMARK` in Section 5. Include exact version numbers rather than terms such as "latest". Include the network type and the fixed context size.

Check remaining placeholders at any time with:

```powershell
Select-String -Path STEP4.md -Pattern 'TBD BEFORE BENCHMARK|`TBD`'
```

### Step 11 Finalise the bottleneck and category predictions

The team should review Sections 6.1 and 6.3 and either accept the proposed wording or replace it. The final text must predict:

- the first component expected to saturate under load;
- the visible symptom of saturation, such as increasing POST latency or queue growth; and
- the category boundaries expected to produce the most errors, with reasons.

These are hypotheses, not measured findings. Do not run the golden set or a load test to improve them.

### Step 12 Enter numerical predictions for every model

For each candidate, enter:

1. One exact predicted overall accuracy percentage on the 160-ticket golden set.
2. One exact predicted warm single-request latency in seconds for a representative ticket near the measured 140-word median.
3. A predicted pass or fail for R1 through R8.
4. A brief explanation based on parameter count, model design, download size, and CPU-only deployment.

Predictions must be specific. Write `84%` rather than `80-90%`, and `12 seconds` rather than `fast`. It is acceptable for the predictions to be wrong; the assignment assesses whether they were falsifiable and whether the team later explains the difference.

Do not derive these predictions by running golden tickets. If the team uses external published evidence, cite it. If no comparable evidence exists for the exact CPU, state that the latency is a reasoned estimate based on model size and is expected to scale approximately with CPU inference work.

### Step 13 Review the requirements without changing them per model

Review R1-R8 against [`workload/WORKLOAD.md`](workload/WORKLOAD.md). The same thresholds apply to all three candidates. Do not create easier latency or accuracy requirements for a larger or smaller model. If the team decides to change a threshold, document the workload or client reason before seeing benchmark results.

### Step 14 Perform the independent freeze review

A second team member should complete the checklist in Section 8. The reviewer should also inspect the evidence folder:

```powershell
Get-ChildItem evidence\step4 | Select-Object Name, Length, LastWriteTime
git diff --check
git status --short
```

Before the first freeze commit, every placeholder must be complete except the `Freeze commit` line itself, whose hash cannot exist until the commit is created.

### Step 15 Create the freeze commit

Stage the completed Step 4 record and its evidence. Include any final golden-set/supporting-file corrections that have not already been committed:

```powershell
git add STEP4.md evidence\step4
git status --short
git diff --cached --check
git diff --cached --stat
git commit -m "Freeze Step 4 requirements and predictions"
```

Capture the resulting commit hash:

```powershell
$freezeCommit = git rev-parse HEAD
$freezeCommit
```

This first commit is the auditable freeze point. Do not amend or rewrite it after benchmarking begins.

### Step 16 Record the freeze hash in a second metadata commit

Insert the first commit's hash into this document without changing any prediction or requirement:

```powershell
python -c "from pathlib import Path; p=Path('STEP4.md'); s=p.read_text(encoding='utf-8'); p.write_text(s.replace('Freeze commit: TBD BEFORE BENCHMARK', 'Freeze commit: $freezeCommit'), encoding='utf-8')"

git add STEP4.md
git diff --cached
git commit -m "Record Step 4 freeze commit"
git log -2 --oneline
```

Verify there are no remaining pre-benchmark placeholders:

```powershell
Select-String -Path STEP4.md -Pattern 'TBD BEFORE BENCHMARK'
git status --short
```

`Select-String` should produce no output, and `git status --short` should be clean. Step 4 is now complete and Step 5 may begin. After this point, do not edit the requirements or predictions to match observed results. Record outcomes in separate Step 5 files.

## 2. Candidate models

All candidates use an instruction-tuned `Q4_K_M` build. Keeping the quantization level consistent reduces a major source of variation in memory consumption, accuracy, and CPU latency.

| Candidate | Exact Ollama tag | Parameter class | Approximate download | Purpose in the comparison | Licence |
|---|---|---:|---:|---|---|
| [Gemma 3 1B](https://ollama.com/library/gemma3/tags) | `gemma3:1b-it-q4_K_M` | Small, 1B | 815 MB | Fast, low-resource baseline | [Gemma Terms](https://ai.google.dev/gemma/terms) |
| [Qwen3 4B Instruct](https://ollama.com/library/qwen3/tags) | `qwen3:4b-instruct-2507-q4_K_M` | Medium, 4B | 2.5 GB | Predicted balance between accuracy and CPU performance | [Apache 2.0](https://huggingface.co/Qwen/Qwen3-4B-Instruct-2507/blob/main/LICENSE) |
| [Llama 3.1 8B Instruct](https://ollama.com/library/llama3.1/tags) | `llama3.1:8b-instruct-q4_K_M` | Large, 8B | 4.9 GB | Accuracy ceiling and large-model comparison | [Llama 3.1 Community License](https://huggingface.co/meta-llama/Llama-3.1-8B-Instruct/blob/main/README.md) |

This set spans three size classes (1B, 4B, 8B), roughly doubling parameters at each step, so the accuracy-versus-latency trade-off is visible across the range a CPU-only server can plausibly run. Phi-4 Mini 3.8B was considered and dropped before benchmarking to keep one candidate per size class within the available test time; it would have duplicated the 4B class.

### 2.1 Pin the local model artifacts

Pull each exact tag using the same Ollama installation that will run the assessed tests:

```bash
docker compose exec ollama ollama pull gemma3:1b-it-q4_K_M
docker compose exec ollama ollama pull qwen3:4b-instruct-2507-q4_K_M
docker compose exec ollama ollama pull llama3.1:8b-instruct-q4_K_M
docker compose exec ollama ollama list
```

For each model, also preserve the output of:

```bash
docker compose exec ollama ollama show MODEL_TAG --modelfile
```

Do not treat a web-page digest as the assessed digest. Record the identifier produced by the team's local Ollama installation after pulling the model.

| Exact tag | Local Ollama model ID or digest | Pull date | Evidence file |
|---|---|---|---|
| `gemma3:1b-it-q4_K_M` | ID `8648f39daa8f`; weights `sha256:7cd4618c1faf8b7233c6c906dac1694b6a47684b37b8895d470ac688520b9c01` (999.89M params, Q4_K_M, 815 MB) | 2026-10-07 | `evidence/step4/ollama-list.txt`, `gemma3-1b-it-q4_K_M-show.txt`, `gemma3-1b-it-q4_K_M-modelfile.txt` |
| `qwen3:4b-instruct-2507-q4_K_M` | ID `0edcdef34593`; weights `sha256:85e4a5b7b8ef0e48af0e8658f5aaab9c2324c76c1641493f4d1e25fce54b18b9` (4.0B params, Q4_K_M, 2.5 GB) | 2026-10-07 | `evidence/step4/ollama-list.txt`, `qwen3-4b-instruct-2507-q4_K_M-show.txt`, `qwen3-4b-instruct-2507-q4_K_M-modelfile.txt` |
| `llama3.1:8b-instruct-q4_K_M` | ID `46e0c10c039e`; weights `sha256:667b0c1932bc6ffc593ed1d03f895bf2dc8dc6df21db3042284a6f4416b06a29` (8.0B params, Q4_K_M, 4.9 GB) | 2026-10-07 | `evidence/step4/ollama-list.txt`, `llama3-1-8b-instruct-q4_K_M-show.txt`, `llama3-1-8b-instruct-q4_K_M-modelfile.txt` |

## 3. Workload basis

The requirements below use the peak-plus-growth-headroom workload from [`workload/WORKLOAD.md`](workload/WORKLOAD.md):

| Workload component | Required rate |
|---|---:|
| Ticket classifications through `POST /tickets` | 105 per hour, or 1.75 per minute |
| Concurrent agent searches through `GET /search` | 316 per hour, or about 5.27 per minute |
| Total offered mixed load | 421 requests per hour |

The requirement test is an open-loop mixed-load test. The load generator must run on a separate machine from the service, Ollama, and PostgreSQL. Each measured run uses a 2-minute warm-up followed by a 20-minute steady-state measurement window and a 1-minute drain with no new arrivals. Warm-up samples are excluded from the reported results. (Changed from 5 + 60 minutes before the freeze: three runs at three levels for three models would otherwise need more than 30 hours of test time before the submission deadline. At 105 tickets per hour a 20-minute window holds about 35 POST arrivals per run and about 105 across the three runs.)

## 4. Client acceptance requirements

These requirements are fixed for all three models. They describe the client's required service quality, not what is convenient for an individual model. A candidate that misses a requirement is reported as failing it; the threshold is not relaxed after results are observed.

### R1 Sustained ticket throughput

Under an open-loop mixed load of 105 `POST /tickets` requests per hour and 316 `GET /search` requests per hour, the service shall complete at least 105 successful ticket classifications per hour during the 60-minute steady-state window.

The completed ticket rate must not fall behind the offered arrival rate, and the request backlog must not show continuing growth at the end of the run.

**Justification.** The workload model identifies 105 tickets per hour as the peak rate including 30% growth headroom. Meeting only the present-day peak of 81 tickets per hour would leave no capacity margin.

### R2 Ticket classification response time

At the R1 mixed-load condition:

- `POST /tickets` p95 response time shall be no more than **30 seconds**.
- `POST /tickets` p99 response time shall be no more than **60 seconds**.

**Justification.** Classification is synchronous, so its latency is visible to the intake system. A 30-second p95 is below the approximately 34-second mean interval between ticket arrivals at 105 tickets per hour and reduces the risk of sustained queue growth. The p99 threshold limits extreme delays without assuming interactive response times for an automated intake channel.

### R3 Agent search response time

At the R1 mixed-load condition:

- `GET /search` p95 response time shall be no more than **2 seconds**.
- `GET /search` p99 response time shall be no more than **5 seconds**.

**Justification.** Search is used interactively by customer-relations agents. Multi-second delays interrupt case handling even when the slower classification endpoint remains within its own target.

### R4 Request reliability

At the R1 mixed-load condition, the error rate for each endpoint shall be no more than **1.0%**. An error includes a timeout, connection failure, HTTP 5xx response, invalid model JSON, or a response that cannot be validated against the API schema.

All successful `POST /tickets` responses must correspond to exactly one stored ticket. At the end of each run, the increase reported by `GET /stats` must reconcile with the number of successful ticket creations.

### R5 Overall classification accuracy

For each candidate, at least **85.0%** of the frozen 160-ticket golden set shall be classified correctly. This means at least **136 of 160 tickets** must match the final golden label exactly.

**Justification.** Automated routing provides limited value if a large proportion of tickets still require correction. An 85% threshold permits comparison among CPU-suitable local models while requiring at least five out of every six tickets to be routed correctly.

### R6 Per-category classification accuracy

Each of the seven categories shall achieve at least **70.0% accuracy**. Based on the current 160-ticket golden-set distribution after category names are canonicalised, the minimum correct predictions are:

| Category | Golden tickets | Minimum correct |
|---|---:|---:|
| Credit reporting | 33 | 24 |
| Debt collection | 24 | 17 |
| Mortgage | 18 | 13 |
| Credit card | 11 | 8 |
| Bank account or service | 30 | 21 |
| Consumer loan | 16 | 12 |
| Money transfer or service | 28 | 20 |

**Justification.** Overall accuracy alone could hide a model that performs poorly on a smaller category. The per-category threshold prevents the recommendation from sacrificing one routing team to improve the aggregate result.

### R7 Output conformance

At least **99.0%** of golden-set classification calls shall return valid JSON containing exactly one of these category strings:

1. `Credit reporting`
2. `Debt collection`
3. `Mortgage`
4. `Credit card`
5. `Bank account or service`
6. `Consumer loan`
7. `Money transfer or service`

An invalid, additional, differently capitalised, or missing category is counted as both an output-conformance failure and an incorrect classification.

### R8 Deployment constraint

All inference shall run locally through Ollama on the designated CPU-only service machine. No GPU, public model API, or external inference service may be used. During a passing requirement run, the service, database, and Ollama containers shall record zero unexpected restarts or out-of-memory terminations.

## 5. Common test controls

The following controls remain identical across all candidates:

- Service machine, load-generator machine, network path, operating system, Docker version, Ollama version, and Compose configuration.
- `Q4_K_M` quantization.
- System prompt and user-message construction.
- JSON response mode and `temperature: 0`.
- Context-window setting and all other Ollama options.
- Golden-set order for accuracy testing.
- JMeter test plan, CSV source, arrival schedules, duration, timeouts, and result fields.
- Database starting state and reset procedure.
- Warm-up procedure and exclusion rules.
- Three measured runs per performance configuration.

Official performance results for different models must not be collected on different service PCs. Team members may operate different model runs, but all assessed runs must use the same designated service machine. JMeter must run from the same separate load-generator machine for every candidate.

Record the controlled environment before benchmarking:

| Item | Recorded value |
|---|---|
| Service machine CPU model | Intel Core Ultra 7 256V (Lunar Lake), laptop Lenovo 83JT, mains power, Windows power plan Balanced |
| Physical cores and logical processors | 8 cores (4 performance + 4 low-power efficiency), 8 logical processors; Docker VM sees 8 CPUs |
| Service machine RAM | 16 GB (15.55 GB usable); Docker Desktop WSL2 VM limited to 7.53 GiB |
| Service machine OS and version | Windows 11 Home 10.0.26200, 64-bit; containers on WSL2 kernel 6.6.87.2 |
| Docker Engine and Compose versions | Docker Engine 29.5.3 (Docker Desktop), Docker Compose v5.1.4 |
| Ollama image/version | `ollama/ollama:0.12.3` (`ollama --version`: 0.12.3), CPU only (`library=cpu`, 7.5 GiB visible), server defaults `OLLAMA_NUM_PARALLEL=1`, `OLLAMA_KEEP_ALIVE=5m`, `OLLAMA_MAX_QUEUE=512` (`evidence/step4/ollama-server-config.txt`) |
| Load-generator CPU, RAM, and OS | Desktop MSI MS-7C91, AMD Ryzen 5 3600 (6 cores / 12 threads), 31.93 GB RAM, Windows 10 Pro 22H2 (10.0.19045), 64-bit (`evidence/step4/load-generator-hardware.txt`) |
| JMeter version and plugins | Apache JMeter 5.6.3 on Eclipse Temurin OpenJDK 17.0.20.1; no plugins (built-in Open Model Thread Group) (`evidence/step4/jmeter-version.txt`) |
| Network connection between machines | Same home router (`kenyap`, 192.168.1.0/24). Load generator 192.168.1.147 on wired Ethernet (1 Gbps); service PC 192.168.1.106 on Wi-Fi (Intel BE201, Wi-Fi 7). Not isolated from other household traffic. |
| Fixed Ollama context size | `num_ctx: 4096` for every request (`app/classifier.py`), `temperature: 0`, `format: json` |

## 6. Prediction record

Complete this section before the freeze commit. Predictions must be numerical and specific enough to be wrong. Do not revise them after the first benchmark run.

### 6.1 Bottleneck prediction

**Proposed prediction:** CPU inference in Ollama will be the primary bottleneck. `POST /tickets` waits synchronously for token generation, while PostgreSQL inserts and substring searches are expected to consume a smaller share of request time at the modelled workload. At overload, POST latency and queueing are expected to increase before database or search failures appear.

Team-approved wording:

1. **First component to saturate: Ollama CPU inference.** More than 95% of each `POST /tickets` response time will be spent waiting on the Ollama `/api/chat` call. Prompt processing (prefill of roughly 300 input tokens: system prompt plus narrative) will take most of that time, because the JSON answer is only about 12 output tokens. PostgreSQL insert time and API overhead together will stay under 100 ms per request.
2. **Symptom at saturation:** Ollama processes requests effectively one at a time on 8 CPU threads. Once the arrival rate exceeds about 3,600 / (single-request latency in seconds) tickets per hour, `POST /tickets` latency will grow steadily for as long as the overload lasts (unbounded queue growth, not a plateau). Once a queued request waits more than the API's 300-second Ollama timeout, it will fail with HTTP 502. Errors will appear only after that point; there will be no early connection failures.
3. **Predicted stress limit (Qwen3 4B):** the maximum sustainable arrival rate is about **700 tickets per hour** (3,600 / 5 s).
4. **Search is not the bottleneck:** `GET /search` p95 will stay below **0.5 seconds** for every candidate at the 105/h condition. Its latency will rise only when inference saturates all CPU cores, because PostgreSQL competes for the same CPU.

### 6.2 Per-model predictions

Enter one numerical overall-accuracy prediction and one numerical single-request latency prediction for every candidate. The latency prediction must be for one representative ticket on the designated service hardware after model warm-up, using the final common inference configuration.

| Candidate | Predicted overall accuracy | Predicted warm single-request latency | Predicted R1-R8 outcome | Reason for prediction |
|---|---:|---:|---|---|
| Gemma 3 1B | 52% (83/160) | 1.5 s | R1 pass, R2 pass, R3 pass, R4 **fail**, R5 **fail**, R6 **fail**, R7 **fail** (96% conformant), R8 pass | Smallest model. Fastest: about 0.8 GB of weights, prefill of about 300 tokens at about 400 tokens/s on 8 CPU threads. Least able to apply the protocol's priority rules from category names alone, and expected to emit a non-exact category string (for example `Bank account`) on about 4% of tickets. Those become HTTP 502, which also breaks the 1% error budget (R4). |
| Qwen3 4B Instruct | 74% (118/160) | 5 s | R1 pass, R2 pass, R3 pass, R4 pass, R5 **fail**, R6 **fail**, R7 pass, R8 pass | 2.5 GB of weights; prefill about 80 tokens/s and decode about 17 tokens/s on this CPU. Recent instruction tuning with no thinking tokens gives strong format compliance. Predicted to be the most accurate candidate, but still below 85% because the golden labels follow team-specific priority rules (for example Mortgage over loan or debt, and Money transfer as the lowest priority) that the prompt does not state. |
| Llama 3.1 8B Instruct | 71% (114/160) | 10 s | R1 pass, R2 pass, R3 pass, R4 pass, R5 **fail**, R6 **fail**, R7 pass, R8 pass | 4.9 GB of weights, about twice Qwen3 4B, so roughly twice the prefill and decode time. At 105/h, utilisation is about 0.3, so p95 (about 22 s, driven by p95-length tickets of about 305 words) remains under 30 s. Predicted slightly *less* accurate than Qwen3 4B despite its size, because it is an older (2024) instruction tune. |

Latency predictions are reasoned estimates, not measurements: no golden or load ticket was sent to any model before the freeze. Per-model throughput was estimated from the parameter count and download size relative to the service CPU (Intel Core Ultra 7 256V: 4 performance cores plus 4 low-power efficiency cores, 8 threads, LPDDR5X memory). Prefill is compute-bound and decode is memory-bandwidth-bound, so time per ticket is expected to scale roughly linearly with model size. The predicted value is the warm p50 of the sequential accuracy run.

### 6.3 Hardest-category prediction

**Proposed prediction:** The hardest boundaries will be:

1. `Bank account or service` versus `Money transfer or service`, especially for payment applications, digital wallets, and inaccessible funds.
2. `Credit reporting` versus the underlying product category when a mortgage, card, or loan complaint mainly concerns credit-file damage.
3. `Consumer loan` versus `Debt collection` when the narrative discusses both repayment difficulty and collection activity.

Team-approved prediction and reasoning:

1. **Money transfer or service will be the hardest category for every candidate** (predicted per-category accuracy: Qwen3 4B 55%, Llama 3.1 8B 50%, Gemma 3 1B 35%). Payment-app and digital-wallet complaints (Cash App, PayPal, Zelle, Apple Cash) look like account problems. The team protocol also makes Money transfer the lowest-priority category, so the golden labels resolve many of these narratives to `Bank account or service` (for example row 9840), and the models cannot know that rule. Expected confusion: mostly between Money transfer and Bank account, in both directions.
2. **Consumer loan will be second hardest** (Qwen3 4B about 60%). Narratives about repayment difficulty and collection calls will be classified as `Debt collection`, and student or auto loans that damage a credit file as `Credit reporting`.
3. **Credit card** (only 11 tickets, so one error costs 9 percentage points) will lose tickets to `Credit reporting` and `Debt collection`, because the protocol excludes credit-card debt from this category.
4. **Credit reporting and Mortgage will be easiest** (≥ 85% for Qwen3 4B and Llama 3.1 8B). Their vocabulary is distinctive (credit bureau names, "inaccurate information", escrow, foreclosure, servicer).

Every candidate is therefore predicted to fail R6, because Money transfer or service falls below 70%.

## 7. Step 5 measurement levels prepared by Step 4

R1-R8 are accepted or rejected at the peak-plus-headroom condition. Every candidate is load-tested at three levels with three runs each; one candidate (Qwen3 4B) is then stress-tested with a continuous ramp:

| Level | POST tickets/hour | GET searches/hour | Purpose | Runs per candidate |
|---|---:|---:|---|---:|
| Average | 43 | 130 | Typical-load reference | 3 |
| Peak | 81 | 243 | Present-day peak | 3 |
| Peak plus headroom | 105 | 316 | Formal requirement condition (R1-R4) | 3 |
| Stress ramp | 60 rising linearly to 1,200 over 40 minutes | 316 | Determine the maximum sustainable arrival rate; passes through the burst (130/h) and incident-surge (243/h) levels | 1 (Qwen3 4B) |

Off-peak (18/h) is not load-tested separately: it is below the average level, and at that rate a 20-minute window would hold only about six tickets. The within-hour burst and incident-surge rates are covered by the stress ramp rather than run as fixed levels, which keeps the schedule within the available test time.

The exact procedure, scripts and metric definitions are in [`step5/README.md`](step5/README.md).

For every measured arrival rate and candidate, retain the raw `.jtl` file and matching service logs. Report p50, p95, and p99 latency, achieved throughput, and error rate. Performance configurations require three runs, with the mean and spread reported.

## 8. Freeze review

Before committing the prediction record, one team member who did not write the first draft should verify:

- [ ] The requirements still match the cited workload model.
- [ ] Thresholds and pass/fail rules have not been changed to favour a candidate.
- [ ] Exact tags, digests, licences, and evidence paths are complete.
- [ ] Hardware and software versions are complete.
- [ ] Every candidate has numerical accuracy and latency predictions.
- [ ] Bottleneck and hardest-category predictions are specific.
- [ ] No golden-set model results were viewed before the freeze commit.
- [ ] Every pre-benchmark placeholder is complete except the freeze hash, which will be inserted immediately after the first freeze commit.

After this checklist passes, follow Steps 15 and 16 above. Do not revise the prediction sections after the first freeze commit. If a factual recording error must be corrected later, retain the original text in Git history and explain the correction in the final presentation.
