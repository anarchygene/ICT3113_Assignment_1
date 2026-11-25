# Step 2 design inputs: memory check and tuning-set evidence

Prepared 18 Nov 2026 on the Lenovo service PC. Inputs for choosing the cascade pair and escalation rule.
**Not** the escalation rule itself, which the team decides and commits with the predictions before any Assignment 2 benchmark.
No test-set (even-row) results were used here. The only test-set run so far is Step 1 (Llama alone, for the limits).

## 1. Memory check (brief Step 2, "Memory")

Method: `assignment2/scripts/memory_check.py`, run inside the api container. Ollama was restarted before each pair, so nothing was loaded at the start.
Each pair ran 8 synthetic tickets (none from the dataset) in the order A, A, B, B, A, B, A, B, using the service's exact request (same system prompt, JSON mode, temperature 0, `num_ctx` 4096).
After each call the script recorded `load_duration` and Ollama's loaded-model list. Docker VM: 8 CPUs, 7.53 GiB (unchanged from Assignment 1).
Raw output and `ollama ps`: `assignment2/evidence/memory_check/*.txt`.

| Pair (small + large) | `ollama ps` lists both after alternating | Reload on alternating calls | Ollama container memory | Alternating-call wall time vs back-to-back |
|---|---|---|---|---|
| Qwen3 4B + Llama 3.1 8B | yes (3.7 + 5.6 GB) | no (load 0.3 s) | 6.92 / 7.53 GiB | Llama 4.0 s → 33.2 / 15.8 s; Qwen 2.1 s → 22.2 s |
| Gemma 3 1B + Llama 3.1 8B | yes (1.2 + 5.6 GB) | no (load 0.1–0.3 s) | 6.60 / 7.53 GiB | Llama 4.0 s → 16.6 / 15.2 s; Gemma 1.7 s → 6.5 / 6.3 s |
| Gemma 3 1B + Qwen3 4B | yes (1.2 + 3.7 GB) | no (load 0.1–0.5 s) | 5.18 / 7.53 GiB | Gemma 2.0 s → 3.4 / 1.8 s; Qwen 2.8 s → 7.8 / 2.1 s |

- ~~**All three pairs pass the brief's check**~~ **CORRECTED 25 Nov:** Qwen + Llama does **not** fit. The Lenovo pre-flight found Ollama evicting one model on every switch and the kernel's out-of-memory killer stopping the Llama runner (`oom_kill 5`), while `ollama ps` still listed both. This check looked only at `ollama ps` and `load_duration`, so it missed that. Gemma + Llama and Gemma + Qwen were re-checked with eviction and out-of-memory counters and do fit. Evidence: `evidence/preflight_lenovo/PREFLIGHT.md`.
- **Caution for the two pairs with Llama:** they run at 88–92% of the VM's memory, and calls slow down 4–10× once the models alternate, even though nothing reloads. The likely cause is model pages being pushed out of memory and re-read from disk. The pair with headroom (Gemma + Qwen) barely slows. This is 8 short calls per pair, so treat it as a lead, not a measurement; the speed test will show whether it holds under load.
- Back-to-back calls are fast partly because Ollama reuses the cached system prompt, so they understate normal latency. Compare pairs with each other, not with the Assignment 1 latencies.

## 2. Tuning-set (odd rows) behaviour of each model, from the Assignment 1 records

Unchanged models, prompt, Ollama and machine (verified in `ACCURACY_LIMITS.md`), so the Assignment 1 per-ticket answers are reused, restricted to the 80 odd rows.

| Model | Tuning accuracy | Invalid outputs |
|---|---:|---:|
| Gemma 3 1B | 28/80 = 35.0% | 15 |
| Qwen3 4B | 54/80 = 67.5% | 0 |
| Llama 3.1 8B | 60/80 = 75.0% | 1 |

**When the model predicts X, how often is X right?** This is what a category-based rule can use, since the true category is unknown when a ticket arrives.

| Predicted category | Gemma | Qwen | Llama |
|---|---:|---:|---:|
| Credit reporting | 12/32 | 7/8 | 9/9 |
| Debt collection | 5/9 | 8/10 | 11/14 |
| Mortgage | 8/11 | **10/10** | 10/10 |
| Credit card | 0/1 | **5/17** | 5/16 |
| Bank account or service | 2/4 | 10/16 | 10/13 |
| Consumer loan | 1/7 | 7/11 | 6/6 |
| Money transfer or service | 0/1 | 7/8 | 9/11 |
| (invalid output) | 0/15 | n/a | 0/1 |

- Qwen's "Credit card" answers are mostly wrong (5/17 right): it labels many Credit-reporting and Bank tickets as Credit card. Its other predictions are mostly right.
- Gemma is reliable on very little, and 15 of its 80 answers are invalid. Any Gemma cascade must escalate invalid answers and will escalate most tickets.
- Ticket length predicts errors only weakly. Qwen: shorter half 30/40 right, longer half 24/40. Llama: 33/40 vs 27/40. A length rule would escalate many correct answers.

## 3. Replay of candidate rules on the tuning set (simulation, not a measurement)

Each candidate was replayed with the Assignment 1 answers: accept the small model's answer unless the rule escalates, in which case take Llama's answer; invalid output always escalates.
"Est. latency" = small-model p50 + escalation fraction × Llama p50, using Assignment 1 sequential medians (Gemma 2.4 s, Qwen 7.9 s, Llama 13.2 s). It ignores queueing and the memory slowdown in §1.

| Candidate (tuning set) | Accuracy | Escalated | Est. mean latency | vs Llama alone (75.0%, 13.2 s) |
|---|---:|---:|---:|---|
| Qwen alone | 54/80 = 67.5% | 0% | 7.9 s | −7.5 pts; Credit reporting 7/14 |
| Qwen → Llama, escalate if Qwen says **Credit card** | 59/80 = 73.8% | 17/80 = 21% | 10.7 s | −1.2 pts, about 19% faster on paper |
| Qwen → Llama, escalate if **Credit card or Consumer loan** | 59/80 = 73.8% | 28/80 = 35% | 12.5 s | same accuracy, little speed gain |
| Qwen → Llama, escalate if **Credit card or Bank account** | 59/80 = 73.8% | 33/80 = 41% | 13.3 s | no faster than Llama |
| Gemma → Llama, accept Gemma only on Mortgage | 58/80 = 72.5% | 69/80 = 86% | 13.8 s | slower than Llama |
| Gemma → Llama, accept Mortgage + Debt collection | 56/80 = 70.0% | 60/80 = 75% | 12.3 s | little gain |

Observations for the team:

1. **Qwen → Llama with a category rule is the only cascade that looks able to beat Llama alone.** Escalating Qwen's "Credit card" answers catches its biggest error pattern, which is why Credit reporting rises from 7/14 to 9/14, at 21% escalation.
2. **Gemma cascades escalate 75–86% of tickets** (Gemma is unreliable and often invalid), so on paper they barely beat or lose to Llama.
3. **The risk for Qwen → Llama is the memory slowdown in §1.** Escalated tickets switch models, and that pair showed the worst alternating-call slowdown. The speed test decides; the on-paper estimate does not.
4. Widening the escalation list beyond Credit card raises escalation without improving tuning accuracy. A natural second setting for the trade-off is one wider list (e.g. Credit card + Consumer loan).
5. Qwen alone is the fastest candidate, but on the tuning set it gets only 7/14 Credit reporting (50%), below that category's test-set floor of 58.7%. Whether it passes is decided only by the Step 4 test-set run.
