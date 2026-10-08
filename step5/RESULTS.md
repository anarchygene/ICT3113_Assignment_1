# Step 5 and Step 6 Results, verdicts and recommendation (Team P1-9)

Every number here comes from files in this repository:

- Load and stress: `step5/results/levels.csv` (mean / min / max across 3 runs), `runs.csv` (per run), `summary.md`, and the stress `timeline.csv`, all produced by `python step5/scripts/analyse_jtl.py` from the raw `.jtl` files.
- Accuracy: `step5/results/<model>/accuracy/summary.json`, `predictions.csv` and `confusion_matrix.csv`.
- Service logs: `evidence/step5/logs/`. Predictions: `STEP4.md`, frozen at commit `3567f80` before any benchmark.

Format: mean of 3 runs [min–max]. Load level "headroom" = 105 POST/h + 316 search/h (the R1–R4 condition).

## 1. Accuracy on the 160-ticket golden set

| | Gemma 3 1B | Qwen3 4B | Llama 3.1 8B |
|---|---:|---:|---:|
| Overall (R5 ≥ 85%) | 48/160 = **30.0%** | 110/160 = **68.8%** | 121/160 = **75.6%** |
| Output conformance (R7 ≥ 99%) | 131/160 = 81.9% | 157/160 = 98.1% | 159/160 = **99.4%** |
| Credit reporting (n 33) | 69.7% | **51.5%** | 69.7% |
| Debt collection (n 24) | 29.2% | 62.5% | 75.0% |
| Mortgage (n 18) | 61.1% | 83.3% | 83.3% |
| Credit card (n 11) | 9.1% | 90.9% | 100.0% |
| Bank account or service (n 30) | 13.3% | 66.7% | **66.7%** |
| Consumer loan (n 16) | 12.5% | 81.2% | 68.8% |
| Money transfer or service (n 28) | **0.0%** | 71.4% | 82.1% |
| Categories ≥ 70% (R6) | 0 / 7 | 4 / 7 | 4 / 7 |
| Sequential single-request latency p50 / p95 | 2.4 s / 4.1 s | 7.9 s / 14.0 s | 13.2 s / 25.6 s |

Where each model goes wrong (confusion matrices in each model's `accuracy/summary.md`):

- **Gemma 3 1B.** 29 outputs are invalid; 26 of them only because of capitalisation (`Consumer Loan` ×24, `Credit Reporting` ×2), plus `Venmo`, `Loan` and `Bank Error`. Of the valid outputs, 18 of 30 Bank-account tickets went to Credit reporting, and 11 of 28 Money-transfer tickets to Consumer loan. Gemma over-predicts Credit reporting.
- **Qwen3 4B.** 9 of 33 Credit-reporting tickets went to Credit card, and 5 Bank-account tickets also went to Credit card. Money transfer and Bank account are confused in both directions (5 and 2). The 3 invalid outputs are lowercase names, e.g. `bank account or service`.
- **Llama 3.1 8B.** Errors are spread out: Credit reporting → Credit card 5, Bank account → Money transfer 4, and Credit card absorbs errors from most rows (16 tickets wrongly predicted as Credit card). 1 invalid output: `Student loan`.

## 2. Load tests: open-loop, 3 runs per level, 2 min warm-up + 20 min window

### POST /tickets

| Model | Level | p50 s | p95 s | p99 s | Achieved/h | Offered/h | Error % |
|---|---|---|---|---|---|---|---|
| Gemma 3 1B | average | 1.88 [1.38–2.82] | 3.63 [2.53–5.83] | 3.63 [2.53–5.83] | 28 [24–33] | 38 [36–42] | 23.8 [21.4–25.0] |
| | peak | 1.59 [1.36–1.74] | 6.71 [2.69–12.99] | 7.27 [2.96–13.97] | 66 [63–69] | 78 [75–81] | 14.1 [12.0–15.4] |
| | headroom | 1.55 [1.53–1.56] | 3.07 [2.67–3.27] | 3.60 [2.90–4.55] | 85 [84–87] | 103 [99–105] | 16.5 [15.2–17.1] |
| Qwen3 4B | average | 4.37 [4.10–4.53] | 9.65 [9.00–10.69] | 9.65 [9.00–10.69] | 37 [33–42] | 38 [36–42] | 0 |
| | peak | 4.87 [4.02–5.37] | 12.11 [10.44–12.95] | 13.07 [11.85–14.37] | 77 [75–81] | 78 [75–81] | 0 |
| | headroom | 4.93 [4.63–5.11] | 11.83 [10.10–12.77] | 14.04 [10.17–17.62] | 102 [99–105] | 103 [99–105] | 0 |
| Llama 3.1 8B | average | 10.20 [9.29–11.95] | 24.17 [18.46–35.42] | 24.17 [18.46–35.42] | 37 [33–42] | 38 [36–42] | 0 |
| | peak | 9.43 [7.68–10.39] | 18.71 [18.18–19.28] | 24.00 [19.70–28.30] | 75 [69–81] | 78 [75–81] | 0 |
| | headroom | 10.99 [9.29–12.06] | **47.52 [18.21–89.69]** | **52.12 [18.22–97.41]** | 97 [93–105] | 103 [99–105] | 1.9 [0–5.7]* |

\* The 2 errors in Llama headroom run 3 are JMeter test-end aborts ("Socket closed"); the server completed both with 201 (`/stats` delta 38). Server-side error rate: 0%. See `step5/README.md` §8.

Why p50 and p99 are sometimes equal: only about 12–35 POSTs fall in each 20-minute window, so nearest-rank p95/p99 can be the maximum.

### GET /search (concurrent agent load)

p95 at headroom: Gemma 0.12 s, Qwen 0.11 s, Llama 0.15 s. Worst p99 in any run was 1.41 s (Gemma peak, run 2), still within R3. Search error rate was 0% in all 27 runs.

### Llama at headroom, per run (why the spread is large)

| Run | p95 | p99/max | Achieved/h | Note |
|---|---|---|---|---|
| 1 | 18.2 s | 18.2 s | 105 | pass |
| 2 | 34.7 s | 40.7 s | 93 | queue builds after closely spaced arrivals |
| 3 | 89.7 s | 97.4 s | 93 | 5 arrivals within ~1.2 min (min 20.6–21.8), each taking 13–25 s, gave a queue of 43–97 s |

With about 13 s mean service time (long tickets about 25 s), utilisation at 105/h is about 0.4. Random clustering of arrivals then produces multi-minute queue spikes, so Llama has no burst margin on this CPU.

## 3. Stress test: Qwen3 4B, one run, POST ramp 60 → 1,200/h over 40 min, search fixed at 316/h

From `step5/results/qwen3-4b/stress_60-1200ph_40min/run1/timeline.csv`:

| Ramp phase (minutes) | Offered POST/h | Completed/h | Max backlog | POST p50 latency |
|---|---:|---:|---:|---|
| 10–20 | 425 | 420 | 3 (recovers) | 4–21 s |
| 15–20 | 450 | 430 | 3 (recovers) | 7–21 s |
| 21–30 | 720 | 480 | 38 (rising every minute) | 52 s → 280 s |
| 30–41 | 1,050 | falls to 0–8 per min | n/a | 300 s, then HTTP 502 timeouts |

- **Limit found:** completions plateau at about **470–480 tickets/h**. Below about 450/h offered the system keeps up with no lasting backlog; from minute 21 (about 600/h offered) the backlog and latency grow without bound.
- **Failure mode:** queued requests reach the API's 300-second Ollama timeout and fail with HTTP 502. There are no connection failures and no crashes; all containers show 0 restarts and no out-of-memory kills.
- Search stayed fast throughout (p95 0.13 s, p99 0.50 s) while the CPU was saturated.
- **Bottleneck diagnosis:** Ollama CPU inference. `OLLAMA_NUM_PARALLEL=1`, so tickets are classified strictly one at a time. POST latency is dominated by queueing behind the model, and nothing else saturates. Over 2,956 successful load-test requests, JMeter's elapsed time exceeds the API-logged duration by a median of 34 ms (p95 about 112 ms, max 1.4 s): Wi-Fi plus connection setup. That is negligible against multi-second classification, but it is most of a search's ~40 ms response time.

## 4. Reconciliation

Across all 28 runs (3,640 JMeter samples), every sample has exactly one service-log line with the same request ID. Exceptions, all explained in `step5/README.md` §8:

- 73 samples have a different status: 71 in the stress run and 2 in Llama headroom run 3. All are JMeter aborting in-flight requests at test end; the server log shows the real outcome.
- `/stats` deltas equal JMeter successful POSTs in 26 of 28 runs. The other 2 are the same abort cases.

## 5. Requirement verdicts at the R1–R4 condition (105 POST/h + 316 search/h)

| Req | Threshold | Gemma 3 1B | Qwen3 4B | Llama 3.1 8B |
|---|---|---|---|---|
| R1 throughput | ≥ 105 successful/h, no growing backlog | **FAIL**: 85/h successful (16.5% rejected) | **PASS**: 102 of 103/h offered, backlog ≤ 1; stress shows 430/h sustained with no growing backlog (see note) | **FAIL**: 93/h in 2 of 3 runs, backlog up to 4 |
| R2 POST latency | p95 ≤ 30 s, p99 ≤ 60 s | PASS (3.1 / 3.6 s) | PASS (11.8 / 14.0 s) | **FAIL** (p95 47.5 s; 2 of 3 runs over 30 s) |
| R3 search latency | p95 ≤ 2 s, p99 ≤ 5 s | PASS (0.12 / 0.18 s) | PASS (0.11 / 0.14 s) | PASS (0.15 / 0.25 s) |
| R4 errors | ≤ 1% per endpoint; `/stats` reconciles | **FAIL** (16.5%) | PASS (0%; reconciles 9/9) | PASS on server log (0%); JMeter shows 1.9% from test-end aborts |
| R5 overall accuracy | ≥ 85% | **FAIL** 30.0% | **FAIL** 68.8% | **FAIL** 75.6% |
| R6 per category | each ≥ 70% | **FAIL** 0/7 | **FAIL** 4/7 | **FAIL** 4/7 |
| R7 conformance | ≥ 99% | **FAIL** 81.9% | **FAIL** 98.1% | PASS 99.4% |
| R8 CPU-only, no restarts or OOM | 0 | PASS | PASS | PASS |

R1 note for Qwen: in each 20-minute window the random-arrival generator produced 34–35 arrivals (103/h offered), so the literal completed count is 102/h. Qwen completed every arrival except the one in flight at the window end, its backlog never exceeded 1, and the stress run shows 430/h sustained with no growing backlog, more than 4× the requirement. We judge R1 met in substance and state the literal figure.

R8 evidence: `ollama ps` shows "100% CPU" for every model (`evidence/step5/deploy-*.txt`), the Ollama log shows `library=cpu`, and the `evidence/step5/logs/containers-*.txt` files show restarts = 0 and OOMKilled = false.

## 6. Predictions vs outcomes (predictions frozen at commit `3567f80`)

| Prediction | Predicted | Measured | Verdict |
|---|---|---|---|
| Bottleneck | Ollama CPU inference; >95% of POST time; latency grows unbounded, then 502 at 300 s | Confirmed: search stays ~0.1 s while POST queues; 502 at 300 s in stress | **Right** |
| Search p95 at 105/h | < 0.5 s | 0.11–0.15 s | **Right** |
| Qwen stress limit | ~700/h | ~470–480/h | **Wrong** (−32%), because single-request latency was 7.9 s, not 5 s |
| Gemma accuracy / latency | 52% / 1.5 s | 30.0% / 2.4 s | Wrong: −22 pts, 1.6× slower |
| Qwen accuracy / latency | 74% / 5 s | 68.8% / 7.9 s | Wrong: −5 pts, 1.6× slower |
| Llama accuracy / latency | 71% / 10 s | 75.6% / 13.2 s | Wrong: +4.6 pts, 1.3× slower |
| Accuracy ranking | Qwen > Llama > Gemma | Llama > Qwen > Gemma | **Wrong** |
| Gemma R-outcomes | R1–R3 pass, R4–R7 fail | R1 also fails (errors cut successful throughput to 85/h) | Mostly right |
| Qwen R-outcomes | R1–R4, R7, R8 pass; R5, R6 fail | R7 fails (98.1%) | Mostly right |
| Llama R-outcomes | R1–R4, R7, R8 pass; R5, R6 fail | R1 and R2 fail (queueing at 105/h) | Wrong on performance |
| Gemma conformance | 96% | 81.9% | Wrong: capitalisation not anticipated |
| Hardest category | Money transfer, for every model | Gemma: Money transfer 0%. Qwen: Credit reporting 51.5%. Llama: Bank account 66.7% | Right for Gemma only |
| Easiest categories | Credit reporting, Mortgage ≥ 85% | Mortgage 83%; Credit reporting 51–70% | **Wrong** |

**Why we were wrong:**

1. *Latency, 1.3–1.6× underestimated for every model.* We scaled from parameter count on 8 equal cores. The 256V has 4 performance cores and 4 low-power efficiency cores, and llama.cpp splits work evenly, so the slow cores pace each step. Inference also runs inside a WSL2 VM, and JSON-constrained decoding adds overhead. Because the error is consistent across models, it is a hardware-model error, not a model-specific one.
2. *Llama at 105/h.* We reasoned from mean utilisation (about 0.3–0.4) and ignored the variance of Poisson arrivals combined with 13–25 s service times. Bursts, not averages, broke R2.
3. *Accuracy.* The prompt lists only category names. Our golden labels follow team protocol rules the model never sees (e.g. Apple Cash → Bank account, Credit card excludes card debt, Money transfer is the lowest priority). Larger models follow general meaning better (Llama), and the newest mid-size model was not more accurate (Qwen).
4. *Credit reporting.* We expected credit-bureau vocabulary to make this category easy. Instead, Qwen sent 9 of 33 to Credit card, yet only 4 of those 9 narratives mention a card at all. So this is not simple product-name matching. The cause is not yet diagnosed and needs ticket-level inspection in Assignment 2.

## 7. Recommendation (Step 6)

**No candidate meets all eight requirements on the client's CPU-only hardware. No model can be recommended for fully automatic routing:** none reaches 85% overall or 70% in every category (R5, R6).

Given that finding, our recommendation is to **deploy Qwen3 4B Instruct (`qwen3:4b-instruct-2507-q4_K_M`, ID `0edcdef34593`) as an assisted-routing tool**: it proposes a category, and an agent confirms it before routing. The reasons:

- It is the **only candidate meeting every service-quality requirement (R1–R4, R8)** at peak plus 30% growth. Its POST p95 is 11.8 s against a 30 s limit, with 0% errors, and its measured capacity of about 470/h is **4.5× the 105/h requirement**, enough to absorb within-hour bursts (130/h) and incident surges (243/h).
- **Llama 3.1 8B is +6.8 points more accurate (75.6% vs 68.8%)** and the only model passing R7. But on this hardware it **fails R1 and R2** at the requirement load (p95 up to 90 s), and its single-stream capacity of about 270/h (3,600 / 13.2 s) leaves no margin for bursts. Our workload model makes peak capacity a hard requirement, so we do not trade it away for 7 points of accuracy that still miss R5.
- **Gemma 3 1B is not deployable.** It is fast, but rejects 16.5% of tickets (R4) and is only 30% accurate.
- In assisted mode, a misroute costs one agent correction rather than a wrongly routed ticket. At 68.8% accuracy, roughly 2 in 3 tickets need only a confirmation.

**Requirements no candidate meets, stated plainly:** R5 (overall ≥ 85%) and R6 (every category ≥ 70%). Qwen also fails R7 (98.1%, 3 lowercase answers).

**For Assignment 2, from the diagnosed causes:**

1. Case-insensitive category matching would recover Qwen's 3 invalid outputs (R7 → 100%) and Gemma's 26.
2. Putting the protocol's category definitions and priority rules in the system prompt targets the measured confusions (Credit reporting ↔ Credit card, Bank account ↔ Money transfer).
3. More or faster CPU cores per Ollama instance, or `OLLAMA_NUM_PARALLEL`/batching, would give Llama burst headroom.
