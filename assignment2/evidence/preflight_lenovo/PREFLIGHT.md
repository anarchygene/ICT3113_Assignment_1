# Pre-flight on the Lenovo service PC (25 Nov 2026)

**Not a benchmark.** Tuning (odd) rows and synthetic tickets only; no test-set (even) rows were used.
This is the test machine (`TEAM_CHECKLIST.md` §3, "before the freeze"). Branch `Assignment2` at `72cbd12`;
the environment record is in `environment.txt`. Expected answers come from the Assignment 1 per-ticket
records (`step5/results/<model>/accuracy/predictions.csv`). Script: `assignment2/scripts/preflight_check.py`.
The laptop was restarted before the session.

## Summary

| Check | Result |
|---|---|
| Environment unchanged from A1 | **Pass**: Docker 29.5.3, VM 8 CPUs / 7.53 GiB, Ollama 0.12.3, same three model IDs, `NUM_PARALLEL=1`, context 4096 (`environment.txt`) |
| Keep-alive 30 min reaches Ollama | **Pass**: `OLLAMA_KEEP_ALIVE:30m0s`; `ollama ps` shows "29 minutes from now" |
| Cascade off (`CASCADE_ENABLED=false`, Llama) gives the A1 answers | **Pass**: 5/5 rows match (9847, 9843, 9857, 9871, 9849), different rows from Eugene's 5. One `triage` line each, `reason=single` (`1_single_llama.txt`) |
| **Qwen + Llama both resident** | **FAIL: not feasible on this machine.** See below |
| Cascade code on the test machine (run with Gemma → Llama, `ESCALATE_ON=Credit card`) | **Pass**: 4/4 rows give the rule's answer, including the first real-model test of **escalate-on-invalid** (9849). One `triage` line per ticket with the `X-Request-ID`; response `model` is the same cascade label whether Gemma or Llama answered; no eviction or kill during the four tickets (`5_gemma_llama_*`) |
| `cascade_warmup.py` | **Needs a fix**: prints NOT READY for Gemma → Llama even though both end up resident. Its order (small, large, small, large) makes the large model's first load evict the small one, so the small model's second call is a reload (1.55 s). That call is one of the two that must load in under 1 s. Loading the large model first, or adding a final small + large pair, would fix it |

## Qwen + Llama do not fit together (7.53 GiB Docker VM)

Ollama's own estimate is 5.2 GiB for Llama (`memory.required.full`, KV 512 MiB) plus about 3.7 GB for Qwen, about
8.9 GB in total, more than the VM's 7.53 GiB. What happened:

- **Qwen loaded, then Llama** (`cascade_warmup.py`, cascade A): every switch reloaded a model (Qwen 14.8 s, Llama
  10–12 s). Ollama logged "model requires more memory than is currently available, evicting a model to make space"
  and twice **"llama runner process no longer running … signal: killed"** (`2_cascadeA_warmup.txt`,
  `ollama_evictions_and_kills.log`).
- **Llama loaded, then Qwen** (`3_memory_llama_first.txt`): both were listed briefly, then the Llama runner was
  **killed** and reloaded (9.2 s), evicting Qwen. The script stopped after 5 of 8 calls.
- The VM kernel's out-of-memory counter reads **`oom_kill 5`** since Docker started that morning. All five kills
  happened during these Qwen + Llama loads, and none during any other pair.
- **`ollama ps` is not enough evidence on its own:** at the end of the Llama-first run it still listed both models
  while the Ollama container held only 559 MiB.

**Correction to `STEP2_DESIGN_INPUTS.md` §1 (18 Nov):** that check reported Qwen + Llama as passing because
`ollama ps` listed both. It did not check Ollama's eviction log or the kernel's out-of-memory counter. The
co-residency it saw was not stable. Under the brief's rule ("a cascade is only tested with both models resident"),
**the Qwen → Llama cascade in `STEP2.md` cannot be tested on this machine.**

## Pairs that do fit (re-checked with eviction and out-of-memory counters)

| Pair | Evictions | Runners killed (VM `oom_kill` before → after) | Calls once both loaded | File |
|---|---|---|---|---|
| Gemma then Llama | 1 (Llama's first load evicts Gemma, which then reloads alongside) | 0 (5 → 5) | 2.7–3.2 s | `4_memory_gemma_llama.txt` |
| Llama then Gemma | 0 | 0 (5 → 5) | 2.9–3.5 s | `4_memory_llama_gemma.txt` |
| Gemma then Qwen | 0 | 0 (5 → 5) | 2.5–2.7 s | `4_memory_gemma_qwen.txt` |

Ollama container memory with both loaded: Gemma + Llama about 6.55 GiB, Gemma + Qwen 5.08 GiB (of 7.53 GiB).
The Gemma + Llama pair is stable once Llama is loaded first.

## What this means for the freeze (for the team)

`STEP2.md` and `PREDICTIONS.md` are built on Qwen → Llama and must be revised before the freeze. The brief's options:
try a smaller pair (Gemma → Llama, or Gemma → Qwen), or report that the chosen cascade is not feasible, with this
evidence. Tuning-set replays for the Gemma pairs are in the message to the team (25 Nov). In short:
Gemma predicts "Credit reporting" for 32 of 80 tuning tickets and is right on only 12 of them, so any Gemma
cascade that gets near the 66.25% limit escalates about 75% of tickets.
