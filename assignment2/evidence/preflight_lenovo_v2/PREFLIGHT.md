# Pre-flight on the Lenovo service PC, Gemma → Llama (26 Nov 2026)

**Not a benchmark.** Tuning (odd) rows only. Run on the test machine against branch `Assignment2` at `de29028`
(`STEP2.md` and `PREDICTIONS.md` rewritten for Gemma → Llama; `cascade_warmup.py` loads the large model first).
The environment is unchanged from the 25 Nov record (`../preflight_lenovo/environment.txt`). Expected answers
come from the Assignment 1 per-ticket records. Script: `assignment2/scripts/preflight_check.py`.

| Check | Result | File |
|---|---|---|
| Per-run procedure (Ollama restart, recreate API, warm-up) | Done as in `STEP2.md` §7 | `A_0`–`A_3` |
| `cascade_warmup.py` (large model first) | **READY**: Llama, Gemma, Llama, Gemma; the last two calls loaded in 0.10 s and 0.18 s; both models in `ollama ps` | `A_2_warmup.txt`, `A_3_ollama_ps.txt` |
| Setting A (accept Mortgage, Debt collection) | **5/5**: accept Mortgage (9841), accept Debt collection (9853), escalate Credit reporting (9851), escalate invalid (9849), escalate Credit card (9911) | `A_1_env.txt`, `A_4_rows.txt` |
| Setting B (accept Mortgage only), changed by `.env` + API recreate only | **4/4**: accept Mortgage (9841); escalate Debt collection (9871); escalate invalid (9849); 9853 escalated and Llama's answer was invalid → **HTTP 502, not stored** (`/stats` +3 for 4 tickets; `triage` line `"outcome": "error"`) | `B_1`–`B_4` |
| One `triage` line per ticket, `request_id` = `X-Request-ID` | Pass (9/9) | `A_4_rows.txt`, `B_2_rows.txt`, `B_4_triage_lines.log` |
| Response `model` field hides the answering model | Pass: `cascade:gemma3:1b-it-q4_K_M>llama3.1:8b-instruct-q4_K_M` on accepted and escalated tickets | same |
| Both models stay resident for the whole session | Pass: 0 evictions, 0 runner kills, VM `oom_kill 0` from the Ollama restart to the end | `AB_5_counters_after.txt`, `AB_ollama.log` |

The Lenovo was left with `CASCADE_ENABLED=false` (Llama alone) and the setting-A list in `.env`.
