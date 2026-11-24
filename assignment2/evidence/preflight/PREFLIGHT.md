# Pre-flight check of the cascade code (24 Nov 2026)

**Not a benchmark, and not on the test machine.** Run on Eugene's PC (Intel Core Ultra 7 155H; Docker 22 CPUs /
15.4 GiB), not the Lenovo service PC. This checks that the code works with real models. Timings here say nothing
about the Lenovo. **Tuning (odd) rows only**; no test rows were used.

Setup: branch `Assignment2` at `d655cd6`, `docker compose up -d --build`, Ollama 0.12.3. The API's settings were set
per mode with a compose override file, leaving `.env` unchanged. Model IDs match the Lenovo
(`ollama_list.txt`): Llama `46e0c10c039e`, Qwen `0edcdef34593`.

## Results

| Check | Result |
|---|---|
| `compose.yaml` keep-alive reaches Ollama | **Pass**: server config shows `OLLAMA_KEEP_ALIVE:30m0s` (`ollama_keep_alive.txt`); `ollama ps` showed both models "29 minutes from now" after warm-up |
| Single-model mode (`CASCADE_ENABLED=false`, Llama) gives the A1 answers | **Pass**: 5/5 rows match `step5/results/llama3.1-8b/accuracy/predictions.csv` (rows 9991, 9851, 9895, 9957, 9961) |
| `cascade_warmup.py` | **Pass**: `READY`, both models listed. First Qwen call loaded in 10.9 s; the next three loaded in under 0.3 s |
| Cascade A (`Credit card`): accept / escalate as the rule says | **Pass**: 5/5 rows give the answer predicted by the A1 replay. 3 accepted (9991, 9851, 9935); 2 escalated on "Credit card" (9957, 9885) |
| Cascade B (`Credit card,Credit reporting`) | **Pass**: 9935 (Qwen "Credit reporting") escalated to Llama; 9991 accepted |
| One `triage {...}` line per ticket, with the request's `X-Request-ID` | **Pass**: 1 line for each of the 12 tickets |
| Response `model` field hides which model answered | **Pass**: `cascade:qwen3:4b-instruct-2507-q4_K_M>llama3.1:8b-instruct-q4_K_M` on accepted and escalated tickets alike |
| Misspelt `CASCADE_ESCALATE_ON` (`credit card`) is rejected at start-up | **Pass**: `CASCADE_ESCALATE_ON has unknown categories ['credit card']` |

Not exercised here: an invalid Qwen answer (none occurred on these rows) and an invalid Llama answer (HTTP 502).
Both are covered by `tests/test_cascade.py` with a faked Ollama.

## Raw per-ticket records

Printed by the pre-flight script right after each request, from the API's `triage` log lines.
The API container was recreated between modes, which clears its log, so only the setting-B lines are saved as a
file (`triage_lines_cascadeB.log`).

```
single    9991 201 Debt collection          A1 Debt collection          match  escalated=false reason=single
single    9851 201 Debt collection          A1 Debt collection          match  escalated=false reason=single
single    9895 201 Bank account or service  A1 Bank account or service  match  escalated=false reason=single
single    9957 201 Bank account or service  A1 Bank account or service  match  escalated=false reason=single
single    9961 201 Mortgage                 A1 Mortgage                 match  escalated=false reason=single
cascadeA  9991 201 Debt collection          A1 replay Debt collection   match  small=Debt collection  accept   final=qwen
cascadeA  9851 201 Consumer loan            A1 replay Consumer loan     match  small=Consumer loan    accept   final=qwen
cascadeA  9957 201 Bank account or service  A1 replay Bank account...   match  small=Credit card      category final=llama
cascadeA  9885 201 Debt collection          A1 replay Debt collection   match  small=Credit card      category final=llama
cascadeA  9935 201 Credit reporting         A1 replay Credit reporting  match  small=Credit reporting accept   final=qwen
cascadeB  9935 201 Credit reporting         A1 replay Credit reporting  match  small=Credit reporting category final=llama
cascadeB  9991 201 Debt collection          A1 replay Debt collection   match  small=Debt collection  accept   final=qwen
```
