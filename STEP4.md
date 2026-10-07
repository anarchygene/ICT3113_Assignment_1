# Step 4 Candidate Models Requirements and Prediction Record

This document defines the candidate model set, the client acceptance requirements, and the prediction record for Assignment 1. Complete every field marked `TBD BEFORE BENCHMARK`, verify the golden set, and commit this document before sending any golden-set ticket through a candidate model.

## 1. Preconditions and freeze point

Step 5 must not begin until all of the following are complete:

- [ ] The golden set contains 150 to 200 tickets and uses only the seven exact category names.
- [ ] Two independent label sheets, the labelling protocol, disagreement resolutions, and the agreement statistic are retained.
- [ ] The final golden set is committed.
- [ ] All four model tags and locally observed digests are recorded below.
- [ ] The test hardware and software environment is recorded below.
- [ ] Every numerical prediction in Section 6 is completed.
- [ ] This prediction record is committed.

The commit containing the frozen golden set and completed prediction record must predate the first benchmark run. Record that commit here:

`Freeze commit: TBD BEFORE BENCHMARK`

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

### Step 6 Pull the four exact model tags

```powershell
docker compose exec ollama ollama pull gemma3:1b-it-q4_K_M
docker compose exec ollama ollama pull phi4-mini:3.8b-q4_K_M
docker compose exec ollama ollama pull qwen3:4b-instruct-2507-q4_K_M
docker compose exec ollama ollama pull llama3.1:8b-instruct-q4_K_M
```

All four commands must finish successfully. Do not replace a failed model with a different tag without updating the candidate justification and committing that decision before benchmarking.

### Step 7 Capture the local IDs, quantization, metadata, and model files

```powershell
docker compose exec -T ollama ollama list |
  Tee-Object -FilePath evidence\step4\ollama-list.txt

$models = @(
  'gemma3:1b-it-q4_K_M',
  'phi4-mini:3.8b-q4_K_M',
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
- One fixed context size for all four candidates. `4096` tokens is sufficient for the supplied ticket lengths and avoids comparing unnecessarily different context-memory allocations.
- The exact system prompt and request construction already stored in `app/classifier.py`.
- One Ollama version and one `Q4_K_M` quantization level.

If the team adds an explicit `num_ctx: 4096` option or makes another configuration correction, commit it before the freeze. Do not tune the prompt or inference settings separately for each candidate after viewing results.

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

Review R1-R8 against [`workload/WORKLOAD.md`](workload/WORKLOAD.md). The same thresholds apply to all four candidates. Do not create easier latency or accuracy requirements for a larger or smaller model. If the team decides to change a threshold, document the workload or client reason before seeing benchmark results.

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
| [Phi-4 Mini](https://ollama.com/library/phi4-mini/tags) | `phi4-mini:3.8b-q4_K_M` | Medium, 3.8B | 2.5 GB | Medium-size competitor designed for constrained environments | [MIT](https://huggingface.co/microsoft/Phi-4-mini-instruct/blob/main/LICENSE) |
| [Qwen3 4B Instruct](https://ollama.com/library/qwen3/tags) | `qwen3:4b-instruct-2507-q4_K_M` | Medium, 4B | 2.5 GB | Predicted balance between accuracy and CPU performance | [Apache 2.0](https://huggingface.co/Qwen/Qwen3-4B-Instruct-2507/blob/main/LICENSE) |
| [Llama 3.1 8B Instruct](https://ollama.com/library/llama3.1/tags) | `llama3.1:8b-instruct-q4_K_M` | Large, 8B | 4.9 GB | Accuracy ceiling and large-model comparison | [Llama 3.1 Community License](https://huggingface.co/meta-llama/Llama-3.1-8B-Instruct/blob/main/README.md) |

This set spans three size classes. The two similarly sized medium candidates also allow the team to observe whether model family and instruction tuning affect classification quality when parameter count is approximately controlled.

### 2.1 Pin the local model artifacts

Pull each exact tag using the same Ollama installation that will run the assessed tests:

```bash
docker compose exec ollama ollama pull gemma3:1b-it-q4_K_M
docker compose exec ollama ollama pull phi4-mini:3.8b-q4_K_M
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
| `gemma3:1b-it-q4_K_M` | `TBD BEFORE BENCHMARK` | `TBD` | `TBD` |
| `phi4-mini:3.8b-q4_K_M` | `TBD BEFORE BENCHMARK` | `TBD` | `TBD` |
| `qwen3:4b-instruct-2507-q4_K_M` | `TBD BEFORE BENCHMARK` | `TBD` | `TBD` |
| `llama3.1:8b-instruct-q4_K_M` | `TBD BEFORE BENCHMARK` | `TBD` | `TBD` |

## 3. Workload basis

The requirements below use the peak-plus-growth-headroom workload from [`workload/WORKLOAD.md`](workload/WORKLOAD.md):

| Workload component | Required rate |
|---|---:|
| Ticket classifications through `POST /tickets` | 105 per hour, or 1.75 per minute |
| Concurrent agent searches through `GET /search` | 316 per hour, or about 5.27 per minute |
| Total offered mixed load | 421 requests per hour |

The requirement test is an open-loop mixed-load test. The load generator must run on a separate machine from the service, Ollama, and PostgreSQL. Each measured run uses a 5-minute warm-up followed by a 60-minute steady-state measurement window. Warm-up samples are excluded from the reported results.

## 4. Client acceptance requirements

These requirements are fixed for all four models. They describe the client's required service quality, not what is convenient for an individual model. A candidate that misses a requirement is reported as failing it; the threshold is not relaxed after results are observed.

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
| Service machine CPU model | `TBD BEFORE BENCHMARK` |
| Physical cores and logical processors | `TBD BEFORE BENCHMARK` |
| Service machine RAM | `TBD BEFORE BENCHMARK` |
| Service machine OS and version | `TBD BEFORE BENCHMARK` |
| Docker Engine and Compose versions | `TBD BEFORE BENCHMARK` |
| Ollama image/version | `TBD BEFORE BENCHMARK` |
| Load-generator CPU, RAM, and OS | `TBD BEFORE BENCHMARK` |
| JMeter version and plugins | `TBD BEFORE BENCHMARK` |
| Network connection between machines | `TBD BEFORE BENCHMARK` |
| Fixed Ollama context size | `TBD BEFORE BENCHMARK` |

## 6. Prediction record

Complete this section before the freeze commit. Predictions must be numerical and specific enough to be wrong. Do not revise them after the first benchmark run.

### 6.1 Bottleneck prediction

**Proposed prediction:** CPU inference in Ollama will be the primary bottleneck. `POST /tickets` waits synchronously for token generation, while PostgreSQL inserts and substring searches are expected to consume a smaller share of request time at the modelled workload. At overload, POST latency and queueing are expected to increase before database or search failures appear.

Team-approved wording:

`TBD BEFORE BENCHMARK`

### 6.2 Per-model predictions

Enter one numerical overall-accuracy prediction and one numerical single-request latency prediction for every candidate. The latency prediction must be for one representative ticket on the designated service hardware after model warm-up, using the final common inference configuration.

| Candidate | Predicted overall accuracy | Predicted warm single-request latency | Predicted R1-R8 outcome | Reason for prediction |
|---|---:|---:|---|---|
| Gemma 3 1B | `TBD BEFORE BENCHMARK` | `TBD BEFORE BENCHMARK` | `TBD` | Smallest candidate; expected to be fastest but least accurate |
| Phi-4 Mini 3.8B | `TBD BEFORE BENCHMARK` | `TBD BEFORE BENCHMARK` | `TBD` | Medium-size model aimed at constrained and latency-sensitive use |
| Qwen3 4B Instruct | `TBD BEFORE BENCHMARK` | `TBD BEFORE BENCHMARK` | `TBD` | Predicted best accuracy-throughput balance |
| Llama 3.1 8B Instruct | `TBD BEFORE BENCHMARK` | `TBD BEFORE BENCHMARK` | `TBD` | Largest candidate; expected to be most accurate or close to it, but slowest |

### 6.3 Hardest-category prediction

**Proposed prediction:** The hardest boundaries will be:

1. `Bank account or service` versus `Money transfer or service`, especially for payment applications, digital wallets, and inaccessible funds.
2. `Credit reporting` versus the underlying product category when a mortgage, card, or loan complaint mainly concerns credit-file damage.
3. `Consumer loan` versus `Debt collection` when the narrative discusses both repayment difficulty and collection activity.

Team-approved prediction and reasoning:

`TBD BEFORE BENCHMARK`

## 7. Step 5 measurement levels prepared by Step 4

R1-R8 are accepted or rejected at the peak-plus-headroom condition. Step 5 should additionally measure the lower levels and then perform a stress ramp:

| Level | POST tickets/hour | GET searches/hour | Purpose |
|---|---:|---:|---|
| Off-peak | 18 | 55 | Low-load reference |
| Average | 43 | 130 | Typical-load reference |
| Peak | 81 | 243 | Present-day peak |
| Peak plus headroom | 105 | 316 | Formal requirement condition |
| Within-hour burst | 130 | 316 | Short burst measurement |
| Incident surge | 243 | 316 | Initial stress level |
| Stress ramp | Increase until a limit is observed | 316 | Determine the system limit |

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
