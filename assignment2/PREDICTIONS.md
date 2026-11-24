# Assignment 2 predictions (frozen before any Assignment 2 benchmark)

**DRAFT for team review. Once committed, this file is not edited; later analysis goes in a separate file.**

Revision (24 Nov, before the freeze): cut to the brief's **two** cascade settings, matched setting B to `STEP2.md`
(Credit card + Credit reporting), and restated the load predictions at the Assignment 2 speed-test rate.
The earlier draft is in the history (commit `1ba8388`).

Basis: Assignment 1 per-ticket answers on the **tuning set only** (odd rows, 80 tickets; `assignment2/STEP2_DESIGN_INPUTS.md`
and `STEP2.md` §4), the Step 2 memory check, the Assignment 1 load-test results (`step5/results/summary.md`), and Llama's
Step 1 test-set result (used only to set the limits in `ACCURACY_LIMITS.md`). No Qwen or Gemma test-set (even-row)
accuracy was used.

## 0. Configurations to be tested

Single models (required by the brief): **Q** = Qwen3 4B alone, **L** = Llama 3.1 8B alone (the reference), and Gemma 3 1B alone.

Cascade (one cascade, two settings, rule in `STEP2.md`): Qwen3 4B answers first. The ticket escalates to Llama 3.1 8B if
Qwen's output is invalid or its predicted category is on the escalation list; otherwise Qwen's answer is final.

| Configuration | Escalation list (Qwen's predicted category) | Tuning-set replay: accuracy / escalated |
|---|---|---|
| Q (single model) | n/a | 54/80 / 0% |
| **A** (cascade setting 1) | Credit card | 59/80 / 21% |
| **B** (cascade setting 2) | Credit card, Credit reporting | 60/80 / 31% |
| L (single model) | n/a | 60/80 / 100% (every ticket is Llama) |

A escalates the one predicted category that is clearly worth a Llama call on the tuning set (+5 tickets). B adds the
next category by net gain per escalated ticket (`STEP2.md` §4a). On the tuning set this recovers one Debt-collection
ticket, the category with the least margin on the test set.

**Gemma 3 1B alone** is predicted to fail both limits by a wide margin (35.0% on the tuning set, 15/80 invalid), so it is
not speed-tested. Gemma cascades are not tested: they would escalate 75–86% of tickets and be no faster than Llama alone.

## 1. Fastest configuration that satisfies the accuracy limits

**Prediction: setting A (Qwen → Llama, escalate on "Credit card") is the fastest configuration that passes all eight limits.**

1. **Qwen alone (Q) fails.** Predicted 54/80 overall (passes the 53/80 floor by one ticket), but it fails **Credit reporting
   (10/19, floor 12)** and **Debt collection (5/11, floor 6)**. On the tuning set Qwen labels 5 of 14 Credit-reporting
   tickets as Credit card and gets only 7/14 Credit reporting right. Q is therefore not speed-tested.
2. **A fixes Credit reporting.** Escalating Qwen's "Credit card" answers sends most of the misrouted Credit-reporting
   tickets to Llama (tuning: Credit reporting 7/14 → 9/14 for 21% escalation).
3. **A passes Debt collection with no margin (predicted 6/11 against a floor of 6).** This is the most likely way for the
   prediction to be wrong. Qwen's Debt-collection errors on the tuning set are spread over Bank account, Consumer loan and
   Credit reporting, so no single-category rule catches them all. If A fails, it fails on Debt collection, and **B is then
   predicted to be the fastest passing configuration**: B also escalates Qwen's "Credit reporting" answers, which recovers
   the Debt-collection ticket Qwen labelled Credit reporting on the tuning set (row 9965).
4. **Credit card must be 6/6 (floor 85%).** Under A and B every ticket Qwen calls Credit card goes to Llama, which scored
   6/6 in Step 1, and Qwen got all 5 true Credit-card tuning tickets right. Predicted 6/6 for every configuration.
5. **A is faster than Llama alone** because about three quarters of tickets never reach Llama. It is predicted to be faster
   than B because each escalation adds a full Llama call *and* a model switch, which the memory check showed to be slow for
   this pair.

## 2. Cascade predictions per setting (test set, 80 tickets)

### 2a. Escalation, accuracy and median latency

**Sequential** = the accuracy run: one ticket at a time through `POST /tickets` (Llama alone was 13.2 s p50 in Assignment 1).

**Under load** = the Assignment 2 speed test (brief Step 4): one ticket every 2×S seconds, where S is Llama alone's middle
time on three typical tickets. S is not yet measured; we predict **S ≈ 13 s**, i.e. one ticket every 26 s, about 30 tickets
per 13-minute run. Load figures are given in seconds at S = 13 s and as a multiple of S, so they can be checked if S differs.

| Configuration | Escalated (of 80) | Overall accuracy | Passes all limits? | p50 sequential | p50 under load | p95 under load (3 runs pooled) |
|---|---:|---:|---|---:|---:|---:|
| Q | 0 (0%) | 54/80 = 67.5% | **no** (Credit reporting, Debt collection) | 7.9 s | not tested | not tested |
| **A** | **19 (24%)** | **60/80 = 75.0%** | **yes** (Debt collection at the floor) | **10.5 s** | **8.5 s (0.65 S)** | **34 s (2.6 S)** |
| B | 30 (38%) | 61/80 = 76.25% | yes | 11.5 s | 9.8 s (0.75 S) | 35 s (2.7 S) |
| L | 80 (100%) | 61/80 = 76.25% (measured, Step 1) | yes | 13.2 s (A1) | 14.3 s (1.1 S) | 26 s (2.0 S) |

Reasons for the numbers:

- **Escalation is higher than on the tuning set** (A 24% vs 21%, B 38% vs 31%) because the test set has more
  Credit-reporting tickets (19 vs 14). Credit reporting is the true category Qwen most often turns into "Credit card"
  (escalated by A and B), and the category Qwen predicts when it does get it right (also escalated by B).
- **Accuracy:** each setting = Llama's Step 1 count per category, plus the tuning-set difference between that setting and
  Llama alone, with tuning-set gains halved since they rest on one or two tickets. A is predicted one ticket below Llama.
  B is predicted equal to Llama, because the extra Credit-reporting escalation recovers a Debt-collection ticket and
  costs nothing else on the tuning set.
- **Sequential p50 is above the simple replay** (A replay 8.8 s). The replay adds Qwen and Llama times. It ignores the
  alternating-model slowdown the memory check showed for Qwen + Llama (calls 4–10× slower once the models alternate,
  at 92% of VM memory). Predicted penalty: about +1.5 s on the median for A, growing with escalation.
- **Llama alone under load:** the rate is set so Llama is busy about half the time. Poisson arrivals still cause short
  queues, so its p50 is predicted a little above S (1.1 S), and its pooled p95 about 2 S (long tickets plus queueing).
- **Cascade p50 under load:** the median ticket is a Qwen-only ticket for both A (76% not escalated) and B (62%), so p50
  stays well below Llama alone. Queueing behind escalated Llama work and the model-switch slowdown push it above Qwen's
  own time. Ratios to Llama alone follow the earlier draft's Assignment 1-load predictions (A 0.59, B 0.68 of Llama alone),
  scaled to Llama alone = 1.1 S.
- **p95 under load:** escalated tickets pay for Qwen + switch + Llama, so both settings' p95 is predicted **above Llama
  alone's** (about 2.6–2.7 S vs 2.0 S). The cascade improves the median, not the tail.
- **Escalation under load** (speed-test tickets, rows 9000–9839) is predicted at A 20–28% and B 32–42%. These are different
  tickets from the test set, so it can differ from the accuracy-test figure.

### 2b. Predicted per-category correct counts (test set)

| Category (floor) | Q | A | B | L (Step 1) |
|---|---:|---:|---:|---:|
| Credit reporting (12/19) | **10** ✗ | 13 | 13 | 14 |
| Debt collection (6/11) | **5** ✗ | 6 | 7 | 7 |
| Mortgage (4/7) | 5 | 5 | 5 | 5 |
| Credit card (6/6) | 6 | 6 | 6 | 6 |
| Bank account or service (8/14) | 10 | 11 | 11 | 10 |
| Consumer loan (4/8) | 6 | 6 | 6 | 5 |
| Money transfer or service (12/15) | 12 | 13 | 13 | 14 |
| **Overall (53/80)** | 54 | 60 | 61 | 61 |

## 3. Categories that lose the most accuracy when Qwen's answer is accepted

Compared with Llama alone, for tickets Qwen keeps (not escalated):

1. **Debt collection loses the most:** predicted −2 tickets with Q, −1 with A, 0 with B.
   On the tuning set Qwen got 8/13 against Llama's 11/13, and its errors went to three different categories (Bank account,
   Consumer loan, Credit reporting), so escalating any one predicted category recovers at most one of them.
2. **Credit reporting loses the most without escalation** (Q: −4) but only −1 under A and B, because its errors are
   concentrated in one wrong label (Credit card) that both settings escalate.
3. **Money transfer or service is third** (Q −2, A and B −1). Qwen sends these to Bank account or Credit card;
   escalating Credit card catches only some of them.
4. **Bank account or service and Consumer loan gain** when Qwen is accepted (+1 each under A and B). On the tuning set
   Qwen beats Llama on both, and neither setting escalates them.
5. **Mortgage and Credit card lose nothing** in any configuration (Qwen's Mortgage predictions were 10/10 correct on the
   tuning set).

## 4. What would show these predictions wrong

- A fails a limit (most likely Debt collection < 6/11, or Credit card < 6/6). The fastest passing configuration is then B,
  or Llama alone if B also fails.
- Qwen alone passes both limits.
- A's escalation is outside 15–30% (12–24 tickets), or B's outside 28–48% (22–38 tickets), in the accuracy test.
- A's sequential p50 is ≥ 13.2 s (no faster than Llama) or ≤ 9.0 s (the switch penalty is negligible).
- Under load, A's or B's p50 is ≥ Llama alone's p50 (no speed gain), or A's p95 is below Llama alone's p95.
- B is faster than A under load.
- Debt collection is not the category with the largest loss under A.
