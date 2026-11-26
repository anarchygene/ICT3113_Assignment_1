# Assignment 2 predictions (frozen before any Assignment 2 benchmark)

**Frozen.** Committed together with `STEP2.md`, before any Assignment 2 benchmark. This file is not edited after that
commit; later analysis goes in a separate file.

Revision (25 Nov, before the freeze): the cascade is now **Gemma 3 1B → Llama 3.1 8B**. The earlier Qwen → Llama
design cannot be tested, because the two models do not both stay loaded on the Lenovo (`STEP2.md` §5,
`evidence/preflight_lenovo/PREFLIGHT.md`). The Qwen → Llama predictions are in the history (commit `e07eac8`).

Basis: Assignment 1 per-ticket answers and latencies on the **tuning set only** (odd rows, 80 tickets; `STEP2.md` §4),
the Lenovo memory check (25 Nov), the Assignment 1 load-test results (`step5/results/summary.md`), and Llama's Step 1
test-set result (used only to set the limits in `ACCURACY_LIMITS.md`). The test set's category sizes come from
`ACCURACY_LIMITS.md`. No Qwen, Gemma or cascade test-set (even-row) answers were used.

"Fastest" means the lowest p50 under load at the speed-test rate (brief Step 4), as the brief reports p50 per run.

## 0. Configurations to be tested

Single models (required by the brief): **Q** = Qwen3 4B alone, **L** = Llama 3.1 8B alone (the reference), and
**G** = Gemma 3 1B alone.

Cascade (one cascade, two settings, rule in `STEP2.md`): Gemma 3 1B answers first. The ticket escalates to Llama 3.1 8B
if Gemma's output is invalid or its predicted category is not on the accept list; otherwise Gemma's answer is final.

| Configuration | Accept list (Gemma's predicted category) | Tuning-set replay: accuracy / escalated |
|---|---|---|
| G (single model) | n/a | 28/80 / 0% |
| Q (single model) | n/a | 54/80 / 0% |
| **A** (cascade setting 1) | Mortgage, Debt collection | 56/80 / 75% |
| **B** (cascade setting 2) | Mortgage | 58/80 / 86% |
| L (single model) | n/a | 60/80 / 100% (every ticket is Llama) |

## 1. Fastest configuration that satisfies the accuracy limits

**Prediction: Llama alone is the fastest configuration that passes all eight limits. The cascade does not improve on it.**

1. **Qwen alone (Q) fails.** Predicted 54/80 overall (passes the 53/80 floor by one ticket), but it fails **Credit reporting
   (10/19, floor 12)** and **Debt collection (5/11, floor 6)**. On the tuning set Qwen labels 5 of 14 Credit-reporting
   tickets as Credit card and gets only 7/14 Credit reporting right. Q would be the fastest configuration if it passed,
   so it is the main way this prediction could be wrong. It is speed-tested only if it passes.
2. **Gemma alone (G) fails both limits by a wide margin** (35.0% on the tuning set, 15/80 invalid). It is not speed-tested.
3. **Setting A fails Consumer loan (predicted 3/8, floor 4/8).** On the tuning set, Gemma labels several Consumer-loan
   tickets as Debt collection or Mortgage, and A accepts both. This costs 2 of Llama's 6 Consumer-loan tickets. The
   category has only 8 test tickets, so one ticket decides it.
4. **Setting B passes, with no margin on Consumer loan (predicted 4/8 against a floor of 4).**
5. **B is slower than Llama alone.** B escalates about 90% of test tickets. Each escalated ticket pays for Gemma (about
   2.4 s) *and then* Llama, so B's median ticket is slower than Llama's. On the tuning-set replay, B's median is 15.4 s
   against Llama's 14.1 s, and its mean is 14.4 s against 13.9 s.
6. **Even if A passed, it would not be faster at the median.** A's median ticket is still an escalated one
   (tuning replay: 14.7 s against 14.1 s). Only its mean is lower, by about 6% (13.1 s against 13.9 s).

## 2. Cascade predictions per setting (test set, 80 tickets)

### 2a. Escalation, accuracy and median latency

**Sequential** = the accuracy run: one ticket at a time through `POST /tickets` (Llama alone was 13.2 s p50 in Assignment 1).

**Under load** = the Assignment 2 speed test (brief Step 4): one ticket every 2×S seconds, where S is Llama alone's middle
time on three typical tickets. S is not yet measured; we predict **S ≈ 13 s**, i.e. one ticket every 26 s, about 30 tickets
per 13-minute run. Load figures are given in seconds at S = 13 s and as a multiple of S, so they can be checked if S differs.

| Configuration | Escalated (of 80) | Overall accuracy | Passes all limits? | p50 sequential | p50 under load | p95 under load (3 runs pooled) |
|---|---:|---:|---|---:|---:|---:|
| Q | 0 (0%) | 54/80 = 67.5% | **no** (Credit reporting, Debt collection) | 7.9 s | not tested | not tested |
| A | 64 (80%) | 57/80 = 71.25% | **no** (Consumer loan) | 13.8 s | 14.9 s (1.15 S) | 29 s (2.25 S) |
| B | 72 (90%) | 59/80 = 73.75% | yes (Consumer loan at the floor) | 14.4 s | 15.6 s (1.2 S) | 29 s (2.25 S) |
| **L** | 80 (100%) | 61/80 = 76.25% (measured, Step 1) | **yes** | 13.2 s (A1) | **14.3 s (1.1 S)** | **26 s (2.0 S)** |

Reasons for the numbers:

- **Escalation is higher than on the tuning set** (A 80% vs 75%, B 90% vs 86%). Each true category's tuning-set
  escalation rate was applied to that category's test-set size. The test set has more Credit-reporting tickets (19 vs 14),
  and every tuning Credit-reporting ticket escalated under both settings: Gemma either calls them Credit reporting
  (not accepted) or gives an invalid answer.
- **Accuracy:** each setting = Llama's Step 1 count per category, plus the tuning-set difference between that setting
  and Llama alone, scaled to the test-set category size and rounded. Every difference is a loss (A: Consumer loan −2,
  Bank −1, Money transfer −1; B: Consumer loan −1, Bank −1). No category gains, so there was nothing to halve.
- **Sequential p50** = Llama's Assignment 1 p50 (13.2 s) × the ratio of each setting's replayed median to Llama's on the
  tuning set (A 14.7/14.1, B 15.4/14.1). The replay adds the Assignment 1 per-ticket Gemma and Llama times. Model
  switching adds little: once both are loaded, a switch costs 0.1–0.3 s of loading (`STEP2.md` §5).
- **Llama alone under load:** the rate is set so Llama is busy about half the time. Poisson arrivals still cause short
  queues, so its p50 is predicted a little above S (1.1 S), and its pooled p95 about 2 S (long tickets plus queueing).
- **Cascade under load:** p50 and p95 = Llama alone's under-load figures × the same tuning-replay ratios (p50: A 1.04,
  B 1.09; p95: 26.7/23.7 = 1.13 for both). A's mean service time is about 6% below Llama's, so its queues are slightly
  shorter, which may bring its p50 close to Llama's. This is the main uncertainty in the A latency figure.
- **p95:** escalated long tickets pay for Gemma + Llama, so both settings' p95 is predicted above Llama alone's.
- **Escalation under load** (speed-test tickets, rows 9000–9839) is predicted at A 70–85% and B 82–95%. These are different
  tickets from the test set, so it can differ from the accuracy-test figure.

### 2b. Predicted per-category correct counts (test set)

| Category (floor) | Q | A | B | L (Step 1) |
|---|---:|---:|---:|---:|
| Credit reporting (12/19) | **10** ✗ | 14 | 14 | 14 |
| Debt collection (6/11) | **5** ✗ | 7 | 7 | 7 |
| Mortgage (4/7) | 5 | 5 | 5 | 5 |
| Credit card (6/6) | 6 | 6 | 6 | 6 |
| Bank account or service (8/14) | 10 | 9 | 9 | 10 |
| Consumer loan (4/8) | 6 | **3** ✗ | 4 | 5 |
| Money transfer or service (12/15) | 12 | 13 | 14 | 14 |
| **Overall (53/80)** | 54 | 57 | 59 | 61 |

## 3. Categories that lose the most accuracy when Gemma's answer is accepted

Compared with Llama alone, for tickets Gemma keeps (not escalated):

1. **Consumer loan loses the most:** predicted −2 tickets with A, −1 with B. On the tuning set, 4 of A's 7 wrong accepted
   answers were Consumer-loan tickets that Gemma called Debt collection or Mortgage.
2. **Bank account or service is second:** −1 with A and B.
3. **Money transfer or service:** −1 with A, 0 with B.
4. **Credit reporting, Debt collection, Mortgage and Credit card lose nothing.** On the tuning set, every accepted Gemma
   answer for a ticket in these true categories was right, and Gemma's Credit-reporting answers are never accepted.

## 4. What would show these predictions wrong

- A passes all limits (most likely if Consumer loan reaches 4/8), or B fails one (most likely Consumer loan < 4/8 or
  Credit card < 6/6).
- Qwen alone passes both limits. It would then be the fastest passing configuration.
- A's escalation is outside 70–88% (56–70 tickets), or B's outside 82–96% (66–77 tickets), in the accuracy test.
- A's or B's sequential p50 is below Llama alone's 13.2 s.
- Under load, B's p50 is below Llama alone's p50, or either setting's pooled p95 is below Llama alone's.
- Under load, A is not faster than B at p50.
- Consumer loan is not the category with the largest loss under A.
