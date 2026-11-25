# Step 2: Cascade design and escalation rule

**DRAFT for team review.** This file is the written escalation rule required by the brief. It is frozen in the
same commit as `PREDICTIONS.md`, before any Assignment 2 benchmark (including the cascade accuracy test).
After that commit it is not edited; anything learned later goes in the results write-up.

**Revision (25 Nov, before the freeze): the pair is now Gemma → Llama.** The earlier draft used Qwen → Llama.
The Lenovo pre-flight (`evidence/preflight_lenovo/PREFLIGHT.md`) showed that Qwen and Llama cannot both stay loaded
in the 7.53 GiB Docker VM, and the brief says a cascade is only tested with both models resident. The Qwen → Llama
draft is in the history (commit `e07eac8`).

Items still open before the freeze are listed in §8.

Inputs: `STEP2_DESIGN_INPUTS.md` (tuning-set analysis), `evidence/preflight_lenovo/` (memory check on the test
machine), `assignment2/data/tuning_set.csv` (odd rows), and the Assignment 1 per-ticket answers and latencies in
`step5/results/<model>/accuracy/predictions.csv`. Only tuning-set (odd-row) answers were used to design the rule.
The only test-set result anyone has seen is Llama alone (Step 1), which sets the limits.

## 1. Summary

| | |
|---|---|
| Small model (answers first) | Gemma 3 1B, `gemma3:1b-it-q4_K_M`, ID `8648f39daa8f` |
| Large model (final on escalation) | Llama 3.1 8B Instruct, `llama3.1:8b-instruct-q4_K_M`, ID `46e0c10c039e` |
| Rule type | Category-based (brief, example method 1), plus "escalate if the small model's output is invalid" |
| Setting A | Accept Gemma's answer when it predicts **Mortgage** or **Debt collection**; escalate everything else |
| Setting B | Accept Gemma's answer only when it predicts **Mortgage**; escalate everything else |
| Prompt and request | Unchanged from Assignment 1 for both models (`app/classifier.py`: same system prompt, `format: json`, `temperature: 0`, `num_ctx: 4096`) |
| Ollama settings | Identical for every Assignment 2 configuration: `OLLAMA_NUM_PARALLEL=1`, `OLLAMA_CONTEXT_LENGTH=4096`, Ollama 0.12.3, as in Assignment 1. **One change from Assignment 1:** `OLLAMA_KEEP_ALIVE=30m` (was the 5 min default), set in `compose.yaml`, so both cascade models stay resident during a run (§8). |

## 2. The rule

Every ticket is classified by Gemma first. Gemma's answer is final only if it is valid and its predicted category is
on the accept list. Otherwise the ticket is sent to Llama, and Llama's answer is final.

```
ACCEPT (setting A) = {"Mortgage", "Debt collection"}
ACCEPT (setting B) = {"Mortgage"}

def triage(narrative):
    small = classify(GEMMA, narrative)         # Assignment 1 request, unchanged
    if small is INVALID:
        return classify(LLAMA, narrative)      # escalated, reason = "invalid"
    if small not in ACCEPT:
        return classify(LLAMA, narrative)      # escalated, reason = "category"
    return small                               # not escalated

# If the Llama call is INVALID, the request fails with HTTP 502 and the ticket is not stored,
# exactly as in Assignment 1. There is no fall-back to Gemma's answer: the brief makes the
# large model's classification final.
```

**INVALID** means the Assignment 1 parser rejects the answer. Any of the following counts:
- the Ollama call fails, including the 300 s timeout;
- the reply is not JSON, or has no `category` key;
- the value is not exactly one of the seven category strings in `app/categories.py`. Matching is case-sensitive.
  Gemma gave an invalid answer on 15 of the 80 tuning tickets in Assignment 1.

The rule uses only what is known when the ticket arrives: Gemma's answer and whether it was valid. It never uses
the true label, ticket length or any other model.

## 3. Why this pair and this rule

**Why Gemma → Llama.** It is the only pair with Llama that stays resident (§5).

- **Qwen → Llama** does not fit in memory. It was the earlier draft's choice and looked better on paper.
- **Gemma → Qwen** fits, but it cannot beat Qwen alone. On the tuning set, every accept list scores at most 53/80,
  against Qwen alone's 54/80, and the best of those lists still escalates 86% of tickets. Qwen alone is already
  predicted to fail two category limits (`PREDICTIONS.md` §1).

**Why a category rule.**

| Method (brief) | Extra model calls | Tuning-set evidence | Decision |
|---|---|---|---|
| **Category-based** | None | Gemma is reliable on few predicted categories, but on two of them (Mortgage 8/11, Debt collection 5/9) accepting its answer costs only 2 tickets each and saves 11 and 9 Llama calls (§4a). | **Chosen** |
| Ticket length | None | No useful signal. Gemma gets 16/40 right on the shorter half and 12/40 on the longer half, and its invalid answers are spread over both (9 and 6). | Rejected |
| Agreement (two small answers) | +1 small call on every ticket | A second small model would have to stay resident next to Gemma and Llama; Qwen + Llama alone does not fit. Gemma asked twice with different wording is untested, and needs a new prompt (Assignment 1's is fixed). It would add about 2.4 s to every ticket on top of escalating most of them. | Rejected |
| Self-reported confidence | +1 call on every ticket (the classification prompt is fixed, so confidence needs a separate call) | Not testable from existing records. Gemma is often confidently wrong (15 invalid answers, 12/32 right when it says Credit reporting). | Rejected |

**What to expect from this cascade.** Gemma is right on only 28/80 tuning tickets, so any Gemma cascade that stays
near Llama's accuracy has to escalate most tickets: 75% for A and 86% for B. On the tuning-set replay, A's mean
latency is about 6% below Llama alone's and B's is about 4% above. Both medians are above Llama alone's (§4b). The
brief allows this outcome: "it is acceptable to conclude that the cascade did not improve on it."

## 4. Choosing the settings (tuning set only)

### 4a. What accepting each predicted category is worth

For the tuning tickets where Gemma predicted each category: how many Gemma got right, how many Llama got right on
the same tickets, and the change in correct answers if Gemma's answer is accepted instead of escalated. Accepting a
category saves one Llama call per ticket in it.

| Gemma predicts | Tickets (Llama calls saved) | Gemma right | Llama right | Net if accepted | Calls saved per ticket lost |
|---|---:|---:|---:|---:|---:|
| Mortgage | 11 | 8 | 10 | −2 | **5.5** |
| Debt collection | 9 | 5 | 7 | −2 | **4.5** |
| Credit reporting | 32 | 12 | 21 | −9 | 3.6 |
| Bank account or service | 4 | 2 | 4 | −2 | 2.0 |
| Consumer loan | 7 | 1 | 5 | −4 | 1.75 |
| Credit card | 1 | 0 | 1 | −1 | 1.0 |
| Money transfer or service | 1 | 0 | 1 | −1 | 1.0 |
| (invalid) | 15 | 0 | 11 | n/a | always escalated |

Categories are added to the accept list in order of Llama calls saved per ticket lost:

- **B** accepts the best category, Mortgage.
- **A** adds the next one, Debt collection.
- **Credit reporting is next, and is not accepted.** It would save 32 Llama calls but lose 9 tickets, taking A from
  56/80 to 47/80, below the overall limit of 53/80.

### 4b. Replay on the tuning set (simulation using Assignment 1 answers and latencies, not a measurement)

Correct counts per true category, 80 tuning tickets. Latency is simulated per ticket from the Assignment 1
accuracy-run times: Gemma's time, plus Llama's time if the ticket escalates. It ignores queueing and model switching
(§5 shows a switch costs about 0.1–0.3 s once both models are loaded).

| True category (n) | Gemma alone | A: accept Mortgage + Debt collection | B: accept Mortgage | Llama alone |
|---|---:|---:|---:|---:|
| Credit reporting (14) | 12 | 9 | 9 | 9 |
| Debt collection (13) | 5 | 11 | 11 | 11 |
| Mortgage (11) | 8 | 10 | 10 | 10 |
| Credit card (5) | 0 | 5 | 5 | 5 |
| Bank account or service (16) | 2 | 9 | 9 | 10 |
| Consumer loan (8) | 1 | **4** | 5 | 6 |
| Money transfer or service (13) | 0 | 8 | 9 | 9 |
| **Overall (80)** | **28** | **56** | **58** | **60** |
| Escalated | 0 | 60 (75%) | 69 (86%) | n/a |
| of which invalid / category | n/a | 15 / 45 | 15 / 54 | n/a |
| Mean latency | 2.5 s | 13.1 s | 14.4 s | 13.9 s |
| Median latency | 2.4 s | 14.7 s | 15.4 s | 14.1 s |
| p95 latency | 3.8 s | 26.7 s | 26.7 s | 23.7 s |

Reading the table:

- **A** saves 20 of 80 Llama calls for 4 tickets (Consumer loan −2, Bank −1, Money transfer −1). Consumer loan falls
  to 4/8 on the tuning set. Its test-set floor is 4/8, against Llama's 5/8, so A is at risk on that category
  (`PREDICTIONS.md` §1).
- **B** saves 11 Llama calls for 2 tickets (Consumer loan −1, Bank −1).
- **Escalated tickets are slower than Llama alone**, because they pay for Gemma first. Since most tickets escalate,
  the median ticket is an escalated one, so both settings' medians are above Llama alone's. Only A's mean is lower.
- **Caveat:** the A-vs-B difference rests on two tickets, so it is a judgement, not a finding.

**Wrong answers that slip through** (brief, example method 1): tuning tickets where Gemma's answer is accepted
because it predicted an accepted category, but the answer is wrong.

| Setting | Accepted (not escalated) | Accepted and wrong | Accuracy of accepted answers | True category of the wrong ones |
|---|---:|---:|---:|---|
| A | 20 | 7 | 13/20 = 65% | Consumer loan 4, Bank 2, Money transfer 1 |
| B | 11 | 3 | 8/11 = 73% | Consumer loan 2, Bank 1 |

Most are Consumer loan tickets that Gemma calls Debt collection or Mortgage. Escalated tickets were right 43/60 (A)
and 50/69 (B).

## 5. Memory check (brief: both models must be resident)

Run on the Lenovo service PC on 25 Nov, Docker VM 8 CPUs / 7.53 GiB, unchanged from Assignment 1. Unlike the 18 Nov
check, this one also read Ollama's eviction log and the VM's out-of-memory counter, because `ollama ps` alone can list a
model that has been killed. Evidence: `evidence/preflight_lenovo/PREFLIGHT.md`, `4_memory_*.txt`.

| Pair, in load order | Evictions | Runners killed | Ollama container memory | Calls once both loaded |
|---|---:|---:|---|---|
| **Llama, then Gemma** | **0** | **0** | 6.57 / 7.53 GiB | 2.9–3.5 s, load 0.1–0.3 s |
| Gemma, then Llama | 1 (Llama's first load evicts Gemma, which then reloads alongside) | 0 | about 6.55 GiB | 2.7–3.2 s |
| Qwen + Llama (either order) | on every switch | 5 (`oom_kill 5`) | not stable | n/a: **does not fit** |

- **Gemma + Llama fit when Llama is loaded first.** The warm-up in §7 does that.
- Ollama estimates Qwen + Llama at about 8.9 GB (Llama 5.2 GiB + Qwen about 3.7 GB), more than the VM's 7.53 GiB.
- The 18 Nov check (`STEP2_DESIGN_INPUTS.md` §1) reported all three pairs as passing; that is corrected there.
- The Docker memory limit is not raised. The brief says more RAM is not an option, and the machine must stay as it
  was in Assignment 1.

## 6. Implementation in the service

The cascade lives inside `POST /tickets`. The endpoint still accepts one ticket and returns one category, and
`GET /search` and `GET /stats` are unchanged. No code change was needed for the new pair; it is configuration only.

| Item | Implementation |
|---|---|
| Switch | `CASCADE_ENABLED=false` reproduces Assignment 1 exactly (one model, `OLLAMA_MODEL`). This is how the single-model configurations run. |
| Models | `CASCADE_SMALL_MODEL=gemma3:1b-it-q4_K_M`, `CASCADE_LARGE_MODEL=llama3.1:8b-instruct-q4_K_M` |
| Setting | `CASCADE_ESCALATE_ON` = comma-separated categories to **escalate**, i.e. the complement of the accept list. A: `Credit reporting,Credit card,Bank account or service,Consumer loan,Money transfer or service`. B: the same plus `Debt collection`. Changing setting is an `.env` change plus `docker compose up -d --force-recreate api` (`restart` does not re-read `.env`); no code change between settings. |
| Request to each model | The Assignment 1 request with only the model name changed |
| Hiding the answering model | In cascade mode the response's and database's `model` field is one fixed label for every ticket (default `cascade:<small>><large>`, or `CASCADE_LABEL`), so the caller cannot tell which model answered |
| Per-ticket log line | One line per `POST /tickets`, in both modes: `triage {"request_id", "mode", "small_model", "small_answer", "small_ms", "escalated", "reason", "final_model", "large_ms", "category", "outcome"}`. `reason` is `accept`, `category` or `invalid` in cascade mode and `single` otherwise. `small_answer` is the category or `invalid`. `outcome` is `error` when the final model's answer is invalid (HTTP 502). `request_id` is the JMeter `X-Request-ID`. |
| Escalation fraction | Count of `"escalated": true` ÷ count of `triage` lines in the API log for the run, matched to the JMeter request IDs |
| Code | `app/cascade.py` (rule and log line), `app/config.py` (settings, validated at start-up: unknown category names stop the API), `app/classifier.py` (model parameter only), `app/main.py` (endpoint calls the triage). Tests: `tests/test_cascade.py`. |

Tested on the Lenovo on 25 Nov with Gemma → Llama: 4/4 tuning rows gave the rule's answer, including one
escalation for an invalid Gemma answer (row 9849) (`evidence/preflight_lenovo/5_gemma_llama_*`).

## 7. Warm-up for cascade runs

Before each cascade run (after the Ollama restart that every run starts with):

1. Send the team's three fixed warm-up tickets through `POST /tickets`, one at a time. Discard the timings.
2. Run `docker compose exec -T api python - < assignment2/scripts/cascade_warmup.py` and save its output with
   the run. It sends one fixed warm-up ticket directly to each model through Ollama, using the service's request,
   in the order **Llama, Gemma, Llama, Gemma**. Llama goes first so that its load does not evict Gemma (§5).
3. Start only if the script prints `READY`: both models are listed by Ollama and the last two calls loaded in under 1 s.
   Also save `ollama ps` from the container with the run, and the Ollama log lines for evictions and killed runners
   (there should be none).

The single-model runs use the normal Assignment 1 warm-up.

## 8. Open items before the freeze

1. **Pair and settings sign-off.** Gemma → Llama, A = accept Mortgage + Debt collection, B = accept Mortgage (§4).
   Proposed by Ye Kai on 25 Nov from Alfred's pre-flight; team to confirm.
2. **Keep-alive: decided, 30 minutes.** Ollama unloads a model after it has been idle for its keep-alive time
   (5 min by default, as in Assignment 1). With Gemma → Llama, both models are called on most tickets, so an idle gap
   over 5 minutes is less likely than with the earlier Qwen → Llama design. The setting is kept for every configuration
   anyway, so all configurations are run the same way:
   - `OLLAMA_KEEP_ALIVE=30m` is set in `compose.yaml`, once, for **every** Assignment 2 configuration, before any speed run.
   - It is not one of the settings the brief fixes (thread count, parallelism, context length). It is recorded with the
     other Ollama settings and held constant.
   - It only stops Ollama unloading an idle model. It does not change the models' answers, so the Assignment 1 accuracy
     reuse still holds. It does not favour any configuration: single models call their model on every ticket, and every
     run starts with an Ollama restart.
   - It is stated on slide 3 as a change from Assignment 1. The lecturer has been told by email; if they object before
     the speed runs, it reverts to 5 min and every cascade run's Ollama log is checked for reloads instead.
   - Evidence: `OLLAMA_KEEP_ALIVE:30m0s` in the Ollama server-config log on the Lenovo (`evidence/preflight_lenovo/`).
3. **Warm-up re-check on the Lenovo.** `cascade_warmup.py` now loads Llama first. Alfred to run it once with
   Gemma → Llama, setting A, and confirm `READY` with no evictions or killed runners.
4. **Freeze commit:** remove the DRAFT lines from this file and `PREDICTIONS.md`, and commit both together, before the
   cascade accuracy test and before any speed run.
