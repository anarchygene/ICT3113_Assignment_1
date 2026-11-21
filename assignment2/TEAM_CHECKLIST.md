# Assignment 2: checklist for the steps after the cascade code

What to watch for, by person, once the cascade code and `STEP2.md` are on `Assignment2`.
Due **Fri 27 Nov, 23:59**. Brief references are to *ICT3113 Assignment 2*, Steps 1–4.

## 0. Rules that apply to everyone

- **Freeze before measuring.** `STEP2.md` and `PREDICTIONS.md` are committed **together**, with the DRAFT lines removed,
  before the cascade accuracy test and before any speed run. After that commit, neither file is edited. Anything
  learned later goes in a separate results file. The commit history is our evidence, so don't rebase or amend past it.
- **No test-set results before the freeze.** Until then, nobody scores Qwen, Gemma or the cascade on even rows.
  Llama's Step 1 run (the limits) is the only exception.
- **Model input comes from the CSVs, not Excel.** Use `assignment2/data/test_set.csv` and `tuning_set.csv`.
  The Excel sheets collapsed double spaces in 26 narratives.
- **Nothing about the machine or Ollama changes between configurations.** That means:
  - same Lenovo, Docker at 8 CPUs / 7.53 GiB, Ollama 0.12.3, same model IDs;
  - `OLLAMA_NUM_PARALLEL=1`, context 4096, same keep-alive;
  - plugged in, same power plan (Balanced in A1), same network as A1, no other heavy apps, Windows updates paused.
  
  If anything does change, write it down and re-run the configurations it affects.
- **Keep every raw file**: `.jtl` files, API logs, Ollama logs, `/stats` before and after, `ollama ps` output.
  Every figure on slides 4–7 must trace back to one of them. Fabricated or irreconcilable figures are an
  academic-integrity matter, not a marking deduction.
- **Configuration changes go through `.env`, then `docker compose up -d --force-recreate api`.**
  `docker compose restart api` does **not** re-read `.env`. Save the output of
  `docker compose exec api env | grep -E "OLLAMA_MODEL|CASCADE"` with every run, as proof of which configuration
  ran (the `triage` log line does not record the escalation list).
- **A misspelt `CASCADE_ESCALATE_ON` stops the API at start-up.** That's deliberate. If `/health` fails after a
  change, check `docker compose logs api` first.

## 1. Ye Kai: close the rule (before the freeze)

- [ ] Confirm setting B in `STEP2.md` §4b: Credit card + Credit reporting (recommended), or Credit card + Consumer loan.
      Whichever you pick, `PREDICTIONS.md` must match.
- [ ] Add the brief's "slip-through" check to `STEP2.md` §4b: how often a wrong Qwen answer is accepted because Qwen
      predicted a category that isn't escalated. Tuning-set figures:
      - **A:** 14 of 63 accepted answers are wrong (49/63 right).
      - **B, with Credit card + Credit reporting:** 13 of 55 are wrong (42/55 right).
- [ ] Once the freeze is in, start slide 2: a diagram of the cascade, the rule in full, the two settings, and why this
      rule. Everything is in `STEP2.md`; the slide must not say anything the file doesn't.

## 2. Youxiong: predictions, workload list, speed analysis

Before the freeze:
- [ ] `PREDICTIONS.md` lists **two** cascade settings (A and B), not three, matching `STEP2.md`.
- [ ] Load predictions are restated at the **Assignment 2 test rate** (one ticket every 2×S seconds), not A1's
      105 tickets/h. S isn't measured yet, so predict it, or predict relative to Llama alone.
- [ ] The required prediction points are specific enough to be shown wrong:
      - the fastest configuration that passes;
      - for each cascade setting, escalation fraction, accuracy and median latency;
      - the categories expected to lose the most.
- [ ] Speed-test workload: a fixed, ordered list of rows from **9000–9839 only** (never golden rows), with some typical
      and some long tickets. Include enough for the longest run (about 30 per run plus spare). Commit it as a file
      before the first run; it's a required supporting file.
- [ ] Three fixed warm-up tickets: not golden rows and not in the workload list. Use the same three for every run.

After the runs (brief Step 4, "Report, per run"):
- [ ] For each run, report:
      - requests sent, completed, errored and **unfinished** (keep unfinished runs; report them as such);
      - p50 from successful samples in the `.jtl`;
      - throughput (completed per second) and error rate.
- [ ] For each configuration, report the mean and spread of p50 across the 3 runs, and **p95 pooled across all 3 runs**
      with the number of samples it's based on. **No p99.** A1's `analyse_jtl.py` prints p99 and uses A1 load-level
      names, so adapt it rather than reusing its output.
- [ ] Escalation fraction under load, for each cascade run: count `"escalated": true` over all `triage` lines in that
      run's API log, matched to the JMeter request IDs (drop warm-up tickets). Compare it with the accuracy-test
      fraction, and explain any large gap (different tickets).
- [ ] Reconcile the `/stats` before/after difference with the completed POSTs for every run.

## 3. Alfred: check the code on the Lenovo, then the speed tests

Before the freeze (doesn't count as a benchmark):
- [ ] Pull `Assignment2`, add the `CASCADE_*` lines from `.env.example` to the Lenovo's `.env` (it isn't in git), and
      rebuild with `docker compose up -d --build api`.
- [ ] Set `CASCADE_ENABLED=false` and `OLLAMA_MODEL` to Llama. Send 3–5 **tuning** rows and confirm the answers match A1's
      `step5/results/llama3.1-8b/accuracy/predictions.csv`. This restores the "unchanged service" claim in
      `ACCURACY_LIMITS.md`, which was true before `app/` changed for the cascade.
- [ ] Turn the cascade on with setting A and send a few **tuning** rows:
      - `docker compose logs api` shows one `triage {...}` line per ticket, with `request_id` matching `X-Request-ID`;
      - the response `model` field is the same for escalated and non-escalated tickets;
      - `cascade_warmup.py` prints `READY`.
- [ ] Record versions, model IDs, Ollama server settings and the Docker limits once (brief Step 4, Set-up). Re-check
      them before each configuration.

Setting the rate (brief Step 4, Set-up):
- [ ] Restart Ollama, do the normal warm-up, then send **three different** typical-length tickets to **Llama alone**,
      one at a time. Never repeat a ticket: Ollama's prompt cache makes repeats fast. S = the middle time.
- [ ] Rate = 1 ticket every 2×S seconds. Run length = S minutes, at least 5. Use the **same rate and length for every
      configuration**. Record S, the three timings and their row numbers.
- [ ] JMeter settings, in this order:
      - HTTP response timeout = 10×S seconds, at least 5 minutes;
      - Open Model schedule pause = timeout + at least 1 minute.
      
      Load generator on the Ryzen desktop, never the Lenovo.
- [ ] A1's plan also sent `GET /search` traffic. Decide whether to keep it. Either way, it must be identical for every
      configuration and stated on slide 3.
- [ ] Compare the rate with the client peak from A1's workload model (81/h, or 105/h with headroom), and note which
      side of it we are on, for the limitations slide.

Every run (brief Step 4, "Each run"):
- [ ] `docker compose restart ollama`, wait for `/health`, then send the 3 fixed warm-up tickets and discard them.
- [ ] **Cascade runs:** run `docker compose exec -T api python - < assignment2/scripts/cascade_warmup.py`, save the output,
      and start only on `READY`. Save `ollama ps` showing both models.
- [ ] `/stats` before → JMeter run → let it drain → `/stats` after. Save the API log, Ollama log, `.jtl` and env dump.
- [ ] Check the Ollama log for **model loads during the run**. If Llama was unloaded (keep-alive 5 min) and reloaded,
      that escalation measures loading, not the cascade. Report it and say so. (The keep-alive question is with the
      lecturer; until answered, nothing changes.)

What gets speed-tested (only after Justin's accuracy results):
- [ ] **Always:** Llama alone, cascade A and cascade B, 3 runs each, even if the cascade fails accuracy (mark it so).
- [ ] Qwen alone and Gemma alone **only if** they pass both accuracy limits.
- [ ] No A1 speed figures are reused for anything.

## 4. Justin: accuracy tests (after the freeze)

- [ ] Run each configuration **once** on the 80 test rows. Never re-run to get a better number.
- [ ] Single models may reuse A1 records (unchanged digest, prompt, Ollama, machine), even rows only, **saying so on
      slide 4**. Llama is already re-run (`assignment2/results/step1_top_model_test_set/`). Qwen and Gemma: score the
      even rows of their A1 `predictions.csv`.
- [ ] Cascade A and B go through `POST /tickets` with `accuracy_test.py --model "cascade:qwen3:4b-instruct-2507-q4_K_M>llama3.1:8b-instruct-q4_K_M"`.
      The script stops if the service's model label doesn't match. Use a distinct `--label` per setting so request IDs
      (`acc-<label>-<row>`) are unique, and save the API log right after each run.
- [ ] For each configuration, report:
      - overall correct out of 80 and %;
      - per category, correct/n against the minimum correct in `ACCURACY_LIMITS.md`;
      - a confusion matrix.
      
      Invalid answers and 502s count as wrong. Ignore the A1 "R6 (≥ 70%)" column in the generated `summary.md`.
- [ ] For each cascade setting, also report from the `triage` lines:
      - number escalated, and the escalation fraction;
      - accuracy of escalated vs non-escalated tickets;
      - how many escalations were for invalid answers vs for category.
- [ ] Flag Mortgage (7), Credit card (6) and Consumer loan (8) as too small for a fair per-category test, and note that
      one Credit card error fails that limit.
- [ ] Hand Alfred the list of configurations that pass both limits. That list decides which get speed-tested.

## 5. Eugene: rule owner

- [ ] Send the lecturer the keep-alive question (`STEP2.md` §8) and share the answer with Alfred.
- [ ] Do the freeze commit once Ye Kai and Youxiong are done.
- [ ] Fix code problems Alfred finds **before** the freeze. After any benchmark has run, a code change means noting it
      and re-running the configurations it touches.
