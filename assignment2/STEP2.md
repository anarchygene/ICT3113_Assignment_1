# Step 2: Cascade design and escalation rule

**DRAFT for team review.** This file is the written escalation rule required by the brief. It is frozen in the
same commit as `PREDICTIONS.md`, before any Assignment 2 benchmark (including the cascade accuracy test).
After that commit it is not edited; anything learned later goes in the results write-up.

Open decisions are marked **DECISION** and must be closed before the freeze.

Inputs: `STEP2_DESIGN_INPUTS.md` (memory check and tuning-set analysis), `assignment2/data/tuning_set.csv`
(odd rows), and the Assignment 1 per-ticket answers in `step5/results/<model>/accuracy/predictions.csv`.
Only tuning-set (odd-row) answers were used to design the rule. The only test-set result anyone has seen is
Llama alone (Step 1), which sets the limits.

## 1. Summary

| | |
|---|---|
| Small model (answers first) | Qwen3 4B Instruct, `qwen3:4b-instruct-2507-q4_K_M`, ID `0edcdef34593` |
| Large model (final on escalation) | Llama 3.1 8B Instruct, `llama3.1:8b-instruct-q4_K_M`, ID `46e0c10c039e` |
| Rule type | Category-based (brief, example method 1), plus "escalate if the small model's output is invalid" |
| Setting A | Escalate when Qwen predicts **Credit card** |
| Setting B | **DECISION** (see §4b): escalate when Qwen predicts **Credit card** or **Credit reporting** (recommended), or **Credit card** or **Consumer loan** (current draft in `PREDICTIONS.md`) |
| Prompt and request | Unchanged from Assignment 1 for both models (`app/classifier.py`: same system prompt, `format: json`, `temperature: 0`, `num_ctx: 4096`) |
| Ollama settings | Unchanged from Assignment 1 and identical for every configuration (`OLLAMA_NUM_PARALLEL=1`, `OLLAMA_CONTEXT_LENGTH=4096`, Ollama 0.12.3). See §8 for the open keep-alive question. |

## 2. The rule

Every ticket is classified by Qwen first. Qwen's answer is final unless one of two things happens, in which case the
ticket is sent to Llama and Llama's answer is final.

```
ESCALATE_ON (setting A) = {"Credit card"}
ESCALATE_ON (setting B) = {"Credit card", "Credit reporting"}      # DECISION, see §4b

def triage(narrative):
    small = classify(QWEN, narrative)          # Assignment 1 request, unchanged
    if small is INVALID:
        return classify(LLAMA, narrative)      # escalated, reason = "invalid"
    if small in ESCALATE_ON:
        return classify(LLAMA, narrative)      # escalated, reason = "category"
    return small                               # not escalated

# If the Llama call is INVALID, the request fails with HTTP 502 and the ticket is not stored,
# exactly as in Assignment 1. There is no fall-back to Qwen's answer: the brief makes the
# large model's classification final.
```

**INVALID** means the Assignment 1 parser rejects the answer. Any of the following counts:
- the Ollama call fails, including the 300 s timeout;
- the reply is not JSON, or has no `category` key;
- the value is not exactly one of the seven category strings in `app/categories.py`. Matching is case-sensitive,
  so `bank account or service` is invalid. Qwen produced exactly that in the memory check and 3 times on the full
  golden set in Assignment 1.

The rule uses only what is known when the ticket arrives: Qwen's answer and whether it was valid. It never uses
the true label, ticket length or any other model.

## 3. Why this rule

| Method (brief) | Extra model calls | Tuning-set evidence | Decision |
|---|---|---|---|
| **Category-based** | None | Qwen's errors cluster in one predicted category: when Qwen says "Credit card" it is right only 5/17 times, and Llama gets 10 of those 17 right. Qwen's other predictions are mostly right. | **Chosen** |
| Ticket length | None | Weak signal. Qwen gets 30/40 right on the shorter half and 24/40 on the longer half, so a length cut-off would escalate many tickets Qwen already gets right. | Rejected |
| Agreement (two small answers) | +1 small call on every ticket | Qwen twice costs about 15.8 s at Assignment 1 speeds, more than Llama alone (13.2 s). Gemma + Qwen agreement cannot be faster than Qwen + escalation. | Rejected |
| Self-reported confidence | +1 call on every ticket (the classification prompt is fixed, so confidence needs a separate call) | Not testable from existing records. Small models tend to report high confidence when wrong. | Rejected |

**Why Qwen → Llama and not a Gemma cascade.** Gemma gives 15/80 invalid answers on the tuning set and is right on few
predicted categories, so any Gemma cascade escalates 75–86% of tickets. At that rate it is no faster than Llama alone
(`STEP2_DESIGN_INPUTS.md` §3). Gemma → Qwen fits comfortably in memory, but its final answers would come from Qwen,
which on the tuning set misses Llama's Credit reporting count by a wide margin (7/14 vs 9/14).

## 4. Choosing the settings (tuning set only)

### 4a. What escalating each predicted category is worth

For the tuning tickets where Qwen predicted each category: how many Qwen got right, how many Llama got right on
the same tickets, and the net change in correct answers if that category is escalated.

| Qwen predicts | Tickets | Qwen right | Llama right | Net if escalated |
|---|---:|---:|---:|---:|
| Credit card | 17 | 5 | 10 | **+5** |
| Credit reporting | 8 | 7 | 8 | +1 |
| Debt collection | 10 | 8 | 9 | +1 |
| Bank account or service | 16 | 10 | 10 | 0 |
| Consumer loan | 11 | 7 | 7 | 0 |
| Money transfer or service | 8 | 7 | 7 | 0 |
| Mortgage | 10 | 10 | 9 | −1 |
| (invalid) | 0 | n/a | n/a | always escalated |

Setting A escalates the one category that is clearly worth it. Every other category gains at most one ticket, and
that one-ticket gain is the only evidence for any second category.

### 4b. Replay on the tuning set (simulation using Assignment 1 answers, not a measurement)

Correct counts per true category, 80 tuning tickets. "Est. latency" = Qwen p50 + escalated fraction × Llama p50,
using Assignment 1 sequential medians (Qwen 7.9 s, Llama 13.2 s). It ignores queueing and the memory slowdown in §5.

| True category (n) | Qwen alone | A: Credit card | B (recommended): + Credit reporting | B (draft): + Consumer loan | Llama alone |
|---|---:|---:|---:|---:|---:|
| Credit reporting (14) | 7 | 9 | 9 | 9 | 9 |
| Debt collection (13) | 8 | 8 | **9** | **9** | 11 |
| Mortgage (11) | 10 | 10 | 10 | 10 | 10 |
| Credit card (5) | 5 | 5 | 5 | 5 | 5 |
| Bank account or service (16) | 10 | 12 | 12 | 12 | 10 |
| Consumer loan (8) | 7 | 7 | 7 | 6 | 6 |
| Money transfer or service (13) | 7 | 8 | 8 | 8 | 9 |
| **Overall (80)** | **54** | **59** | **60** | **59** | **60** |
| Escalated | 0 | 17 (21%) | 25 (31%) | 28 (35%) | 80 (100%) |
| Est. mean latency | 7.9 s | 10.7 s | 12.0 s | 12.5 s | 13.2 s |

Reading the table:

- **A** recovers 5 tickets, mostly Credit reporting and Bank tickets that Qwen mislabels as Credit card, for 21%
  escalation. It does not help Debt collection, which is the tightest test-set limit (floor 6/11, with Llama alone
  at 7/11). This risk is already the main stated way `PREDICTIONS.md` could be wrong.
- **B** adds one more category to protect Debt collection. Both candidate second categories recover the same single
  Debt-collection ticket on the tuning set (row 9965 via Credit reporting, or row 9849 via Consumer loan).
- **Credit reporting is the better second category on the tuning evidence:** it escalates fewer tickets (25 vs 28),
  gains one more ticket overall (60 vs 59), and does not give back Qwen's Consumer-loan advantage (7/8 vs 6/8).
  It also follows the order of §4a mechanically: add categories by net gain per escalated ticket.
- **Caveat for both:** the B-vs-A difference rests on one or two tickets, so it is a judgement, not a finding.
  Consumer loan has one extra cost on the tuning set: Llama returns an invalid answer on row 9853, which Qwen had
  right, so under the Consumer-loan list that ticket would become a 502.

**DECISION:** confirm setting B. If the team switches B to Credit card + Credit reporting, update `PREDICTIONS.md`
§0–§3 to match before the freeze. A third setting (the draft's C, adding Bank account) is not tested: the brief asks
for two settings, and on the tuning set C escalates 55% and is predicted to be no faster than Llama alone.

## 5. Memory check (brief: both models must be resident)

Run on the Lenovo service PC, Docker VM 8 CPUs / 7.53 GiB, unchanged from Assignment 1.
Script: `assignment2/scripts/memory_check.py`. Evidence: `assignment2/evidence/memory_check/qwen_llama.txt`
(and the two other pairs).

- After alternating calls, `ollama ps` lists both models (Llama 5.6 GB, Qwen 3.7 GB, both "100% CPU"), and the
  Ollama container uses 6.92 of 7.53 GiB.
- **The first switch is a reload, not a resident switch.** When Llama first loaded (call 3), Qwen dropped out of the
  loaded list. Qwen's next call (call 5) reloaded it (`load_duration` 9.2 s). From then on both stayed listed and every
  load took under 0.4 s. The warm-up in §7 therefore runs both models twice before a run starts.
- **Calls slow down once the models alternate**, even without reloads. Llama went from 3.3 s back-to-back to
  33.2 s and 15.8 s; Qwen from 2.1 s to 22.2 s. The likely cause is memory pressure, with model pages being dropped
  and re-read from disk. This comes from 8 short calls, so it is a risk to measure, not a result. The speed test decides
  whether the cascade is faster in practice.

## 6. Implementation in the service

The cascade lives inside `POST /tickets`. The endpoint still accepts one ticket and returns one category, and
`GET /search` and `GET /stats` are unchanged.

| Item | Implementation |
|---|---|
| Switch | `CASCADE_ENABLED=false` reproduces Assignment 1 exactly (one model, `OLLAMA_MODEL`). This is how the single-model configurations run. |
| Models | `CASCADE_SMALL_MODEL=qwen3:4b-instruct-2507-q4_K_M`, `CASCADE_LARGE_MODEL=llama3.1:8b-instruct-q4_K_M` |
| Setting | `CASCADE_ESCALATE_ON` = comma-separated category names: `Credit card` for A; the confirmed B list for B. Changing setting is an `.env` change plus an API restart; no code change between settings. |
| Request to each model | The Assignment 1 request with only the model name changed |
| Hiding the answering model | In cascade mode the response's and database's `model` field is one fixed label for every ticket (default `cascade:<small>><large>`, or `CASCADE_LABEL`), so the caller cannot tell which model answered |
| Per-ticket log line | One line per `POST /tickets`, in both modes: `triage {"request_id", "mode", "small_model", "small_answer", "small_ms", "escalated", "reason", "final_model", "large_ms", "category", "outcome"}`. `reason` is `accept`, `category` or `invalid` in cascade mode and `single` otherwise. `small_answer` is the category or `invalid`. `outcome` is `error` when the final model's answer is invalid (HTTP 502). `request_id` is the JMeter `X-Request-ID`. |
| Escalation fraction | Count of `"escalated": true` ÷ count of `triage` lines in the API log for the run, matched to the JMeter request IDs |
| Code | `app/cascade.py` (rule and log line), `app/config.py` (settings, validated at start-up: unknown category names stop the API), `app/classifier.py` (model parameter only), `app/main.py` (endpoint calls the triage). Tests: `tests/test_cascade.py`. |

## 7. Warm-up for cascade runs

Before each cascade run (after the Ollama restart that every run starts with):

1. Send the team's three fixed warm-up tickets through `POST /tickets`, one at a time. Discard the timings.
2. Run `docker compose exec -T api python - < assignment2/scripts/cascade_warmup.py` and save its output with
   the run. It sends one fixed warm-up ticket directly to each model through Ollama, using the service's request,
   in the order Qwen, Llama, Qwen, Llama. This forces the first-switch reload from §5 to happen before the run.
3. Start only if the script prints `READY`: both models are listed by Ollama and the last two calls loaded in under 1 s.
   Also save `ollama ps` from the container with the run.

The single-model runs use the normal Assignment 1 warm-up.

## 8. Open items before the freeze

1. **DECISION, setting B** (§4b): Credit card + Credit reporting (recommended), or Credit card + Consumer loan.
   Then align `PREDICTIONS.md`.
2. **Keep-alive.** Ollama unloads a model after 5 minutes unused (`OLLAMA_KEEP_ALIVE=5m`, the Assignment 1 setting).
   At the Step 4 arrival rate (one ticket every 2×S seconds; roughly every 26 s if S is about 13 s) and 21% escalation,
   Llama is called only about every 2 minutes. That leaves a real chance of a gap over 5 minutes in some runs, after
   which the next escalation pays a full Llama load (30 s in the memory check). The brief calls that a loading
   result, not a cascade result. Options:
   - ask the lecturer whether a longer `OLLAMA_KEEP_ALIVE`, set once and held constant for every Assignment 2
     configuration, is in scope (it affects scheduling, not thread count, parallelism or context length); or
   - keep 5m and check every cascade run's Ollama log for load events, reporting any as such.
3. **Arrival rate in `PREDICTIONS.md`.** Its "p50 under load" column is predicted at the Assignment 1 headroom load
   (105 tickets/h plus searches). The Step 4 speed test uses the brief's rate, one ticket every 2×S seconds, and
   POSTs only. Restate the load predictions for that rate before the freeze.
4. **Code done, unit tests pass** (§6; `pytest -q`, Ollama faked). Still to do on the Lenovo: rebuild the API image,
   run a few tuning tickets with `CASCADE_ENABLED=false` and confirm the same answers as Assignment 1, then a few with
   the cascade on and check the `triage` log lines and the warm-up script.
5. **Freeze commit:** `STEP2.md` and `PREDICTIONS.md` together, before the cascade accuracy test and before any speed run.
