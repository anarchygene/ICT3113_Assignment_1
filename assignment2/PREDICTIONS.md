# Assignment 2 predictions (frozen before any Assignment 2 benchmark)

**DRAFT for team review. Once committed, this file is not edited; later analysis goes in a separate file.**

Basis: Assignment 1 per-ticket answers on the **tuning set only** (odd rows, 80 tickets; `assignment2/STEP2_DESIGN_INPUTS.md`),
the Step 2 memory check, the Assignment 1 load-test results (`step5/results/summary.md`), and Llama's Step 1 test-set
result (used only to set the limits in `ACCURACY_LIMITS.md`). No Qwen or Gemma test-set (even-row) accuracy was used.

## 0. Configurations to be tested

Every cascade uses Qwen3 4B as the small model and Llama 3.1 8B as the large model. Qwen answers first.
The ticket escalates to Llama if Qwen's output is invalid or its predicted category is on the escalation list; otherwise Qwen's answer is final.

| Setting | Escalation list (Qwen's predicted category) | Tuning-set replay: accuracy / escalated |
|---|---|---|
| Q | none (Qwen alone; invalid output only) | 54/80 / 0% |
| A | Credit card | 59/80 / 21% |
| B | Credit card, Consumer loan | 59/80 / 35% |
| C | Credit card, Consumer loan, Bank account or service | 59/80 / 55% |
| L | everything (Llama alone, reference) | 60/80 / 100% |

The list grows from A to C in order of how often Qwen is wrong when it predicts that category on the tuning set
(Credit card 5/17, Bank account 10/16, Consumer loan 7/11). B and C are the points along the speed/accuracy trade-off.

Gemma 3 1B cascades are not tested as a main candidate: on the tuning set Gemma would escalate 75–86% of tickets
(15/80 invalid outputs), which is predicted to be slower than Llama alone.

## 1. Fastest configuration that satisfies the accuracy limits

**Prediction: setting A (Qwen → Llama, escalate on "Credit card") is the fastest configuration that passes all eight limits.**

1. **Qwen alone (Q) fails.** Predicted 54/80 overall (passes the 53/80 floor by one ticket) but it fails **Credit reporting
   (10/19, floor 12)** and **Debt collection (5/11, floor 6)**. On the tuning set Qwen labels 5 of 14 Credit-reporting
   tickets as Credit card and gets only 7/14 Credit reporting right.
2. **A fixes Credit reporting.** Escalating Qwen's "Credit card" answers sends most of the misrouted Credit-reporting tickets to
   Llama (tuning: Credit reporting 7/14 → 9/14 for 21% escalation).
3. **A passes Debt collection with no margin (predicted 6/11 against a floor of 6).** This is the most likely way for the
   prediction to be wrong. Qwen's Debt-collection errors on the tuning set are spread over Bank account, Consumer loan and
   Credit reporting, so no single-category rule catches them. If A fails, it will fail on Debt collection, and B
   (which also escalates Consumer loan) is predicted to be the fastest passing setting instead.
4. **Credit card must be 6/6 (floor 85%).** Under A every ticket Qwen calls Credit card goes to Llama, which scored 6/6 in Step 1;
   Qwen got all 5 true Credit-card tuning tickets right. Predicted 6/6 for every setting.
5. **A is faster than Llama alone** because about three quarters of tickets never reach Llama. It is predicted to be faster than B and C
   because each escalation adds a full Llama call *and* a model switch, which the memory check showed to be slow for this pair.

## 2. Cascade predictions per setting (test set, 80 tickets)

### 2a. Escalation, accuracy and median latency

Sequential = the accuracy run (one ticket at a time, as in Assignment 1 Step 5 accuracy runs; Llama alone was 13.2 s p50).
Load = the speed test at the Assignment 1 headroom load (105 tickets/h + 316 searches/h); Llama alone was 11.0 s p50 there and Qwen alone 4.9 s.

| Setting | Escalated (of 80) | Overall accuracy | Passes all limits? | p50 sequential | p50 under load |
|---|---:|---:|---|---:|---:|
| Q | 0 (0%) | 54/80 = 67.5% | **no** (Credit reporting, Debt collection) | 7.9 s | 4.9 s |
| A | **19 (24%)** | **60/80 = 75.0%** | **yes** (Debt collection at the floor) | **10.5 s** | **6.5 s** |
| B | 29 (36%) | 60/80 = 75.0% | yes | 11.5 s | 7.5 s |
| C | 44 (55%) | 61/80 = 76.25% | yes | 14.0 s | 10.5 s |
| L | 80 (100%) | 61/80 = 76.25% (measured, Step 1) | yes | 13.2 s (A1) | 11.0 s (A1) |

Reasons for the numbers:

- **Escalation is a little higher than on the tuning set** (A 24% vs 21%) because the test set has more Credit-reporting tickets
  (19 vs 14), and Credit reporting is the true category Qwen most often turns into "Credit card".
- **Accuracy:** setting = Llama's Step 1 count per category plus the tuning-set difference between that setting and Llama alone,
  with tuning-set gains halved, since they rest on one or two tickets. Overall, A and B are predicted one ticket below Llama, and C equal to Llama.
- **Sequential p50 is above the simple replay** (A replay 8.8 s). The replay adds Qwen and Llama times; it ignores the
  alternating-model slowdown the memory check showed for Qwen + Llama (calls 4–10× slower once the models alternate, at 92% of VM memory).
  Predicted penalty: about +1.5 s on the median for A, growing with escalation.
- **Under load the median ticket is still a Qwen-only ticket for A and B**, so p50 stays near Qwen's 4.9 s plus queueing behind
  escalated Llama work. For C, over half the tickets include a Llama call, so p50 approaches Llama alone.
- **C is predicted slower than Llama alone in the sequential run** (14.0 vs 13.2 s): 55% of tickets pay for two models plus a switch.
  So C is accurate but has no speed benefit.
- **p95 under load:** escalated tickets pay for Qwen + switch + Llama, so A's p95 is predicted to be **about 25 s, above Llama alone's
  ~18 s p95 at average/peak load**. The cascade improves the median, not the tail.

### 2b. Predicted per-category correct counts (test set)

| Category (floor) | Q | A | B | C | L (Step 1) |
|---|---:|---:|---:|---:|---:|
| Credit reporting (12/19) | **10** ✗ | 13 | 13 | 14 | 14 |
| Debt collection (6/11) | **5** ✗ | 6 | 7 | 7 | 7 |
| Mortgage (4/7) | 5 | 5 | 5 | 5 | 5 |
| Credit card (6/6) | 6 | 6 | 6 | 6 | 6 |
| Bank account or service (8/14) | 10 | 11 | 11 | 10 | 10 |
| Consumer loan (4/8) | 6 | 6 | 5 | 5 | 5 |
| Money transfer or service (12/15) | 12 | 13 | 13 | 14 | 14 |
| **Overall (53/80)** | 54 | 60 | 60 | 61 | 61 |

## 3. Categories that lose the most accuracy when Qwen's answer is accepted

Compared with Llama alone, for tickets Qwen keeps (not escalated):

1. **Debt collection loses the most** under every cascade setting: predicted −2 tickets with Q, −1 with A, 0 with B and C.
   On the tuning set Qwen got 8/13 against Llama's 11/13, and its errors went to three different categories (Bank account,
   Consumer loan, Credit reporting), so escalating any one predicted category recovers at most one of them.
2. **Credit reporting loses the most without escalation** (Q: −4) but almost nothing under A (−1), because its errors are
   concentrated in one wrong label (Credit card) that A escalates.
3. **Money transfer or service is third** (Q −2, A −1). Qwen sends these to Bank account or Credit card.
4. **Bank account or service and Consumer loan gain** when Qwen is accepted (+1 each under A): on the tuning set Qwen beats
   Llama on both, so escalating them (B, C) gives those gains back.
5. **Mortgage and Credit card lose nothing** in any setting (Qwen's Mortgage predictions were 10/10 correct on the tuning set).

## 4. What would show these predictions wrong

- A fails a limit (most likely Debt collection < 6/11, or Credit card < 6/6) → the fastest passing setting is B or C, or none.
- A's escalation fraction falls outside 15–30% (12–24 tickets).
- A's sequential p50 is ≥ 13.2 s (no faster than Llama) or ≤ 9.0 s (the switch penalty is negligible).
- Debt collection is not the category with the largest loss under A.
- C is faster than Llama alone in the sequential run.
